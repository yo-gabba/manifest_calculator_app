from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from datetime import datetime, timedelta
from models import db, Driver, Manifest, Stop, ZipZone
from sqlalchemy import func
import os


app = Flask(__name__)

# Database config
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'manifest.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "gabbifer98"

# Initialize the database with app
db.init_app(app)

# Zone ranges and rates
ZONE_RANGES = [
    (0, 20, 'A'),
    (20.1, 30, 'B'),
    (30.1, 40, 'C'),
    (40.1, 60, 'D'),
    (60.1, 80, 'E'),
    (80.1, 100, 'F'),
    (100.1, 120, 'G'),
    (120.1, 140, 'H'),
    (140.1, 160, 'I'),
    (160.1, 500, 'J')
]

STOP_RATES = {
    'A': 11.11,
    'B': 12.37,
    'C': 13.38,
    'D': 14.39,
    'E': 17.42,
    'F': 19.44,
    'G': 21.46,
    'H': 23.48,
    'I': 25.50,
    'J': 27.52
}

PALLET_RATES = {
    'A': 9.09,
    'B': 9.34,
    'C': 9.34,
    'D': 9.34,
    'E': 11.36,
    'F': 11.36,
    'G': 11.36,
    'H': 11.36,
    'I': 11.36,
    'J': 11.36
}

ACCESSORIAL_RATES = {
    'Liftgate': 20.0,
    'Residential': 15.0,
    'Inside Delivery': 25.0
}


# Helper functions
def get_zone(miles):
    for min_m, max_m, zone in ZONE_RANGES:
        if min_m <= miles <= max_m:
            return zone
    return None

def calculate_stop_total(miles, pallet_spaces, accessorials=''):
    """
    Calculate freight and total charges for a stop.
    - Look up zone from miles.
    - Base = STOP_RATES[zone] + PALLET_RATES[zone] * pallet_spaces
    - Add accessorial charges.
    Returns (freight_total, total, zone).
    """
    zone = get_zone(miles)
    if not zone:
        return 0.0, 0.0, ''  # no valid zone, no charges

    # Base freight
    freight_total = STOP_RATES.get(zone, 0) + (PALLET_RATES.get(zone, 0) * float(pallet_spaces or 0))

    # Accessorial charges
    accessorial_total = 0.0
    if accessorials:
        for key, val in ACCESSORIAL_RATES.items():
            if key.lower() in accessorials.lower():
                accessorial_total += val

    total = freight_total + accessorial_total
    return freight_total, total, zone



# ROUTES 
@app.route('/')
def index():
    return render_template('index.html', active_page='dashboard')

@app.context_processor
def inject_drivers():
    all_drivers = Driver.query.order_by(Driver.name).all()
    return dict(all_drivers=all_drivers)

@app.route('/drivers', methods=['GET', 'POST'])
def drivers():
    all_drivers = Driver.query.order_by(Driver.name).all()
    selected_driver_id = request.form.get('driver') or request.args.get('driver')
    manifests = []
    totals = {'day_miles': 0, 'week_miles': 0, 'day_total': 0.0, 'week_total': 0.0}

    if selected_driver_id:
        manifests = Manifest.query.filter_by(driver_id=selected_driver_id).order_by(Manifest.date.asc()).all()
        today = datetime.today().date()
        start_of_week = today - timedelta(days=today.weekday())
        daily = [m for m in manifests if m.date == today]
        weekly = [m for m in manifests if start_of_week <= m.date <= today]
        totals['day_miles'] = sum(m.total_miles or 0 for m in daily)
        totals['week_miles'] = sum(m.total_miles or 0 for m in weekly)
        totals['day_total'] = sum(m.day_total or 0 for m in daily)
        totals['week_total'] = sum(m.day_total or 0 for m in weekly)

    return render_template(
        'drivers.html',
        drivers=all_drivers,
        selected_driver_id=selected_driver_id,
        manifests=manifests,
        totals=totals,
        active_page='drivers'
    )


@app.route('/manifests/new', methods=['POST'])
def create_manifest():
    driver_id = int(request.form['driver'])
    date_obj = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
    start = int(request.form['start_odometer'])
    end = int(request.form['end_odometer'])
    total_miles = end - start

    manifest = Manifest(
        driver_id=driver_id,
        date=date_obj,
        start_odometer=start,
        end_odometer=end,
        total_miles=total_miles,
        day_total=0.0
    )
    db.session.add(manifest)
    db.session.commit()
    return redirect(url_for('manifest_detail', manifest_id=manifest.id))

@app.route('/manifests/<int:manifest_id>/delete', methods=['POST'])
def delete_manifest(manifest_id):
    manifest = Manifest.query.get_or_404(manifest_id)
    db.session.delete(manifest)
    db.session.commit()
    return redirect(url_for('drivers'))


@app.route('/manifest/<int:manifest_id>', methods=['GET'])
def manifest_detail(manifest_id):
    manifest = Manifest.query.get_or_404(manifest_id)
    stops = Stop.query.filter_by(manifest_id=manifest_id).order_by(Stop.id.asc()).all()
    return render_template('manifest_detail.html', manifest=manifest, stops=stops, active_page='drivers')


@app.route('/manifest/<int:manifest_id>/stops', methods=['POST'])
def add_stop(manifest_id):
    manifest = Manifest.query.get_or_404(manifest_id)

    # Grab form data
    zip_code = request.form.get('zip_code', '')
    pallet_spaces = float(request.form.get('pallet_spaces', 0))
    accessorials = request.form.get('accessorials', '')

    # Try to look up miles + zone from ZipZone
    zone_entry = ZipZone.query.filter_by(zip_code=zip_code).first()

    if not zone_entry:
        # ZIP not found → prompt user to add it
        flash(f"ZIP {zip_code} not found in database. Please add miles and zone first.")
        return redirect(url_for('add_zip', zip_code=zip_code, manifest_id=manifest_id))
    
    # ZIP found → use its values
    miles = zone_entry.miles_from_warehouse
    zone = zone_entry.zone

    # Calculate freight/total with given or looked-up miles
    freight_total, total, calc_zone= calculate_stop_total(miles, pallet_spaces, accessorials)
    zone = zone or calc_zone

    stop = Stop(
        manifest_id=manifest_id,
        type=request.form.get('type', ''),
        city=request.form.get('city', ''),
        zip_code=zip_code,
        zone=zone,
        pallets=int(request.form.get('pallets', 0)),
        pallet_spaces=pallet_spaces,
        miles=miles,
        rate=freight_total,
        accessorials=accessorials,
        total=total
    )
    db.session.add(stop)
    db.session.flush()

    # Recalculate manifest day_total
    manifest.day_total = db.session.query(func.coalesce(func.sum(Stop.total), 0.0))\
        .filter_by(manifest_id=manifest_id).scalar()
    db.session.commit()
    return redirect(url_for('manifest_detail', manifest_id=manifest_id))


@app.route("/edit_stop/<int:stop_id>/<int:manifest_id>", methods=["GET", "POST"])
def edit_stop(stop_id, manifest_id):
    stop = Stop.query.get_or_404(stop_id)

    if request.method == "POST":
        # Update stop fields
        stop.type = request.form["type"]
        stop.city = request.form["city"]
        stop.zip_code = request.form["zip_code"]
        stop.pallets = request.form["pallets"]
        stop.pallet_spaces = request.form["pallet_spaces"]
        stop.accessorials = request.form["accessorials"]

        # If zone is set, we lock miles. If not, update it from form.
        if not stop.zone:
            stop.miles = request.form.get("miles", 0)

        # Recalculate rate + total
        stop.rate, stop.total, stop.zone = calculate_stop_total(
            stop.miles, stop.pallet_spaces, stop.accessorials
        )

        db.session.commit()
        flash("Stop updated successfully.", "success")
        return redirect(url_for("manifest_detail", manifest_id=manifest_id))

    return render_template("edit_stop.html", stop=stop, manifest_id=manifest_id)


@app.route('/stops/<int:stop_id>/delete', methods=['POST'])
def delete_stop(stop_id):
    stop = Stop.query.get_or_404(stop_id)
    manifest_id = stop.manifest_id
    db.session.delete(stop)
    db.session.flush()
    new_total = db.session.query(func.coalesce(func.sum(Stop.total), 0.0)).filter_by(manifest_id=manifest_id).scalar()
    manifest = Manifest.query.get(manifest_id)
    manifest.day_total = new_total
    db.session.commit()
    return redirect(url_for('manifest_detail', manifest_id=manifest_id))


@app.route('/zip_lookup/<zip_code>')
def zip_lookup(zip_code):
    zone_entry = ZipZone.query.filter_by(zip_code=zip_code).first()
    if zone_entry:
        return jsonify({
            'miles': zone_entry.miles_from_warehouse,
            'zone': zone_entry.zone
        })
    return jsonify({'miles': '', 'zone': ''})

@app.route('/zip/add', methods=['GET', 'POST'])
def add_zip():
    if request.method == 'POST':
        zip_code = request.form['zip_code'].strip()
        miles = float(request.form['miles'])
        zone = request.form['zone'].strip().upper()

        new_zip = ZipZone(
            zip_code=zip_code,
            miles_from_warehouse=miles,
            zone=zone
        )
        db.session.add(new_zip)
        db.session.commit()

        flash(f"ZIP {zip_code} added successfully.")
        # Redirect back to the manifest that triggered this
        manifest_id = request.form.get('manifest_id')
        if manifest_id:
            return redirect(url_for('manifest_detail', manifest_id=manifest_id))
        return redirect(url_for('drivers'))

    # GET → render form
    zip_code = request.args.get('zip_code', '')
    manifest_id = request.args.get('manifest_id', None)
    return render_template('add_zip.html', zip_code=zip_code, manifest_id=manifest_id)




@app.route('/reports')
def reports():
    return render_template('reports.html', active_page='reports')


@app.route('/logout')
def logout():
    return render_template('logout.html', active_page='logout')


@app.route('/login')
def login():
    return render_template('login.html', active_page='login')


if __name__ == '__main__':
    app.run(debug=True)

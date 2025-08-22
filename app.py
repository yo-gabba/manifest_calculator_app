from flask import Flask, render_template, request
from models import db, Driver, Manifest
from datetime import datetime, timedelta
from sqlalchemy import func
import os

app = Flask(__name__)

# Database config
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'manifest.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with app
db.init_app(app)

#ROUTES
# Route for the dashboard / home page
@app.route('/')
def index():
    return render_template('index.html', active_page='dashboard')

# Route for the Drivers tab
@app.route('/drivers', methods=['GET', 'POST'])
def drivers():
    drivers = Driver.query.all()
    selected_driver_id = request.form.get('driver') if request.method == 'POST' else None

    # Handle adding a new manifest
    if request.method == 'POST' and 'start_odometer' in request.form:
        start = float(request.form['start_odometer'])
        end = float(request.form['end_odometer'])
        total_miles = end - start
        rate = float(request.form['weekly_rate'])
        percentage = float(request.form['payback_percentage'])
        payback_amount = total_miles * rate * percentage

        manifest = Manifest(
            driver_id=selected_driver_id,
            date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
            start_odometer=start,
            end_odometer=end,
            total_miles=total_miles,
            weekly_rate=rate,
            payback_percentage=percentage,
            payback_amount=payback_amount
        )
        db.session.add(manifest)
        db.session.commit()

    totals = {'day_miles': 0, 'week_miles': 0, 'day_payback': 0, 'week_payback': 0}

    if selected_driver_id:
        driver = Driver.query.get(selected_driver_id)
        manifests = driver.manifests

        today = datetime.today().date()
        start_of_week = today - timedelta(days=today.weekday())  # Monday

        # Daily totals (for today)
        daily_manifests = [m for m in manifests if m.date == today]
        totals['day_miles'] = sum(m.total_miles for m in daily_manifests)
        totals['day_payback'] = sum(m.payback_amount for m in daily_manifests)

        # Weekly totals
        weekly_manifests = [m for m in manifests if start_of_week <= m.date <= today]
        totals['week_miles'] = sum(m.total_miles for m in weekly_manifests)
        totals['week_payback'] = sum(m.payback_amount for m in weekly_manifests)

    return render_template(
        'drivers.html',
        drivers=drivers,
        selected_driver_id=selected_driver_id,
        totals=totals,
        active_page='drivers'
    )

# Route for the Reports tab
@app.route('/reports')
def reports():
    return render_template('reports.html', active_page='reports')

# Route for the Logout page
@app.route('/logout')
def logout():
    return render_template('logout.html', active_page='logout')

# Route for the Login page
@app.route('/login')
def login():
    return render_template('login.html', active_page='login')


if __name__ == '__main__':
    app.run(debug=True)

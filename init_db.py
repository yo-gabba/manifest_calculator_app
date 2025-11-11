from app import app
from models import db, Driver, ZipZone, Manifest, Stop
import os, csv, random
from datetime import date, timedelta

db_path = 'instance/manifest.db'

# Delete existing database (dev/demo only!)
if os.path.exists(db_path):
    os.remove(db_path)
    print("🗑️ Deleted old database.")

with app.app_context():
    # Create tables
    db.create_all()
    print("✅ Database and tables created!")

    # Add sample drivers
    sample_drivers = ['Gabby', 'Marcus', 'Alex', 'Taylor', 'Jordan', 'Chris']
    for name in sample_drivers:
        if not Driver.query.filter_by(name=name).first():
            driver = Driver(name=name)
            db.session.add(driver)
    db.session.commit()
    print(f"✅ Added sample drivers: {', '.join(sample_drivers)}")

    # Import ZipZones from CSV
    csv_file = "zipzones.csv"
    if os.path.exists(csv_file):
        with open(csv_file, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not ZipZone.query.filter_by(zip_code=row['zip_code']).first():
                    zone = ZipZone(
                        zip_code=row['zip_code'],
                        miles_from_warehouse=float(row['miles_from_warehouse']),
                        zone=row['zone']
                    )
                    db.session.add(zone)
        db.session.commit()
        print(f"✅ Imported {ZipZone.query.count()} zip zones from CSV.")
    else:
        print("⚠️ CSV file not found, skipping zip zone import.")

    # Create sample manifests with stops
    all_drivers = Driver.query.all()
    all_zones = ZipZone.query.limit(10).all()  # use first 10 for demo
    today = date.today()

    for i in range(3):  # 3 sample manifests
        driver = random.choice(all_drivers)
        manifest_date = today - timedelta(days=i)
        manifest = Manifest(
            driver_id=driver.id,
            date=manifest_date,
            start_odometer=10000 + i * 300,
            end_odometer=10000 + i * 300 + 120,
            total_miles=120,
            day_total=0.0  # will update after adding stops
        )
        db.session.add(manifest)
        db.session.commit()

        # Add 3–4 stops per manifest
        num_stops = random.randint(3, 5)
        total_day_earnings = 0
        for _ in range(num_stops):
            zone = random.choice(all_zones)
            pallets = random.randint(1, 12)
            miles = zone.miles_from_warehouse
            rate = round(random.uniform(25, 45), 2)
            total = round(pallets * rate, 2)

            stop = Stop(
                manifest_id=manifest.id,
                type=random.choice(['Delivery', 'Pickup']),
                city=f"City {zone.zone}",
                zip_code=zone.zip_code,
                zone=zone.zone,
                pallets=pallets,
                pallet_spaces=round(pallets / 2.0, 1),
                miles=miles,
                rate=rate,
                accessorials="None",
                total=total
            )
            db.session.add(stop)
            total_day_earnings += total

        manifest.day_total = total_day_earnings
        db.session.commit()
        print(f"✅ Created manifest for {driver.name} on {manifest_date} with {num_stops} stops.")

    print("🎉 Demo database successfully initialized!")

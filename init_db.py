from app import app
from models import db, Driver, ZipZone
import os, csv

db_path = 'instance/manifest.db'

# Delete existing database (dev only!)
if os.path.exists(db_path):
    os.remove(db_path)
    print("Deleted old database.")

with app.app_context():
    # Create tables
    db.create_all()
    print("Database and tables created!")

    # Add sample drivers
    sample_drivers = ['Gabby', 'Marcus', 'Alex', 'Taylor']
    for name in sample_drivers:
        if not Driver.query.filter_by(name=name).first():
            driver = Driver(name=name)
            db.session.add(driver)
    
    db.session.commit()
    print(f"Added sample drivers: {', '.join(sample_drivers)}")

    # Import ZipZones from CSV
    csv_file = "zipzones.csv"  # put this file in your project root
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
    print("Imported zip zones from CSV.")

from app import app
from models import db, Driver
import os

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

from app import app
from models import db, Driver

drivers_list = ['Gabby', 'John', 'Alex', 'Maria']

with app.app_context():
    # Ensure tables exist
    db.create_all()
    
    for name in drivers_list:
        # Avoid duplicates
        if not Driver.query.filter_by(name=name).first():
            driver = Driver(name=name)
            db.session.add(driver)
    db.session.commit()
    print("Sample drivers added!")

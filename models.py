from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Driver model
class Driver(db.Model):
    __tablename__ = 'driver'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    # Relationship to manifests
    manifests = db.relationship('Manifest', back_populates='driver', cascade="all, delete-orphan")

# Manifest model
class Manifest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_odometer = db.Column(db.Integer)
    end_odometer = db.Column(db.Integer)
    total_miles = db.Column(db.Integer)
    day_total = db.Column(db.Float)  # sum of all stops
    driver = db.relationship('Driver', back_populates='manifests')
    stops = db.relationship('Stop', back_populates='manifest', cascade="all, delete-orphan")

# Stop model
class Stop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    manifest_id = db.Column(db.Integer, db.ForeignKey('manifest.id'), nullable=False)
    type = db.Column(db.String(20))   # Delivery / Pickup
    city = db.Column(db.String(100))
    zip_code = db.Column(db.String(10))
    zone = db.Column(db.String(5))
    pallets = db.Column(db.Integer)
    pallet_spaces = db.Column(db.Float)
    miles = db.Column(db.Float, default=0.0)
    rate = db.Column(db.Float)        # lookup from zone table
    accessorials = db.Column(db.String(200))
    total = db.Column(db.Float)       # rate + extras
    manifest = db.relationship('Manifest', back_populates='stops')

# Zip Codes model
class ZipZone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    zip_code = db.Column(db.String(10), unique=True, nullable=False)
    miles_from_warehouse = db.Column(db.Float, nullable=False)
    zone = db.Column(db.String(5), nullable=False)

    def __repr__(self):
        return f"<ZipZone {self.zip_code} - {self.zone}>"


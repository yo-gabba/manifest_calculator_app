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
    __tablename__ = 'manifest'

    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    driver = db.relationship('Driver', back_populates='manifests')  # <-- only back_populates

    # Daily Info
    date = db.Column(db.Date, nullable=False)
    start_odometer = db.Column(db.Float, nullable=False)
    end_odometer = db.Column(db.Float, nullable=False)
    total_miles = db.Column(db.Float, nullable=False)  # calculated field : end - start

    # Payment Info
    weekly_rate = db.Column(db.Float, nullable=True)   # gas rate per mile
    payback_percentage = db.Column(db.Float, nullable=True)
    payback_amount = db.Column(db.Float, nullable=True)  # calculated

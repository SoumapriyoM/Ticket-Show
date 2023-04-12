from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    bookings = db.relationship('Booking', backref='user', lazy=True)

class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    place = db.Column(db.String(120), nullable=False)
    location= db.Column(db.String(120), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    shows = db.relationship('Show', backref='venue', lazy=True)

class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    tags = db.Column(db.String(120), nullable=False)
    timing = db.Column(db.String(120), nullable=False)
    ticket_price = db.Column(db.Float, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    bookings = db.relationship('Booking', backref='show', lazy=True)

    __table_args__ = (
        db.UniqueConstraint('venue_id', 'name', name='_venue_show_uc'),
        db.UniqueConstraint('venue_id', 'timing', name='_venue_timing_uc'),
    )

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), nullable=False)
    seats_booked = db.Column(db.Integer, nullable=False)

# Database Connection
def get_db_connection():
    conn = db.engine.connect()
    return conn

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ARRAY
db = SQLAlchemy()

def my_db(app):
    db.app = app
    db.init_app(app)
    Migrate(app,db)
  

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(300), nullable=False)   
    shows= db.relationship('Shows', backref='Venue', lazy=True,cascade="save-update, merge, delete")

    def __repr__(self):
      return f'<Venue: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, address: {self.address}, phone: {self.phone}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, website_link: {self.website_link}, seeking_talent: {self.seeking_talent} , seeking_description:{self.seeking_description}, genres: {self.genres}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(120), nullable=False)    
    noofalbum = db.Column(db.Integer, nullable=False)
    nameyear = db.Column(db.String(500), nullable=False)
    albumtrack = db.Column(db.String(500), nullable=False)
    shows= db.relationship('Shows', backref='Artist', lazy=True,cascade="save-update, merge, delete")

    def __repr__(self):
      return f'<Artist: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, address: {self.address}, phone: {self.phone}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, website_link: {self.website_link}, genres: {self.genres}, seeking_venue: {self.seeking_venue} ,seeking_description:{self.seeking_description}, noofalbum:{self.noofalbum}, nameyear:{self.nameyear}, albumtrack:{self.albumtrack}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Shows(db.Model):
    __tablename__ = 'Shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
      return f'<Shows: {self.id}, artist_id: {self.artist_id}, venue_id: {self.venue_id} , start_time: {self.start_time}>'

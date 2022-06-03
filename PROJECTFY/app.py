#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from models import db, my_db
from models import Venue, Shows , Artist
from flask import Flask, jsonify, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)

moment = Moment(app)
app.config.from_object('config')
my_db(app)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root1986@localhost:5432/projectfy'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
        date = dateutil.parser.parse(value)
  else:
        date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  rvenues = Venue.query.order_by(db.asc(Venue.id)).limit(6).all()
  rartists = Artist.query.order_by(db.asc(Artist.id)).limit(6).all()
  return render_template('pages/home.html',lvenue = rvenues, lartist = rartists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
  vdata = []
  venues = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
  for venue in venues:
      resultvenue = Venue.query.filter(Venue.state == venue.state).filter(Venue.city == venue.city).all()
      data = []
      for venue in resultvenue:
          data.append({
              'id': venue.id,
              'name': venue.name,
              'num_upcoming_shows': len(db.session.query(Shows).filter(Shows.start_time > datetime.now()).all())
          })
          vdata.append({
              'city': venue.city,
              'state': venue.state,
              'venues': data
          })
  return render_template('pages/venues.html', venues=vdata)
  
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  vdata = Venue.query.filter(Venue.name.like('%{}%'.format(request.form['search_term']))).all()
  response={
    "count": len(vdata),
    "data": []
    }
  for venue in vdata:
    response["data"].append({
        "id": venue.id,
        "name": venue.name,
        
      })
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<venue_id>', methods=['GET'])
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
 
# Query and get results---------------------
  venue = Venue.query.get(venue_id)
  showsd = venue.shows
  pshow = []
  ushow = []  
  for show in showsd:
    sinfo ={
      "artist_id": show.artist_id,
      "artist_name": show.Artist.name,
      "artist_image_link": show.Artist.image_link,
      "start_time": show.start_time
    }
    if show.start_time > datetime.now():
      ushow.append(sinfo)
    else:
      pshow.append(sinfo)

  vdatas={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website_link": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": pshow,
    "upcoming_shows": ushow,
    "past_shows_count": len(pshow),
    "upcoming_shows_count": len(ushow)
  }
    
  return render_template('pages/show_venue.html', venue=vdatas)
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  #body= {}
  error  = False  
  try:  
    form = VenueForm(request.form)
    if request.method == 'POST' and form.validate():  
      name= form.name.data
      city= form.city.data
      state= form.state.data
      address= form.address.data
      phone= form.phone.data
      image_link= form.image_link.data
      genreslist= request.form.getlist('genres')
      genres= ','.join(genreslist)
      facebook_link= form.facebook_link.data
      website_link= form.website_link.data 
      seeking_description= form.seeking_description.data
      seeking_talent= bool(form.seeking_talent.data)       
      venueli= Venue(name=name, city=city, state=state, address=address, phone=phone,
      seeking_description=seeking_description, facebook_link=facebook_link, image_link=image_link,
      website_link=website_link, genres=genres, seeking_talent=seeking_talent)
      db.session.add(venueli)
      db.session.commit()            
  except:
    error = True    
    db.session.rollback()       
  finally:
    db.session.close()
  if  error == True:
    # Unsuccessful db insertion
      flash('An error occurred. Venue ' + name + ' could not be listed.')
  else:      
    # Successful db insertion  
      flash('Venue '  + name + ' was successfully listed!')      
  return render_template('/pages/home.html')

@app.route('/venues/<int:venue_id>', methods=['POST'])
def delete_venue(venue_id):
  #venue_id = request.form.get('venue_id')
  vdel = Venue.query.get(venue_id)
  vname = vdel.name
  error=False
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:     
    db.session.delete(vdel)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  if  error == True:
    # Unsuccessful record deletion
      flash('An error occurred. Venue ' + vname +  'could not be deleted.')
  else:      
    # Successful record deletion
      flash('Venue ' + vname +  'was succesfully deleted!')      
  return render_template('/pages/home.html')  
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artist= Artist.query.order_by(db.asc(Artist.id)).all()
  return render_template('pages/artists.html', artists=artist)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  adatas = Artist.query.filter(Artist.name.like('%{}%'.format(request.form['search_term']))).all()

  response={
    "count": len(adatas),
    "data": []
  }
  for adata in adatas:
    response['data'].append({
      "id": adata.id,
      "name": adata.name,
      "num_upcoming_shows": adata.u_show_count,
      })
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  current_time = datetime.now()
  artist = Artist.query.get(artist_id)
  showsd = artist.shows
  pshow = []
  ushow = []
 
  for show in showsd:
   sinfo={
      "venue_id": show.venue_id,
      "venue_name": show.Venue.name,
      "venue_image_link": show.Venue.image_link,
      "start_time": show.start_time
    } 
   if show.start_time > current_time:
     ushow.append(sinfo)     
   else:
     pshow.append(sinfo) 
  adata = {
     "id": artist.id,
     "name": artist.name,
     "genres": artist.genres.split(','), 
     "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website_link": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description":artist.seeking_description,
    "image_link": artist.image_link,
    "noofalbum": artist.noofalbum,
    "nameyear": artist.nameyear,
    "albumtrack": artist.albumtrack,
    "past_shows": pshow,
    "upcoming_shows": ushow,
    "past_shows_count": len(pshow),
    "upcoming_shows_count": len(ushow)
  }
  return render_template('pages/show_artist.html', artist=adata)


#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()  
  aedit = Artist.query.get(artist_id)
  aedit1 = Artist.query.filter_by(id=artist_id) 
  form.name.data = aedit.name
  form.city.data = aedit.city
  form.state.data = aedit.state
  form.phone.data = aedit.phone
  form.genres.data = aedit.genres
  form.facebook_link.data = aedit.facebook_link
  form.image_link.data = aedit.image_link
  form.website_link.data = aedit.website_link
  form.seeking_venue.data = aedit.seeking_venue
  form.seeking_description.data = aedit.seeking_description
  form.noofalbum.data = aedit.noofalbum
  form.nameyear.data = aedit.nameyear
  form.albumtrack.data = aedit.albumtrack
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=aedit1)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  aform = Artist.query.filter(Artist.id==artist_id).first()
  form= ArtistForm(request.form)
  aform.name = form.name.data
  aform.city = form.city.data
  aform.state = form.state.data
  aform.phone = form.phone.data
  genreslist = request.form.getlist('genres')
  aform.genres= ','.join(genreslist)
  aform.facebook_link = form.facebook_link.data
  aform.image_link = form.image_link.data
  aform.website_link = form.website_link.data
  aform.seeking_venue = bool(form.seeking_venue.data)
  aform.seeking_description = form.seeking_description.data
  aform.noofalbum = form.noofalbum.data
  aform.nameyear = form.nameyear.data
  aform.albumtrack = form.albumtrack.data
  
  if request.method == 'POST': 
        # update Venue database 
        db.session.commit()
        # succesful update
        flash('Artist ' + aform.name + ' has been updated.')
  else:
    # Unsuccesful update
        flash('An error occurred. Artist ' + aform.name + ' cannot be updated.') 


  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  vedit = Venue.query.get(venue_id)
  vedit1 = Venue.query.filter_by(id=venue_id) 
  form.name.data = vedit.name
  form.city.data = vedit.city
  form.state.data = vedit.state
  form.address.data = vedit.address
  form.phone.data = vedit.phone
  form.genres.data = vedit.genres
  form.facebook_link.data = vedit.facebook_link
  form.image_link.data = vedit.image_link
  form.website_link.data = vedit.website_link
  form.seeking_talent.data = vedit.seeking_talent
  form.seeking_description.data = vedit.seeking_description 

  
    # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=vedit1)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):  
  vform = Venue.query.filter(Venue.id==venue_id).first()
  form = VenueForm(request.form)
  vform.name = form.name.data
  vform.city = form.city.data
  vform.state = form.state.data
  vform.address = form.address.data
  vform.phone = form.phone.data
  genreslist = request.form.getlist('genres')
  vform.genres= ','.join(genreslist)
  vform.facebook_link = form.facebook_link.data
  vform.image_link = form.image_link.data
  vform.website_link = form.website_link.data
  vform.seeking_talent = bool(form.seeking_talent.data)
  vform.seeking_description = form.seeking_description.data
  
  if request.method == 'POST': 
        # update Venue database 
        db.session.commit()
        # succesful update
        flash('Venue ' + vform.name + ' has been updated.')
  else:
    # Unsuccesful update
        flash('An error occurred. Venue ' + vform.name + ' cannot be updated.') 

  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error  = False  
  try: 
    form = ArtistForm(request.form)
    if request.method == 'POST' and form.validate():     
      name= form.name.data
      city= form.city.data
      state= form.state.data
      phone= form.phone.data
      image_link= form.image_link.data
      genreslist= request.form.getlist('genres')
      genres= ','.join(genreslist)
      facebook_link= form.facebook_link.data
      website_link= form.website_link.data 
      seeking_description= form.seeking_description.data
      seeking_venue= bool(form.seeking_venue.data)  
      noofalbum= form.noofalbum.data  
      nameyear= form.nameyear.data
      albumtrack= form.albumtrack.data        
      artistli= Artist(name=name, city=city, state=state, phone=phone,
      seeking_description=seeking_description, facebook_link=facebook_link, image_link=image_link,
      website_link=website_link, genres=genres, seeking_venue=seeking_venue, noofalbum=noofalbum, nameyear=nameyear, albumtrack=albumtrack)
      db.session.add(artistli)
      db.session.commit()            
  except:
    error = True    
    db.session.rollback()       
  finally:
    db.session.close()
  if  error == True:
    # Unsuccessful db insertion
      flash('An error occurred. Artist ' + name + ' could not be listed.')
  else:        
    # Successful db insertion
      flash('Artist '  + name + ' was successfully listed!')
     
  return render_template('/pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  current_time = datetime.now()   
  sdata = []
  ashow = Shows.query.order_by(db.desc(Shows.start_time)).all()

  for show in ashow:
    artistm = Artist.query.get(show.artist_id)
    venuem = Venue.query.get(show.venue_id)    
  
    sdata.append({
        "venue_id": show.venue_id,
        "venue_name": venuem.name,
        "artist_id": show.artist_id,
        "artist_name": artistm.name,
        "artist_image_link": artistm.image_link,
        "start_time": show.start_time
      })
  
  return render_template('pages/shows.html', shows=sdata)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
 error  = False  
 try:   
   form = ShowForm(request.form)
   if request.method == 'POST' and form.validate(): 
      artist_id= form.artist_id.data
      venue_id= form.venue_id.data
      start_time= form.start_time.data                    
      showli= Shows(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
      db.session.add(showli)
      db.session.commit()  
          
 except:
    error = True    
    db.session.rollback()       
 finally:
    db.session.close()  
 if  error == True:
    # Unsuccessful db insertion
      flash('An error occurred.' + 'Show could not be listed.')
 else:        
    # Successful db insertion
      flash('Show was successfully listed!')
     
 return render_template('/pages/home.html')  



@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

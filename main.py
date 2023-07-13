from flask import Flask,render_template,redirect,url_for,request,session,flash,abort
from werkzeug.security import check_password_hash
from sqlalchemy import func
from sqlalchemy import or_
from flask import render_template
# from models_1 import *
from model import *
from sqlalchemy.orm import joinedload
#*************************** config ************************
app = Flask(__name__)
app.secret_key = '12345'
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydatabom.sqlite3"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///manymanydata.sqlite3"

db.init_app(app)
app.app_context().push()

#*************************** controllers ************************
# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('/index.html')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Invalid email or password. Please check your credentials or sign up.', 'error')
            return redirect('/sign_up')
        u_id = user.id
        if user and user.password == password:
            return redirect(f'/user_dashboard/{u_id}')
        else:
            flash('Invalid email or password. Please check your credentials.', 'error')
            return redirect('/')
        
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'GET':
        return render_template('sign_up.html')
    if request.method == 'POST':
        user = request.form.get('username')
        em = request.form.get('email')
        pas = request.form.get('password')
        u = User(username=user, email=em, password=pas)
        db.session.add(u)
        try:
            db.session.commit()
            flash('User registered successfully.', 'success')
            return redirect('/')
        except Exception as e:
            flash('An error occurred while adding the user. Please try again later.', 'error')
            db.session.rollback()
            return redirect('/sign_up')
    
# Route for the admin login page
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # authenticate admin user
        if username == 'admin' and password == 'password':
            session['admin'] = True
            return redirect('/admin_dashboard')
        else:
            flash('Invalid admin credentials.', 'error')
            return render_template('admin_login.html')

@app.route('/search/<int:u_id>',methods=['GET', 'POST'])
def search(u_id):
    if request.method == 'GET':
        return render_template('search.html',u_id=u_id)
    if request.method == 'POST':
        location = request.form.get('location')
        tags = request.form.get('tags')
        rating = request.form.get('rating')
        v=0
        l=0
        if location:
            venues = Venue.query.filter(
            or_(
                Venue.location == location,
                Venue.location.ilike(f'%{location}%'),
                Venue.location.ilike(f'{location}%'),
                Venue.location.ilike(f'%{location}'),
                Venue.place == location,
                Venue.place.ilike(f'%{location}'),
                Venue.place.ilike(f'%{location}%'),
                Venue.place.ilike(f'{location}%'),)).all()
            v=1
        else:
            venues = Venue.query.all()
        if tags and rating:
            shows = Show.query.filter(Show.tags.ilike(f'%{tags}%'),Show.rating >= rating).all()
            l=1
        elif tags:
            shows = Show.query.filter(Show.tags.ilike(f'%{tags}%')).all()
            l=1
        elif rating:
            shows = Show.query.filter(Show.rating >= rating).all()
            l=1
        else:
            shows = Show.query.all()
        return render_template('search_result.html', venues=venues, shows=shows,u_id=u_id,v=v,l=l)
    
# Route for the dashboard page
@app.route('/admin_dashboard')
def admin_dashboard():
    venues = Venue.query.all()
    return render_template('admin_dashboard.html',venues=venues)
# Route for the dashboard page
@app.route('/user_dashboard/<int:u_id>')
def user_dashboard(u_id):
    venues = Venue.query.all()
    user=User.query.get(u_id)
    return render_template('user_dashboard.html',venues=venues,user=user)

@app.route('/add_venue', methods=['GET','POST'])
def add_venue():
    if request.method == 'GET':
        return render_template('add_venue.html')
    if request.method == 'POST':
        name=request.form.get("name")
        place=request.form.get("place")
        location=request.form.get("location")
        capacity= request.form.get("capacity")
        existing_venue = Venue.query.filter_by(name=name).first()
        if existing_venue:
            return redirect('/add_venue')
        v=Venue(name=name,place=place,location=location,capacity=capacity)
        db.session.add(v)
        db.session.commit()
        return redirect('/admin_dashboard')

@app.route('/add_show/<int:v_id>', methods=['GET', 'POST'])
def add_show(v_id):
    tm = {1: '8-11 am', 2: '1-4 pm', 3: '5-8 pm', 4: '9-12 pm'}
    venues = Venue.query.get(v_id)
    s=Show.query.filter_by(venue_id=v_id).all()
    tm_l = [k.timing for k in s]
    tm_l.sort()
    l=list(tm.values())
    l.sort()
    if tm_l == l:
        return redirect('/admin_dashboard')
    if request.method == 'GET':
        return render_template('add_show.html',tm=tm,venues=venues,tm_l=tm_l)
    if request.method == 'POST':
        name = request.form.get("name")
        rating = request.form.get("rating")
        tags = request.form.get("tags")
        timing = request.form.get("timing")
        ticket_price = request.form.get("ticket_price")
        venue_id=venues.id

        existing_show = Show.query.filter_by(name=name, venue_id=venue_id).first()
        if existing_show:
            return redirect(f'/add_show/{v_id}')
        s = Show(name=name, rating=rating, tags=tags, timing=timing, ticket_price=ticket_price, venue_id=venue_id)
        db.session.add(s)
        db.session.commit()
        return redirect('/admin_dashboard')


@app.route('/update_show/<int:id>', methods=['GET', 'POST'])
def update_show(id):
    tm = {1: '8-11 am', 2: '1-4 pm', 3: '5-8 pm', 4: '9-12 pm'}
    show = Show.query.get(id)
    if not show:
        flash('Invalid show.', 'error')
        return redirect('/admin_dashboard')
    if request.method == 'POST':
        show.name = request.form.get('name')
        show.rating = request.form.get('rating')
        show.tags = request.form.get('tags')
        show.timing = request.form.get('timing')
        show.ticket_price = request.form.get('ticket_price')
        new_venue_id = request.form.get('venue_id')

        exist_same_time = Show.query.filter_by(venue_id=new_venue_id, timing=show.timing).first()
        exist_same_name = Show.query.filter_by(venue_id=new_venue_id, name=show.name).first()

        if new_venue_id != show.venue_id and (exist_same_time is not None or exist_same_name is not None):
            flash('Show with the same name or timing already exists for the selected venue.', 'error')
            return redirect('/admin_dashboard')

        if new_venue_id != show.venue_id:
            new_venue = Venue.query.get(new_venue_id)
            if not new_venue:
                flash('Invalid venue.', 'error')
                return redirect('/admin_dashboard')
            else:
                show.venue_id = new_venue.id
            try:
                db.session.commit()
                flash('Show updated successfully.', 'success')
                return redirect('/admin_dashboard')
            except Exception as e:
                flash('An error occurred while updating the show. Please try again later.', 'error')
                db.session.rollback()
                return redirect('/admin_dashboard')
    venues = Venue.query.all()
    return render_template('update_show.html', tm=tm, show=show, venues=venues)
    

@app.route('/update_venue/<int:venue_id>', methods=['GET', 'POST'])
def update_venue(venue_id):
    venue = Venue.query.get(venue_id)
    if not venue:
        flash('Venue not found.', 'error')
        return redirect('/admin_dashboard')
    if request.method == 'POST':
        venue.name = request.form.get('name')
        venue.place = request.form.get('place')
        venue.location = request.form.get('location')
        venue.capacity = request.form.get('capacity')
        try:
            db.session.commit()
            flash('Venue updated successfully.', 'success')
            return redirect('/admin_dashboard')
        except Exception as e:
            flash('An error occurred while updating the venue. Please try again later.', 'error')
            db.session.rollback()
            return redirect(f'/update_venue/{venue_id}')
    return render_template('update_venue.html', venue=venue)

@app.route('/delete_show/<int:id>', methods=['GET', 'POST'])
def delete_show(id):
    show = Show.query.get(id)
    if not show:
        return redirect('/admin_dashboard')
    for booking in show.bookings:
        db.session.delete(booking)
    db.session.delete(show)
    db.session.commit()
    return redirect('/admin_dashboard')

@app.route('/delete_venue/<int:id>', methods=['GET', 'POST'])
def delete_venue(id):
    venue = Venue.query.get(id)
    if not venue:
        return redirect('/admin_dashboard')
    for show in venue.shows:
        db.session.delete(show)
    db.session.commit()
    db.session.delete(venue)
    db.session.commit()
    return redirect('/admin_dashboard')

@app.route('/book/<int:s_id>/<int:u_id>', methods=['GET', 'POST'])
def book_show(s_id,u_id):
    if request.method == 'GET': 
        show = Show.query.get(s_id)
        venue = Venue.query.get(show.venue_id)
        user_id=u_id
        return render_template('book_show.html', show=show, venue=venue,user_id=user_id)
    if request.method == 'POST':
        show = Show.query.get(s_id)
        venue = Venue.query.get(show.venue_id)
        seats_booked=int(request.form.get('seats_booked'))
        user_id=u_id
        sh_id=s_id
        b=Booking(user_id=user_id,show_id=sh_id,seats_booked=seats_booked)
        db.session.add(b)
        db.session.commit()
        venue.capacity=venue.capacity-seats_booked
        db.session.commit()
        return redirect(f'/confirm_booking/{b.id}')

@app.route('/confirm_booking/<int:b_id>', methods=['GET','POST'])
def confirm_booking(b_id):
    book=Booking.query.get(b_id)
    if request.method =='GET':
        show = Show.query.get(book.show_id)
        total=book.seats_booked * show.ticket_price
        return render_template('booking_confirmation.html',show=show,book=book,total=total)
    if request.method =='POST':
        total=request.form.get('seats_booked')
        return redirect(f'/user_bookings/{book.user_id}')

@app.route('/user_bookings/<int:user_id>')
def user_bookings(user_id):
    user = User.query.get(user_id)
    bookings = Booking.query.filter_by(user_id=user_id).all()
    return render_template('user_booking.html', user=user, bookings=bookings)

@app.route('/show/<int:show_id>')
def show_info(show_id):
    show = Show.query.get(show_id)
    return render_template('show_info.html', show=show)

@app.route('/venue/<int:venue_id>')
def venue_info(venue_id):
    venue= Venue.query.get(venue_id)
    return render_template('venue_info.html', venue=venue)

@app.route('/rate_show/<int:booking_id>', methods=['GET','POST'])
def rate_show(booking_id):
    rate = int(request.form['rating'])
    booking = Booking.query.get(booking_id)
    name=booking.show.name
    show=Show.query.filter_by(name=name).all()
    seat=booking.seats_booked
    total_cap=0
    for i in show:
        total_cap+=i.venue.capacity
    total_weight=total_cap
    x= (total_weight*booking.show.rating + rate*seat)/(total_cap+seat)
    if x >10:
        x=10
    for i in show:
        i.rating=round(x)
    db.session.commit()
    return redirect(f'/user_bookings/{booking.user_id}')

@app.route('/unbook/<int:user_id>/<int:show_id>/<int:v_id>', methods=['GET','POST'])
def unbook(user_id, v_id, show_id):
    # Find the show with the given ID and venue ID
    show = Show.query.filter_by(id=show_id, venue_id=v_id).first()
    # Delete each booking from the database
    bookings = Booking.query.filter_by(user_id=user_id, show_id=show_id).all()
    # Delete each booking from the database
    for booking in bookings:
        booking.show.venue.capacity += booking.seats_booked
        db.session.delete(booking)
    # Commit the changes to the database
    db.session.commit()
    
    return redirect(f'/user_bookings/{user_id}')

if __name__ == '__main__':
    db.create_all()
    from waitress import serve
    serve(app, host='0.0.0.0', port=8000)

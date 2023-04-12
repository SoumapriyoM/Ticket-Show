@app.route('/update_show/<int:id>', methods=['GET', 'POST'])
def update_show(id):
    tm = {1: '8-11 am', 2: '1-4 pm', 3: '5-8 pm', 4: '9-12 pm'}
    show = Show.query.get(id)
    if not show:
        abort(404)
    if request.method == 'POST':
        show.name = request.form.get('name')
        show.rating = request.form.get('rating')
        show.tags = request.form.get('tags')
        show.timing = request.form.get('timing')
        show.ticket_price = request.form.get('ticket_price')
        new_venue_id = request.form.get('venue_id')
        
        exist_same_time = Show.query.filter_by(venue_id=new_venue_id, timing=show.timing).first()
        exist_same_name = Show.query.filter_by(venue_id=new_venue_id, name=show.name).first()
        
        if new_venue_id != show.venue_id and (exist_same_time or exist_same_name):
            return redirect('/admin_dashboard')
        
        if new_venue_id != show.venue_id:
            new_venue = Venue.query.get(new_venue_id)
            if not new_venue:
                return redirect('/admin_dashboard')
            else:
                show.venue = new_venue
            db.session.commit()
        
        return redirect('/admin_dashboard')

    venues = Venue.query.all()
    return render_template('update_show.html',tm=tm, show=show, venues=venues)
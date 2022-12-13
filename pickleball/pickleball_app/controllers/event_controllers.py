from pickleball_app import app
from flask import render_template, redirect, session, request
import os
import requests
from pickleball_app.models.event_model import Event
from pickleball_app.models.user_model import User
from pickleball_app.config.mysqlconnection import connectToMySQL
from pprint import pprint

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id':session['user_id']
    }
    user = User.get_one(data)
    attending = Event.users_who_are_attending(data)
    return render_template('dashboard.html', user = user, events = Event.all_events(), attending = attending )

@app.route('/add_event')
def add_event():
    return render_template('add_event.html')

@app.route('/create_event', methods=['POST'])
def create_event():
    address = {
        'streetNumber' : request.form['streetNumber'],
        'streetName' : request.form['streetName'],
        'municipality' : request.form['municipality'],
        'countrySubdivision' : request.form['countrySubdivision'],
        'postalCode' : request.form['postalCode'],
    }
    headers = os.environ.get("KEY")
    address = f"streetNumber={address['streetNumber']}&streetName={address['streetName']}&municipality={address['municipality']}&countrySubdivision={address['countrySubdivision']}&postalCode={address['postalCode']}&view=Unified&key={headers}"
    json_url = f"https://api.tomtom.com/search/2/structuredGeocode.json?countryCode=US&{address}&view=Unified&key={headers}"
    response = requests.get(json_url)
    lat = response.json()['results'][0]['position']['lat']
    lon = response.json()['results'][0]['position']['lon']
    location = f"https://api.tomtom.com/map/1/staticimage?key={headers}&zoom=15&center={lon},{lat}&format=jpg&layer=basic&style=main&width=400&height=400&view=Unified&language=en-GB"
    data = {
        'title' : request.form['title'],
        'date' : request.form['date'],
        'streetNumber' : request.form['streetNumber'],
        'streetName' : request.form['streetName'],
        'municipality' : request.form['municipality'],
        'countrySubdivision' : request.form['countrySubdivision'],
        'postalCode' : request.form['postalCode'],
        'capacity' : request.form['capacity'],
        'information' : request.form['information'],
        'url' : location,
        'user_id' : session['user_id']
    }
    pprint(data)
    Event.create_event(data)
    return redirect('/dashboard')

@app.route('/show_event/<int:event_id>')
def show_one_event(event_id):
    data = {
        'id' : event_id
    }
    user = User.get_one({'id':session['user_id']})
    event = Event.show_one_event(data)
    print('from database', event)
    return render_template('show_event.html', user = user, event = event)

@app.route('/edit_event/<int:event_id>')
def edit_one_event(event_id):
    data = {
        'id' : event_id
    }
    event = Event.show_one_event(data)
    return render_template('edit_event.html', event = event)

@app.route('/update_event/<int:event_id>', methods=['POST'])
def update_event(event_id):
    Event.update_event(request.form, event_id)
    return redirect('/dashboard')

@app.route('/join_event/<int:event_id>')
def join_event(event_id):
    data = {
        'event_id' : event_id,
        'user_id' : session['user_id']
    }
    Event.join_event(data)
    return redirect('/dashboard')

@app.route('/unjoin_event/<int:event_id>')
def unjoin_event(event_id):
    data = {
        'event_id' : event_id,
        'user_id' : session['user_id']
    }
    Event.unjoin_event(data)
    return redirect('/dashboard')

@app.route('/delete/<int:event_id>')
def delete_event(event_id):
    data = {
        'id' : event_id
    }
    Event.delete_event(data)
    return redirect('/dashboard')
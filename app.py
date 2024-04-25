from flask import Flask, render_template, redirect, request, jsonify
import firebase_admin
from firebase_admin import credentials, auth, db
import time
import requests

windSpeeds = {}

app = Flask(__name__)

cred = credentials.Certificate("finalproject-89a6e-firebase-adminsdk-7o1n7-0b1800bdde.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://finalproject-89a6e-default-rtdb.firebaseio.com'
})


@app.route('/')
def login():
    return render_template('login.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    email = request.form['email']
    password = request.form['password']

    try:
        user = auth.get_user_by_email(email)
        return render_template('landing.html')
    except:
        try:
            user = auth.create_user(email=email, password=password)
            return render_template('landing.html')
        except:
            return "Authentication failed"

@app.route('/landing')
def landing_page():
    return render_template('landing.html')

@app.route('/run', methods=['POST'])
def run():
    boolRef = db.reference('/Start Recording/Start/')
    boolRef.set(True)

    return '', 200

@app.route('/get_wind_data', methods=['GET'])
def get_wind_data():
    windSpeeds = {}
    for i  in range(0, 10):
        windDataRef = db.reference('/Data/WindSpeed' + str(i) + '/')
        windSpeeds.update({str(i) : windDataRef.get()})
        time.sleep(0.5)

    # Convert the windSpeeds dictionary to a list of tuples
    windSpeedsList = list(windSpeeds.items())

    return jsonify(windSpeedsList)

@app.route('/get_velocity_data', methods=['GET'])
def get_velocity_data():
    velocity_data = {}
    velocity_data_ref = db.reference('/Throw Data/')
    velocity_data['v'] = float(velocity_data_ref.child('v').get())

    return jsonify(velocity_data)

@app.route('/get_angle_data', methods=['GET'])
def get_angle_data():
    angle_data = {}
    angle_data_ref = db.reference('/Throw Data/')
    angle_data['angle'] = float(angle_data_ref.child('angle').get())

    return jsonify(angle_data)

@app.route('/get_distance_data', methods=['GET'])
def get_distance_data():
    distance_data = {}
    distance_data_ref = db.reference('/Throw Data/')
    distance_data['d'] = float(distance_data_ref.child('d').get())
    distance_data['a'] = float(distance_data_ref.child('a').get())
    distance_data['b'] = float(distance_data_ref.child('b').get())
    distance_data['c'] = float(distance_data_ref.child('c').get())

    return jsonify(distance_data)

@app.route('/get_wind_direction', methods=['POST'])
def get_wind_direction():
    data = request.get_json()
    print(data)
    latitude = data["latitude"]
    longitude = data["longitude"]
    windDirection = get_wind_direction(latitude, longitude, "2d6064c316de6cb90a1c735ea4a312bc")
    return jsonify(windDirection)



def get_wind_direction(latitude, longitude, api_key):
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={latitude}&lon={longitude}&appid={api_key}"
    response = requests.get(url)
    data = response.json()
    
    if response.status_code == 200:
        try:
            wind_deg = data['current']['wind_deg']
            return wind_deg
        except KeyError:
            return "Wind direction data not available"
    else:
        return "Make sure Lat, Long is correct"

if __name__ == '__main__':
    app.run(debug=True)
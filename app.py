from flask import Flask, render_template, redirect, request, jsonify
import firebase_admin
from firebase_admin import credentials, auth, db
import time

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

@app.route('/get_heading_data', methods=['GET'])
def get_heading_data():
    heading = 0
    headingDataRef = db.reference('/Wind Deg/Wind Degree/')
    heading = headingDataRef.get()

    return jsonify(heading)

@app.route('/get_distance_data', methods=['GET'])
def get_distance_data():
    distance_data = {}
    distance_data_ref = db.reference('/Throw Data/')
    distance_data['d'] = distance_data_ref.child('d').get()
    distance_data['a'] = distance_data_ref.child('a').get()
    distance_data['b'] = distance_data_ref.child('b').get()
    distance_data['c'] = distance_data_ref.child('c').get()

    return jsonify(distance_data)

if __name__ == '__main__':
    app.run(debug=True)

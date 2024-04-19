from flask import Flask, render_template, redirect, request, session
import firebase_admin
from firebase_admin import credentials, auth

app = Flask(__name__)

cred = credentials.Certificate("finalproject-89a6e-firebase-adminsdk-7o1n7-0b1800bdde.json")
firebase_admin.initialize_app(cred)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    email = request.form['email']
    password = request.form['password']

    try:
        user = auth.get_user_by_email(email)
        print(user.uid) # Gets the uuid from authenticate
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

if __name__ == '__main__':
    app.run(debug=True)
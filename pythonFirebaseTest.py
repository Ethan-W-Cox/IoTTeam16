import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Fetch the service account key JSON file contents
cred = credentials.Certificate(r'C:\Users\ethan\Documents\University Documents\Year 3\Semester Two\Internet of Things\FinalProject\finalproject-89a6e-firebase-adminsdk-7o1n7-0b1800bdde.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://finalproject-89a6e-default-rtdb.firebaseio.com'
})

# As an admin, the app has access to read and write all data, regradless of Security Rules
ref = db.reference('Throw Data')

# Write data to Firebase
ref.set({
    'a': 0,
    'b': 0,
    'c': 0,
    'd': 0
})

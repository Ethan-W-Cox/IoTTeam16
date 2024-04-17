# IoTTeam16

## Firebase Link
https://console.firebase.google.com/project/finalproject-89a6e/database/finalproject-89a6e-default-rtdb/data/~2F

## app.html
This file holds the html data for the app.

## style.css
This file styles the html page.

## login.js
This file handles the backend of the html page.

## ReceivingWindSpeed.js
This file receives the wind speed from the Arduino via bluetooth. It then sends 5 seconds of wind speed data to Firebase when the Start Recording boolean in Firebase is updated to true.

## pythonFirebaseTest.py
You will need to download the JSON file that is in the repo locally and add its path to the cred = credentials.Certificate line. Right now, this code is just setting a, b, c, and d to 0 in Firebase, but you will obviously replace this with the correct values you want to send. You should be able to add this code to your existing Python code fairly easily. You will also need to run "pip3 install firebase-admin" to get the correct libraries. Other than that you should be good. Make sure you accept the invite I sent you to gain access to the Firebase.  



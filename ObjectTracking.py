import numpy as np
import cv2
from orange_detector import OrangeDetector
import matplotlib.pyplot as plt 
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import requests

def convert_coordinates(x,y, height):
    return (x/728, (height - y)/750)

def calcDistance (a,b,c):
    x2 = (-b + np.sqrt(b*b-4*a*c))/2/a
    c -= 1.7
    x1 = (-b - np.sqrt(b*b-4*a*c))/2/a

    return x1 - x2

def writeThrowToDatabase(data):
    # Fetch the service account key JSON file contents
    cred = credentials.Certificate(r'cred.json')

    # Initialize the app with a service account, granting admin privileges
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://finalproject-89a6e-default-rtdb.firebaseio.com'
    })

    # As an admin, the app has access to read and write all data, regradless of Security Rules
    ref = db.reference('Throw Data')

    # Write data to Firebase
    # Write data to Firebase
    ref.set({
        'a' : data[0],
        'b' : data[1],
        'c' : data[2],
        'd' : data[3],
        'angle' : data[4],
        'v' :  data[5]
    })
    return

def writeWindToDatabase(data):
    # Fetch the service account key JSON file contents
    #cred = credentials.Certificate(r'cred.json')

    # Initialize the app with a service account, granting admin privileges
    #firebase_admin.initialize_app(cred, {
    #    'databaseURL': 'https://finalproject-89a6e-default-rtdb.firebaseio.com'
    #})

    # As an admin, the app has access to read and write all data, regradless of Security Rules
    ref = db.reference('Wind Deg')

    # Write data to Firebase
    ref.set({
        'Wind Degree': data
    })
    return

def track(inputFile, startPixel, stopPixel):

    cap = cv2.VideoCapture(inputFile)
    od = OrangeDetector()

    startFrame = 52
    trigger = False

    xpts = []
    ypts = []
    frameCount = 0

    while True:
    
        ret, frame = cap.read()

        if ret == False:
            break

        bbox = od.detect(frame)
        x, y, x2, y2 = bbox

        cx = int((x+x2)/2)
        cy = int((y+y2)/2)

        cv2.circle(frame, (cx,cy), 20, (255,0,0), 4)


        if(frameCount == startFrame):
            for i in range(10):
                cv2.circle(frame, (10*i,i*10), 5, (255,0,0), -1)
                cv2.imshow("Frame", frame)
                key = cv2.waitKey(100)


        if(cx > startPixel and cx < stopPixel):
            xpts.append(cx)
            ypts.append(cy)
            trigger = True

        if(cx < startPixel and trigger == True):
            trigger = False
            height, width = frame.shape[:2]
            model = np.poly1d(np.polyfit(xpts, ypts, 2))
            
            a = model[2]
            b = model[1]
            c = model[0]

            for i in range(80):
                x = xpts[-1] - i*10
                y = int(a*x*x + b*x + c)
                cv2.circle(frame, (x,y), 10, (0,255,0), -1)
                cv2.imshow("Frame", frame)
                key = cv2.waitKey(100)
                
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(100)
        frameCount += 1

        if key == 27:
            break

    xpts_conv = []
    ypts_conv = []

    for i in range(0,len(xpts)):
        new_pts = convert_coordinates(xpts[i], ypts[i], height)
        xpts_conv.append(new_pts[0])
        ypts_conv.append(new_pts[1])
    
    model_conv = np.poly1d(np.polyfit(xpts_conv, ypts_conv, 2))
    a_conv = model_conv[2]
    b_conv = model_conv[1]
    c_conv = model_conv[0]
    distance = calcDistance(a_conv, b_conv, c_conv)
    launch_angle = np.rad2deg(np.arctan(b_conv))
    launch_angle_rad = np.deg2rad(launch_angle)
    launch_velocity = np.sqrt(-9.81/2/a_conv/np.cos(launch_angle_rad)/np.cos(launch_angle_rad))

    return [a_conv, b_conv, c_conv, distance, launch_angle, launch_velocity]

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
        return "Error fetching data"


inputFile = "throw.mp4"
startPixel = 1048
stopPixel = 3073

modelParams = track(inputFile, startPixel, stopPixel)

writeThrowToDatabase(modelParams)

print(modelParams)    

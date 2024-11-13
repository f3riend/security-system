from flask import Flask,render_template,Response
from flask_socketio import SocketIO
from twilio.rest import Client
from pyngrok import ngrok
import requests
import cv2
import time
import datetime
import os


app = Flask(__name__)



def getFrames():
    cap = cv2.VideoCapture(0)

    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    body_cascade = cv2.CascadeClassifier('haarcascade_fullbody.xml')

    detection = False
    detection_stopped_time = None
    timer_started = False 

    SECONDS_TO_RECORD_AFTER_DETECTION = 5

    frame_size = (int(cap.get(3)), int(cap.get(4)))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = None  
    public_url = ngrok.connect(5000)

    message = f'Detection detected link: {public_url}'
    messageSwitch = True

    account_sid = os.getenv("SID")
    auth_token = os.getenv("AUTH_TOKEN")



    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            bodies = body_cascade.detectMultiScale(gray, 1.3, 5)

            if len(faces) + len(bodies) > 0:  
                if messageSwitch:
                    client = Client(account_sid, auth_token)
                    message = client.messages.create(
                    from_='VIRTURAL NUMBER',
                    body=message,
                    to='REAL NUMBER'
                    )
                    messageSwitch = False


                if not detection:
                    detection = True
                    current_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                    if out is None:  
                        out = cv2.VideoWriter(f'videos/{current_time}.mp4', fourcc, 20, frame_size)
                    print(f'Detection started at {current_time}')
            elif detection:
                if timer_started:
                    if time.time() - detection_stopped_time >= SECONDS_TO_RECORD_AFTER_DETECTION:
                        detection = False
                        if out:  
                            out.release()
                            out = None  
                        print(f'Detection stopped at {current_time}')
                else:
                    timer_started = True
                    detection_stopped_time = time.time()

            if out:  
                out.write(frame)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



@app.route('/')
def index():
    return render_template('index.html')



@app.route('/video')
def video():
    return Response(getFrames(),mimetype='multipart/x-mixed-replace; boundary=frame')



    


    


if __name__ == '__main__':
    app.run(debug=True,port=5000)
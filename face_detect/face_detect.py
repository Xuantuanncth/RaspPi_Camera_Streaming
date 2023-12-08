#! /usr/bin/python # import the necessary packages 
import multiprocessing
import threading
from imutils.video import VideoStream
from imutils import paths
import face_recognition 
import imutils 
import pickle 
import time 
import cv2 
import smtplib
import os
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from flask import Flask, render_template, Response
import socketio
import json 


#Initialize 'current_name' to trigger only when a new person is identified. 
current_name = "unknown" 
#Determine faces from encodings.pickle file model created from train_model.py 
encodingsP = "encodings.pickle" 
# load the known faces and embeddings along with OpenCV's Haar # cascade for face detection 
print("[INFO] loading encodings + face detector...") 
data = pickle.loads(open(encodingsP, "rb").read()) 

# initialize the video stream and allow the camera sensor to warm up 
# Set the ser to the following # src = 0 : for the build in single web cam, could be your laptop webcam 
# src = 2 : I had to set it to 2 inode to use the USB webcam attached to my laptop 
# vs = VideoStream(src=2,framerate=10).start() 
# Is streaming now 
isStreaming = multiprocessing.Value('b', False) 
isTakePicture = multiprocessing.Value('b', False)
isTrainModel = multiprocessing.Value('b', False)
isNewConfig = multiprocessing.Value('b', True)

strange_images = "/home/pi/camera_detect/camera_streaming/photo/strange_images.jpg"
dataset_path = "/home/pi/camera_detect/camera_streaming/dataset"


counter = 0
counter_picture = 0

#================================================================#
#                       App initialization
#================================================================#
app = Flask(__name__)
#================================================================# 
#                   Initialize the SocketIO 
#================================================================# 
sio = socketio.Client()

# Define event handlers
@sio.on('connect')
def on_connect():
    print('Connected to server')

@sio.on('disconnect')
def on_disconnect():
    print('Disconnected from server')

@sio.on('setting_time')
def on_chat_message(data):
    print('Received setting_time:', data)
    global isNewConfig
    with isNewConfig.get_lock():
        isNewConfig.value = True

@sio.on('setting_owner')
def on_setting_message(data):
    print('Received setting_owner:', data)
    global isNewConfig
    with isNewConfig.get_lock():
        isNewConfig.value = True

@sio.on('take_picture')
def on_setting_message(data):
    global isTakePicture
    with isTakePicture.get_lock():
        isTakePicture.value = True

@sio.on('train_model')
def on_setting_message(data):
    global isTrainModel
    print('Received train_model:', data)
    isTrainModel = True
    trainModel()

@sio.on('stream_mode')
def on_setting_message(data):
    global isStreaming
    print('Received stream_mode:', data)
    if data == "ON":
        print('Begin streaming mode')
        with isStreaming.get_lock():
            isStreaming.value = True
    else:
        print('Off streaming mode')
        with isStreaming.get_lock():
            isStreaming.value = False

#================================================================# 
#                   Face detection
#================================================================# 
def face_detect(frame): 
    global counter
    # Detect the fce boxes 
    boxes = face_recognition.face_locations(frame)
    # compute the facial embeddings for each face bounding box
    encodings = face_recognition.face_encodings(frame, boxes)
    names = []
    print("Beginning face detection")
    # loop over the facial embeddings
    for encoding in encodings:
        # attempt to match each face in the input image to our known
        # encodings
        matches = face_recognition.compare_faces(data["encodings"],encoding)
        name = "Unknown" #if face is not recognized, then print Unknown
        if True in matches:
            print("Có nguoi quen")
        else:
            takePicture(frame,strange_images)
            counter += 1
            print("Nguoi la xuat hien")

#================================================================# 
#                   Send email
#================================================================# 
def sendMail(receive_mail): 
    #Set the sender email and password and recipient email 
    from_email_addr = "sendersmarthome@gmail.com"
    from_email_password = "xxke ueoq onjo uthl"
    # to_email_addr="xuantuanncth1@gmail.com"
    email_subject = "[WARNING!] Có người lạ mặt!"
    email_body = "Cảnh báo có người lạ mặt trong sân nhà bạn!"
    if receive_mail != "":
        to_email_addr = receive_mail
    else:
        to_email_addr = "hieutran21042k@gmail.com"
    # create a multipart message
    msg = MIMEMultipart()
    
    # set the email body
    msg.attach(MIMEText(email_body, 'plain'))
    
    # set sender and recipient
    msg['From'] = from_email_addr
    msg['To'] = to_email_addr
    
    # set your email subject
    msg['Subject'] = email_subject
    
    # attach the image
    with open(strange_images, 'rb') as image_file:
        image_data = image_file.read()
        image = MIMEImage(image_data, name="motion_image.jpg")
        msg.attach(image)
    
    # connect to server and send email
    # edit this line with your provider's SMTP server details
    server = smtplib.SMTP('smtp.gmail.com', 587)
    
    # comment out this line if your provider doesn't use TLS
    server.starttls()
    
    server.login(from_email_addr, from_email_password)
    server.send_message(msg)
    server.quit()
    
    print('Email sent')

#================================================================# 
#                  Read configuration file
#================================================================#  
def readingConfiguration():
    file_path = "./configuration.txt" 
    try:
        # Read data from the JSON file
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        return data
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Unable to parse JSON in file '{file_path}'.")
        return None

#================================================================# 
#                  Main program
#================================================================#     
def startFaceDetection(): 
    # global isStreaming
    global counter_picture 
    global isTakePicture 
    global isTrainModel
    global counter

    print("[INFO] loading camera...") 
    vs = VideoStream(usePiCamera=True).start() 
    time.sleep(2.0) 
    
    # loop over frames from the video file stream
    while True:  
        # grab the frame from the threaded video stream and resize it 
        # to 500px (to speedup processing) 
        frame = vs.read() 
        frame = imutils.resize(frame, width=500)
        # Check and update new configuration
        if isNewConfig.value:
            config_data = readingConfiguration()
            if config_data:
                name_model = config_data.get('name')
                email = config_data.get('email')
                start_time = config_data.get('start_time')
                end_time = config_data.get('end_time') 

                # Printing the data
                print("Name:", name_model)
                print("Email:", email)
                print("Start Time:", start_time)
                print("End Time:", end_time)

            with isNewConfig.get_lock():
                isNewConfig.value = False

        if isStreaming.value:
            face_detect(frame)
        if counter == 5:
            sendMail(email)
            counter = 0 
        # display the image to our screen 
        # cv2.imshow("Facial Recognition is Running", frame) 
        if isTakePicture.value:
            print("Take a picture")
            img_name = os.path.join(dataset_path, name_model, "image_{}.jpg".format(counter_picture))
            takePicture(frame,img_name)
            counter_picture += 1
            with isTakePicture.get_lock():
                isTakePicture.value = False

        jpeg = cv2.imencode('.jpg', frame)
        frame=jpeg.tobytes()
        yield (b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        key = cv2.waitKey(1) & 0xFF 
        # quit when 'q' key is pressed 
        if key == ord("q"): 
            break 

#================================================================# 
#                   Take pictures and train models
#================================================================# 
def takePicture(frame,image_name):
    cv2.imwrite(image_name, frame)
    print("{} written!".format(image_name))

def trainModel():
    global counter_picture
    counter_picture = 0
    # our images are located in the dataset folder
    print("[INFO] ============> Starting train model <================")
    imagePaths = list(paths.list_images("dataset"))

    # initialize the list of known encodings and known names
    knownEncodings = []
    knownNames = []

    # loop over the image paths
    for (i, imagePath) in enumerate(imagePaths):
        # extract the person name from the image path
        print("[INFO] processing image {}/{}".format(i + 1,len(imagePaths)))
        name = imagePath.split(os.path.sep)[-2]

        # load the input image and convert it from RGB (OpenCV ordering)
        # to dlib ordering (RGB)
        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # detect the (x, y)-coordinates of the bounding boxes
        # corresponding to each face in the input image
        boxes = face_recognition.face_locations(rgb,
            model="hog")

        # compute the facial embedding for the face
        encodings = face_recognition.face_encodings(rgb, boxes)

        # loop over the encodings
        for encoding in encodings:
            # add each encoding + name to our set of known names and
            # encodings
            knownEncodings.append(encoding)
            knownNames.append(name)

    # dump the facial encodings + names to disk
    print("[INFO] serializing encodings...")
    data = {"encodings": knownEncodings, "names": knownNames}
    f = open("encodings.pickle", "wb")
    f.write(pickle.dumps(data))
    f.close()
    print("[INFO] ============> Finish train model <================")

def stopFaceDetection(): 
    # do a bit of cleanup 
    cv2.destroyAllWindows() 
    vs.stop() 

def socketConnect():
    # Connect to the Socket.IO server
    sio.connect('http://localhost:3000')
    sio.wait()

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(startFaceDetection(),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__": 
    print("This code is executed when the script is run directly.")
    faceProcess = multiprocessing.Process(target=startFaceDetection)
    faceProcess.start()

    socket_io_thread = threading.Thread(target=socketConnect)
    socket_io_thread.start()

    faceProcess.join()
    socket_io_thread.join()


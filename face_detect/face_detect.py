#! /usr/bin/python # import the necessary packages 
import multiprocessing
from imutils.video import VideoStream 
from imutils.video import FPS 
import face_recognition 
import imutils 
import pickle 
import time 
import cv2 
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import socketio 
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
print("[INFO] loading camera...") 
vs = VideoStream(usePiCamera=True).start() 
time.sleep(2.0) 
# start the FPS counter 
fps = FPS().start() 

# Is streaming now 
noStreaming = False 

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

@sio.on('chat')
def on_chat_message(data):
    print('Received message:', data)

@sio.on('setting')
def on_setting_message(data):
    print('Received setting:', data)

#================================================================# 
#                   Face detection
#================================================================# 
def face_detect(frame): 
    # Detect the fce boxes 
	boxes = face_recognition.face_locations(frame)
	# compute the facial embeddings for each face bounding box
	encodings = face_recognition.face_encodings(frame, boxes)
	names = []

	# loop over the facial embeddings
	for encoding in encodings:
		# attempt to match each face in the input image to our known
		# encodings
		matches = face_recognition.compare_faces(data["encodings"],encoding)
		name = "Unknown" #if face is not recognized, then print Unknown

		# check to see if we have found a match
		if True in matches:
			# find the indexes of all matched faces then initialize a
			# dictionary to count the total number of times each face
			# was matched
			matched_Index = [i for (i, b) in enumerate(matches) if b]
			counts = {}

			# loop over the matched indexes and maintain a count for
			# each recognized face face
			for i in matched_Index:
				name = data["names"][i]
				counts[name] = counts.get(name, 0) + 1

			# determine the recognized face with the largest number
			# of votes (note: in the event of an unlikely tie Python
			# will select first entry in the dictionary)
			name = max(counts, key=counts.get)

			#If someone in your dataset is identified, print their name on the screen
			if current_name != name:
				current_name = name
				print(current_name)

		# update the list of names
		names.append(name)

	# loop over the recognized faces
	for ((top, right, bottom, left), name) in zip(boxes, names):
		# draw the predicted face name on the image - color is in BGR
		cv2.rectangle(frame, (left, top), (right, bottom),
			(0, 255, 225), 2)
		y = top - 15 if top - 15 > 15 else top + 15
		cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
			.8, (0, 255, 255), 2)  

#================================================================# 
#                   Send email
#================================================================# 
def sendMail(): 
    #Set the sender email and password and recipient email 
    from_email_addr = "sendersmarthome@gmail.com"
    from_email_password = "xxke ueoq onjo uthl"
    to_email_addr = "hieutran21042k@gmail.com"
    email_subject = "[WARNING!] Có người lạ mặt!"
    email_body = "Cảnh báo có người lạ mặt trong sân nhà bạn!"

    # specify the path to the image file
    image_path = "/home/pi/camera_detect/facial_recognition/dataset/tuan/image_0.jpg"
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
    with open(image_path, 'rb') as image_file:
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
    
def startFaceDetection(): 
    # loop over frames from the video file stream 
    while True: 
        # grab the frame from the threaded video stream and resize it 
        # to 500px (to speedup processing) 
        frame = vs.read() 
        frame = imutils.resize(frame, width=500) 
        if (noStreaming): 
            frame = face_detect(frame) 
            # display the image to our screen 
        cv2.imshow("Facial Recognition is Running", frame) 
        key = cv2.waitKey(1) & 0xFF 
        # quit when 'q' key is pressed 
        if key == ord("q"): 
            break 
        # update the FPS counter 
        fps.update() 
        # stop the timer and display FPS information 
        fps.stop() 
        # print("[INFO] elasped time: {:.2f}".format(fps.elapsed())) 
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps())) 

#================================================================# 
#                   Take pictures and train models
#================================================================# 
def takePicture(frame):
    cv2.imwrite(img_name, frame)
    print("{} written!".format(img_name))cv2.imwrite(img_name, frame)
    print("{} written!".format(img_name))

def trainModel():
    # our images are located in the dataset folder
    print("[INFO] start processing faces...")
    imagePaths = list(paths.list_images("dataset"))

    # initialize the list of known encodings and known names
    knownEncodings = []
    knownNames = []

    # loop over the image paths
    for (i, imagePath) in enumerate(imagePaths):
        # extract the person name from the image path
        print("[INFO] processing image {}/{}".format(i + 1,
            len(imagePaths)))
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

def stopFaceDetection(): 
    # do a bit of cleanup 
    cv2.destroyAllWindows() 
    vs.stop() 
    
if __name__ == "__main__": 
    print("This code is executed when the script is run directly.")
    # Connect to the Socket.IO server
    sio.connect('http://localhost:3000')
    sio.wait()
    startFaceDetection()

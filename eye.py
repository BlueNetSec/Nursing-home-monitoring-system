import face_recognition
from pymongo import MongoClient
import picamera
import numpy as np
import socket
import os
from param import *
import pyimgur
import sys

def main():
    
    client_info = "mongodb://" + "zack" + ":" + "password" + "@" + "localhost" + ":" + "27017" + "/" + "admin"
    dbclient = MongoClient('172.29.60.160')
    db = dbclient["NursingHome"]

    if len(sys.argv) < 5:
        sys.exit("Insufficient arguments.")
    elif sys.argv[1] != '-l':
        sys.exit("Improper flag for argument 1.")
    elif sys.argv[3] != '-e':
        sys.exit("Improper flag for argument 3.")
    


    host = sys.argv[2]
    #host = '172.29.42.244'
    port = 2000
    size = 1024
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))
            
    host2 = sys.argv[4]
    port2 = 2004
    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s2.connect((host2,port2))
    
    while 1:
        command = input("Please enter a command. A: Add a new approved visitor. R: Run monitoring system.")

        if (command == "A"):
            name = input("What is the new approved visitors name?")
            relation = input("What is the new approved visitors relationship to the resident?")
            input("Enter any key to take the photo.")
            imagePath = "/home/pi/Desktop/ProjectFinal_NetApps/approved/{0}.png".format(name)
            systemCommand = 'fswebcam -q -r 320x240 --no-banner --png --save {0}'.format(imagePath)
            os.system(systemCommand)
            filename = name + ".png"
            collection = 'approvedvisitorslog'
            db[collection].insert_one({'Name': name, 'Relation': relation, 'AssociatedImage': filename})
            imgur_client_id = param['imgur_client_id']
            image_path = imagePath
            im = pyimgur.Imgur(imgur_client_id)
            
            print("ImagePath: ", image_path)
            uploaded_image = im.upload_image(image_path, title="Unknown persononal")
            link = uploaded_image.link
            print("Link: ", link)
            msg = "AddProfile:{0}:{1}".format(filename, link)
            s.send(msg.encode())
            s2.send(msg.encode())


        elif (command == "R"):
            msg = "break"
            s2.send(msg.encode())
            
            for f in os.listdir('./approved'):
                if f.endswith('.png'):
                    filepath = './approved/{}'.format(f)
                    pic = face_recognition.load_image_file(filepath)
                    picencode = face_recognition.face_encodings(pic)[0]
                    filename = f.split('.')[0]
                    filename = './approved/{}'.format(filename)
                    np.save(filename, picencode)

            # Initialize some variables
            face_locations = []
            face_encodings = []
            
            while True:
                print("Capturing image.")
                # Grab a single frame of video from the RPi camera as a numpy array
                #camera.capture('face.jpg')
                #camera.capture(output, format="rgb")
                #use fswebcam
                os.system('fswebcam -q -r 320x240 --no-banner -S 3 --png --save unknown.png')
                unknown_image = face_recognition.load_image_file("unknown.png")
                print("Image captured.")
                # Find all the faces and face encodings in the current frame of video
                print("Looking for faces in image.")
                face_locations = face_recognition.face_locations(unknown_image)
                print("Found {} faces in image.".format(len(face_locations)))
                if len(face_locations) > 0:
                    print("Creating face encoding")
                    unknown_face_encoding = face_recognition.face_encodings(unknown_image)[0]

                    flag = False
                    print("Comparing faces")
                    for f in os.listdir('./approved'):
                        if f.endswith('.npy'):
                            filepath = './approved/{}'.format(f)
                            encoding = np.load(filepath)
                            if face_recognition.compare_faces([encoding], unknown_face_encoding)[0] == True:
                                print("Visitor is approved.")
                                flag = True
                                name = f.split('.')[0]
                                msg = "Approved:" + name
                                s.send(msg.encode())

                    if flag == False:
                        print("Unknown person, sending image to log RPi.")
                        msg = "Unauthorized:"
                        imgur_client_id = param['imgur_client_id']
                        image_path = param['image_path']
                        im = pyimgur.Imgur(imgur_client_id)
                        uploaded_image = im.upload_image(image_path, title="Unknown persononal")
                        link = uploaded_image.link
                        msg += link
                        s.send(msg.encode())
                        s.recv(1024)


if __name__ == "__main__":
    main()
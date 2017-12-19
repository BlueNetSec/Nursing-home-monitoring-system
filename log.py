import socket
import pymongo
from pymongo import MongoClient
from time import gmtime, strftime
from PIL import Image
from param import *
from twilio.rest import Client
import requests

def main():
    client_info = "mongodb://" + "zack" + ":" + "password" + "@" + "localhost" + ":" + "27017" + "/" + "admin"
    dbclient = MongoClient('localhost')
    db = dbclient["NursingHome"]

    host = ''
    port = 2000
    backlog = 5
    size = 1024
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host,port))
    s.listen(backlog)
    client, address = s.accept()

    myImage = b''
    potential_message = ""
    while True:
        while True:
            data = client.recv(size)
            potential_message = data.decode()

            if "AddProfile:" in potential_message:
                potential_message = potential_message.split(':', 2)
                filename = potential_message[1]
                link = potential_message[2]
                print("Link: ", link)
                f = open (filename, 'wb')
                f.write(requests.get(link).content)
                f.close


            elif "Approved:" in potential_message:
                name = potential_message.split(':')[1]
                displayImage(name, db)

            elif "Unauthorized:" in potential_message:
                collection = "visitorlog"
                link = potential_message.split(':', 1)[1]
                print(link)
                print(potential_message)
                db[collection].insert_one({'Visitor': 'Unknown', 'Time of Visit': strftime("%Y-%m-%d %H:%M:%S", gmtime())})
                print("Unapproved Visitor. Image being received.")
                sendImageToSecurity(link)
                print("Sending unknown visitor image to security.")

            done = "done"
            client.send(done.encode())


def displayImage(name, db):
    collection = "visitorlog"
    filename = name + ".png"
    db[collection].insert_one({'Visitor': name, 'Time of Visit': strftime("%Y-%m-%d %H:%M:%S", gmtime())})
    print("Approved Visitor.")
    theVisitor = db.approvedvisitorslog.find_one({'Name': name}, {'_id': 0, 'Name': 1, 'Relation': 1})
    relation = theVisitor.get('Relation')
    visitorname = theVisitor.get('Name')
    print(visitorname, " is here to see you. They are your ", relation, ".")
    display = Image.open(filename)
    display.show()


def sendImageToSecurity(link):
    twilio_account_sid = param['twilio_account_sid']
    twilio_auth_token = param['twilio_auth_token']
    security_guard_number = param['security_guard_number']
    system_number = param['system_number']

    client = Client(twilio_account_sid, twilio_auth_token)

    message = client.api.account.messages.create(
        to=security_guard_number,
        from_=system_number,
        body="Person Unrecognized!",
        media_url=link)


if __name__ == "__main__":
    main()

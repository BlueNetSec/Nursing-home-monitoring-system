import pymongo
from pymongo import MongoClient
from time import gmtime, strftime
from PIL import Image
import socket
import requests
import urllib.request
import sys

def main():
    if len(sys.argv) < 3:
        sys.exit("Insufficient arguments.")
    elif sys.argv[1] != '-l':
        sys.exit("Improper flag for argument 1.")

    client_info = "mongodb://" + "zack" + ":" + "password" + "@" + "localhost" + ":" + "27017" + "/" + "admin"
    dbclient = MongoClient(sys.argv[2])
    db = dbclient["NursingHome"]

    host = ''
    port = 2004
    backlog = 5
    size = 1024
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(backlog)
    client, address = s.accept()

    while 1:
        data = client.recv(size)
        data = data.decode()
        if "AddProfile:" in data:
            msg = data.split(':',2)
            filename = msg[1]
            link = msg[2]
            print(link)
            urllib.request.urlretrieve(link, filename)
            #f = open(filename, 'wb')  # create file locally
            #f.write(requests.get(link).content)  # write image content to this file
            #f.close()
        else:
            break

    while True:
        command = input("Please enter the letter for the command you would like to use. U: Add an a new event. H: See past events. V: See history of visitors. A: View list of approved visitors.")
        if command is "U":
            addEvent(db)
        elif command is "H":
            requestEventHistory(db)
        elif command is "V":
            requestVisitorHistory(db)
        elif command is "A":
            requestApprovedVisitors(db)
        else:
            print("Command entered was invalid. Re-enter a valid command")


def addEvent(db):
    collection = 'eventlog'
    name = input("Enter your name.")
    description = input("Please enter What happened during your visit with the resident.")
    db[collection].insert_one({'Name': name, 'Description of visit': description, 'Time of Visit': strftime("%Y-%m-%d %H:%M:%S", gmtime())})

def requestEventHistory(db):
    collection = 'eventlog'
    events = db[collection].find({'Name': {'$exists': 'true'}},
                                  {'_id':0, 'Name': 1, 'Description of visit': 1, 'Time of Visit': 1})
    for event in events:
        print(event)

def requestVisitorHistory(db):
    collection = 'visitorlog'
    visitors = db[collection].find({'Visitor': {'$exists': 'true'}},
                                 {'_id': 0, 'Visitor': 1, 'Time of Visit': 1})
    for visitor in visitors:
        print(visitor)

def requestApprovedVisitors(db):
    collection = 'approvedvisitorslog'
    visitors = db[collection].find({'Name': {'$exists': 'true'}},
                                   {'_id': 0, 'Name': 1, 'Relation': 1, 'AssociatedImage': 1})
    for visitor in visitors:
        filename = visitor.get('AssociatedImage')
        display = Image.open(filename)
        display.show()
        print(visitor)

if __name__ == "__main__":
    main()
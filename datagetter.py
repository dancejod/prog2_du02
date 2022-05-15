import requests, zipfile
from io import BytesIO

def get_data():
    user_input = str(input("Prajete si stiahnut nove data? Y/N"))
    if user_input == 'Y':
        req = requests.get("http://data.pid.cz/PID_GTFS.zip")
        print("Stahovanie dokoncene.")

        zip = zipfile.ZipFile(BytesIO(req.content))
        zip.extractall("gtfs")
        print("Data uspesne extrahovane.")
    
    if user_input == 'N':
        pass
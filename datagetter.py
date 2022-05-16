# Tento skript sluzi na stiahnutie potrebnych dat z databazy PID.

try:
    import requests, zipfile
    from requests import exceptions
    from urllib.error import HTTPError
    from io import BytesIO
    import sys

except ModuleNotFoundError:
    sys.exit("Pozadovana kniznica nebola najdena. Skontrolujte, ci mate nainstalovanu kniznicu requests.")

def get_data():
    try:
        user_input = str(input("Prajete si stiahnut nove data? Y/N "))
        if user_input.lower() == 'y':
            req = requests.get("http://data.pid.cz/PID_GTFS.zip")
            print("Stahovanie dokoncene. Data budu rozbalene do zlozky gtfs/ v tomto adresari.")

            zip = zipfile.ZipFile(BytesIO(req.content))
            zip.extractall("gtfs")
            print("Data uspesne extrahovane.")
        
        elif user_input.lower() == 'n':
            pass

        else:
            sys.exit("Neplatny vstup. Program sa teraz ukonci.")
        
    except zipfile.BadZipFile:
        sys.exit("Data nie su vo validnom .zip subore.")
    
    except zipfile.LargeZipFile:
        sys.exit("Zip subor je prilis velky na rozbalenie.")

    except FileNotFoundError:
        sys.exit("Subor neexistuje. Skontrolujte, ci je k nemu spravne zadana adresa.")

    except ConnectionError:
        sys.exit("Nemate pripojenie k internetu.")
    
    except exceptions.Timeout:
        sys.exit("Vyprsal cas na poziadavku.")
    
    except exceptions.URLRequired:
        sys.exit("K suboru nie je zadana platna adresa. Skontrolujte ju a opravte ju.")
    
    except HTTPError:
        sys.exit("Nepodarilo sa stiahnut data.")

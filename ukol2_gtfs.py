import csv
import sys
from datetime import datetime, timedelta

# Priprava potrebnych slovnikov a zoznamov
our_data_stops={}
our_data_stop_times=[]
our_data_trips={}
our_data_routes={}
our_data_services={}

try:
    '''
    Import pomocneho skriptu datagetter.py a vykonanie metody get_data().
    
    Funkcia sa dotazuje na stiahnutie novych dat, ak pouzivatel suhlasi, stiahne
    najnovsie data jizdnich radu z PID.
    '''
    import datagetter
    datagetter.get_data()

except ModuleNotFoundError:
    sys.exit("Nepodarilo sa nacitat skript datagetter.py. Skontrolujte, ci je umiestneny v rovnakom adresari ako tento skript.")

except FileNotFoundError:
    sys.exit("Subor datagetter.py nebol najdeny. Skontrolujte, ci je umiestneny v rovnakom adresari ako tento skript.")

except PermissionError:
    sys.exit("Nemate opravnenia na subor datagetter.py.")

except IOError:
    sys.exit("Subor datagetter.py neexistuje, alebo nie je v spravnom adresari.")

def convert_user_date(date_user):
    '''
    Funkce konvertuje datum zadany uzivatelem na objekt tridy date.

        Parametry:
            date_user (str): Datum zadany uzivatelem v terminali.

        Vraci:
            user_date_obj (objekt): Objekt tridy date.
    '''
    date_time_obj = datetime.strptime(date_user,'%d.%m.%Y')
    user_date_obj=datetime.date(date_time_obj)
    return user_date_obj

def convert_int_date(date_int):
    '''
    Funkce konvertuje datum ze souboru calendar.txt na objekt tridy date.

        Parametry:
            date_int (int): Datum ze souboru calendar.txt.

        Vraci:
            data_date_obj (objekt): Objekt tridy date.
    '''
    date_time_obj = datetime.strptime(date_int,'%Y%m%d')
    data_date_obj=datetime.date(date_time_obj)
    return data_date_obj

def daterange(start, end):
    '''
    Funkce vezme objekty tridy date a vrati set datumu v intervalu mezi start a end.

        Parametry:
            start (objekt): Objekt tridy date.
            end (objekt): Objekt tridy date.

        Vraci:
            dates (set): Set datumu v intervalu <start, end>.
    '''
    dates=set()
    # Postupne pridavani datumu v zadanem intervalu do setu
    for n in range(int ((end - start).days)+1):
        dates.add(start + timedelta(n))
    return dates

class Stop(object):
    """
    Trida objektu Stop.

        Atributy:
            id (str): ID zastavky z jizdnych radu.
            stop_name (str): Nazev zastavky z jizdnich radu.
    """
    def __init__ (self, stop_id, stop_name):
        self.id=stop_id
        self.name=stop_name

class Route(object):
    """
    Trida objektu Route.

        Atributy:
            id (str): ID linky z jizdnych radu.
            route_name (str): Nazev linky z jizdnich radu.
    """
    def __init__(self, route_id, route_name):
        self.id = route_id
        self.name = route_name

class Service(object):
    """
    Trida objektu Service.

        Atributy:
            service_id (str): ID sluzby, ktera sprovoznuje spoje.
            service_days (set): Set objektu tridy date, kdy dana sluzba jezdi.
    """
    def __init__(self,service_id,service_days):
        self.id=service_id
        self.service_days=service_days

    @classmethod
    def get_service(cls,service_row):
        """ Vrati objekt tridy Service, kde je parametrem radek z csv.DictReaderu."""
        # Ukladani dnu, kdy sluzba funguje
        service_days = set()
        #Konverze datumu ze souboru na objekt tridy date
        start,end = convert_int_date(service_row['start_date']),convert_int_date(service_row['end_date'])
        # Vytvoreni setu datumu ziskany z intervalu <start; end>
        service_dates = daterange(start,end)
        week_service_list=[service_row['monday'],service_row['tuesday'],service_row['wednesday'],service_row['thursday'],service_row['friday'],service_row['saturday'],service_row['sunday']]
        # Seznam, ve kterém je uloženo, jaké dny v týdnu funguje service, když funguje, tak položka je '1'
        for date in service_dates:
            # Iterace přes dny v odpovídajícím intervalu, uloží se den v týdnu podle data (0-6)
            day_in_week_int=date.weekday()
            # Když service funguje daný den v týdnu, tak ho přidáme do setu dní, kdy vybraný service funguje
            if week_service_list[day_in_week_int] == '1': 
                service_days.add(date)
        # Ulozeni noveho objektu tridy Service a jeho vraceni
        service_complete=Service(service_row['service_id'],service_days) 
        return service_complete 

class Trip(object):
    """
    Trida objektu Trip.

        Atributy:
            trip_id (str): ID spoje z jizdnich radu.
            route (objekt): Objekt tridy Route.
            service (objekt): Objekt tridy Service.
    """
    def __init__ (self, trip_id, route, service):
        self.id=trip_id
        self.route=route
        self.service=service

class StopTime(object):
    """
    Trida objektu StopTime.

        Atributy:
            trip (objekt): Objekt tridy Trip.
            stop (objekt): Objekt tridy Stop.
            stop_sequence (str): Poradi zastavky v spoji.
    """
    def __init__(self, trip, stop, stop_sequence):
        self.trip=trip
        self.stop=stop
        self.stop_sequence=stop_sequence

class StopSegment(object):
    """
    Trida objektu StopSegment.

        Atributy:
            from_stop (objekt): Objekt tridy Stop.
            to_stop (objekt): Objekt tridy Stop.
            trip (list): Seznam spoju prochazejicich mezi from_stop a to_stop.
            route (objekt): Set linek prochazejicich mezi from_stop a to_stop.
    """
    def __init__(self, from_stop, to_stop, trip, route):
        self.from_stop = from_stop
        self.to_stop = to_stop
        self.trips = [trip]
        self.routes = {route}
        
    @classmethod
    def get_segment_dict(cls, data_stop_times,date_string):
        """
        Class metoda vrati slovnik, kde klicem je dvojice ID za sebou jdoucich zastavek
        a hodnotou objekt tridy StopSegment.

            Parametry:
                    data_stop_times (list): Seznam objektu tridy StopTime.
                    date_string (str): Datum ve formatu DD.MM.RRRR zadane uzivatelem.
        """
        # Konverze date_string na objekt tridy date
        user_date=convert_user_date(date_string)
        segment_dict={}
        for current_stop_time in data_stop_times:
            # Kdyz datum zadane uzivatelem neni v seznamu datumu kdy funguje sluzba,
            # ktera odpovida spoji, cyklus pokracuje s dalsi iteraci
            if user_date not in current_stop_time.trip.service.service_days:
                continue
            # Jinak cyklus probehne a bude se pokouset vytvaret objekt typu StopSegment
            # Kdyz je zastavka prvni na spoji, priradime prave iterovanou zastavku vychozi zastavce
            # a cyklus pokracuje s dalsi iteraci
            if current_stop_time.stop_sequence == '1':
                from_stop = current_stop_time.stop
                continue
            # Kdyz je zastavka druha na spoji, priradime prave iterovanou zastavku cilove zastavce
            elif current_stop_time.stop_sequence == '2':
                to_stop = current_stop_time.stop
            # Jinak se z cílové stane výchozí a cílové přiřadíme aktualni zastavku
            else:
                from_stop = to_stop
                to_stop = current_stop_time.stop
            # Vytvorime segment_key z ID obou zastavek, ktery jednoznacne identifikuje segment
            segment_key=(from_stop.id,to_stop.id)
            # Objekt tridy Trip pro aktualni zastavku ulozime do promenne
            trip=current_stop_time.trip
            # Objekt třídy Route pro aktualni spoj uložíme do proměnné
            route=trip.route.name 
            # Kdyz segment_key jeste neni klicem ve slovniku segmentu,
            # vytvorime objekt tridy StopSegment, ktery vezme jako parametry
            # promenne vytvorene behem aktualni iterace
            if segment_key not in segment_dict:
                segment=StopSegment(from_stop,to_stop,trip,route)
                # Objekt třídy StopSegment uložíme jako hodnotu do slovníku
                segment_dict[(segment_key)]=segment 
            else:
            # Když ve slovníku už segment_key je,
            # přidáme odpovídající trip do seznamů tripů odpovídajícího segmentu,
            # pokud v slovníku linek odpovídajího segmentu není aktuální linka uložena, tak jí tam přidáme
                segment_dict[segment_key].trips.append(trip) 
                segment_dict[segment_key].routes.add(route)
        # Na závěr vrátime cely slovník
        return segment_dict 
    
    @classmethod
    def print_trip_count_from_segments(cls, segment_dict):
        """
        Class metoda seřadí slovník segmentů podle délky seznamu tripů jím projíždějících 
        a vytiskne 5. nejfrekventovanějších.

            Parametry:
                segment_dict (dict): Slovnik segmentu ziskanych v metode get_segmet_dict.
        """
        # Seřadení slovník segmentů podle délky seznamu tripů jím projíždějících
        sorted_segment_dict = sorted(segment_dict.values(), key = lambda x: len(x.trips), reverse=True)
        i = 1
        for item in sorted_segment_dict[:5]:
            print(f"{i}. nejfrekventovanější úsek je mezi zastávkami {item.from_stop.name} a {item.to_stop.name}. Projede jím {len(item.trips)} spojů linek {', '.join(sorted(item.routes))}.")
            i+=1

# Otevreni potrebnych souboru pro chod programu
try:
    stops = "stops.txt"
    with open("gtfs/"+stops, encoding="utf-8", newline='') as raw_stops:
        # otevření souboru stops.txt a uložení potřebných dat do slovníku
        stops_reader = csv.DictReader(raw_stops)
        for row in stops_reader:
            stop = Stop(row['stop_id'], row['stop_name'])
            our_data_stops[stop.id]= stop

except FileNotFoundError:
    sys.exit(f"Subor {stops} nebol najdeny. Uistite sa, ze je umiestneny v tomto adresari v priecinku gtfs/.")

except PermissionError:
    sys.exit(f"K suboru {stops} nemate pozadovane prava.")

try:
    routes = 'routes.txt'
    with open("gtfs/"+routes, encoding="utf-8", newline='') as raw_routes:
        # otevření souboru routes.txt a uložení potřebných dat do slovníku
        routes_reader = csv.DictReader(raw_routes)
        for row in routes_reader:
            route = Route(row['route_id'], row['route_short_name'])
            our_data_routes[route.id] = route

except FileNotFoundError:
    sys.exit(f"Subor {routes} nebol najdeny. Uistite sa, ze je umiestneny v tomto adresari v priecinku gtfs/.")

except PermissionError:
    sys.exit(f"K suboru {routes} nemate pozadovane prava.")

try:
    calendar = 'calendar.txt'        
    with open("gtfs/"+calendar, encoding="utf-8", newline='') as raw_calendar:
        # otevření souboru calendar.txt a uložení potřebných dat do slovníku za použití implementované metody v tride Service
        calendar_reader = csv.DictReader(raw_calendar)
        for row in calendar_reader:
            service=Service.get_service(row)
            our_data_services[service.id]=service

except FileNotFoundError:
    sys.exit(f"Subor {calendar} nebol najdeny. Uistite sa, ze je umiestneny v tomto adresari v priecinku gtfs/.")

except PermissionError:
    sys.exit(f"K suboru {calendar} nemate pozadovane prava.")

try:
    trips = 'trips.txt'
    with open("gtfs/"+trips, encoding="utf-8", newline='') as raw_trips:
        # otevření souboru trips.txt a uložení potřebných dat do slovníku
        trips_reader = csv.DictReader(raw_trips)
        for row in trips_reader:
            route_pk = row['route_id']
            service_pk = row['service_id']
            trip = Trip(row['trip_id'], our_data_routes[route_pk], our_data_services[service_pk])
            our_data_trips[trip.id] = trip

except FileNotFoundError:
    sys.exit(f"Subor {trips} nebol najdeny. Uistite sa, ze je umiestneny v tomto adresari v priecinku gtfs/.")

except PermissionError:
    sys.exit(f"K suboru {trips} nemate pozadovane prava.")

try:
    stop_times = 'stop_times.txt'
    with open("gtfs/"+stop_times, encoding="utf-8", newline='') as raw_stop_times:
        # otevření souboru stop_times.txt a uložení potřebných dat do seznamu
        stop_times_reader = csv.DictReader(raw_stop_times)
        for row in stop_times_reader:
            trip_pk = row['trip_id']
            stop_pk = row['stop_id']
            stop_time = StopTime(our_data_trips[trip_pk], our_data_stops[stop_pk], row['stop_sequence'])
            our_data_stop_times.append(stop_time)

except FileNotFoundError:
    sys.exit(f"Subor {stop_times} nebol najdeny. Uistite sa, ze je umiestneny v tomto adresari v priecinku gtfs/.")

except PermissionError:
    sys.exit(f"K suboru {stop_times} nemate pozadovane prava.")

# Sprovozneni programu, uzivatel musi otevrit skript v terminalu
# zadanim python ./ukol2_gtfs.py DD.MM.RRRR
# Jinak se program ukonci
try:    
    user_date = StopSegment.get_segment_dict(our_data_stop_times, sys.argv[1])

except ValueError:
    sys.exit("Zadali ste datum v nespravnom formate. Uistite sa, ze ho zadavate vo formate: DD.MM.RRRR")

except IndexError:
    sys.exit("Nezadali ste datum, pre ktory chcete vygenerovat najfrekventovanejsie useky.")

# Vytisknuti nejfrekventovanejsich linek v zadany den
StopSegment.print_trip_count_from_segments(user_date)
import csv
import sys
from datetime import datetime,date,timedelta

our_data_stops={}
our_data_stop_times=[]
our_data_trips={}
our_data_routes={}
our_data_services={}

try:
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

except:
    sys.exit("Nieco sa pokazilo, program sa teraz ukonci.")

def convert_user_date(date_user):
    # konvertuje datum zadaný uživatelem (string) na objekt třídy date
    date_time_obj = datetime.strptime(date_user,'%d.%m.%Y')
    user_date_obj=datetime.date(date_time_obj)
    return user_date_obj

def convert_int_date(date_int):
    # konvertuje datum ze souboru calendar.txt na objekt třídy date
    date_time_obj = datetime.strptime(date_int,'%Y%m%d')
    data_date_obj=datetime.date(date_time_obj)
    return data_date_obj

def daterange(start, end):
    # vezme objekty typu date a vratí seznam datumů v intervalu mezi start a end
    dates=[]
    for n in range(int ((end - start).days)+1):
        dates.append(start + timedelta(n))
    return dates

class Stop(object):
    # třída objektů Stop s atributy id(str) a stop_name(str)
    def __init__ (self, stop_id, stop_name):
        self.id=stop_id
        self.name=stop_name

class Route(object):
    # třída objektů Route s atributy id(str) a route_name(str)
    def __init__(self, route_id, route_name):
        self.id = route_id
        self.short_name = route_name

class Service(object):
    # třída objektů Service s atributy id(str) a service_days(list) s položkami třídy date, kdy service funguje
    def __init__(self,service_id,service_days):
        self.id=service_id
        self.service_days=service_days # list objektu tridy date, kdy danej service jezdi

    @classmethod
    def get_service(cls,service_row):
        # vrátí objekt třídy Service, parametrem je řádek z csv.DictReaderu
        service_days = [] # sem se budou ukládat dny, kdy service funguje
        start,end = convert_int_date(service_row['start_date']),convert_int_date(service_row['end_date']) # konverze datumů ze souboru na objekt třídy date
        service_dates = daterange(start,end) # seznam datumů získaný z intervalu mezi start a end
        week_service_list=[service_row['monday'],service_row['tuesday'],service_row['wednesday'],service_row['thursday'],service_row['friday'],service_row['saturday'],service_row['sunday']]
        # seznam, ve kterém je uloženo, jaké dny v týdnu funguje service, když funguje, tak položka je '1'
        for date in service_dates:
            # iterace přes dny v odpovídajícím intervalu
            day_in_week_int=date.weekday() # uloží se den v týdnu podle data (0-6)
            if week_service_list[day_in_week_int] == '1': 
                # když service funguje daný den v týdnu, tak ho přidáme do seznamu dní, kdy vybraný service funguje
                service_days.append(date)
        service_complete=Service(service_row['service_id'],service_days) # sem se uloží objekt třídy Service
        return service_complete # vrátíme objekt třídy Service

class Trip(object):
    # objekt třídy Trip s atributy id(str), route(Route) a service(Service)
    def __init__ (self, trip_id, route, service):
        self.id=trip_id
        self.route=route
        self.service=service

class StopTime(object):
    # objekt třídy StopTime s atributy trip(Trip), stop(Stop) a stop_sequence(str)
    def __init__(self, trip, stop, stop_sequence):
        self.trip=trip
        self.stop=stop
        self.stop_sequence=stop_sequence

class StopSegment(object):
    # objekt třídy StopSegment s atributy from_stop(Stop), to_stop(Stop), trips(list) a routes(list)
    # vždy je definovaný dvojicí from_stop a to_stop
    def __init__(self, from_stop, to_stop, trip,route):
        self.from_stop = from_stop
        self.to_stop = to_stop
        self.trips = [trip]
        self.routes = [route]
        
    @classmethod
    def get_segment_dict(cls, data_stop_times,date_string):
        # vrátí slovník, kde klíčem je dvojice from_stop.id a to_stop.id a hodnotou objekt třídy StopSegment
        # parametrem je seznam objektů třídy StopTime a datum ve formátu DD.MM.RRRR zadané uživatelem
        user_date=convert_user_date(date_string) # konverze date_string na objekt třídy date
        segment_dict={}
        for current_stop_time in data_stop_times:
            if user_date not in current_stop_time.trip.service.service_days:
                # když je datum zadané uživatelem není seznamu datumů, kdy funguje service odpovídající tripu odpovídající current_stop_time
                continue # pokračujeme s další iterací
            else:
                # jinak se cyklus proběhne
                if current_stop_time.stop_sequence == '1':
                    # když je zastávka první na tripu, přiřadíme zastávku z current_stop_time výchozí zastávce
                    from_stop = current_stop_time.stop
                    continue
                elif current_stop_time.stop_sequence == '2':
                    # když zastávka 2. na tripu, přiřadíme zastávku z current_stop_time cílové zastávce
                    to_stop = current_stop_time.stop
                else:
                    # jinak se z cílové stane výchozí a cílové přiřadíme zastávku z current_stop_time
                    from_stop = to_stop
                    to_stop = current_stop_time.stop
                segment_key=(from_stop.id,to_stop.id) # vytvoříme segment_key z id obou zastávek, což je jednoznačný identifikátor segmentů
                trip=current_stop_time.trip # objekt třídy Trip uložíme do proměnné
                route=trip.route.short_name # objekt třídy Route uložíme do proměnné
                if segment_key not in segment_dict:
                # když segment_key jestě není jako klíč ve slovníku segmentů:
                    segment=StopSegment(from_stop,to_stop,trip,route) # vytvoříme objekt třídy StopSegment, který vezme jako parametry proměnné vytvořené během této iterace
                    segment_dict[(segment_key)]=segment # objekt třídy StopSegment uložíme jako hodnotu do slovníku
                else:
                # když ve slovníku už segment_key je:
                    segment_dict[segment_key].trips.append(trip) # přidáme odpovídající trip do seznamů tripů odpovídajícího segmentu
                    if route not in segment_dict[segment_key].routes:
                        # pokud v slovníku linek odpovídajího segmentu není aktuální linka uložena, tak jí tam přidáme
                        segment_dict[segment_key].routes.append(route)
        return segment_dict # vratíme cely slovník
    

    @classmethod
    def print_trip_count_from_segments(cls, segment_dict):
        # seřadí slovník segmentů podle délky seznamu tripů jím projíždějících a vytiskne 5. nejfrekventovanějších
        sorted_segment_dict = sorted(segment_dict.values(), key = lambda x: len(x.trips), reverse=True)
        i = 1
        for item in sorted_segment_dict[:5]:
            print(f"{i}. nejfrekventovanější úsek je mezi zastávkami {item.from_stop.name} a {item.to_stop.name}. Projede jím {len(item.trips)} spojů linek {', '.join(sorted(item.routes))}.")
            i+=1
        

with open('gtfs/stops.txt',encoding="utf-8", newline='') as raw_stops:
    # otevření souboru stops.txt a uložení potřebných dat do slovníku
    stops_reader = csv.DictReader(raw_stops)
    for row in stops_reader:
        stop = Stop(row['stop_id'], row['stop_name'])
        our_data_stops[stop.id]= stop

with open('gtfs/routes.txt',encoding="utf-8", newline='') as raw_routes:
    # otevření souboru routes.txt a uložení potřebných dat do slovníku
    routes_reader = csv.DictReader(raw_routes)
    for row in routes_reader:
        route = Route(row['route_id'], row['route_short_name'])
        our_data_routes[route.id] = route
        
with open('gtfs/calendar.txt',encoding="utf-8", newline='') as raw_calendar:
    # otevření souboru calendar.txt a uložení potřebných dat do slovníku za použití námi implementované metody
    calendar_reader = csv.DictReader(raw_calendar)
    for row in calendar_reader:
        service=Service.get_service(row)
        our_data_services[service.id]=service

with open('gtfs/trips.txt',encoding="utf-8", newline='') as raw_trips:
    # otevření souboru trips.txt a uložení potřebných dat do slovníku
    trips_reader = csv.DictReader(raw_trips)
    for row in trips_reader:
        route_pk = row['route_id']
        service_pk = row['service_id']
        trip = Trip(row['trip_id'], our_data_routes[route_pk], our_data_services[service_pk])
        our_data_trips[trip.id] = trip

with open('gtfs/stop_times.txt',encoding="utf-8", newline='') as raw_stop_times:
    # otevření souboru stop_times.txt a uložení potřebných dat do seznamu
    stop_times_reader = csv.DictReader(raw_stop_times)
    for row in stop_times_reader:
        trip_pk = row['trip_id']
        stop_pk = row['stop_id']
        stop_time = StopTime(our_data_trips[trip_pk], our_data_stops[stop_pk], row['stop_sequence'])
        our_data_stop_times.append(stop_time)

#datum=str(input("zadejte datum ve formátu dd.mm.rrrr "))
x=StopSegment.get_segment_dict(our_data_stop_times, sys.argv[1])
StopSegment.print_trip_count_from_segments(x)




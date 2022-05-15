import csv
import sys
from datetime import datetime,date,timedelta

our_data_stops={}
our_data_stop_times=[]
our_data_trips={}
our_data_routes={}
our_data_services={}

def convert_user_date(date_user):
    date_time_obj = datetime.strptime(date_user,'%d.%m.%Y')
    year=date_time_obj.year
    month=date_time_obj.month
    day=date_time_obj.day
    user_date_obj=date(year,month,day)
    return user_date_obj


def convert_int_date(date_int): # konvertuje treba 20220429 (29. aprila 2022) na objekt typu date
    date_time_obj = datetime.strptime(date_int,'%Y%m%d')
    year=date_time_obj.year
    month=date_time_obj.month
    day=date_time_obj.day
    data_date_obj=date(year,month,day)
    return data_date_obj

def daterange(start, end): # vezme obejkty typu date a vrati list objektu typu date v tom zadanym intervalu, ukrdeno z internetu
    dates=[]
    for n in range(int ((end - start).days)+1):
        dates.append(start + timedelta(n))
    return dates

class Stop(object):
    def __init__ (self, stop_id, stop_name):
        self.id=stop_id
        self.name=stop_name

class Route(object):
    def __init__(self, route_id, route_short_name, route_long_name):
        self.id = route_id
        self.short_name = route_short_name
        self.long_name = route_long_name
        #self.routes[route_id] = {'id:': self.id,'short_name:': self.short_name, 'long_name:': self.long_name}

    def __str__(self):
        return f"oznaceni linky: {self.short_name}, usek: {self.long_name}"
# ZATIM JEN POKUS #

class Service(object): # v tom calendar.txt je na kazdym radku jeden service a je tam prave jednou, proto trida service a ne calendar
    def __init__(self,service_id,service_days):
        self.id=service_id
        self.service_days=service_days # list objektu tridy date, kdy danej service jezdi

    @classmethod # tady zacina ta fun part
    def get_service(cls,service_row): # pak bude brat primo z calendar readeru
        service_days = [] # sem se budou ukladat dny, kdy service funguje/jezdi
        a = service_row['start_date']
        b = service_row['end_date'] # just in case z toho delam integer, obcas to bullshitovalo
        start = convert_int_date(a)
        end = convert_int_date(b) # convert na objekt date
        service_dates=daterange(start,end) # list datumu ziskany z toho intervalu v puvodnim souboru
        week_service_list=[service_row['monday'],service_row['tuesday'],service_row['wednesday'],service_row['thursday'],service_row['friday'],service_row['saturday'],service_row['sunday']]
        # list ve kterym je ulozeno, jaky dny v tydnu funguje service
        for date in service_dates: # iterace pres dny v intervalu
            day_in_week_int=date.weekday() # zjistime den v tydnu, 0-6, je to integer
            if week_service_list[day_in_week_int] == '1': 
                # zname den v tydnu, takze muzeme kouknout do week_service_listu, abychom zjistili, jestli ten service fakt jede a vyuzijeme k tomu to,
                # ze week service list je oindexovanej uplne stejne jako dny v tydnu u date.weekday()
                service_days.append(date) # a kdyz to fakt jede, tak to datum hodime do service_days
        service_complete=Service(service_row['service_id'],service_days) # vytvorime objekt tridy service..
        return service_complete # ..a tahle funkce nam ho vrati


    def __str__(self):
        return f"{self.id}: {self.service_days}"

class Trip(object):
    def __init__ (self, trip_id, route, service):
        # navic atribute service
        self.id=trip_id
        self.route=route
        self.service=service
       

    """ def add_stoptime(self, stoptime):
        self.stoptime_list.append(stoptime) """
    
    def __str__(self):
        return f"id tripu {self.id}, linka {self.route.short_name}"

class StopTime(object):
    def __init__(self, trip, stop, stop_sequence, deptime, arrtime):
        self.trip=trip
        self.stop=stop
        self.stop_sequence=stop_sequence
        self.departure=deptime
        self.arrival=arrtime
        #self.trip.add_stoptime(self)
    
    def __str__(self):
        return f"zastavka: {self.stop.name}"

class StopSegment(object):

    def __init__(self, from_stop, to_stop, trip,route):
        self.from_stop = from_stop
        self.to_stop = to_stop
        self.trips = [trip]  # z toho pak ziskame count
        self.routes = [route]
    @classmethod
    def get_segment_dict(cls, data_stop_times,date_string): # tady pak bude parametrem i to datum..
        user_date_ex=convert_user_date(date_string)

        segment_dict={}
        
        for current_stop_time in data_stop_times: #zatim random range, abych si nazabila pc lmao
            if user_date_ex in current_stop_time.trip.service.service_days:
                # accessneme service pres trip ulozeny v stoptimu a checkneme, jestli je v service_days ulozeny to datum, ktery jsme zadali jako parametr
                # a pokud tam je, tak probehne celej ten shitfest tvorby StopSegmentu
                if current_stop_time.stop_sequence == '1':
                    # kdyz je zastavka prvni na tripu, current priradime vychozi zastavce a cilova je none
                    from_stop = current_stop_time.stop
                    continue
                elif current_stop_time.stop_sequence == '2':
                    # kdyz je to 2. zastavka v tripu, cilovy je priradena current
                    to_stop = current_stop_time.stop
                else:
                    # jinak se z cilovy stane vychozi a cilova je current
                    from_stop = to_stop
                    to_stop = current_stop_time.stop
                    # kdyz cilova neni None (respektive vychozi i cilova):
                        # vytvorime segment_key z id obou zastavek, coz je jednoznacny identifikator segmentu
                        # accessneme trip z currentu, se kterym si pak budeme hrat
                segment_key=(from_stop.id,to_stop.id)
                trip=current_stop_time.trip
                route=trip.route.short_name
                if segment_key not in segment_dict.keys():
                        # kdyz segment_key jeste neni jako klic ve slovniku:
                            # vytvorime objekt StopSegment, ktery vezme jako parametry ty promenny, ktery jsme prave ziskaly
                            # tenhle novy StopSegment dame do slovniku jako value, jehoz key bude tuple s id obou zastavek (segment_key)
                    segment=StopSegment(from_stop,to_stop,trip,route)
                    segment_dict[(segment_key)]=segment

                else:
                        # kdyz tam segement uz je, odpovidajici StopSegment accessneme pres segment_key a do seznamu prihodime ten ziskany trip
                    segment_dict[segment_key].trips.append(trip)
                    if route not in segment_dict[segment_key].routes:
                        segment_dict[segment_key].routes.append(route) # BAD ELISKA TO JE ZAKAZANE JAIL

        return segment_dict # vratime cely slovnik StopSegmentu
    

    @classmethod
    def get_trip_count_from_segments(cls, segment_dict):
        sorted_segment_dict = sorted(segment_dict.values(), key = lambda x: len(x.trips), reverse=True)
        #print(sorted_segment_dict)
        i = 1
        for item in sorted_segment_dict[:5]:
            print(f"{i}. nejfrekventovanější úsek je mezi zastávkami {item.from_stop.name} a {item.to_stop.name}. Projede jím {len(item.trips)} spojů linek {', '.join(item.routes)}.")
            i+=1
        

    """ def __str__(self):
        return f"z: {self.from_stop.name} do: {self.to_stop.name} tripy: {self.trips}" """

with open('PID_GTFS/stops.txt',encoding="utf-8", newline='') as raw_stops:
    stops_reader = csv.DictReader(raw_stops)
    for row in stops_reader:
        stop = Stop(row['stop_id'], row['stop_name'])
        our_data_stops[stop.id]= stop # !! Niektore stops nemaju jmeno, ale to asi neva
                                                    # Sample: 'U1072S1E1081': {'jmeno': 'E8'}
with open('PID_GTFS/routes.txt',encoding="utf-8", newline='') as raw_routes:
    routes_reader = csv.DictReader(raw_routes)
    for row in routes_reader:
        route = Route(row['route_id'], row['route_short_name'], row['route_long_name'])
        our_data_routes[route.id] = route
        
with open('PID_GTFS/calendar.txt',encoding="utf-8", newline='') as raw_calendar:
    # klasicky nacitame soubor
    calendar_reader = csv.DictReader(raw_calendar)
    for row in calendar_reader: # row odpovida jednomu servicu
        service=Service.get_service(row) # ziskame service pomoci ty fancy metody
        our_data_services[service.id]=service # service hodime do slovniku, kde je klicem service.id a value je objekt tridy service

with open('PID_GTFS/trips.txt',encoding="utf-8", newline='') as raw_trips:
    trips_reader = csv.DictReader(raw_trips)
    for row in trips_reader:
        route_pk = row['route_id']
        service_pk = row['service_id']
        trip = Trip(row['trip_id'], our_data_routes[route_pk], our_data_services[service_pk]) # pridano nappjeni na service pres pk
        our_data_trips[trip.id] = trip # Sample: '1349_28156_211212': {'linka_id': 'L1349'},

with open('PID_GTFS/stop_times.txt',encoding="utf-8", newline='') as raw_stop_times:
    stop_times_reader = csv.DictReader(raw_stop_times)
    for row in stop_times_reader:
        trip_pk = row['trip_id']
        stop_pk = row['stop_id']
        stop_time = StopTime(our_data_trips[trip_pk], our_data_stops[stop_pk], row['stop_sequence'], row['departure_time'], row['arrival_time'])
        our_data_stop_times.append(stop_time)

datum=str(input("zadejte datum ve formatu dd.mm.rrrr "))
x=StopSegment.get_segment_dict(our_data_stop_times, datum)
StopSegment.get_trip_count_from_segments(x)


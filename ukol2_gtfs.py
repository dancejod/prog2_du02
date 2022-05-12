import csv

with open('PID_GTFS/stops.txt',encoding="utf-8", newline='') as raw_stops, open('PID_GTFS/stop_times.txt',encoding="utf-8", newline='') as raw_stop_times, open('PID_GTFS/trips.txt',encoding="utf-8", newline='') as raw_trips, open('PID_GTFS/routes.txt',encoding="utf-8", newline='') as raw_routes:
    stops_reader = csv.DictReader(raw_stops)
    stop_times_reader = csv.DictReader(raw_stop_times)
    trips_reader = csv.DictReader(raw_trips)
    routes_reader = csv.DictReader(raw_routes)

    our_data_stops={}
    our_data_stop_times=[]
    our_data_trips={}
    our_data_routes={}

    for row in stops_reader:
        stop_pk=row['stop_id']
        stop_jmeno=row['stop_name'] # Vo finalnej verzii len nezabudnut na cechizmy, dat po anglicky
        our_data_stops[stop_pk]={'jmeno':stop_jmeno} # !! Niektore stops nemaju jmeno, ale to asi neva
                                                    # Sample: 'U1072S1E1081': {'jmeno': 'E8'}
    
    for row in trips_reader:
        trip_pk=row['trip_id']
        linka_id=row['route_id']
        our_data_trips[trip_pk]={'linka_id':linka_id} # Sample: '1349_28156_211212': {'linka_id': 'L1349'},

    for row in routes_reader:
        route_pk=row['route_id']
        route_kratke_jmeno=row['route_short_name']
        route_dlouhe_jmeno=row['route_long_name']     
        our_data_routes[route_pk]={'kratke_jmeno':route_kratke_jmeno,'dlouhe_jmeno':route_dlouhe_jmeno}

    for row in stop_times_reader:
        cesta=row['trip_id'] #matuce
        zastavka=row['stop_id']
        poradi=row['stop_sequence']
        prichod=row['arrival_time']
        odchod=row['departure_time']
        our_data_stop_times.append({'cesta':cesta,'zastavka':zastavka,'poradi':poradi, 'prichod': prichod, 'odchod': odchod})

class Route(object):
    def __init__(self,route_data, route_id):
        self.id=route_id
        self.short_name=route_data[route_id]['kratke_jmeno']
        self.long_name=route_data[route_id]['dlouhe_jmeno']
        #self.routes[route_id] = {'id:': self.id,'short_name:': self.short_name, 'long_name:': self.long_name}

    def __str__(self):
        return f"{id(self)}:{self.id}, {id(self)}:{self.short_name}, {id(self)}:{self.long_name}"

class Stop(object):
    def __init__ (self, stop_id, stop_name):
        self.id=stop_id
        self.name=stop_name

class Trip(object):
    def __init__ (self, trip_id, route):
        self.id=trip_id
        self.route=route
        #self.stoptime_list = []

    """ def add_stoptime(self, stoptime):
        self.stoptime_list.append(stoptime) """

class StopTime(object):
    def __init__(self, stop_time_index, trip, stop, stop_sequence, deptime, arrtime):
        self.stop_time_index=stop_time_index
        self.trip=trip
        self.stop=stop
        self.rank=stop_sequence
        self.departure=deptime
        self.arrival=arrtime
        #self.trip.add_stoptime(self)
    
    def __str__(self):
        return f"{id(self)}:{self.trip}, {id(self)}:{self.stop}, {id(self)}:{self.rank}"

class StopSegment(object):

    def __init__(self):
        self.from_stop = None
        self.to_stop = None
        self.trips = []  # z toho pak ziskame count

    def create_segment(self, data_stop_times, data_trips, data_stops, data_routes):
        segment_list=[]
        for i in range(100): #zatim random range, abych si nazabila pc lmao
            current_stop_time = StopTime(i, trip, stop, stop_sequence, deptime, arrtime) #sem se ulozi stoptime podle indexu v our_data_stop_times
            if current_stop_time.stop_sequence == '1':
                # kdyz je zastvaka prvni na tripu, current priradime vychozi zastavce a cilova je none
                self.from_stop = current_stop_time.stop
                self.to_stop = None
            else:
                #kdyz to neni prvni zastavka...
                if self.to_stop == None:
                    # kdyz je cilova none, priradime ji current, to by se melo asi stat jen u rank = 2, jinak se z puvodni cilovy stane vychozi a cilova je current
                    self.to_stop = current_stop_time.stop
                else:
                    self.from_stop = self.to_stop
                    self.to_stop = current_stop_time.stop
        
    def add_trip_to_list(self, trip):
        self.trips_list.append(trip)

    def __str__(self):
        return f"z: {self.from_stop.name} do: {self.to_stop.name}"

StopSegment().create_segment(our_data_stop_times,our_data_trips,our_data_stops,our_data_routes)

#print(StopTime().get_data(our_data_stop_times,our_data_trips,our_data_stops,our_data_routes))
#print(StopTime().get_data(our_data_stop_times,our_data_trips,our_data_stops,our_data_routes))
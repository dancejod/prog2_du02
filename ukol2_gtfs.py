import csv

our_data_stops={}
our_data_stop_times=[]
our_data_trips={}
our_data_routes={}

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
        return f"{id(self)}:{self.id}, {id(self)}:{self.short_name}, {id(self)}:{self.long_name}"


class Trip(object):
    def __init__ (self, trip_id, route):
        self.id=trip_id
        self.route=route
        #self.stoptime_list = []

    """ def add_stoptime(self, stoptime):
        self.stoptime_list.append(stoptime) """

class StopTime(object):
    def __init__(self, trip, stop, stop_sequence, deptime, arrtime):
        self.trip=trip
        self.stop=stop
        self.stop_sequence=stop_sequence
        self.departure=deptime
        self.arrival=arrtime
        #self.trip.add_stoptime(self)
    
    def __str__(self):
        return f"{id(self)}:{self.trip}, {id(self)}:{self.stop}, {id(self)}:{self.stop_sequence}"

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
                    # kdyz je cilova none, priradime ji current, to by se melo asi stat jen u stop_sequence = 2, jinak se z puvodni cilovy stane vychozi a cilova je current
                    self.to_stop = current_stop_time.stop
                else:
                    self.from_stop = self.to_stop
                    self.to_stop = current_stop_time.stop
        
    def add_trip_to_list(self, trip):
        self.trips_list.append(trip)

    def __str__(self):
        return f"z: {self.from_stop.name} do: {self.to_stop.name}"

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
        
with open('PID_GTFS/trips.txt',encoding="utf-8", newline='') as raw_trips:
    trips_reader = csv.DictReader(raw_trips)
    for row in trips_reader:
        route_pk = row['route_id']
        trip = Trip(row['trip_id'], our_data_routes.get(route_pk))
        our_data_trips[trip.id] = trip # Sample: '1349_28156_211212': {'linka_id': 'L1349'},

with open('PID_GTFS/stop_times.txt',encoding="utf-8", newline='') as raw_stop_times:
    stop_times_reader = csv.DictReader(raw_stop_times)
    for row in stop_times_reader:
        trip_pk = row['trip_id']
        stop_pk = row['stop_id']
        stop_time = StopTime(our_data_trips.get(trip_pk), our_data_stops.get(stop_pk), row['stop_sequence'], row['departure_time'], row['arrival_time'])
        our_data_stop_times.append(stop_time)




#print(StopTime().get_data(our_data_stop_times,our_data_trips,our_data_stops,our_data_routes))
#print(StopTime().get_data(our_data_stop_times,our_data_trips,our_data_stops,our_data_routes))
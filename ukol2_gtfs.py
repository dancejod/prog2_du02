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
        cesta=row['trip_id']
        zastavka=row['stop_id']
        poradi=row['stop_sequence']
        our_data_stop_times.append({'cesta':cesta,'zastavka':zastavka,'poradi':poradi})

class Stop(object):
    def __init__ (self):
        self.id=None
        self.name=None
    
    def get_data(self,data,pk):
        self.id=pk
        self.name=data[pk]['jmeno']
        return self

class Trip(object):
    def __init__ (self):
        self.id=None
        self.route=None
        #self.stops=[]

    def get_data(self,data,data_routes,pk):
        self.id=pk
        pk_route=data[pk]['linka_id']
        self.route=Route().get_data(data_routes,pk_route)
        return self


class Route(object):
    def __init__(self):
        self.id=None
        self.short_name=None
        self.long_name=None
        #self.trips=[]

    def get_data(self,data,pk):
        self.id=pk
        self.short_name=data[pk]['kratke_jmeno']
        self.long_name=data[pk]['dlouhe_jmeno']
        return self

    def __str__(self):
        return f"{id(self)}:{self.id}, {id(self)}:{self.short_name}, {id(self)}:{self.long_name}"

class StopTime(object):
    def __init__(self):
        self.trip=None
        self.stop=None
        self.rank=None

    def get_data(self,data,data_trips,data_stops,data_routes):  # this might be illegal
        for i in data:
            pk_trip=i['cesta']
            pk_stop=i['zastavka']
            self.trip=Trip().get_data(data_trips,data_routes,pk_trip)
            self.stop=Stop().get_data(data_stops,pk_stop)
            self.poradi=i['poradi']
            return self

class StopSegment(object):
    def __init__(self):
        self.from_stop=None
        self.to_stop=None
        self.trips=[] # z toho pak ziskame count



#print(our_data_stops)
#print(StopTime().get_data(our_data_stop_times,our_data_trips,our_data_stops,our_data_routes))
print(Route().get_data(our_data_routes,'L14'))
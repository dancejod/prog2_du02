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
    def __init__ (self, trip_id, route, service_id):
        self.id=trip_id
        self.route=route
        self.service_id=service_id
        #self.stoptime_list = []

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
    def create_segment(cls, data_stop_times):
        segment_dict={}
        for current_stop_time in data_stop_times: #zatim random range, abych si nazabila pc lmao
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
            print(f"{i}.  Z: {item.from_stop.name} Do: {item.to_stop.name} Pocet vyjezdu: {len(item.trips)} linky: {', '.join(item.routes)}")
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
        
with open('PID_GTFS/trips.txt',encoding="utf-8", newline='') as raw_trips:
    trips_reader = csv.DictReader(raw_trips)
    for row in trips_reader:
        route_pk = row['route_id']
        trip = Trip(row['trip_id'], our_data_routes[route_pk], row['service_id'])
        our_data_trips[trip.id] = trip # Sample: '1349_28156_211212': {'linka_id': 'L1349'},

with open('PID_GTFS/stop_times.txt',encoding="utf-8", newline='') as raw_stop_times:
    stop_times_reader = csv.DictReader(raw_stop_times)
    for row in stop_times_reader:
        trip_pk = row['trip_id']
        stop_pk = row['stop_id']
        stop_time = StopTime(our_data_trips[trip_pk], our_data_stops[stop_pk], row['stop_sequence'], row['departure_time'], row['arrival_time'])
        our_data_stop_times.append(stop_time)

ggwp=StopSegment.create_segment(our_data_stop_times)
yes = StopSegment.get_trip_count_from_segments(ggwp)
#print(ggwp)
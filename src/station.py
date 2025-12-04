import json

class ChargingStation:
    def __init__(self, name, lat, lon, power_kw=50):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.power = power_kw 

def load_stations(filepath):
    with open(filepath, 'r', encoding='utf8') as f:
        gj = json.load(f)

    stations = []
    for feat in gj['features']:
        props = feat['properties']
        geom = feat['geometry']
        
        if geom['type'] == 'Point':
            coords = geom['coordinates']
            
            lon = float(coords[0]) 
            lat = float(coords[1])
            
            name = props.get('name', "Trạm sạc")
            stations.append(ChargingStation(name, lat, lon))
            
    return stations
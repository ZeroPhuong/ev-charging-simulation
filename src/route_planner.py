# route_planner.py
from heapq import heappush, heappop
from src.graph import haversine
from shapely.geometry import Point, LineString
import polyline
import requests

def get_corridor_stations(start_lat, start_lon, end_lat, end_lon, all_stations, buffer_deg=0.15):
    """
    Lọc các trạm sạc nằm dọc theo đường đi dự kiến (trong khoảng 15-20km).
    """
    url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full"
    try:
        resp = requests.get(url, timeout=2)
        if resp.status_code != 200: return all_stations
        data = resp.json()
        geometry = data['routes'][0]['geometry']
        path_coords = polyline.decode(geometry) 
        
        shapely_line = LineString([(lon, lat) for lat, lon in path_coords])
        
        corridor = shapely_line.buffer(buffer_deg)
        
        filtered_stations = []
        for st in all_stations:
            st_point = Point(st.lon, st.lat)
            if st_point.within(corridor):
                filtered_stations.append(st)
                
        print(f"Đã lọc: Giữ lại {len(filtered_stations)}/{len(all_stations)} trạm dọc lộ trình.")
        return filtered_stations
        
    except Exception as e:
        print(f"Lỗi lọc trạm: {e}. Dùng toàn bộ trạm.")
        return all_stations

def plan_route(ev, start_lat, start_lon, end_lat, end_lon, stations):
    start = ("START", float(start_lat), float(start_lon))
    
    heappush(frontier := [], (0, 0, start, ev.soc, []))
    visited = set()

    min_lat, max_lat = min(start_lat, end_lat) - 1.0, max(start_lat, end_lat) + 1.0
    relevant_stations = [st for st in stations if min_lat <= st.lat <= max_lat]
    
    SAFE_LIMIT = ev.min_safe / 100.0

    while frontier:
        f, g, (name, lat, lon), soc, path = heappop(frontier)

        state_id = (name, int(soc * 100)) 
        if state_id in visited: continue
        visited.add(state_id)

        dist_to_goal = haversine(lat, lon, end_lat, end_lon)
        soc_needed_to_goal = (dist_to_goal * ev.wh_per_km) / (ev.capacity * 1000)
        
        if soc - soc_needed_to_goal >= SAFE_LIMIT: 
            final_path = path + [(name, lat, lon, soc)]
            final_path.append(("END", end_lat, end_lon, soc - soc_needed_to_goal))
            return final_path, g + dist_to_goal

        for st in relevant_stations:
            if st.name == name: continue

            dist = haversine(lat, lon, st.lat, st.lon)
            
            soc_consumed = (dist * ev.wh_per_km) / (ev.capacity * 1000)
            arrival_soc = soc - soc_consumed

            if arrival_soc < SAFE_LIMIT:
                continue 

            new_soc = 0.9 
            
            new_g = g + dist
            new_f = new_g + haversine(st.lat, st.lon, end_lat, end_lon)

            heappush(frontier, (new_f, new_g, (st.name, st.lat, st.lon), new_soc, path + [(name, lat, lon, soc)]))

    return None, None
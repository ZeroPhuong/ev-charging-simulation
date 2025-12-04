import math
import requests
import polyline

# --- PHẦN 1: Hàm tính khoảng cách chim bay (Dùng cho thuật toán tìm đường A*) ---
def haversine(lat1, lon1, lat2, lon2):
    try:
        lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)
    except (ValueError, TypeError):
        return float('inf')

    R = 6371
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    
    a = (math.sin(dLat/2)**2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dLon/2)**2)
    
   
    if a > 1: a = 1.0
    if a < 0: a = 0.0
         
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# --- PHẦN 2: Hàm lấy đường đi thực tế từ API (Dùng cho hiển thị bản đồ) ---
def get_real_path_osrm(lat1, lon1, lat2, lon2):
    """
    Gọi API OSRM để lấy đường đi thực tế giữa 2 điểm.
    Trả về: (danh_sách_tọa_độ_chi_tiết, khoảng_cách_km)
    """
   
    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=polyline"
    
    try:
       
        response = requests.get(url, timeout=5)
        
        if response.status_code != 200:
            return None, 0
            
        data = response.json()
        if data['code'] != 'Ok':
            return None, 0

        route = data['routes'][0]
        distance_km = route['distance'] / 1000
        
       
        path_points = polyline.decode(route['geometry'])
        
        return path_points, distance_km
        
    except Exception as e:
       
        print(f"Lỗi OSRM: {e}")
        return None, 0
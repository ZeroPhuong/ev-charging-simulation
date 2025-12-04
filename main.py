import streamlit as st
from src.ev import ElectricVehicle
from src.station import load_stations
from src.route_planner import plan_route
from src.visualize import visualize_simulation

st.set_page_config(page_title="EV Route Planner", layout="wide")

DATA_PATH = "data/TramSacEV.json"

def main():
    st.title("Ứng dụng Tìm đường Trạm sạc EV")
    st.markdown("Đồ án môn Trí tuệ nhân tạo - Mô phỏng lộ trình xe điện tối ưu.")

    if 'route' not in st.session_state:
        st.session_state.route = None
    if 'cost' not in st.session_state:
        st.session_state.cost = 0
    if 'stations_data' not in st.session_state:
        st.session_state.stations_data = load_stations(DATA_PATH)

    with st.sidebar:
        st.header("Thông số xe & Hành trình")
        
       
        with st.form("input_form"):
            start_lat = st.number_input("Vĩ độ điểm đi", value=10.670119)
            start_lon = st.number_input("Kinh độ điểm đi", value=106.576248)
            
            end_lat = st.number_input("Vĩ độ điểm đến", value=11.882085)
            end_lon = st.number_input("Kinh độ điểm đến", value=108.470695)

            st.divider()
            
            capacity = st.number_input("Dung lượng pin (kWh)", value=42)
            current_soc = st.slider("Pin hiện tại (%)", 0, 100, 90)
            wh_km = st.number_input("Mức tiêu thụ (Wh/km)", value=150)

            submitted = st.form_submit_button("Tìm đường ngay")

   
    if submitted:
       
        ev = ElectricVehicle(capacity, current_soc, wh_km)
        
       
        stations = st.session_state.stations_data
        
        st.toast(f"Đã tải {len(stations)} trạm sạc.")

       
        with st.spinner("Đang tính toán lộ trình tối ưu (A*)..."):
            try:
                route, cost = plan_route(ev, start_lat, start_lon, end_lat, end_lon, stations)
                
               
                st.session_state.route = route
                st.session_state.cost = cost
                st.session_state.ev_params = ev
                
                if not route:
                    st.error("Không tìm thấy đường đi phù hợp.")
            except Exception as e:
                st.error(f"Có lỗi xảy ra: {e}")

   
   
    if st.session_state.route:
        route = st.session_state.route
        cost = st.session_state.cost
        
        st.success(f"Đã tìm thấy lộ trình! Tổng chi phí/quãng đường: {cost:.2f} km")
       
        ev_temp = st.session_state.get('ev_params', None) 
        if ev_temp is None:
            ev_temp = ElectricVehicle(42, 0.9, 150)
        visualize_simulation(ev_temp, route)
        
       
        with st.expander("Xem chi tiết các chặng dừng"):
            st.dataframe([
                {"Trạm": r[0], "Vĩ độ": r[1], "Kinh độ": r[2], "Pin còn lại": f"{r[3]*100:.1f}%"} 
                for r in route
            ])
            
       
        if st.button("Xóa kết quả"):
            st.session_state.route = None
            st.rerun()

if __name__ == "__main__":
    main()
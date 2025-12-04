import streamlit as st
import folium
from folium.plugins import TimestampedGeoJson, AntPath
from streamlit_folium import st_folium
from src.graph import get_real_path_osrm
from datetime import datetime, timedelta
import pandas as pd
import altair as alt

def visualize_simulation(ev, route_nodes):
    st.divider()
    st.subheader("Mô phỏng & Phân tích Hành trình")
    
    # XỬ LÝ DỮ LIỆU
    with st.status("Đang xây dựng kịch bản mô phỏng...", expanded=True) as status:
        full_coords = []
        features = []
        chart_data = [] 
        
        
        sim_time = datetime.now().replace(hour=7, minute=0, second=0, microsecond=0)
        total_dist = 0
        
        
        for i in range(len(route_nodes) - 1):
            start_node = route_nodes[i]
            end_node = route_nodes[i+1]
            
            # Gọi OSRM lấy đường thực tế
            path, dist_km = get_real_path_osrm(start_node[1], start_node[2], end_node[1], end_node[2])
            
            if not path:
                path = [(start_node[1], start_node[2]), (end_node[1], end_node[2])]
                dist_km = 0
            
            full_coords.extend(path)
            
            # ANIMATION DI CHUYỂN
            points_count = len(path)
            start_soc = start_node[3]
            
            for idx, coord in enumerate(path):
                fraction = idx / points_count
                
                soc_consumed = (dist_km * ev.wh_per_km / 1000) / ev.capacity 
                current_soc = start_node[3] - (soc_consumed * fraction)
                
                sim_time += timedelta(seconds=2)
                total_dist += (dist_km / points_count)
                
                color = "#2ecc71"
                if current_soc < 0.2: color = "#f1c40f"
                if current_soc < 0.1: color = "#e74c3c"
                status_msg = f"Pin: {current_soc*100:.1f}% | Tốc độ: 60km/h"

                features.append({
                    'type': 'Feature',
                    'geometry': { 'type': 'Point', 'coordinates': [coord[1], coord[0]] },
                    'properties': {
                        'time': sim_time.isoformat(),
                        'style': {'color': color},
                        'icon': 'car',
                        'iconstyle': {
                            'fillColor': color,
                            'fillOpacity': 1,
                            'stroke': 'false',
                            'radius': 6
                        },
                        'popup': status_msg,
                        'tooltip': status_msg
                    }
                })
                
                if idx % 5 == 0:
                    chart_data.append({
                        "Time": sim_time, 
                        "SOC": current_soc * 100, 
                        "Distance": total_dist,
                        "Type": "Moving"
                    })

            # ANIMATION DỪNG SẠC PIN
            if i < len(route_nodes) - 2:
                target_soc = end_node[3] 
                
                charge_frames = 20
                soc_gain_per_frame = (target_soc - current_soc) / charge_frames
                
                for _ in range(charge_frames):
                    sim_time += timedelta(seconds=2)
                    current_soc += soc_gain_per_frame
                    if current_soc > 1.0: current_soc = 1.0
                    
                    features.append({
                        'type': 'Feature',
                        'geometry': { 'type': 'Point', 'coordinates': [end_node[2], end_node[1]] },
                        'properties': {
                            'time': sim_time.isoformat(),
                            'icon': 'bolt',
                            'iconstyle': {
                                'fillColor': '#3498db',
                                'fillOpacity': 1,
                                'stroke': 'true',
                                'radius': 10
                            },
                            'popup': f"ĐANG SẠC... {current_soc*100:.1f}%",
                            'tooltip': f"ĐANG SẠC... {current_soc*100:.1f}%"
                        }
                    })
                    
                    chart_data.append({
                        "Time": sim_time, 
                        "SOC": current_soc * 100, 
                        "Distance": total_dist,
                        "Type": "Charging"
                    })
        
        status.update(label="Dữ liệu sẵn sàng!", state="complete", expanded=False)

    # VẼ BIỂU ĐỒ TRẠNG THÁI PIN
    st.markdown("### Biểu đồ trạng thái Pin")
    
    df_chart = pd.DataFrame(chart_data)
    
    # Altair Line Chart
    chart = alt.Chart(df_chart).mark_line().encode(
        x=alt.X('Distance', title='Quãng đường (km)'),
        y=alt.Y('SOC', title='Dung lượng Pin (%)', scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('Type', legend=alt.Legend(title="Trạng thái"), scale=alt.Scale(domain=['Moving', 'Charging'], range=['#2ecc71', '#3498db'])),
        tooltip=['Distance', 'SOC', 'Type']
    ).properties(height=200, width='container')
    
    st.altair_chart(chart, use_container_width=True)


    # VẼ BẢN ĐỒ ANIMATION
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info("Nhấn nút **Play ▶** góc trái bản đồ. Rê chuột vào chấm tròn để xem Pin.")
        
        center_idx = len(full_coords) // 2
        m = folium.Map(location=full_coords[center_idx], zoom_start=6)

        AntPath(locations=full_coords, color='gray', weight=3, opacity=0.5).add_to(m)

        for node in route_nodes:
            color = "red" if node[0] in ["START", "END"] else "green"
            folium.Marker(
                [node[1], node[2]],
                popup=f"<b>{node[0]}</b>",
                icon=folium.Icon(color=color, icon="map-marker", prefix="fa")
            ).add_to(m)

        TimestampedGeoJson(
            {'type': 'FeatureCollection', 'features': features},
            period='PT2S',
            duration='PT2S',
            add_last_point=False,
            auto_play=True,
            loop=False,
            max_speed=20,
            loop_button=True,
            time_slider_drag_update=True
        ).add_to(m)

        st_folium(m, width=700, height=500, returned_objects=[])

    with col2:
        st.markdown("### Điểm dừng chi tiết")
        for idx, node in enumerate(route_nodes):
            with st.container(border=True):
                if idx == 0:
                    st.write("**Xuất phát**")
                elif idx == len(route_nodes)-1:
                    st.write("**Đích đến**")
                else:
                    st.write(f"**Trạm {idx}**")
                    st.caption(node[0])
                
                st.metric("Pin", f"{node[3]*100:.1f}%")
                if idx < len(route_nodes)-1 and node[3] < 0.2:
                    st.error("Pin yếu!")
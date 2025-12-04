# EV Route Planner simulation

Đồ án môn Trí tuệ nhân tạo: Ứng dụng tìm đường tối ưu cho xe điện chạy dọc Việt Nam, tích hợp tính toán trạm sạc.

## Tóm tắt đồ án
- Tìm đường đi thực tế (sử dụng OSRM API).
- Thuật toán tối ưu lộ trình dựa trên dung lượng Pin.
- Tự động gợi ý trạm sạc khi pin yếu.
- Mô phỏng Animation xe chạy thời gian thực trên bản đồ.
- Biểu đồ theo dõi mức tiêu hao năng lượng.

## Công nghệ sử dụng
- **Ngôn ngữ:** Python 3.12
- **Giao diện:** Streamlit
- **Bản đồ:** Folium, Leaflet
- **Xử lý dữ liệu:** Pandas, Shapely, Polyline
- **Thuật toán:** A* Search (Heuristic + Road Factor)

## Hướng dẫn cài đặt
1. Clone dự án:
   `git clone https://github.com/ZeroPhuong/ev-charging-simulation.git`
2. Cài đặt thư viện:
   `pip install -r requirements.txt`
3. Chạy ứng dụng:
   `streamlit run main.py`
from langchain_core.tools import tool

# =====================================================================
# MOCK DATA - Dữ liệu giả lập hệ thống du lịch
# Lưu ý: Giá cả có logic (VD: cuối tuần đắt hơn, hạng cao hơn đắt hơn)
# Sinh viên cần đọc hiểu data để debug test cases.
# =====================================================================

FLIGHTS_DB = {
    ("Hà Nội", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "07:20", "price": 1_450_000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "14:00", "arrival": "15:20", "price": 2_800_000, "class": "business"},
        {"airline": "VietJet Air", "departure": "08:30", "arrival": "09:50", "price": 890_000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "11:00", "arrival": "12:20", "price": 1_200_000, "class": "economy"},
    ],
    ("Hà Nội", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "07:00", "arrival": "09:15", "price": 2_100_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "10:00", "arrival": "12:15", "price": 1_350_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "16:00", "arrival": "18:15", "price": 1_100_000, "class": "economy"},
    ],
    ("Hà Nội", "Hồ Chí Minh"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "08:10", "price": 1_600_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "07:30", "arrival": "09:40", "price": 950_000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "12:00", "arrival": "14:10", "price": 1_300_000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "18:00", "arrival": "20:10", "price": 3_200_000, "class": "business"},
    ],
    ("Hồ Chí Minh", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "09:00", "arrival": "10:20", "price": 1_300_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "13:00", "arrival": "14:20", "price": 780_000, "class": "economy"},
    ],
    ("Hồ Chí Minh", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "08:00", "arrival": "09:00", "price": 1_100_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "15:00", "arrival": "16:00", "price": 650_000, "class": "economy"},
    ]
}

HOTELS_DB = {
    "Đà Nẵng": [
        {"name": "Mường Thanh Luxury", "stars": 5, "price_per_night": 1_800_000, "area": "Mỹ Khê", "rating": 4.5},
        {"name": "Sala Danang Beach", "stars": 4, "price_per_night": 1_200_000, "area": "Mỹ Khê", "rating": 4.3},
        {"name": "Fivitel Danang", "stars": 3, "price_per_night": 650_000, "area": "Sơn Trà", "rating": 4.1},
        {"name": "Memory Hostel", "stars": 2, "price_per_night": 250_000, "area": "Hải Châu", "rating": 4.6},
        {"name": "Christina's Homestay", "stars": 2, "price_per_night": 350_000, "area": "An Thượng", "rating": 4.7},
    ],
    "Phú Quốc": [
        {"name": "Vinpearl Resort", "stars": 5, "price_per_night": 3_500_000, "area": "Bãi Dài", "rating": 4.4},
        {"name": "Sol by Meliá", "stars": 4, "price_per_night": 1_500_000, "area": "Bãi Trường", "rating": 4.2},
        {"name": "Lahana Resort", "stars": 3, "price_per_night": 800_000, "area": "Dương Đông", "rating": 4.0},
        {"name": "9Station Hostel", "stars": 2, "price_per_night": 200_000, "area": "Dương Đông", "rating": 4.5},
    ],
    "Hồ Chí Minh": [
        {"name": "Rex Hotel", "stars": 5, "price_per_night": 2_800_000, "area": "Quận 1", "rating": 4.3},
        {"name": "Liberty Central", "stars": 4, "price_per_night": 1_400_000, "area": "Quận 1", "rating": 4.1},
        {"name": "Cochin Zen Hotel", "stars": 3, "price_per_night": 550_000, "area": "Quận 3", "rating": 4.4},
        {"name": "The Common Room", "stars": 2, "price_per_night": 180_000, "area": "Quận 1", "rating": 4.6},
    ]
}

# Hàm helper format tiền tệ VNĐ (VD: 1.450.000đ)
def format_vnd(amount: int) -> str:
    return f"{amount:,.0f}".replace(",", ".") + "đ"

@tool
def search_flights(origin: str, destination: str) -> str:
    """
    Tìm kiếm các chuyến bay giữa hai thành phố.
    Tham số:
    - origin: thành phố khởi hành (VD: 'Hà Nội', 'Hồ Chí Minh')
    - destination: thành phố đến (VD: 'Đà Nẵng', 'Phú Quốc')
    Trả về danh sách chuyến bay với hãng, giờ bay, giá vé.
    Nếu không tìm thấy tuyến bay, trả về thông báo không có chuyến.
    """
    # Tra cứu FLIGHTS_DB với key (origin, destination)
    flights = FLIGHTS_DB.get((origin, destination))
    
    # Nếu không tìm thấy -> thử tra ngược (destination, origin) xem có không
    if not flights:
        flights = FLIGHTS_DB.get((destination, origin))
        if flights:
            return f"Không tìm thấy chuyến bay từ {origin} đến {destination}. Tuy nhiên, có chuyến bay chiều ngược lại từ {destination} về {origin}:\n" + \
                   "\n".join([f"- {f['airline']} ({f['class']}): {f['departure']} -> {f['arrival']} | Giá: {format_vnd(f['price'])}" for f in flights])
        else:
            # nếu cũng không có -> "Không tìm thấy chuyến bay từ X đến Y."
            return f"Không tìm thấy chuyến bay nào giữa {origin} và {destination}."

    # Nếu tìm thấy -> format danh sách chuyến bay dễ đọc, bao gồm giá tiền
    result = f"Danh sách chuyến bay từ {origin} đến {destination}:\n"
    for f in flights:
        result += f"- Hãng {f['airline']} ({f['class']}): Khởi hành {f['departure']} - Đến {f['arrival']} | Giá vé: {format_vnd(f['price'])}\n"
    
    return result

@tool
def search_hotels(city: str, max_price_per_night: int = 99999999) -> str:
    """
    Tìm kiếm khách sạn tại một thành phố, có thể lọc theo giá tối đa mỗi đêm.
    Tham số:
    - city: tên thành phố (VD: 'Đà Nẵng', 'Phú Quốc', 'Hồ Chí Minh')
    - max_price_per_night: giá tối đa mỗi đêm (VNĐ), mặc định không giới hạn
    Trả về danh sách khách sạn phù hợp với tên, số sao, giá, khu vực, rating.
    """
    if city not in HOTELS_DB:
        return f"Hiện chưa có dữ liệu khách sạn tại thành phố {city}."

    # Tra cứu HOTELS_DB[city]
    hotels = HOTELS_DB[city]
    
    # Lọc theo max_price_per_night
    filtered_hotels = [h for h in hotels if h['price_per_night'] <= max_price_per_night]
    
    # Nếu không có kết quả -> "Không tìm thấy khách sạn tại X với giá dưới Y/đêm. Hãy thử tăng ngân sách."
    if not filtered_hotels:
        return f"Không tìm thấy khách sạn tại {city} với giá dưới {format_vnd(max_price_per_night)}/đêm. Hãy thử tăng ngân sách."
    
    # Sắp xếp theo rating giảm dần
    filtered_hotels.sort(key=lambda x: x['rating'], reverse=True)
    
    # Format đẹp
    result = f"Danh sách khách sạn tại {city} (Giá dưới {format_vnd(max_price_per_night)}/đêm):\n"
    for h in filtered_hotels:
        result += f"- {h['name']} ({h['stars']} sao, Khu vực {h['area']}) | Đánh giá: {h['rating']}/5.0 | Giá: {format_vnd(h['price_per_night'])}/đêm\n"
        
    return result

@tool
def calculate_budget(total_budget: int, expenses: str) -> str:
    """
    Tính toán ngân sách còn lại sau khi trừ các khoản chi phí.
    Tham số:
    - total_budget: tổng ngân sách ban đầu (VNĐ)
    - expenses: chuỗi mô tả các khoản chi, mỗi khoản cách nhau bởi dấu phẩy, 
                định dạng 'tên_khoản:số_tiền' (VD: 'vé_máy_bay:890000,khách_sạn:650000')
    Trả về bảng chi tiết các khoản chi và số tiền còn lại.
    Nếu vượt ngân sách, cảnh báo rõ ràng số tiền thiếu.
    """
    # Sinh viên tự triển khai
    try:
        # Parse chuỗi expenses thành dict {tên: số_tiền}
        expense_dict = {}
        total_expense = 0
        
        # Xử lý chuỗi (loại bỏ khoảng trắng dư thừa nếu có)
        if expenses.strip():
            items = expenses.split(',')
            for item in items:
                name, amount_str = item.split(':')
                amount = int(amount_str.strip())
                expense_dict[name.strip()] = amount
                # Tính tổng chi phí
                total_expense += amount

        # Tính số tiền còn lại
        remaining = total_budget - total_expense
        
        # Format bảng chi tiết
        result = "Bảng chi phí:\n"
        for name, amount in expense_dict.items():
            # Format tên cho đẹp (thay _ bằng khoảng trắng)
            clean_name = name.replace('_', ' ').capitalize()
            result += f"- {clean_name}: {format_vnd(amount)}\n"
            
        result += "---\n"
        result += f"Tổng chi: {format_vnd(total_expense)}\n"
        result += f"Ngân sách: {format_vnd(total_budget)}\n"
        result += f"Còn lại: {format_vnd(remaining)}\n"
        
        # Nếu âm -> Cảnh báo
        if remaining < 0:
            result += f"\n⚠️ CẢNH BÁO: Vượt ngân sách {format_vnd(abs(remaining))}! Cần điều chỉnh lại kế hoạch."
            
        return result
        
    except ValueError:
        # Xử lý lỗi: nếu expenses format sai -> trả về thông báo lỗi rõ ràng
        return "Lỗi: Định dạng chi phí (expenses) không hợp lệ. Vui lòng sử dụng định dạng 'tên_khoản:số_tiền,tên_khoản2:số_tiền2'."
    except Exception as e:
        return f"Lỗi hệ thống khi tính toán ngân sách: {str(e)}"
    

import math
import folium

# Başlangıç konumu: Gölbaşı, Ankara
current_latitude = 39.7849
current_longitude = 32.8149

# Hedef konumu: İncek, Ankara
target_latitude = 39.8707
target_longitude = 32.7353

# Harita oluşturma
map_center = [(current_latitude + target_latitude) / 2,
              (current_longitude + target_longitude) / 2]
my_map = folium.Map(location=map_center, zoom_start=13)

# Başlangıç ve hedef noktalarını ekleme
folium.Marker([current_latitude, current_longitude],
              tooltip='Başlangıç Konumu: Gölbaşı').add_to(my_map)
folium.Marker([target_latitude, target_longitude],
              tooltip='Hedef Konumu: İncek', icon=folium.Icon(color='red')).add_to(my_map)


def update_current_location(new_latitude, new_longitude):
    global current_latitude, current_longitude
    current_latitude = new_latitude
    current_longitude = new_longitude


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance


def calculate_bearing(lat1, lon1, lat2, lon2):
    dlon = math.radians(lon2 - lon1)
    y = math.sin(dlon) * math.cos(math.radians(lat2))
    x = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - \
        math.sin(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.cos(dlon)
    bearing = math.degrees(math.atan2(y, x))
    bearing = (bearing + 360) % 360
    return bearing


def move_robot(left_motor_speed, right_motor_speed):
    global current_latitude, current_longitude
    distance_travelled = 0.001  # her adımda gidilen mesafe
    angle = math.radians(calculate_bearing(
        current_latitude, current_longitude, target_latitude, target_longitude))
    current_latitude += distance_travelled * math.cos(angle)
    current_longitude += distance_travelled * math.sin(angle)
    update_current_location(current_latitude, current_longitude)
    folium.CircleMarker(location=[
                        current_latitude, current_longitude], radius=2, color='blue').add_to(my_map)


def navigate_to_target():
    while True:
        distance = haversine_distance(
            current_latitude, current_longitude, target_latitude, target_longitude)
        if distance < 0.01:
            print("Hedefe ulaşıldı!")
            move_robot(0, 0)
            break

        bearing = calculate_bearing(
            current_latitude, current_longitude, target_latitude, target_longitude)

        left_motor_speed = 100 - bearing
        right_motor_speed = 100 + bearing

        left_motor_speed = max(-100, min(100, left_motor_speed))
        right_motor_speed = max(-100, min(100, right_motor_speed))

        move_robot(left_motor_speed, right_motor_speed)


# Robotu hedefe götür
navigate_to_target()

# Haritayı HTML dosyasına kaydet
my_map.save("robot_simulation.html")

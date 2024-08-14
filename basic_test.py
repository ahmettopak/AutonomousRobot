import math

current_latitude = 0.0  # Anlık enlem
current_longitude = 0.0  # Anlık boylam

target_latitude = 41.015137  # Hedef enlem
target_longitude = 28.979530  # Hedef boylam


def update_current_location(new_latitude, new_longitude):
    global current_latitude, current_longitude
    current_latitude = new_latitude
    current_longitude = new_longitude


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Dünya yarıçapı (kilometre cinsinden)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
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
    bearing = (bearing + 360) % 360  # 0-360 derece arası
    return bearing


def navigate_to_target():
    while True:
        distance = haversine_distance(
            current_latitude, current_longitude, target_latitude, target_longitude)
        if distance < 0.01:  # Hedefe ulaşıldıysa döngüden çık
            print("Hedefe ulaşıldı!")
            move_robot(0, 0)  # Motorları durdur
            break

        bearing = calculate_bearing(
            current_latitude, current_longitude, target_latitude, target_longitude)

        # Hassas yönlendirme
        left_motor_speed = 100 - bearing
        right_motor_speed = 100 + bearing

        # Hızları -100 ile 100 arasında sınırlayın
        left_motor_speed = max(-100, min(100, left_motor_speed))
        right_motor_speed = max(-100, min(100, right_motor_speed))

        move_robot(left_motor_speed, right_motor_speed)


def basic_navigate_to_target():
    while True:
        distance = haversine_distance(
            current_latitude, current_longitude, target_latitude, target_longitude)
        if distance < 0.01:  # Hedefe ulaşıldıysa döngüden çık
            print("Hedefe ulaşıldı!")
            move_robot(0, 0)  # Motorları durdur
            break

        bearing = calculate_bearing(
            current_latitude, current_longitude, target_latitude, target_longitude)

        # Basit bir yönlendirme algoritması
        if bearing > 10:  # Sağa dön
            left_motor_speed = 50
            right_motor_speed = -50
        elif bearing < -10:  # Sola dön
            left_motor_speed = -50
            right_motor_speed = 50
        else:  # Düz git
            left_motor_speed = 100
            right_motor_speed = 100

        move_robot(left_motor_speed, right_motor_speed)


def move_robot(left_motor_speed, right_motor_speed):
    pass

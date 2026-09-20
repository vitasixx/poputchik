import requests
import os 
import numpy as np 
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from routingpy import OSRM
from datetime import datetime
from scipy.interpolate import CubicSpline
load_dotenv()
app = Flask(__name__)
client = OSRM(base_url="https://router.project-osrm.org")
FUEL_CONSUMPTION=8
@app.route('/')
def index():
    return render_template('index.html')
def get_coordinates(address):
    url = 'https://geocode-maps.yandex.ru/1.x/'
    api_key = os.getenv('yandex_key')
    if not api_key:
        raise ValueError("Ключ не найден!")
    params = {'apikey': api_key, 'geocode': address, 'format': 'json'}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    members = data['response']['GeoObjectCollection']['featureMember']
    if not members:
        raise ValueError(f'Адрес не найден: {address}')
    pos = members[0]['GeoObject']['Point']['pos']
    lon, lat = pos.split()
    return float(lon), float(lat)
@app.route('/calculate', methods=['POST'])
def calculate():
    addr1 = request.form.get('address_1') 
    addr2 = request.form.get('address_2')
    if not addr1 or not addr2:
        return jsonify({'error': 'Введите оба адреса'}), 400
    try:
        lon1, lat1 = get_coordinates(addr1)
        lon2, lat2 = get_coordinates(addr2)
    except (ValueError, KeyError, requests.RequestException) as e:
        return jsonify({'error': f'Не удалось определить координаты: {e}'}), 400
    coords = [[lon1, lat1], [lon2, lat2]]
    try:
        route = client.directions(locations=coords, profile='car') 
    except Exception as e:
        return jsonify({'error': f'Не удалось построить маршрут: {e}'}), 400
    t = route.duration / 60
    d = route.distance / 1000
    lon_min, lon_max = 38.875000, 39.095000
    lat_min, lat_max = 44.975000, 45.145000
    liters_one_way = d / 100 * FUEL_CONSUMPTION
    in_zone = any(lon_min <= p[0] <= lon_max and lat_min <= p[1] <= lat_max for p in route.geometry)
    current_hour = datetime.now().hour + datetime.now().minute / 60
    week_day = datetime.now().weekday()
    if in_zone:
        y = np.array([1, 0.5, 1.1, 1.3, 1.5, 1.8, 2.2, 2.6, 3.6])
        x = np.array(list(range(len(y))))
        f = CubicSpline(x,y)
        if week_day < 5:
            if 6.25 <= current_hour < 8.75:
                a = 0.035667 * (current_hour * 60 - 360) - 0.5350
            elif 8.75 <= current_hour < 9.5:
                a = -0.037778 * (current_hour * 60 - 360) + 11.5833
            elif 9.5 <= current_hour < 10.1667:
                a = -0.016250 * (current_hour * 60 - 360) + 7.0625
            elif 10.1667 <= current_hour < 16.3333:
                a = 0 * (current_hour * 60 - 360) + 3
            elif 16.3333 <= current_hour < 17.25:
                a = 0.007273 * (current_hour * 60 - 360) - 1.5091
            elif 17.25 <= current_hour < 17.75:
                a = 0.061667 * (current_hour * 60 - 360) - 38.2250
            elif 17.75 <= current_hour < 18.8:
                a = 0.015873 * (current_hour * 60 - 360) - 5.9405
            elif 18.8 <= current_hour < 20.5:
                a = -0.048529 * (current_hour * 60 - 360) + 43.5206
            elif 20.5 <= current_hour < 21.5:
                a = -0.009167 * (current_hour * 60 - 360) + 9.2750
            elif 21.5 <= current_hour < 23:
                a = -0.008333 * (current_hour * 60 - 360) + 8.5000
            else:  
                a = 0  
        else:
            if 6.0 <= current_hour < 8.0:
                a = 0.004167 * (current_hour * 60 - 360) + 0
            elif 8.0 <= current_hour < 10.0:
                a = 0.012500 * (current_hour * 60 - 360) - 1.0
            elif 10.0 <= current_hour < 12.0:
                a = 0.016667 * (current_hour * 60 - 360) - 2.0
            elif 12.0 <= current_hour < 15.0:
                a = 0.002778 * (current_hour * 60 - 360) + 3.0
            elif 15.0 <= current_hour < 18.0:
                a = -0.002778 * (current_hour * 60 - 360) + 6.0
            elif 18.0 <= current_hour < 20.5:
                a = -0.010000 * (current_hour * 60 - 360) + 11.2
            elif 20.5 <= current_hour < 22.0:
                a = -0.016667 * (current_hour * 60 - 360) + 17.0
            elif 22.0 <= current_hour <= 23.0:
                a = -0.016667 * (current_hour * 60 - 360) + 17.0
            else:
                a = 0
        return jsonify({'distance_km': round (d, 1), 'time_minutes': round (t * f(a), 1)})   
    else: 
        return jsonify({'time_minutes': round(t,  1), 'distance_km': round(d, 1), 'fuel_liters': round(liters_one_way, 2) })
if __name__ == '__main__':
    app.run(debug=True) 
import requests
import os 
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from routingpy import OSRM
from traffic import get_traffic_factor 

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
    liters_one_way = d / 100 * FUEL_CONSUMPTION
    minutes = t * get_traffic_factor(route.geometry)
    return jsonify({'time_minutes': round(minutes,  1), 'distance_km': round(d, 1), 'fuel_liters': round(liters_one_way, 2) }) 
if __name__ == "__main__":
    app.run(debug=True)
  
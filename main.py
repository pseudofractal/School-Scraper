import requests
import json
from config import API_KEY
from math import radians, sin, cos, sqrt, atan2

def get_places(api_key, latitude, longitude, radius):
    endpoint_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    location = f"{latitude},{longitude}"
    search_terms = [
        'school', 'primary school', 'high school', 'secondary school', 'junior school', 'university', 'college'
    ]
    
    places = []

    for term in search_terms:
        params = {
            'location': location,
            'radius': radius,
            'keyword': term,
            'key': api_key
        }

        response = requests.get(endpoint_url, params=params)
        results = response.json().get('results', [])
        
        for place in results:
            place_info = {
                'name': place.get('name'),
                'address': place.get('vicinity'),
                'distance': calculate_distance(latitude, longitude, place.get('geometry', {}).get('location', {}).get('lat'), place.get('geometry', {}).get('location', {}).get('lng'))
            }
            if place_info not in places:
                places.append(place_info)
        
        next_page_token = response.json().get('next_page_token')
        while next_page_token:
            params['pagetoken'] = next_page_token
            response = requests.get(endpoint_url, params=params)
            results = response.json().get('results', [])
            for place in results:
                place_info = {
                    'name': place.get('name'),
                    'address': place.get('vicinity'),
                    'distance': calculate_distance(latitude, longitude, place.get('geometry', {}).get('location', {}).get('lat'), place.get('geometry', {}).get('location', {}).get('lng'))
                }
                if place_info not in places:
                    places.append(place_info)
            next_page_token = response.json().get('next_page_token')
    
    places.sort(key=lambda x: x['distance'])

    return places

def calculate_distance(lat1, lon1, lat2, lon2):
    # Weird ass distance calculation
    R = 6400
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return round(distance, 2)

if __name__ == "__main__":
    # IISER M Coords
    latitude = 30.6676
    longitude = 76.7297
    radius = 200 * 1e3
    
    places = get_places(API_KEY, latitude, longitude, radius)
    
    with open('schools.json', 'w') as json_file:
        json.dump(places, json_file, indent=4)
        
    with open('schools.tsv', 'w') as tsv_file:
        for place in places:
            tsv_file.write(f"{place['name']}\t{place['address']}\t{place['distance']}\n")
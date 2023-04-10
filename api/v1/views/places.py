#!/usr/bin/python3
"""Defines the 'Place' api uri"""
from api.v1.views import app_views
from flask import abort, jsonify, request
from models import storage
from os import getenv
import requests


@app_views.route('/cities/<city_id>/places', strict_slashes=False)
def fetch_city_places(city_id):
    """Returns the list of all `Place` objects of a `City`"""
    city = storage.get("City", city_id)
    if city is None:
        abort(404)

    return jsonify([place.to_dict() for place in city.places])


@app_views.route('/places/<place_id>', strict_slashes=False)
def fetch_places_2(place_id):
    """Retrieves a `Place` object"""
    place = storage.get("Place", place_id)
    if place is None:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route('/places/<places_id>', strict_slashes=False,
                 methods=["DELETE"])
def delete_place(places_id):
    """Deletes a place object with an id == @places_id"""
    place = storage.get("Place", places_id)
    if place is None:
        abort(404)
    else:
        storage.delete(place)

    storage.save()
    return jsonify({}), 200


@app_views.route('/cities/<city_id>/places', strict_slashes=False,
                 methods=["POST"])
def post_place(city_id):
    """Handles post request to the `Place` uri"""
    city = storage.get("City", city_id)
    if city is None:
        abort(404)

    data = request.get_json()
    if not data:
        return "Not a JSON", 400

    user_id = data.get('user_id')
    if user_id is None:
        return "Missing user_id", 400
    if storage.get("User", user_id) is None:
        abort(404)
    if data.get('name') is None:
        return "Missing name", 400

    from models.place import Place
    new_place = Place(**data)
    # Make sure 'city_id' wasn't omitted in data
    setattr(new_place, 'city_id', city_id)
    new_place.save()

    return jsonify(new_place.to_dict()), 201


@app_views.route('/places/<place_id>', strict_slashes=False,
                 methods=["PUT"])
def update_places(place_id):
    """Updates a `Place` object"""
    place = storage.get("Place", place_id)
    if place is None:
        abort(404)

    data = request.get_json()
    if not data:
        return "Not a JSON", 400

    for key, value in data.items():
        if key in ['id', 'user_id', 'city_id', 'created_at', 'updated_at']:
            continue
        setattr(place, key, value)

    place.save()
    return jsonify(place.to_dict()), 200


"""
@app_views.route('/places_search', strict_slashes=False,
                 methods=["POST"])
def search_places():
    """Retrieves all 'Place' objects depending of the JSON
    in the body of the request
    """
    data = request.get_json()
    if data is None:
        return "Not a JSON", 400

    classes = ["amenities", "cities", "states"]
    result_places = []
    HBNB_API_HOST = getenv('HBNB_API_HOST')
    HBNB_API_PORT = getenv('HBNB_API_PORT')
    if HBNB_API_HOST is None:
        HBNB_API_HOST = '0.0.0.0'
    if HBNB_API_PORT is None:
        HBNB_API_PORT = '5050'

    root_url = 'http://{}:{}/api/v1'.format(HBNB_API_HOST, HBNB_API_PORT)

    for key, id_list in data.items():
        if key not in classes:
            continue
        if key == "states":
            for state_id in id_list:
                s_cities_url = root_url + '/states/{}/cities'
                s_cities = requests.get(s_cities_url.format(state_id))
                if s_cities.status_code > 299:
                    continue
                s_cities = s_cities.json()
                for sc_id in s_cities:
                    c_places_url = root_url + '/cities/{}/places'
                    c_places = requests.get(c_places_url.format(sc_id))
                    if c_places.status_code > 299:
                        continue
                    for place_1 in c_places:
                        result_places.append(place_1)
                    # result_places.append(place for place in c_places)
        elif key == "cities":
            for city_id in id_list:
                curr_city_url = root_url + '/cities/{}'.format(city_id)
                current_city = requests.get(curr_city_url)
                if current_city.status_code > 299:
                    continue

                current_city = current_city.json()
                if (('states' in data) and
                   (current_city.state_id in data['states'])):
                    continue

                c_places_url = root_url + '/cities/{}/places'
                c_places_2 = requests.get(c_places_url.format(city_id))
                c_places_2 = c_places_2.json()
                for place in c_places_2:
                    result_places.append(place)

    # If at this point 'result_places' is empty, fetch all 'Place' objects
    if len(result_places) == 0:
        all_place = storage.all('Place')
        for key, value in all_place.items():
            all_place[key] = value.to_dict()
            result_places.append(all_place[key])

    if 'amenities' in data:
        amenities_id = data['amenities']
        for place in result_places:
            p_obj = storage.get('Place', place['id'])
            p_amenities_id = p_obj.amenity_ids

            for a_id in amenities_id:
                if a_id not in p_amenities_id:
                    result_places.remove(place)

    return jsonify(result_places), 200
"""

@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
@swag_from('documentation/place/post_search.yml', methods=['POST'])
def places_search():
    """
    Retrieves all Place objects depending of the JSON in the body
    of the request
    """

    if request.get_json() is None:
        abort(400, description="Not a JSON")

    data = request.get_json()

    if data and len(data):
        states = data.get('states', None)
        cities = data.get('cities', None)
        amenities = data.get('amenities', None)

    if not data or not len(data) or (
            not states and
            not cities and
            not amenities):
        places = storage.all(Place).values()
        list_places = []
        for place in places:
            list_places.append(place.to_dict()) 
        return jsonify(list_places) 
 
    list_places = [] 
    if states: 
        states_obj = [storage.get(State, s_id) for s_id in states] 
        for state in states_obj: 
            if state: 
                for city in state.cities: 
                    if city: 
                        for place in city.places: 
                            list_places.append(place) 
 
    if cities: 
        city_obj = [storage.get(City, c_id) for c_id in cities]
        for city in city_obj:
            if city:
                for place in city.places:
                    if place not in list_places:
                        list_places.append(place)

    if amenities:
        if not list_places:
            list_places = storage.all(Place).values()
        amenities_obj = [storage.get(Amenity, a_id) for a_id in amenities]
        list_places = [place for place in list_places
                       if all([am in place.amenities
                               for am in amenities_obj])]

    places = []
    for p in list_places:
        d = p.to_dict()
        d.pop('amenities', None)
        places.append(d)

    return jsonify(places)

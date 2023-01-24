#!/usr/bin/python3
"""Defines the 'Place' api uri"""
from api.v1.views import app_views
from flask import abort, jsonify, request
from models import storage


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


@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
def places_search():
    """
    retrieves all Place objects depending
    of the JSON in the body of the request
    """
    req = request.get_json()
    if req is None:
        abort(400, "Not a JSON")

    req = request.get_json()
    if req is None or (
        req.get('states') is None and
        req.get('cities') is None and
        req.get('amenities') is None
    ):
        obj_places = storage.all(Place)
        return jsonify([obj.to_dict() for obj in obj_places.values()])

    places = []

    if req.get('states'):
        obj_states = []
        for ids in req.get('states'):
            obj_states.append(storage.get(State, ids))

        for obj_state in obj_states:
            for obj_city in obj_state.cities:
                for obj_place in obj_city.places:
                    places.append(obj_place)

    if req.get('cities'):
        obj_cities = []
        for ids in req.get('cities'):
            obj_cities.append(storage.get(City, ids))

        for obj_city in obj_cities:
            for obj_place in obj_city.places:
                if obj_place not in places:
                    places.append(obj_place)

    if not places:
        places = storage.all(Place)
        places = [place for place in places.values()]

    if req.get('amenities'):
        obj_am = [storage.get(Amenity, id) for id in req.get('amenities')]
        i = 0
        limit = len(places)
        HBNB_API_HOST = getenv('HBNB_API_HOST')
        HBNB_API_PORT = getenv('HBNB_API_PORT')

        port = 5000 if not HBNB_API_PORT else HBNB_API_PORT
        first_url = "http://0.0.0.0:{}/api/v1/places/".format(port)
        while i < limit:
            place = places[i]
            url = first_url + '{}/amenities'
            req = url.format(place.id)
            response = requests.get(req)
            place_am = json.loads(response.text)
            amenities = [storage.get(Amenity, obj['id']) for obj in place_am]
            for amenity in obj_am:
                if amenity not in amenities:
                    places.pop(i)
                    i -= 1
                    limit -= 1
                    break
            i += 1

    return jsonify([obj.to_dict() for obj in places])

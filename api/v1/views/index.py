"""Configures app_views"""
from api.v1.views import app_views
from models import storage


@app_views.route('/status')
def app_status():
    """Returns a JSON object, status-OK"""
    return {"status": "OK"}

@app_views.route('/stats')
def app_stats():
    """Returns the number of each objects by type"""
    amenities = storage.count("Amenity")
    cities = storage.count("City")
    places = storage.count("Place")
    reviews = storage.count("Review")
    states = storage.count("State")
    users = storage.count("User")

    return {
            "amenities": amenities,
            "cities": cities,
            "places": places,
            "reviews": reviews,
            "states": states,
            "users": users
            }

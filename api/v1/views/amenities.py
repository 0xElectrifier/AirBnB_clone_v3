#!/usr/bin/python3
"""
"""
from api.v1.views import app_views
from models.engine import storage


@app_views.route('/amenities')
@app_views.route('/amenities/<amenity_id>')
def fetch_amenity(amenity_id=None):
    """Retrieves a list of Amenity objects if @amenity_id is specified
    or just one object if argument is not none
    """
    d

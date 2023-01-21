"""Configures app_views"""
from views import app_views


@app_views.route('/status')
def app_view():
    """Returns a JSON object, status-OK"""
    return {"status": "OK"}

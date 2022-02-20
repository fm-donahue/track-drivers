from flask import Flask, jsonify, make_response

from errors import ServerApplicationError, ServerRequestsError
from helper import manufacturer_class
from request_helpers import open_session

app = Flask(__name__)

@app.errorhandler(ServerRequestsError)
def handle_requests_error(e):
    r = e.args[1]
    response = {
        "Error": e.description,
        "Request Error Code": r.status_code,
        "Message": e.args[0],
        "Url": r.url
    }
    return make_response(jsonify(response), e.code)

@app.errorhandler(ServerApplicationError)
def handle_app_error(e):
    response = {
        "Error": type(e).__name__,
    }
    if len(e.args) > 0:
        response["Message"] = e.args[0]
    return make_response(jsonify(response), e.code)

@app.errorhandler(NotImplementedError)
def handle_error(e):
    response = {
        "Error": type(e).__name__,
    }
    if len(e.args) > 0:
        response["Message"] = e.args[0]
    return make_response(jsonify(response), 501)

@app.errorhandler(404)
def handle_404_error(e):
    return make_response(jsonify({'Error': 'Not Found'}), 404)

@app.errorhandler(500)
def handle_500_error(e):
    response = {
        "Error": "Something else happened on the server"
    }
    return make_response(jsonify(response), 500)

app.register_error_handler(Exception, handle_500_error)

@app.get("/drivers/<string:manufacturer>/<string:model>/<string:os_info>")
def get_drivers(manufacturer, model, os_info):
    os_info = os_info.split(' ')
    with open_session() as s:
        driver_class = manufacturer_class(manufacturer, model, os_info, s)
        requests_drivers = driver_class.run_drivers()
        drivers = requests_drivers.get_drivers()
    return make_response(jsonify(drivers), 200)

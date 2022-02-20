import datetime
import os
import webbrowser

import requests

dir_path = os.path.dirname(os.path.abspath(__file__))

def save_error(response):
    filename = dir_path + 'responseError' + str(datetime.datetime.now()) + '.html'
    with open(filename, 'w') as f:
        f.write(response.text)
    return filename

def open_error(filename):
    webbrowser.open('file://' + dir_path + filename)

#Call api to get all drivers
def get_request_drivers(manufacturer, model, os_info):
    os_str = ' '.join(os_info)

    #ip address hidden
    response = requests.get(f'https://api.drivertracker.xyz/drivers/{manufacturer}/{model}/{os_str}')
    if response.status_code == 200:
        return response.json()
    filename = save_error(response)
    open_error(filename)
    raise

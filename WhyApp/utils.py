import itertools
from flask import request
import requests
import json
from . import app



# check VPN
def check_client_net():
    api = app.config.get("NETWORK_CHECKER_KEY")
    ip_addy = "73.143.122.22" #request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    response = requests.get("https://vpnapi.io/api/" + ip_addy + "?key=" + api)
    data = json.loads(response.text)
    if sum(data["security"].values()) > 0:
        print("Someone is attempting to access through hidden network. ")
        return True
    else:
        return False
import json
import requests
import threading
from flask import Flask

app = Flask(__name__)

# add api_urls as needed in 2D array below
api_urls = [["twitter", "facebook", "instagram", ],
            ["https://takehome.io/twitter", "https://takehome.io/facebook", "https://takehome.io/instagram"]]
# calculate once here, so not needed elsewhere
num_apis = len(api_urls[0])

# set up json to be returned, default values are for when no valid data can be obtained
return_json = {}
default_json = {}
for i in range(num_apis):
    default_json[api_urls[0][i]] = -1
return_json = dict(default_json)  # necessary at startup because if not forgetting prev values, but first requests have
# invalid json(s), we need to return return -1(s)

# Some program settings/parameters
forget_prev_values = True  # if external api gives non-json, our api can either return nothing or the previous value
retries_if_bad_data = 1  # value of one will contact endpoint twice in total

# contact endpoints with multiple threads to get activity data and then returns the data as a json
@app.route("/")
def social_network_activity():
    global return_json

    if forget_prev_values:
        return_json = dict(default_json)

    # set up and run threads
    threads = []
    for i in range(num_apis):
        thread = threading.Thread(target=process_api, args=[i])
        threads.append(thread)
        thread.start()

    # wait for threads to end
    for thread in threads:
        thread.join()

    # print("RETURNING JSON:", return_json)
    # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    return return_json


# receives text and returns false if not a json, otherwise it returns the json as dictionary
def parse_json(myjson):
    # not sure if good practice to sometimes return false, other times a json. For instance, Pycharm thinks it receives
    # boolean in process_api and gives warning
    try:
        received_json = json.loads(myjson)
    except ValueError:
        return False
    return received_json


# thread function that tries to contact the endpoint a certain number of times until it gets valid json and then
# counts entries in json and puts that into global dictionary
def process_api(api_number):
    global return_json
    tries = 0
    successful = False
    while (tries <= retries_if_bad_data) and not successful:
        response = requests.get(api_urls[1][api_number], timeout=2)
        received_json = parse_json(response.text)
        # print("-------  TRY:", tries, "  --------  API:", api_number, "  -------\n", response.text, "\n^^^^^^^^^^^")
        if received_json:
            return_json[api_urls[0][api_number]] = len(received_json)
            successful = True
        else:
            tries = tries + 1
    # print("RECEIVED JSON:", return_json)

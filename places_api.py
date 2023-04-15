import requests
import json
from config import rapid_api_key, rapid_api_host


def get_city_url(city):

    url = "https://find-places-to-live.p.rapidapi.com/location"

    querystring = {"query": city}

    headers = {
        "X-RapidAPI-Key": rapid_api_key,
        "X-RapidAPI-Host": rapid_api_host
    }

    response = requests.request(
        "GET", url, headers=headers, params=querystring)

    data = json.loads(response.text)

    for place in data:
        if place["type"] == "Town":
            url_fragment = place["urlFragment"]
            city_type = place["type"]
            return (url_fragment, city_type)
    return (None, None)


def get_crime_data(place, place_type):

    url = "https://find-places-to-live.p.rapidapi.com/placesToLive"

    querystring = {"place": place, "type": place_type}

    headers = {
        "X-RapidAPI-Key": rapid_api_key,
        "X-RapidAPI-Host": rapid_api_host
    }

    response2 = requests.request(
        "GET", url, headers=headers, params=querystring)

    place_data = json.loads(response2.text)

    print("############################")
    print(response2)
    print("############################")
    print("############################")
    print("############################")
    print("{'name': 'Service Unavailable', 'message': 'Internal Exception. Contact apimaker', 'code': 0, 'status': 503}")
    print("############################")

    if response2.status_code == 200:
        return place_data
    else:
        return {"error": "status is not 200"}

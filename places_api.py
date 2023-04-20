import requests
import json
import os

rapid_api_key = os.getenv('rapid_api_key')
rapid_api_host = os.getenv("rapid_api_host")


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
        if isinstance(place, dict) and place["type"] == "Town":
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

    if response2.status_code == 200:
        return place_data
    else:
        return {"error": "status is not 200"}

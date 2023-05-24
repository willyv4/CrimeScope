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

# make a seperate folder to handle api responnse


def crime_data_formulated(crimes):

    violent_crime_list = []
    violent_crimes = crimes['Violent Crimes']
    for crime_name, crime_values in violent_crimes.items():
        crime_value = crime_values['value']
        national_crime = crime_values['national']
        difference = national_crime - crime_value
        percent_difference = difference / national_crime * 100
        percent_difference = int(round(percent_difference))
        violent_crime_list.append({
            'crime': crime_name,
            'city': int(round(crime_value)),
            'national': int(round(national_crime)),
            'difference': difference,
            'percent_difference': percent_difference
        })

    # extract and compare property crime data
    property_crime_list = []
    property_crimes = crimes['Property Crimes']
    for crime_name, crime_values in property_crimes.items():
        crime_value = crime_values['value']
        national_crime = crime_values['national']
        difference = national_crime - crime_value
        percent_difference = difference / national_crime * 100
        percent_difference = int(round(percent_difference))
        property_crime_list.append({
            'crime': crime_name,
            'city': int(round(crime_value)),
            'national': int(round(national_crime)),
            'difference': difference,
            'percent_difference': percent_difference
        })

    return violent_crime_list, property_crime_list

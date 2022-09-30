from .keys import PEXELS_API_KEY, OPEN_WEATHER_API_KEY
import requests
import json


def get_photo(city, state):
    headers = {"Authorization": PEXELS_API_KEY}

    params = {"per_page": 1, "query": city + " " + state}

    url = "https://api.pexels.com/v1/search"

    response = requests.get(url, params=params, headers=headers)

    content = json.loads(response.content)

    try:
        return {"picture_url": content["photos"][0]["src"]["original"]}

    except:
        return {"picture_url": None}


def get_weather_data(city, state):

    geo_response = requests.get(
        f"http://api.openweathermap.org/geo/1.0/direct?q={city},{state},US&limit=1&appid={OPEN_WEATHER_API_KEY}"
    )
    content = json.loads(geo_response.content)
    print(content)
    lat = content[0]["lat"]
    lon = content[0]["lon"]

    weather_response = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPEN_WEATHER_API_KEY}&units=imperial"
    )
    weather_content = json.loads(weather_response.content)
    description = weather_content["weather"][0]["description"]
    temp = weather_content["main"]["temp"]
    return {"temp": temp, "description": description}

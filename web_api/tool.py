import requests


def get_weather(city_name):
    api_key = 'cfa4206962272d3cc3cf15200d229196'
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}'
    response = requests.get(url)
    weather_data = response.json()
    print(weather_data)


if __name__ == '__main__':
    city_name = '杭州'
    get_weather(city_name)

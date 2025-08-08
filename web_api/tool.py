import requests

# from data import find_duplicates
# # 查找重复文件
# @router.post("/find_duplicates")
# async def find_repeat_file(req: BaseReq):
#     folder_path = req.folder_path
#     duplicates = find_duplicates.run_duplicates(folder_path)
#     return result(0, duplicates)



def get_weather(city_name):
    api_key = 'cfa4206962272d3cc3cf15200d229196'
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}'
    response = requests.get(url)
    weather_data = response.json()
    print(weather_data)


if __name__ == '__main__':
    city_name = '杭州'
    get_weather(city_name)

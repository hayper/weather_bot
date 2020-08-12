import requests
import datetime
from time import sleep

class BotHandler:

    def __init__ (self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token) 
     
    def get_updates(self, offset=None, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        response = requests.get(self.api_url + method, data=params)
        result_json = response.json()['result']
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        response = requests.post(self.api_url + method, data=params)
        return response

    def get_last_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
            last_update = None
            
        return last_update

class YWeather:

    def __init__(self, token):
        self.token = token
        self.lat = "56.50"
        self.lon = "60.35"
        self.lang = "ru_RU"
        self.extra = "true"
        self.api_url = "https://api.weather.yandex.ru/v2/forecast?"

    def get_weather(self):    
        response = requests.get(self.api_url + "lat=" + self.lat + "&lon=" + self.lon + "&lang=" 
                                + self.lang + "&extra=" + self.extra, 
                                headers={'X-Yandex-API-Key': self.token})
        return response.json()

    

Yandex_weather = YWeather('578a5be9-5d10-46bc-a072-b8814cd15a27')
greet_bot = BotHandler('1211842153:AAHhY54IlyraxIHA0fTJKQEDmW9cSVUSFQI')
greetings = ('здравствуйте', 'привет', 'ку', 'здорово')
now = datetime.datetime.now()


def main():
    new_offset = None
    today = now.day
    hour = now.hour

    condition = {'clear': 'ясно',
                'partly-cloudy': 'малооблачно',
                'cloudy': 'облачно с прояснениями',
                'overcast': 'пасмурно',
                'drizzle': 'морось',
                'light-rain': 'небольшой дождь',
                'rain': 'дождь',
                'moderate-rain': 'умеренно сильный дождь',
                'heavy-rain': 'сильный дождь',
                'continuous-heavy-rain': 'длительный сильный дождь',
                'showers': 'ливень',
                'wet-snow': 'дождь со снегом',
                'light-snow': 'небольшой снег',
                'snow': 'снег',
                'snow-showers': 'снегопад',
                'hail': 'град',
                'thunderstorm': 'гроза',
                'thunderstorm-with-rain': 'дождь с грозой',
                'thunderstorm-with-hail': 'гроза с градом'}

    wind_dir = {'nw':'северо-западное',
                'n':'северное',
                'ne':'северо-восточное',
                'e':'восточное',
                'se':'юго-восточное',
                's':'южное',
                'sw':'юго-западное',
                'w':'западное',
                'с':'штиль'}
    while True:
        greet_bot.get_updates(new_offset)

        last_update = greet_bot.get_last_update()
        
        if last_update == None:
            continue

        last_update_id = last_update['update_id']
        last_chat_text = last_update['message']['text']
        last_chat_id = last_update['message']['chat']['id']
        last_chat_name = last_update['message']['chat']['first_name']

        if last_chat_text.lower() in greetings and today == now.day and 6 <= hour < 12:
            greet_bot.send_message(last_chat_id, 'Доброе утро, {}'.format(last_chat_name))
        
        if last_chat_text.lower() in greetings and today == now.day and 12 <= hour < 17:
            greet_bot.send_message(last_chat_id, 'Добрый день {}'.format(last_chat_name))

        if last_chat_text.lower() in greetings and today == now.day and 17 <= hour < 23:
            greet_bot.send_message(last_chat_id, 'Добрый вечер, {}'.format(last_chat_name))
        
        if last_chat_text.lower() == "погода":
            weather = Yandex_weather.get_weather()
            greet_bot.send_message(last_chat_id,  condition[weather['fact']['condition']] + '\n' + 'Температура ' + str(weather['fact']['temp']) + '°C' + '\n' +
                                    'По ощущениям ' + str(weather['fact']['feels_like']) + '°C' + '\n' +'Скорость ветра ' + str(weather['fact']['wind_speed']) + ' м/с' + 
                                    '\n' + ' направление ветра ' + wind_dir[weather['fact']['wind_dir']])

        new_offset = last_update_id + 1

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
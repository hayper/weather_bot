import requests
import datetime
from time import sleep
#import locale
import json
import os

#locale.setlocale(locale.LC_ALL, "ru")

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

with open(os.path.abspath('data.json'), encoding='utf-8') as data_json:
    data = json.load(data_json)

condition = data['condition']
wind_dir = data['wind_dir']
command_variants = data['command_variants']


def getTemp(temp):
    if temp > 0:
        return '+' + str(temp)
    else:
        return str(temp)

def getMessageForTimesOfDay(strTimesOfDay, TimesOfDay):
    part_mess = (strTimesOfDay + '\n' + getTemp(TimesOfDay['temp_min']) + '°..' +  getTemp(TimesOfDay['temp_max']) + '°      ' +
                condition[TimesOfDay['condition']] + '\n' +
                ' ' * 10 + 'Давление  -  '+ str(TimesOfDay['pressure_mm']) + '  мм рт. ст.' + '\n' +
                ' ' * 10 + 'Влажность  -  ' + str(TimesOfDay['humidity']) + '%' + '\n' +
                ' ' * 10 + 'Ветер  -  ' + str(TimesOfDay['wind_speed']) + ' м/с ' + wind_dir[TimesOfDay['wind_dir']] + '\n' + 
                ' ' * 10 + 'Ощущается как  -  ' + str(getTemp(TimesOfDay['feels_like'])) + '°')
    return part_mess

def main():
    new_offset = None
    today = now.day
    hour = now.hour

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
        
        if last_chat_text.lower() in command_variants:
            weather = Yandex_weather.get_weather()
            today_weather = weather['forecasts'][0]['parts']
            tomorrow_weather = weather['forecasts'][1]['parts']
            day_after_tomorrow_weather = weather['forecasts'][2]['parts']

            if last_chat_text.lower() == 'погода' or last_chat_text.lower() == '/weather':
                message = (condition[weather['fact']['condition']] + '\n' + 
                            '🌡 Температура    ' + getTemp(weather['fact']['temp']) + '°C' + '\n' +
                            '🌚 По ощущениям    ' + getTemp(weather['fact']['feels_like']) + '°C' + '\n' + 
                            '🌬 Скорость ветра    ' + str(weather['fact']['wind_speed']) + ' м/с' + '\n' + 
                            '🧭 Направление ветра    ' + wind_dir[weather['fact']['wind_dir']])
                greet_bot.send_message(last_chat_id,  message)

            elif last_chat_text.lower() == 'погода на сегодня' or last_chat_text.lower() == '/weatherfortoday':
                morning = today_weather['morning']
                day = today_weather['day']
                evening = today_weather['evening']
                night = tomorrow_weather['night']
                str_dt = datetime.datetime.strftime(datetime.datetime.utcfromtimestamp(weather['forecasts'][0]['date_ts'] + 86400), "%A, %d %B")

                message = (str_dt + '\n' +
                            getMessageForTimesOfDay('Утро', morning) + '\n' +
                            getMessageForTimesOfDay('День', day) + '\n' +
                            getMessageForTimesOfDay('Вечер', evening) + '\n' +
                            getMessageForTimesOfDay('Ночь', day))
                greet_bot.send_message(last_chat_id, message)

            elif last_chat_text.lower() == 'погода на завтра' or last_chat_text.lower() == '/theweatherfortomorrow':
                morning = tomorrow_weather['morning']
                day = tomorrow_weather['day']
                evening = tomorrow_weather['evening']
                night = day_after_tomorrow_weather['night']
                str_dt = datetime.datetime.strftime(datetime.datetime.utcfromtimestamp(weather['forecasts'][1]['date_ts'] + 86400), "%A, %d %B")
                
                message = (weather['forecasts'][0]['date'] + '\n' +
                            getMessageForTimesOfDay('Утро', morning) + '\n' +
                            getMessageForTimesOfDay('День', day) + '\n' +
                            getMessageForTimesOfDay('Вечер', evening) + '\n' +
                            getMessageForTimesOfDay('Ночь', day))
                greet_bot.send_message(last_chat_id, message)

        new_offset = last_update_id + 1

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
from loader import bot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import date, datetime, timedelta
from statess.lowprice_state import UserState
from databases.history_classes import User, Hotel


min_date = ''


url1 = "https://hotels4.p.rapidapi.com/locations/v3/search"
url2 = "https://hotels4.p.rapidapi.com/properties/v2/list"
url3 = "https://hotels4.p.rapidapi.com/properties/v2/detail"
headers1 = {
        "X-RapidAPI-Key": "bb7ec06b11msh5f4c6b0fe0f3cf0p1a1a39jsn0814ed71a496",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
payload = {
                "currency": "USD",
                "eapid": 1,
                "locale": "en_US",
                "siteId": 300000001,
                "destination": {"regionId": ""},
                "checkInDate": {
                    "day": 0,
                    "month": 0,
                    "year": 0
                },
                "checkOutDate": {
                    "day": 0,
                    "month": 0,
                    "year": 0
                },
                "rooms": [
                    {
                        "adults": 0
                    }
                ],
                "resultsStartingIndex": 0,
                "resultsSize": 0,
                "sort": "PRICE_LOW_TO_HIGH",
                "filters": {"price": {
                    "max": 200,
                    "min": 10
                }}
            }
headers2 = {
                "content-type": "application/json",
                "X-RapidAPI-Key": "bb7ec06b11msh5f4c6b0fe0f3cf0p1a1a39jsn0814ed71a496",
                "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
            }

payload_detail = {
	"currency": "USD",
	"eapid": 1,
	"locale": "en_US",
	"siteId": 300000001,
	"propertyId": ''
}


@bot.message_handler(commands=['lowprice'])
def first_low(message: types.Message) -> None:
    bot.set_state(user_id=message.from_user.id, state=UserState.city, chat_id=message.chat.id)
    with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
        data['command'] = message.text
    bot.send_message(chat_id=message.chat.id, text='Введите город:')


@bot.message_handler(state=UserState.city)
def get_city(message: types.Message) -> None:
    if message.text.isalpha():
        params = {'q': message.text.capitalize()}
        response = requests.request("GET", url1, headers=headers1, params=params)
        ssd = [x for x in response.json()['sr'] if x['type'] == 'CITY']

        if ssd:
            ikm = InlineKeyboardMarkup()
            for x in ssd:
                ikm.add(InlineKeyboardButton(text=x['regionNames']['fullName'], callback_data=f'city_id_{x["gaiaId"]}'))
            bot.send_message(chat_id=message.chat.id, text='Выбери нужный город из списка', reply_markup=ikm)

            with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
                data['city'] = message.text
        else:
            bot.send_message(chat_id=message.chat.id, text='Этого города нет в списке. Введите другой город:')
    else:
        bot.send_message(chat_id=message.chat.id, text='Введите только буквы!')


@bot.callback_query_handler(func=lambda call: call.data.startswith('city_id'))
def callback(call):
    regionId = call.data.strip('city_id_')
    with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
        data['regionId'] = regionId
        print(data)
    bot.set_state(user_id=call.from_user.id, state=UserState.hotels_count, chat_id=call.message.chat.id)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    bot.send_message(chat_id=call.from_user.id, text='Теперь введите количество отелей(не больше 5):')


@bot.message_handler(state=UserState.hotels_count)
def get_hotels_count(message: types.Message) -> None:
    if message.text.isdigit() and 0 < int(message.text) <= 5:
        bot.send_message(chat_id=message.chat.id, text='Сколько человек будет проживать?')
        bot.set_state(user_id=message.from_user.id, state=UserState.people_count, chat_id=message.chat.id)

        with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
            data['hotels_count'] = message.text
    else:
        bot.send_message(chat_id=message.chat.id, text='Некорректные данные.\nПожалуйста, повторите ввод:')


@bot.message_handler(state=UserState.people_count)
def get_people_count(message: types.Message) -> None:
    if message.text.isdigit():
        calendar, step = DetailedTelegramCalendar(calendar_id=1, min_date=date.today() + timedelta(days=1),
                                                  max_date=date.today() + timedelta(days=180)).build()
        bot.send_message(chat_id=message.chat.id, text='Укажите дату заезда:')
        bot.send_message(message.chat.id,
                         f"Select {LSTEP[step]}",
                         reply_markup=calendar)

        with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
            data['people_count'] = message.text
    else:
        bot.send_message(chat_id=message.chat.id, text='Введите только цифры!')


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def cal(call):
    result, key, step = DetailedTelegramCalendar(calendar_id=1, min_date=date.today(),
                                                 max_date=date.today() + timedelta(days=180)).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Select {LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"You selected {result}",
                              call.message.chat.id,
                              call.message.message_id)

        with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
            a = str(result).split('-')
            if a[1].startswith('0'):
                a[1] = a[1][1:]
            if a[2].startswith('0'):
                a[2] = a[2][1:]
            data['date_in'] = {'d': a[2], 'm': a[1], 'y': a[0]}
            global min_date
            min_date = date(int(data['date_in']['y']), int(data['date_in']['m']), int(data['date_in']['d']))
            bot.send_message(chat_id=call.from_user.id, text='Укажите дату выезда:')
            calendar, step = DetailedTelegramCalendar(calendar_id=2, min_date=min_date,
                                                      max_date=min_date + timedelta(days=180)).build()
            bot.send_message(call.message.chat.id,
                             f"Select {LSTEP[step]}",
                             reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def calling(call):
    result, key, step = DetailedTelegramCalendar(calendar_id=2, min_date=min_date,
                                                 max_date=min_date + timedelta(days=180)).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Select {LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"You selected {result}",
                              call.message.chat.id,
                              call.message.message_id)
        bot.set_state(user_id=call.from_user.id, state=UserState.photo, chat_id=call.message.chat.id)

        with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
            a = str(result).split('-')
            data['date_out'] = {'d': a[2], 'm': a[1], 'y': a[0]}
            bot.send_message(chat_id=call.from_user.id, text='Вывести фотографии отелей?')


@bot.message_handler(state=UserState.photo)
def get_hotels_count(message: types.Message) -> None:
    if message.text.lower() == 'да':
        bot.send_message(chat_id=message.chat.id, text='Сколько фотографий вывести?(не больше 5)')
        bot.set_state(user_id=message.from_user.id, state=UserState.photo_count, chat_id=message.chat.id)

        with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
            data['photo'] = message.text
    else:
        bot.send_message(chat_id=message.chat.id, text='Значит без фотографий')
        with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
            data['photo_count'] = 0

        payload['destination']['regionId'] = data['regionId']
        payload['checkInDate']['day'] = int(data['date_in']['d'])
        payload['checkInDate']['month'] = int(data['date_in']['m'])
        payload['checkInDate']['year'] = int(data['date_in']['y'])
        payload['checkOutDate']['day'] = int(data['date_out']['d'])
        payload['checkOutDate']['month'] = int(data['date_out']['m'])
        payload['checkOutDate']['year'] = int(data['date_out']['y'])
        payload['rooms'][0]['adults'] = int(data['people_count'])
        payload['resultsSize'] = int(data['hotels_count'])
        # print(data)

        response = requests.request("POST", url2, json=payload, headers=headers2)
        # print(response.text)
        id_price = dict()
        distance = list()
        index = 0
        for hotel in response.json()['data']['propertySearch']['properties']:
            id_price[hotel['id']] = hotel['price']['options'][0]['formattedDisplayPrice']
            distance.append(hotel['destinationInfo']['distanceFromDestination']['value'])

        mess_db = User.create(command=data['command'], date=datetime.now(), user_id=message.from_user.id)
        for iden, price in id_price.items():
            payload_detail['propertyId'] = iden
            resp = requests.request("POST", url3, json=payload_detail, headers=headers2)
            name = resp.json()['data']['propertyInfo']['summary']['name']
            address = resp.json()['data']['propertyInfo']['summary']['location']['address']['firstAddressLine']
            result_text = f'Название отеля: {name}\nАдрес: {address}\nЦена за одну ночь: {price}\nРасстояние до центра: {distance[index]} миль'
            bot.send_message(message.chat.id, text=result_text)
            hotel_db = Hotel.create(name=name, address=address, price=price, distance=distance[index], req=mess_db)
            index += 1

        bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state=UserState.photo_count)
def get_hotels_count(message: types.Message) -> None:
    if message.text.isdigit() and 0 < int(message.text) <= 5:

        with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
            data['photo_count'] = message.text

        payload['destination']['regionId'] = data['regionId']
        payload['checkInDate']['day'] = int(data['date_in']['d'])
        payload['checkInDate']['month'] = int(data['date_in']['m'])
        payload['checkInDate']['year'] = int(data['date_in']['y'])
        payload['checkOutDate']['day'] = int(data['date_out']['d'])
        payload['checkOutDate']['month'] = int(data['date_out']['m'])
        payload['checkOutDate']['year'] = int(data['date_out']['y'])
        payload['rooms'][0]['adults'] = int(data['people_count'])
        payload['resultsSize'] = int(data['hotels_count'])
        # print(data)

        response = requests.request("POST", url2, json=payload, headers=headers2)
        print(response.text)
        id_price = dict()
        distance = list()
        index = 0
        for hotel in response.json()['data']['propertySearch']['properties']:
            id_price[hotel['id']] = hotel['price']['options'][0]['formattedDisplayPrice']
            distance.append(hotel['destinationInfo']['distanceFromDestination']['value'])

        mess_db = User.create(command=data['command'], date=datetime.now(), user_id=message.from_user.id)
        for iden, price in id_price.items():
            payload_detail['propertyId'] = iden
            resp = requests.request("POST", url3, json=payload_detail, headers=headers2)
            # print(resp.text)
            name = resp.json()['data']['propertyInfo']['summary']['name']
            address = resp.json()['data']['propertyInfo']['summary']['location']['address']['firstAddressLine']
            result_text = f'Название отеля: {name}\nАдрес: {address}\nЦена за одну ночь: {price}' \
                          f'\nРасстояние до центра: {distance[index]} миль\nФотографии:'
            bot.send_message(message.chat.id, text=result_text)
            hotel_db = Hotel.create(name=name, address=address, price=price, distance=distance[index], req=mess_db)
            index += 1
                # photo = resp.json()['data']['propertyInfo']['propertyGallery']['images'][5]['image']['url']
            for num in range(int(data['photo_count'])):
                photo = resp.json()['data']['propertyInfo']['propertyGallery']['images'][num]['image']['url']
                bot.send_photo(message.chat.id, photo=photo)

        bot.delete_state(message.from_user.id, message.chat.id)
    else:
        bot.send_message(chat_id=message.chat.id, text='Некорректные данные.\nПожалуйста, повторите ввод:')
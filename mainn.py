import requests
from telebot.handler_backends import State, StatesGroup
import telebot
from telebot import types
from telebot.custom_filters import StateFilter
from telebot.storage import StateMemoryStorage

TOKEN = '6023364429:AAHhRuf-xjxivwjHNX_o0kFlkzyQZO6hVYc'

bot = telebot.TeleBot(TOKEN)


# 1. Город, где будет проводиться поиск.
# 2. Количество отелей, которые необходимо вывести в результате (не больше
# заранее определённого максимума).
# 3. Необходимость загрузки и вывода фотографий для каждого отеля (“Да/Нет”)
# a. При положительном ответе пользователь также вводит количество
# необходимых фотографий (не больше заранее определённого
# максимума)


class UserInfoState(StatesGroup):
    city = State()
    hotels_count = State()


@bot.message_handler(commands=['lowprice'])
def lowprice(message: types.Message) -> None:
    bot.set_state(user_id=message.from_user.id, state=UserInfoState.city, chat_id=message.chat.id)
    bot.send_message(chat_id=message.chat.id, text='Введите город:')


@bot.message_handler(state=UserInfoState.city)
def get_city(message: types.Message) -> None:
    if message.text.isalpha():
        bot.send_message(chat_id=message.chat.id, text='Теперь введите количество отелей:')
        bot.set_state(user_id=message.from_user.id, state=UserInfoState.hotels_count, chat_id=message.chat.id)

        with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
            data['city'] = message.text
            print(data)
    else:
        bot.send_message(chat_id=message.chat.id, text='Введите только буквы!')


@bot.message_handler(state=UserInfoState.hotels_count)
def get_hotels_count(message: types.Message) -> None:
    if message.text.isdigit():
        bot.send_message(chat_id=message.chat.id, text='Хорошо')

        with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
            data['hotels_count'] = message.text
    else:
        bot.send_message(chat_id=message.chat.id, text='Введите только буквы!')


@bot.message_handler(commands=['start'])
def start(message: types.Message):
    bot.send_message(message.chat.id, text=f'Привет, {message.from_user.first_name}')


@bot.message_handler(commands=['berlin'])
def lowprice(message: types.Message):
    a = message.text[1:]
    params = {'q': a.capitalize()}
    print(params)
    url = "https://hotels4.p.rapidapi.com/locations/v3/search"
    headers = {
        "X-RapidAPI-Key": "4770d2cd46msh4e586a662880ae4p1ccec4jsn56e4f1115adc",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers, params=params)
    print(response.text)
    bot.send_message(message.chat.id, text=response.text[:999])


@bot.message_handler(content_types=['photo'])
def get_user_photo(message: types.Message):
    bot.send_message(message.chat.id, text='Вау, крутое фото!')


@bot.message_handler(commands=['website'])
def website(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Посетить веб-сайт', url='https://www.youtube.com/'))
    bot.send_message(message.chat.id, text='Выбери, что сделать:', reply_markup=markup)


@bot.message_handler(commands=['help'])
def website(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    website = types.KeyboardButton(text='Веб-сайт')
    start = types.KeyboardButton(text='Start')
    markup.add(website, start)
    bot.send_message(message.chat.id, text='Выбирай:', reply_markup=markup)


@bot.message_handler()
def any(message: types.Message):
    if message.text == 'id':
        bot.send_message(message.chat.id, text=f'Твой id: {message.from_user.id}')
    else:
        bot.send_message(message.from_user.id, text=f'{message.text} - это неправильное сообщение')


if __name__ == '__main__':
    bot.polling(none_stop=True)
    bot.add_custom_filter(StateFilter(bot))

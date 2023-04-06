from loader import bot
from telebot import types
from databases.history_classes import User, Hotel


@bot.message_handler(commands=['history'])
def first_low(message: types.Message) -> None:
    if not User.select().where(User.user_id == message.from_user.id):
        bot.send_message(message.chat.id, text='Ваша история пуста.')
    for user in User.select().where(User.user_id == message.from_user.id):
        print(user.command, user.date)
        bot.send_message(chat_id=message.chat.id,
                            text=f'Команда: {user.command}\nДата и время команды: {user.date}\nНайденные отели:')
        for hotel in Hotel.select().where(Hotel.req == user.id):
            print(hotel.name)
            bot.send_message(chat_id=message.chat.id,
                                text=f'Название отеля: {hotel.name}\n'
                                    f'Адрес: {hotel.address}\n'
                                    f'Цена за одну ночь: {hotel.price}\n'
                                    f'Расстояние до центра: {hotel.distance} миль')

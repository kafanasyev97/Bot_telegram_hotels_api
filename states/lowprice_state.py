from telebot.handler_backends import State, StatesGroup


class UserState(StatesGroup):
    city = State()
    hotels_count = State()
    people_count = State()
    photo = State()
    photo_count = State()

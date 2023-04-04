from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_datas import config

storage = StateMemoryStorage()
TOKEN = '6023364429:AAHhRuf-xjxivwjHNX_o0kFlkzyQZO6hVYc'
bot = TeleBot(token=TOKEN, state_storage=storage)


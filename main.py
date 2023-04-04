from telebot import types
from telebot.custom_filters import StateFilter
from loader import bot
from utilss.set_bot_commands import set_default_commands
import handlerss


@bot.message_handler()
def any(message: types.Message):
    if message.text == 'id':
        bot.send_message(message.chat.id, text=f'Твой id: {message.from_user.id}')
    else:
        bot.send_message(message.from_user.id, text=f'{message.text} - это неправильное сообщение')


if __name__ == '__main__':
    set_default_commands(bot)
    bot.add_custom_filter(StateFilter(bot))
    bot.polling(none_stop=True)

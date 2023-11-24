import telebot
from dotenv import load_dotenv
from os import environ

load_dotenv()
TOKEN = environ["TELEGRAM_TOKEN"]

HELP_TEXT = """/help - помощь(это сообщение)
/auth - авторизация
/menu - посмотреть меню
/review - оставить отзыв о блюде"""
START_TEXT = """Это бот для организации корпоротивного питания
(добавлять отзывы и оценку блюду)
/help - помощь"""

bot = telebot.TeleBot(TOKEN)


# Handle '/start' and '/help'
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(
        message,
        START_TEXT,
    )


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(
        message,
        HELP_TEXT,
    )


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)


bot.infinity_polling()

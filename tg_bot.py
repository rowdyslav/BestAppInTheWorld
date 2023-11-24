import telebot
from dotenv import load_dotenv
from os import environ
from .db_conn import *

load_dotenv()
TOKEN = environ["TELEGRAM_TOKEN"]

bot = telebot.TeleBot(TOKEN)

START_TEXT = """"""


# Handle '/start' and '/help'
@bot.message_handler(commands=["help", "start"])
def send_welcome(message):
    bot.reply_to(
        message,
        """\
Hi there, I am EchoBot.
I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
""",
    )


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda _: True)
def echo_message(message):
    bot.reply_to(message, message.text)

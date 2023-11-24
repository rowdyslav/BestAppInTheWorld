import telebot
from telebot.types import Message
from dotenv import load_dotenv
from os import environ
from db_conn import DISHES

load_dotenv()
TOKEN = environ["TELEGRAM_TOKEN"]

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["menu"])
def menu(message):
    dishes = list(DISHES.find())
    ans_message = []
    for i in dishes:
        current = []
        for j in ["title", "structure", "photo", "scores"]:
            current.append(i[j])
        ans_message.append(": ".join(current))
    ans_message = "\n".join(ans_message)

    bot.reply_to(
        message,
        ans_message,
    )


["title", "structure", "photo", "scores"]

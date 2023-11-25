import telebot
from telebot.types import Message
from dotenv import load_dotenv
from os import environ
from db_conn import DISHES, USERS
from roles import User

from icecream import ic

load_dotenv()
TOKEN = environ["TELEGRAM_TOKEN"]

HELP_TEXT = """
**/review <имя блюда> <оценка>** - оставить отзыв о блюде
"""


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["help", "start"])
def help(message):
    bot.reply_to(
        message,
        HELP_TEXT,
    )


@bot.message_handler(commands=["review"])
def review(message: Message):
    status_message = bot.send_message(
        message.chat.id,
        "Загрузка..",
    )
    args = message.text.split()  # type: ignore

    dish_title = "".join(args[1:-1])
    q = {"title": dish_title}

    dish = DISHES.find_one(q)
    if not dish:
        bot.reply_to(message, "Блюдо не найдено!")
        return
    if not args[-1].isnumeric() or not 1 <= int(args[-1]) <= 5:
        bot.reply_to(message, f'Ожидалось число от 1 до 5, получено "{args[-1]}"')
        return

    DISHES.update_one(q, {"$inc": {"scores": {"sum": int(args[-1]), "len": 1}}})
    bot.delete_message(message.chat.id, status_message.message_id)

    bot.reply_to(
        message,
        f"Блюду {dish_title} успешно поствлена оценка {args[-1]}!",
    )


bot.infinity_polling()

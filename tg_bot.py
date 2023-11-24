import telebot
from telebot.types import Message
from dotenv import load_dotenv
from os import environ
from db_conn import DISHES

from icecream import ic

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
def start(message):
    bot.reply_to(
        message,
        START_TEXT,
    )


@bot.message_handler(commands=["help"])
def help(message):
    bot.reply_to(
        message,
        HELP_TEXT,
    )


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


@bot.message_handler(commands=["rewiew"])
def review(message: Message):
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

    DISHES.update_one(q, {"$push": {"scores": int(args[-1])}})

    bot.reply_to(
        message,
        f"Блюду {dish_title} успешно поствлена оценка {args[-1]}!",
    )


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)


bot.infinity_polling()

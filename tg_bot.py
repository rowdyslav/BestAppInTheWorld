import telebot
from telebot.types import Message
from telebot import types
from dotenv import load_dotenv
from os import environ
from db_conn import DISHES, USERS, ORDERS
from datetime import datetime as dt
from roles import User
from roles import Worker
from roles import Manager
from roles import Cooker
from roles import Deliverier
from roles import Admin

from icecream import ic

load_dotenv()
TOKEN = environ["TELEGRAM_TOKEN"]

HELP_TEXT = """
*/review <имя блюда> <оценка>* - оставить отзыв о блюде
"""

USER_LOGINS = {}

bot = telebot.TeleBot(TOKEN)


buttons_dict = {i: x[0] for i, x in enumerate(["/help", "/orders"])}
deliverier_ikb = types.InlineKeyboardMarkup()
button_list = [
    types.InlineKeyboardButton(text=x, callback_data=x) for x in buttons_dict.values()
]
deliverier_ikb.add(*button_list)

deliverier_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = types.KeyboardButton("/orders")
btn3 = types.KeyboardButton("/help")
deliverier_kb.add(btn1).add(btn3)

start_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
sbtn1 = types.KeyboardButton("/auth")
sbtn2 = types.KeyboardButton("/help")
start_kb.add(sbtn1).add(sbtn2)


@bot.message_handler(commands=["help", "start"])
def help(message):
    bot.reply_to(message, HELP_TEXT, parse_mode="Markdown", reply_markup=start_kb)


@bot.message_handler(commands=["review"])
def review(message: Message):
    args = message.text.split()  # type: ignore

    if len(args) < 3:
        bot.reply_to(message, HELP_TEXT, parse_mode="Markdown")
        return

    if not args[-1].isnumeric() or not 1 <= int(args[-1]) <= 5:
        bot.reply_to(
            message,
            f"Ожидалось число от 1 до 5, получено *{args[-1]}*",
            parse_mode="Markdown",
        )
        return

    status_message = bot.send_message(
        message.chat.id, "_Загрузка.._", parse_mode="Markdown"
    )

    dish_title = "".join(args[1:-1])
    q = {"title": dish_title}

    dish = DISHES.find_one(q)
    if not dish:
        bot.delete_message(message.chat.id, status_message.message_id)
        bot.reply_to(message, "Блюдо не найдено!")
        return

    DISHES.update_one(
        q,
        {
            "$set": {
                "scores": {
                    "sum": dish["scores"]["sum"] + int(args[-1]),
                    "len": dish["scores"]["len"] + 1,
                }
            }
        },
    )
    bot.delete_message(message.chat.id, status_message.message_id)

    bot.reply_to(
        message,
        f"Блюду {dish_title} успешно поствлена оценка {args[-1]}!",
    )


@bot.message_handler(commands=["auth"])
def auth(message):
    send_msg = bot.send_message(
        message.chat.id,
        "Отправте свой логин и пароль через пробел",
    )
    bot.register_next_step_handler(send_msg, wait_auth)


def wait_auth(message):
    status_message = bot.send_message(
        message.chat.id, "_Обработка.._", parse_mode="Markdown"
    )
    login, password = message.text.split()
    log_result = User(login, password)._login()

    bot.delete_message(message.chat.id, status_message.message_id)

    if not log_result[1]:
        bot.send_message(message.chat.id, log_result[0])
    else:
        if isinstance(log_result[1], Worker):
            keyboard = deliverier_kb
        else:
            keyboard = deliverier_kb
        USER_LOGINS[message.from_user.id] = log_result[1]
        bot.send_message(
            message.chat.id,
            f"Вы авторизованы под логином {login}",
            reply_markup=keyboard,
        )
        print(USER_LOGINS)


@bot.message_handler(commands=["logout"])
def logout(message):
    bot.send_message(message.chat.id, "Вы вышли из аккаунта")
    USER_LOGINS = USER_LOGINS[message.from_user.id] = None


@bot.message_handler(commands=["orders"])
def orders(message):
    login = USER_LOGINS[message.from_user.id].login
    deliverier = USERS.find_one({"login": login})
    orders = list(ORDERS.find({"deliverier": login}))
    for ind, order in enumerate(orders):
        orders[ind]["date"] = dt.strftime(order["date"], "%d/%m/%Y")
    to_send = []
    for ind, order in enumerate(orders):
        current = [orders[ind]["date"], orders[ind]["cost"], orders[ind]["status"]]
        current = list(map(str, current))
        address = "/".join(
            [orders[ind]["address"][ob] for ob in orders[ind]["address"]]
        )
        current.append(address)
        to_send.append("; ".join(current))

    bot.send_message(message.chat.id, "\n".join(to_send))


bot.infinity_polling()

{
    "status": "Доставляется",
    "cost": 370,
    "date": {"$date": "2023-11-25T00:00:00.000Z"},
    "address": {"officeFloor": "2", "officeNumber": "3", "placeNumber": "5"},
}

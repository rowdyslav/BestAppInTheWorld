import telebot
from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from dotenv import load_dotenv
from os import environ
from db_conn import DISHES, ORDERS
from datetime import datetime as dt
from roles import User
from roles import Deliverier

from icecream import ic
from bson import ObjectId

load_dotenv()
TOKEN = environ["TELEGRAM_TOKEN"]

HELP_TEXT = """
*/review <имя блюда> <оценка>* - оставить отзыв о блюде
"""

USER_LOGINS = {}

bot = telebot.TeleBot(TOKEN)

start_rkm = ReplyKeyboardMarkup(resize_keyboard=True)
start_rkm.add(KeyboardButton("/auth"))
start_rkm.add(KeyboardButton("/help"))

deliverier_rkm = ReplyKeyboardMarkup(resize_keyboard=True)
deliverier_rkm.add(KeyboardButton("/orders"))
deliverier_rkm.add(KeyboardButton("/help"))

deliverier_ikm = InlineKeyboardMarkup()



@bot.message_handler(commands=["help", "start"])
def help(message):
    bot.reply_to(message, HELP_TEXT, parse_mode="Markdown", reply_markup=start_rkm)


@bot.message_handler(commands=["review"])
def review(message):
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
        return

    if isinstance(log_result[1], Deliverier):
        keyboard = deliverier_rkm
    else:
        keyboard = start_rkm
    USER_LOGINS[message.from_user.id] = log_result[1]
    bot.send_message(
        message.chat.id,
        f"Вы авторизованы под логином {login}",
        reply_markup=keyboard,
    )


@bot.message_handler(commands=["logout"])
def logout(message):
    bot.send_message(message.chat.id, "Вы вышли из аккаунта")
    USER_LOGINS[message.from_user.id] = None


@bot.message_handler(commands=["orders"])
def orders(message):
    deliverier = USER_LOGINS[message.from_user.id]
    orders = list(ORDERS.find({"deliverier": deliverier.login}))

    msg = []
    for ind, order in enumerate(orders, start=1):
        deliverier_ikm.add(InlineKeyboardButton(text=f'{ind} {order['status']}', callback_data=str(order["_id"])))

        current = [
            f'№ {ind}',
            dt.strftime(order["date"], "%d/%m/%Y"),
            str(orders[ind-1]["cost"]) + "₽",
            orders[ind-1]["status"],
            "/".join([orders[ind-1]["address"][ob] for ob in orders[ind-1]["address"]]),
        ]

        msg.append("- ".join(current))

    bot.send_message(message.chat.id, "\n".join(msg), reply_markup=deliverier_ikm)

@bot.callback_query_handler(func=lambda call: True)
def deliverier_callback_inline(call):
    order = ORDERS.find_one({'_id': ObjectId(call.data)})
    USER_LOGINS[call.from_user.id]._set_order_status(order['_id'], order['status'])
    bot.edit_message_text(call.from_user.id, message_id=call.message.id, text=call.message.text,reply_markup=deliverier_ikm)
bot.infinity_polling()

{
    "status": "Доставляется",
    "cost": 370,
    "date": {"$date": "2023-11-25T00:00:00.000Z"},
    "address": {"officeFloor": "2", "officeNumber": "3", "placeNumber": "5"},
}

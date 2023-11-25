import telebot
from telebot.types import Message
from dotenv import load_dotenv
from os import environ
from db_conn import DISHES, USERS, ORDERS
from roles import User
from datetime import datetime as dt

from icecream import ic

load_dotenv()
TOKEN = environ["TELEGRAM_TOKEN"]

HELP_TEXT = """
*/review <имя блюда> <оценка>* - оставить отзыв о блюде
"""

USER_LOGINS = {}

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["help", "start"])
def help(message):
    bot.reply_to(message, HELP_TEXT, parse_mode="Markdown")


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
        USER_LOGINS[message.from_user.id] = log_result[1]
        bot.send_message(message.chat.id, f"Вы авторизованы под логином {login}")
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

    context = {"deliverier": deliverier, "orders": orders}

    bot.send_message(message.chat.id, str(context))


bot.infinity_polling()

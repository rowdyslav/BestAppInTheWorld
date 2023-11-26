from itsdangerous import exc
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
from roles import User, Worker, Manager, Deliverier
from roles import Deliverier

from icecream import ic
from bson import ObjectId

load_dotenv()
TOKEN = environ["TELEGRAM_TOKEN"]

HELP_TEXTS = {
    Worker: '*/review <имя блюда> <оценка>* - оставить отзыв о блюде',
    Manager: '*/review <имя блюда> <оценка>* - оставить отзыв о блюде',
    Deliverier: '*/orders* - получить список ваших заказов с интерактивным меню'
}



SESSION = {}

bot = telebot.TeleBot(TOKEN)


def get_user_keyboard() -> ReplyKeyboardMarkup:
    start_rkm = ReplyKeyboardMarkup(resize_keyboard=True)
    start_rkm.add(KeyboardButton("/auth"))
    start_rkm.add(KeyboardButton("/help"))
    return start_rkm


def get_deliverier_keyboard() -> ReplyKeyboardMarkup:
    deliverier_rkm = ReplyKeyboardMarkup(resize_keyboard=True)
    deliverier_rkm.add(KeyboardButton("/orders"))
    deliverier_rkm.add(KeyboardButton("/help"))
    return deliverier_rkm


def get_orders_inline(orders: list) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width = 1)
    buttons = []
    for i, order in enumerate(orders):
        buttons.append(InlineKeyboardButton(f'№{i + 1} {order['status']}',callback_data=f'order_{order['_id']}'))
    kb.add(*buttons)
    return kb


@bot.message_handler(commands=["help"])
def help(message):
    bot.reply_to(
        message, HELP_TEXTS.get(type(SESSION[message.from_user.id]), '*/auth* - авторизация'), parse_mode="Markdown", reply_markup=get_user_keyboard()
    )


@bot.message_handler(commands=["auth", "start"])
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
    try:
        login, password = message.text.split()
    except ValueError:
        bot.reply_to(message, "Отправте свой логин и пароль через пробел")
        return
        
    log_result = User(login, password)._login()

    bot.delete_message(message.chat.id, status_message.message_id)

    if not log_result[1]:
        bot.send_message(message.chat.id, log_result[0])
        return

    if isinstance(log_result[1], Deliverier):
        keyboard = get_deliverier_keyboard()
    else:
        keyboard = get_user_keyboard()
    SESSION[message.from_user.id] = log_result[1]
    bot.send_message(
        message.chat.id,
        f"Вы авторизованы под логином {login}",
        reply_markup=keyboard,
    )


@bot.message_handler(commands=["logout"])
def logout(message):
    bot.send_message(message.chat.id, "Вы вышли из аккаунта")
    SESSION[message.from_user.id] = None


@bot.message_handler(commands=["review"])
def review(message):
    args = message.text.split()

    if not type(SESSION[message.from_user.id]) in (Worker, Manager):
        bot.reply_to(message, 'Вашей роли недоступна эта команда!')
        return

    if len(args) < 3:
        bot.reply_to(message, '*/review <имя блюда> <оценка>*', parse_mode="Markdown")
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

    dish_title = " ".join(args[1:-1])
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


@bot.message_handler(commands=["orders"])
def orders(message):
    if not type(SESSION[message.from_user.id]) is Deliverier:
        bot.reply_to(message, 'Вашей роли недоступна эта команда!')
        return

    deliverier = SESSION[message.from_user.id]
    orders = list(ORDERS.find({"deliverier": deliverier.login}))

    msg = []
    for ind, order in enumerate(orders, start=1):
        current = [
            dt.strftime(order["date"], "%d/%m/%Y"),
            str(orders[ind-1]["cost"]) + "₽",
            orders[ind-1]["status"],
            '\nАдрес ' + " | ".join([orders[ind-1]["address"][ob] for ob in orders[ind-1]["address"]]),
        ]

        msg.append(f'№{ind} - ' + " ; ".join(current))

    bot.send_message(message.chat.id, "\n".join(msg), reply_markup=get_orders_inline(orders))

@bot.callback_query_handler(func=lambda call: call.data.startswith('order_'))
def orders_callback_inline(call):
    order = ORDERS.find_one({'_id': ObjectId(call.data.lstrip('order_'))})
    if not order:
        return

    if order['status'] == 'Доставлен':
        return

    status_cycle = ['Готовится', 'Доставляется', 'Доставлен']
    ind = status_cycle.index(order['status']) + 1

    deliverier = SESSION[call.from_user.id]
    deliverier._set_order_status(order['_id'], status_cycle[ind])

    orders = list(ORDERS.find({"deliverier": deliverier.login}))
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=get_orders_inline(orders))



bot.infinity_polling()

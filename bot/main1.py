import asyncio
import os
from datetime import datetime as dt

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from dotenv import load_dotenv
from icecream import ic

from misc.db import DISHES, ORDERS
from misc.roles import Deliverier, Manager, User, Worker

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
HELP_TEXTS = {
    Worker: "*/review <имя блюда> <оценка>* - оставить отзыв о блюде",
    Manager: "*/review <имя блюда> <оценка>* - оставить отзыв о блюде",
    Deliverier: "*/orders* - получить список ваших заказов с интерактивным меню",
}
SESSION = {}
bot = Bot(token=TOKEN)
dp = Dispatcher()


def get_worker_keyboard() -> ReplyKeyboardMarkup:
    start_rkm = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="/auth"), KeyboardButton(text="/help")]],
        resize_keyboard=True,
    )
    return start_rkm


def get_deliverier_keyboard() -> ReplyKeyboardMarkup:
    deliverier_rkm = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="/orders"), KeyboardButton(text="/help")]],
        resize_keyboard=True,
    )
    return deliverier_rkm


def get_orders_inline(orders: list) -> InlineKeyboardMarkup:
    buttons = [[]]
    for i, order in enumerate(orders):
        buttons[0].append(
            InlineKeyboardButton(
                text=f"№{i + 1} {order['status']}",
                callback_data=f"order_{order['_id']}",
            )
        )
    kb = InlineKeyboardMarkup(inline_keyboard=buttons, row_width=1)
    return kb


@dp.message()
async def wait_auth(message: types.Message):
    if not (message.text and message.from_user) or not SESSION.get(
        message.from_user.id
    ):
        return

    try:
        login, password = message.text.split()
    except ValueError:
        await message.answer("Отправте свой логин и пароль через пробел")
        return

    log_result, user = User(login, password)._login()

    match user:
        case Worker():
            keyboard = get_worker_keyboard()
        case Manager():
            keyboard = get_worker_keyboard()
        case Deliverier():
            keyboard = get_deliverier_keyboard()
        case _:
            await message.answer(log_result)
            return

    SESSION[message.from_user.id] = user
    await message.answer(
        f"Вы авторизованы под логином {login}",
        reply_markup=keyboard,
    )


@dp.message(Command("help"))
async def help(message: types.Message):
    await message.answer(
        HELP_TEXTS.get(type(SESSION[message.from_user.id]), "*/auth* - авторизация"),
        parse_mode="Markdown",
        reply_markup=get_worker_keyboard(),
    )


@dp.message(Command("auth"), CommandStart())
async def auth(message: types.Message):
    await message.answer("Отправте свой логин и пароль через пробел")
    SESSION[message.from_user.id] = {}


@dp.message(Command("review"))
async def review(message: types.Message):
    args = message.text.split()

    if not type(SESSION[message.from_user.id]) in (Worker, Manager):
        await message.answer("Вашей роли недоступна эта команда!")
        return

    if len(args) < 3:
        await message.answer("*/review <имя блюда> <оценка>*", parse_mode="Markdown")
        return

    if not args[-1].isnumeric() or not 1 <= int(args[-1]) <= 5:
        await message.answer(
            f"Ожидалось число от 1 до 5, получено *{args[-1]}*",
            parse_mode="Markdown",
        )
        return

    dish_title = " ".join(args[1:-1])
    q = {"title": dish_title}

    dish = DISHES.find_one(q)
    if not dish:
        await message.answer("Блюдо не найдено!")
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

    await message.answer(
        f"Блюду {dish_title} успешно поставлена оценка {args[-1]}!",
    )


@dp.message(Command("orders"))
async def orders(message: types.Message):
    if not type(SESSION[message.from_user.id]) is Deliverier:
        await message.answer("Вашей роли недоступна эта команда!")
        return

    deliverier = SESSION[message.from_user.id]
    orders = list(ORDERS.find({"deliverier": deliverier.login}))

    msg = []
    for ind, order in enumerate(orders, start=1):
        current = [
            dt.strftime(order["date"], "%d/%m/%Y"),
            str(orders[ind - 1]["cost"]) + "₽",
            orders[ind - 1]["status"],
            "\nАдрес "
            + " | ".join(
                [orders[ind - 1]["address"][ob] for ob in orders[ind - 1]["address"]]
            ),
        ]

        msg.append(f"№{ind} - " + " ; ".join(current))

    await message.answer("\n".join(msg), reply_markup=get_orders_inline(orders))


async def start():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start())


# @bot.callback_query_handler(func=lambda call: call.data.startswith('order_'))
# def orders_callback_inline(call):
#     order = ORDERS.find_one({'_id': ObjectId(call.data.lstrip('order_'))})
#     if not order:
#         return

#     if order['status'] == 'Доставлен':
#         return

#     status_cycle = ['Готовится', 'Доставляется', 'Доставлен']
#     ind = status_cycle.index(order['status']) + 1

#     deliverier = SESSION[call.from_user.id]
#     deliverier._set_order_status(order['_id'], status_cycle[ind])

#     orders = list(ORDERS.find({"deliverier": deliverier.login}))
#     bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=get_orders_inline(orders))

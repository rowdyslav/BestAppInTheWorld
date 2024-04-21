import asyncio
import os
from datetime import datetime as dt

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from bson import ObjectId
from dotenv import load_dotenv
from icecream import ic

from misc.db import DISHES, ORDERS
from misc.roles import Deliverier, Manager, User, Worker
import keyboards

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


@dp.message(Command("help"))
async def help(message: types.Message):
    await message.answer(
        HELP_TEXTS.get(type(SESSION[message.from_user.id]), "*/auth* - авторизация"),
        parse_mode="Markdown",
        reply_markup=keyboards.start_rkm,
    )


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
    deliverier_orders = list(ORDERS.find({"deliverier": deliverier.login}))

    msg = []
    template = "*№{} {}*\n{} {}\nАдрес {}"
    for order in deliverier_orders:
        number = deliverier_orders.index(order) + 1
        status = order["status"]
        date = dt.strftime(order["date"], "%d/%m/%Y")
        price = str(order["cost"]) + "₽"
        address = ' | '.join(order["address"].values())
        msg.append(template.format(number, status, date, price, address))

    await message.answer(
        "\n\n".join(msg),
        parse_mode='Markdown',
        reply_markup=keyboards.get_orders_ikm(deliverier_orders)
    )


@dp.callback_query(F.data.startswith('order_'))
async def orders_ikm_callback(call):
    order = ORDERS.find_one({'_id': ObjectId(call.data.lstrip('order_'))})
    if not order:
        return

    if order['status'] == 'Доставлен':
        return

    status_cycle = ['Готовится', 'Доставляется', 'Доставлен']
    ind = status_cycle.index(order['status']) + 1

    deliverier = SESSION[call.from_user.id]
    deliverier.__set_order_status(order['_id'], status_cycle[ind])

    deliverier_orders = list(ORDERS.find({"deliverier": deliverier.login}))
    await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        reply_markup=keyboards.get_orders_ikm(deliverier_orders))


@dp.message()
async def wait_auth(message: types.Message):
    ic(0)
    if not (message.text and message.from_user):
        return
    try:
        login, password = message.text.split()
    except ValueError:
        await message.answer("Отправте свой логин и пароль через пробел")
        return
    log_result, user = User(login, password)._login()
    match user:
        case Worker():
            keyboard = keyboards.worker_rkm
        case Manager():
            keyboard = keyboards.manager_rkm
        case Deliverier():
            keyboard = keyboards.deliverier_rkm
        case _:
            await message.answer(log_result)
            return
    SESSION[message.from_user.id] = user
    await message.answer(
        f"Вы авторизованы под логином {login}",
        reply_markup=keyboard,
    )


@dp.message(Command('start', 'auth'))
async def auth(message: types.Message):
    await message.answer("Отправте свой логин и пароль через пробел")


async def start():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start())

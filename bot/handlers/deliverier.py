from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from datetime import datetime as dt
from bson import ObjectId

from bot.keyboards import user
from bot.keyboards.deliverier import get_orders_ikm

from misc.db import ORDERS, USERS
from misc.roles import Deliverier, User

router = Router()


@router.message(Command("orders"))
async def orders(message: Message):
    user_dict = USERS.find_one({"tg_id": message.from_user.id})
    if not user_dict:
        await message.answer("Для авторизации отправте свой логин и пароль через пробел", reply_markup=user.rkm)

    user_obj: Deliverier = User(user_dict["login"], '')._get()
    if not type(user_obj) is Deliverier:
        await message.answer("Вашей роли недоступна эта команда!")
        return

    deliverier_orders = list(ORDERS.find({"deliverier": user_obj.login}))

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
        reply_markup=get_orders_ikm(deliverier_orders)
    )


@router.callback_query(F.data.startswith('order_'))
async def orders_ikm_callback(call: CallbackQuery, bot: Bot):
    user_obj: Deliverier = User(USERS.find_one({"tg_id": call.from_user.id})["login"], '')._get()

    order = ORDERS.find_one({'_id': ObjectId(call.data.lstrip('order_'))})
    if not order:
        return

    if order['status'] == 'Доставлен':
        return

    status_cycle = ['Готовится', 'Доставляется', 'Доставлен']
    i = status_cycle.index(order['status']) + 1

    user_obj._set_order_status(order['_id'], status_cycle[i])

    user_tg_id = USERS.find_one({"login": order['user_login']}).get('tg_id')
    if user_tg_id:
        await bot.send_message(user_tg_id, f"Ваш заказ {status_cycle[i]}")

    deliverier_orders = list(ORDERS.find({"deliverier": user_obj.login}))
    await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        reply_markup=get_orders_ikm(deliverier_orders))

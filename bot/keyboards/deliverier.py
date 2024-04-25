from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove


router = Router()


@router.message(Command("orders"))
async def orders(message: types.Message):
    user_id = message.from_user.id

    if not SESSION.get(user_id):
        await auth(message)

    if not type(SESSION[user_id]) is Deliverier:
        await message.answer("Вашей роли недоступна эта команда!")
        return

    deliverier = SESSION[user_id]
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


@router.callback_query(F.data.startswith('order_'))
async def orders_ikm_callback(call):
    order = ORDERS.find_one({'_id': ObjectId(call.data.lstrip('order_'))})
    if not order:
        return

    if order['status'] == 'Доставлен':
        return

    status_cycle = ['Готовится', 'Доставляется', 'Доставлен']
    i = status_cycle.index(order['status']) + 1

    deliverier = SESSION[call.from_user.id]
    deliverier.__set_order_status(order['_id'], status_cycle[i])

    user_tg_id = USERS.find_one({"user_login": order['user_login']}).get('tg_id')
    if user_tg_id:
        await bot.send_message(user_tg_id, f"Ваш заказ {status_cycle[i]}")

    deliverier_orders = list(ORDERS.find({"deliverier": deliverier.login}))
    await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        reply_markup=keyboards.get_orders_ikm(deliverier_orders))

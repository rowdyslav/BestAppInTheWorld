from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

rkm = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="/orders"), KeyboardButton(text="/help")]],
    resize_keyboard=True,
)


def get_orders_ikm(orders: list) -> InlineKeyboardMarkup:
    buttons = [[]]
    for i, order in enumerate(orders, start=1):
        if order['status'] != 'Доставлен':
            buttons[0].append(
                InlineKeyboardButton(
                    text=f"№{i} {order['status']}",
                    callback_data=f"order_{order['_id']}",
                )
            )
    ikm = InlineKeyboardMarkup(inline_keyboard=buttons, row_width=1)
    return ikm

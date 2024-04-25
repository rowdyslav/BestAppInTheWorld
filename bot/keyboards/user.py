from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


rkm = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="/auth")]],
    resize_keyboard=True,
)

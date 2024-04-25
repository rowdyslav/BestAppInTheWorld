from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

rkm = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="/review"), KeyboardButton(text="/help")]]
)

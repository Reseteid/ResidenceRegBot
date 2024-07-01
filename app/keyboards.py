from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text = 'Регистрация 🔑'), KeyboardButton(text = 'Войти 🔐')],
    [KeyboardButton(text = 'Помощь❓')]
], 
resize_keyboard=True,
input_field_placeholder='Выберите пункт меню')

skip_email = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Пропустить', callback_data='skip')],
])

choice = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='Yes'), InlineKeyboardButton(text='Нет', callback_data='No')],
])

link_to_profile = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Личный кабинет', url='https://ya.ru')], # Заменить на ссылку на личный кабинет
])

recovery_password = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Восстановить пароль 🔐', callback_data='RecoveryPassword')],
])

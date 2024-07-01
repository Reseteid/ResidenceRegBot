from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from email_validator import validate_email, EmailNotValidError
from passlib.context import CryptContext
from yagmail import SMTP

import app.keyboards as kb
import app.database.requests as rq
from app.email import generate_code_and_send_email
from app.help import help_string

router = Router()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def is_valid_email(email):
    try:
        v = validate_email(email)
        return True
    except EmailNotValidError:
        return False

class Registration(StatesGroup):
    tg_id = State()
    fio = State()
    adress = State()
    login = State()
    email = State()
    skip_email = State()
    password = State()
    confirm_password = State()

class Login(StatesGroup):
    login = State()
    password = State()

class Recovery(StatesGroup):
    recovery_password = State()
    code = State()
    password = State()
    confirm_password = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f'Добро пожаловать, {message.from_user.full_name}! \nЧтобы продолжить, пожалуйста, выберите один из вариантов ниже: \n1️⃣ Регистрация - если вы еще не зарегистрированы и хотите создать новый аккаунт. \n2️⃣ Войти - если у вас уже есть аккаунт и вы хотите войти в свою учетную запись.', reply_markup= kb.main)

@router.message(Command('cancel'))
async def cmd_cancel(message: Message, state: FSMContext):
    await message.answer('Операция прекращена')
    await state.clear()

@router.message(F.text == 'Помощь❓')
async def button_help(message: Message):
    await message.answer(help_string)

@router.message(F.text == 'Войти 🔐')
async def start_login(message: Message, state: FSMContext):
    await state.set_state(Login.login)
    await message.answer("Введите логин вашего аккаунта")

@router.message(F.text == 'Регистрация 🔑')
async def start_registration(message: Message, state: FSMContext):
    await state.set_state(Registration.tg_id)
    await state.update_data(tg_id = message.from_user.id)
    await state.set_state(Registration.fio)
    await message.answer('Введите ваше полное ФИО')

@router.message(Registration.fio)
async def registration_fio(message: Message, state: FSMContext):
    await state.update_data(fio = message.text)
    await state.set_state(Registration.adress)
    await message.answer('Введите ваш адрес проживания')

@router.message(Registration.adress)
async def registration_adress(message: Message, state: FSMContext):
    await state.update_data(adress = message.text)
    await state.set_state(Registration.login)
    await message.answer('Придумайте логин аккаунта, который будет использоваться при авторизации')

@router.message(Registration.login)
async def registration_login(message: Message, state: FSMContext):
    if await rq.check_login(message.text):
        await message.reply('Логин занят, пожалуйста, придумайте новый')
    else:
        await state.update_data(login = message.text)
        await state.set_state(Registration.email)
        await message.answer('Введите адрес электронной почты для возможности восстановления пароля', reply_markup= kb.skip_email)

@router.message(Registration.email)
async def registration_email(message: Message, state: FSMContext):
    if is_valid_email(message.text) == False:
        await message.reply('Некорректный адрес электронной почты, пожалуйста, введите адрес электронной почты еще раз')
    else: 
        if await rq.check_email(message.text):
            await message.reply('Данная почта занята, используйте другую или войдите в свой аккаунт')
        else:
            await state.update_data(email = message.text)
            await state.set_state(Registration.password)
            await message.answer('Придумайте надежный пароль для защиты аккаунта')

@router.message(Registration.skip_email)
async def registration_email(message: Message, state: FSMContext):
    await message.answer('Неизвестная команда, пожалуйтста, выберите один из вариантов ниже', reply_markup= kb.choice)
    await message.answer('Вы уверены, что хотите пропустить этот шаг? \nВвостановление пароля в будущем будет невозможно', reply_markup= kb.choice)

@router.message(Registration.password)
async def registration_password(message: Message, state: FSMContext):
    await state.update_data(password = message.text)
    await state.set_state(Registration.confirm_password)
    await message.answer('Повторите пароль')

@router.message(Registration.confirm_password)
async def registration_сonfirm_password(message: Message, state: FSMContext):
    confirm_hashed_password = pwd_context.hash(message.text)
    data = await state.get_data()
    if data['password']!= message.text:
        await message.answer('Пароли не совпадают, пожалуйтста, введите пароль заново')
        await state.set_state(Registration.password)
    else:
        await state.set_state(Registration.password)
        await state.update_data(password = confirm_hashed_password)
        data = await state.get_data()
        try:
            if (await rq.add_user(data)):
                await message.answer(f'Регистрация прошла успешно 🔓\nВаше имя: {data["fio"]}\nВаш логин: {data["login"]}')
        except Exception as e:
                print(f"Ошибка при добавлении пользователя: {e}")
        await state.clear()

@router.callback_query(F.data == 'skip')
async def get_katalog(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Registration.skip_email)
    await callback.message.edit_text('Вы уверены, что хотите пропустить этот шаг? \nВвостановление пароля в будущем будет невозможно', reply_markup= kb.choice)

@router.callback_query(F.data == "Yes")
async def choice_email_Yes(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Registration.email)
    await state.update_data(email = None)
    await state.set_state(Registration.password)
    await callback.message.edit_text('Придумайте надежный пароль для защиты аккаунта')

@router.callback_query(F.data == "No")
async def choice_email_No(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Registration.email)
    await callback.message.edit_text('Введите адрес электронной почты для возможности восстановления пароля', reply_markup= kb.skip_email)

@router.message(Login.login)
async def Login_login(message: Message, state: FSMContext):
    await state.update_data(login = message.text)
    await state.set_state(Login.password)
    await message.answer('Введите пароль для вашего аккаунта')

@router.message(Login.password)
async def Login_login(message: Message, state: FSMContext):
    await state.update_data(password = message.text)
    data = await state.get_data()
    if await rq.verify_credentials(data):
        await message.answer('Вход выполнен успешно', reply_markup= kb.link_to_profile)
    else:
        await message.answer('Не существует введенной пары логин-пароль, пожалуйста, попробуйте еще раз или восстановите пароль', reply_markup= kb.recovery_password)
    await state.clear()

@router.callback_query(F.data == 'RecoveryPassword')
async def recovery_pass(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Recovery.recovery_password)
    await callback.message.edit_text('Введите адрес электронной почты, который вы использовали при регистрации')

@router.message(Recovery.recovery_password)
async def Login_recovery_pass(message: Message, state: FSMContext):
    if await rq.email_exists(message.text):
        await state.update_data(recovery_password = message.text)
        code = generate_code_and_send_email(message.text)
        await state.set_state(Recovery.code)
        await state.update_data(code = code)
        await message.answer('Код успешно отправлен на вашу почту, пожалуйста, введите его')
    else:
        await message.answer('Извините, но аккаунта с такой почтой не существует')
        await state.clear()

@router.message(Recovery.code)
async def Login_recovery_pass(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text == data["code"]:
        await state.set_state(Recovery.password)
        await message.answer('Введен верный код, пожалуйста, введите новый пароль')
    else:
        await message.answer('Введен неверный код')
        await state.clear()

@router.message(Recovery.password)
async def recovery_new_pass(message: Message, state: FSMContext):
    await state.update_data(password = message.text)
    await state.set_state(Recovery.confirm_password)
    await message.answer('Повторите пароль')

@router.message(Recovery.confirm_password)
async def recovery_сonfirm_password(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text != data["password"]:
        await message.answer('Пароли не совпадают, пожалуйтста, введите пароль заново')
        await state.set_state(Registration.password)
    else:
        hashed_password = pwd_context.hash(message.text)
        await state.update_data(password = hashed_password)
        data = await state.get_data()
        try:
            if (await rq.update_user_password_by_email(data)):
                await message.answer("Ваш пароль был успешно изменен")
        except Exception as e:
                print(f"Ошибка при изменении пароля: {e}")
        await state.clear()
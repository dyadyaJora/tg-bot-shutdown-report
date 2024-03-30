from os import getenv

import dotenv
from aiogram import types
from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder


dotenv.load_dotenv()
WEB_APP_URL = getenv("WEB_APP_URL")


def get_report_callback_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Сервис заработал",
        callback_data="report_available")
    )
    return builder.as_markup()


def get_report_unavailable_again_callback_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Сервис снова недоступен",
        callback_data="report_unavailable_again")
    )
    return builder.as_markup()


def get_report_confirm_unavailable_callback_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="🟢 Да",
        callback_data="report_unavailable_confirm")
    )
    builder.add(types.InlineKeyboardButton(
        text="🔴 Нет",
        callback_data="report_unavailable_decline")
    )
    return builder.as_markup()


def get_report_confirm_callback_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="🟢 Да",
        callback_data="report_available_confirm")
    )
    builder.add(types.InlineKeyboardButton(
        text="🔴 Нет",
        callback_data="report_available_decline")
    )
    return builder.as_markup()


def get_web_app_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Создать отчет о сбое",
        web_app=WebAppInfo(url=WEB_APP_URL))
    )
    return builder


def get_default_keyboard():
    kb = [
        [
            types.KeyboardButton(text="📌 Отправить отчет", web_app=WebAppInfo(url=WEB_APP_URL))
        ],
        [
            types.KeyboardButton(text="💬 Связаться с оператором")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите способ подачи"
    )
    return keyboard

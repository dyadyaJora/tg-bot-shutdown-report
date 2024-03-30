import asyncio
import json
from datetime import datetime

import yaml
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from src.adapter import GoogleSheetStorageAdapter
import dotenv

from src.keyboards import get_default_keyboard, get_report_callback_keyboard, get_report_confirm_callback_keyboard, \
    get_report_unavailable_again_callback_keyboard, get_report_confirm_unavailable_callback_keyboard
from src.models import Report
from src.utils import parse_yaml_data_from_report_message

dotenv.load_dotenv()

TOKEN = getenv("BOT_TOKEN")
SPREADSHEET_ID = getenv('SPREADSHEET_ID')
RANGE_NAME = getenv('RANGE_NAME')

dp = Dispatcher()
storage_adapter = GoogleSheetStorageAdapter(SPREADSHEET_ID, RANGE_NAME)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    keyboard = get_default_keyboard()
    await message.answer(f"Добро пожаловать!", reply_markup=keyboard)


@dp.callback_query(F.data == "random_value")
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.answer("Callback успешно вызван")
    await callback.answer()

REPORT_TEXT_PREFIX = "Получен репорт\n====\n<pre language=\"yaml\">\n"
REPORT_TEXT_SUFFIX = "</pre>\n===="


@dp.message(F.web_app_data)
async def enter_date(message: Message) -> None:
    report = Report.from_json(message.web_app_data.data)
    print(vars(report))
    report.status = 'DOWN'
    report.time = datetime.utcnow().isoformat() + "Z"
    storage_adapter.insert(report)
    await message.answer(
        REPORT_TEXT_PREFIX + yaml.dump(vars(report), allow_unicode=True) + REPORT_TEXT_SUFFIX,
        reply_markup=get_report_callback_keyboard(),
        parse_mode=ParseMode.HTML
    )


CONFIRMATION_TEXT = "\nВы подтверждаете, что сервис из этого репорта теперь доступен?"


@dp.callback_query(F.data == "report_available")
async def answer_report_available(callback: types.CallbackQuery):
    new_text = callback.message.html_text + CONFIRMATION_TEXT
    await callback.message.edit_text(
        new_text,
        reply_markup=get_report_confirm_callback_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


@dp.callback_query(F.data == "report_available_confirm")
async def answer_report_available_confirm(callback: types.CallbackQuery):
    await handle_report_confirm(callback, 'UP')


@dp.callback_query(F.data == "report_available_decline")
async def answer_report_available_decline(callback: types.CallbackQuery):
    await handle_report_decline(callback, CONFIRMATION_TEXT)

CONFIRMATION_AGAIN_TEXT = "\nВы подтверждаете, что сервис снова недоступен?"


@dp.callback_query(F.data == "report_unavailable_again")
async def answer_report_unavailable_again(callback: types.CallbackQuery):
    new_text = callback.message.html_text + CONFIRMATION_AGAIN_TEXT
    await callback.message.edit_text(
        new_text,
        reply_markup=get_report_confirm_unavailable_callback_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


@dp.callback_query(F.data == "report_unavailable_confirm")
async def answer_report_unavailable_confirm(callback: types.CallbackQuery):
    await handle_report_confirm(callback, 'DOWN')


@dp.callback_query(F.data == "report_unavailable_decline")
async def answer_report_unavailable_decline(callback: types.CallbackQuery):
    await handle_report_decline(callback, CONFIRMATION_AGAIN_TEXT)


@dp.message()
async def echo_handler(message: types.Message) -> None:
    keyboard = get_default_keyboard()
    try:
        await message.answer("test message: Обработчик события не найден", keyboard=keyboard)
    except TypeError:
        await message.answer("Что-то пошло не так!")


def update_report_data(text, status):
    data = parse_yaml_data_from_report_message(text)
    data['status'] = status
    data['time'] = datetime.utcnow().isoformat() + "Z"
    return data


async def handle_report_confirm(callback: types.CallbackQuery, status):
    text = callback.message.text
    data = update_report_data(text, status)
    report = Report(**data)
    storage_adapter.insert(report)
    new_text = REPORT_TEXT_PREFIX + yaml.dump(data, allow_unicode=True) + REPORT_TEXT_SUFFIX
    await callback.message.edit_text(
        new_text,
        reply_markup=get_report_unavailable_again_callback_keyboard() if status == 'UP' else get_report_callback_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await callback.answer(
        text="Вы подтвердили доступность сервиса. Спасибо!" if status == 'UP' else "Вы подтвердили что сервис недоступен. Спасибо!",
        show_alert=True
    )


async def handle_report_decline(callback: types.CallbackQuery, confirmation_text):
    text = callback.message.html_text
    new_text = text[:len(text)-len(confirmation_text)]
    await callback.message.edit_text(
        new_text,
        reply_markup=get_report_callback_keyboard() if confirmation_text == CONFIRMATION_TEXT else get_report_unavailable_again_callback_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await callback.answer(
        text="Репорт отменен" if confirmation_text == CONFIRMATION_TEXT else "Репорт о недоступности отменен",
        show_alert=True
    )


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    asyncio.run(main())

import re
from aiogram import types, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from tgbot.database import add_link
from tgbot.keyboards import category, priority
from tgbot.states.states import LinkStates
from data import config

URL_REGEX = r'(https?://\S+?)(?=[.,!?;:]?\s|$)'


main_router = Router()
LOG_CHANNEL_ID = config.CHANNEL_ID

@main_router.message(Command("start"))
async def start_command_handler(message: types.Message, state: FSMContext):
    await state.clear()

    # await message.delete_reply_markup()
    await message.answer(f"Привет, {message.from_user.full_name}! Отправьте текст с ссылкой, чтобы начать.")


@main_router.message(Command("help"))
async def help_command_handler(message: types.Message):
    await message.answer("Этот бот сохраняет ссылки. Отправьте сообщение с ссылками для начала.")


@main_router.message(StateFilter(None))
async def handle_message_with_links(message: types.Message, state: FSMContext):
    await message.answer('пытаюсь обработать ссылку')
    links = re.findall(URL_REGEX, message.text)
    if links:
        await state.update_data(links=links)
        await message.answer("Выберите категорию для ссылки:", reply_markup=category)
        await state.set_state(LinkStates.waiting_for_category)

    else:
        await message.answer("Ссылок не найдено. Отправьте текст с ссылкой.")


@main_router.message(LinkStates.waiting_for_category, F.text.in_(["Работа 🧠", "Путешествия ✈️", "Финансы 💰", "Другое ⚙️"]))
async def handle_category_selection(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer("Выберите приоритет:", reply_markup=priority)
    await state.set_state(LinkStates.waiting_for_priority)


@main_router.message(LinkStates.waiting_for_priority, F.text.in_(["Высокий ⬆️", "Средний ↔️", "Низкий ⬇️"]))
async def handle_priority_selection(message: types.Message, state: FSMContext):
    await state.update_data(priority=message.text)
    await message.answer("Введите источник (например, сайт или приложение):",
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(LinkStates.waiting_for_source)


@main_router.message(LinkStates.waiting_for_source)
async def handle_source_input(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = message.from_user.id

    user_data["source"] = message.text
    for link in user_data["links"]:
        # url: str, title: str, category: str, priority: int, source: str,
        add_link(url=link,
                 title="Unknown",
                 category=user_data["category"],
                 priority=user_data["priority"],
                 source=user_data["source"],
                 telegram_user_id=user_id,
                 )
        # Логируем в канал
        log_message = (f"Новая ссылка добавлена:\n"
                       f"URL: {link}\n"
                       f"Категория: {user_data['category']}\n"
                       f"Приоритет: {user_data['priority']}\n"
                       f"Источник: {user_data['source']}\n"
                       f"Telegram User ID: {user_id}")
        await message.bot.send_message(LOG_CHANNEL_ID, log_message)

    # Сообщаем об успешном сохранении
    await message.answer("Ссылка сохранена в базе данных.")
    await state.clear()  # Сбрасываем состояние после завершения обработки

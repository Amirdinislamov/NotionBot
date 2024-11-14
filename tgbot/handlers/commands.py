import re
from aiogram import types, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from tgbot.database.localdb import add_link
from tgbot.database.integration_notiondb import add_link_to_notion
from tgbot.keyboards import category, priority
from tgbot.states.states import LinkStates
import requests
from bs4 import BeautifulSoup
import urllib.parse
from tgbot.database.users import save_user_token, get_user_token
from data import config


URL_REGEX = r'(https?://\S+?)(?=[.,!?;:]?\s|$)'


main_router = Router()
LOG_CHANNEL_ID = config.CHANNEL_ID

def fetch_title(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string if soup.title else "Unknown"
        return title
    except requests.RequestException:
        return "Unknown"

def determine_source(message: types.Message):
    if message.forward_from:
        source = message.forward_from.username if message.forward_from.username else str(message.forward_from.id)
    elif message.forward_from_chat:
        source = message.forward_from_chat.title or message.forward_from_chat.username
    else:
        source = "Unknown"
    return source

def determine_social_media_source(url):
    parsed_url = urllib.parse.urlparse(url)
    domain = parsed_url.netloc
    if "instagram" in domain:
        return "Instagram"
    elif "twitter" in domain:
        return "Twitter"
    elif "youtube" in domain:
        return "YouTube"
    else:
        return "Unknown"

@main_router.message(Command("start"))
async def start_command_handler(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    notion_token, notion_database_id = get_user_token(user_id)

    if not notion_token or not notion_database_id:
        await message.answer("Отправьте ваш Notion токен:")
        await state.set_state(LinkStates.waiting_for_notion_token)
    else:
        await message.answer("Привет! Отправьте текст с ссылкой, чтобы начать.")

@main_router.message(LinkStates.waiting_for_notion_token)
async def handle_notion_token(message: types.Message, state: FSMContext):
    await state.update_data(notion_token=message.text)
    await message.answer("Теперь отправьте ваш Notion ID базы данных:")
    await state.set_state(LinkStates.waiting_for_notion_database_id)

@main_router.message(LinkStates.waiting_for_notion_database_id)
async def handle_notion_database_id(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = message.from_user.id
    notion_token = user_data["notion_token"]
    notion_database_id = message.text
    save_user_token(user_id, notion_token, notion_database_id)
    await message.answer("Настройки сохранены! Теперь отправьте текст с ссылкой для добавления.")
    await state.clear()

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
    notion_token, notion_database_id = get_user_token(user_id)
    for link in user_data["links"]:
        user_data["source"] = f"Переслали от: {determine_source(message)}. Социальная сеть: {determine_social_media_source(link)}. Ресурс: {message.text}"
        title = fetch_title(link)
        add_link(url=link,
                 title=title,
                 category=user_data["category"],
                 priority=user_data["priority"],
                 source=user_data["source"],
                 telegram_user_id=user_id,
                 )
        add_link_to_notion(url=link,
                 title=title,
                 category=user_data["category"],
                 priority=user_data["priority"],
                 source=user_data["source"],
                 telegram_user_id=user_id,
                 notion_token = notion_token,
                 notion_database_id = notion_database_id
                 )

        log_message = (f"Новая ссылка добавлена:\n"
                       f"URL: {link}\n"
                       f"Заголовок: {title}\n"
                       f"Категория: {user_data['category']}\n"
                       f"Приоритет: {user_data['priority']}\n"
                       f"Источник: {user_data['source']}\n"
                       f"Telegram User ID: {user_id}")
        await message.bot.send_message(LOG_CHANNEL_ID, log_message)


    await message.answer("Ссылка(и) сохранена(ы) в базе данных.")
    await state.clear()
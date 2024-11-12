from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

category = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Работа 🧠'), KeyboardButton(text='Путешествия ✈️')],
    [KeyboardButton(text='Финансы 💰'), KeyboardButton(text='Другое ⚙️')]
], resize_keyboard=True, input_field_placeholder="Выберите нужную категорию")

priority = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Высокий ⬆️')],
    [KeyboardButton(text='Средний ↔️')],
    [KeyboardButton(text='Низкий ⬇️')]
], resize_keyboard=True, input_field_placeholder="Выберите нужный приоритет")

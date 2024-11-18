from aiogram.fsm.state import StatesGroup, State

class LinkStates(StatesGroup):
    waiting_for_category = State()
    waiting_for_priority = State()
    waiting_for_source = State()
    waiting_for_notion_token = State()
    waiting_for_notion_database_id = State()
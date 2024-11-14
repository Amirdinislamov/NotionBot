from notion_client import Client
from tgbot.data import config

notion = Client(auth=config.NOTION_TOKEN)
database_id = config.NOTION_DATABASE_ID

def add_link_to_notion(url, title, category, priority, source, telegram_user_id):
    try:
        response = notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "Title": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                },
                "URL": {
                    "url": url
                },
                "Category": {
                    "select": {
                        "name": category
                    }
                },
                "Priority": {
                    "select": {
                        "name": priority
                    }
                },
                "Source": {
                    "rich_text": [
                        {
                            "text": {
                                "content": source
                            }
                        }
                    ]
                },
                "User ID": {
                    "number": telegram_user_id
                }
            }
        )
        print("Запись добавлена в Notion:", response)
    except Exception as e:
        print("Ошибка при добавлении записи в Notion:", e)
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# Создание движка и базы
engine = create_engine('sqlite:///users.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_user_id = Column(Integer, unique=True, nullable=False)
    notion_token = Column(String, nullable=False)
    notion_database_id = Column(String, nullable=False)

# Создаем таблицы
Base.metadata.create_all(engine)

# Функция для сохранения токенов
def save_user_token(telegram_user_id, notion_token, notion_database_id):
    session = Session()
    user = session.query(User).filter(User.telegram_user_id == telegram_user_id).first()
    if user:
        user.notion_token = notion_token
        user.notion_database_id = notion_database_id
    else:
        user = User(
            telegram_user_id=telegram_user_id,
            notion_token=notion_token,
            notion_database_id=notion_database_id
        )
        session.add(user)
    session.commit()
    session.close()

# Функция для получения токенов
def get_user_token(telegram_user_id):
    session = Session()
    user = session.query(User).filter(User.telegram_user_id == telegram_user_id).first()
    session.close()
    return (user.notion_token, user.notion_database_id) if user else (None, None)

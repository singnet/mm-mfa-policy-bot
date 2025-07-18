from abc import abstractmethod
from dataclasses import dataclass
from sqlite3 import connect
import logging

from settings import BotSettings


logger = logging.getLogger(__name__)


@dataclass
class UserModel:
    user_id: str
    username: str
    mfa_active: int
    days_left: int
    last_check_datetime: str


class UserRepo:
    def __init__(self):
        self.create_tables()

    @abstractmethod
    def create_tables(self):
        pass

    @abstractmethod
    def get_users(self, only_without_mfa):
        pass

    @abstractmethod
    def upsert_user(self, user_id, username, mfa_active, last_check_datetime):
        pass

    @abstractmethod
    def delete_inactive_users(self, active_users_ids):
        pass

    @abstractmethod
    def reset_days_left(self):
        pass


class SqliteUserRepo(UserRepo):
    def __init__(self):
        self.db_path = BotSettings.DB_PATH
        logger.setLevel(logging.DEBUG if BotSettings.DEBUG else logging.INFO)
        super().__init__()

    def create_tables(self):
        with connect(self.db_path) as db:
            cursor = db.cursor()
            cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY, 
            username TEXT NOT NULL, 
            mfa_active INTEGER NOT NULL DEFAULT 0,
            days_left INTEGER NOT NULL DEFAULT {BotSettings.DAYS_ALLOWED},
            last_check_datetime TEXT
            )''')
            db.commit()

    def get_users(
            self,
            only_without_mfa: bool = False
    ) -> list[UserModel]:
        with connect(self.db_path) as db:
            cursor = db.cursor()
            query = 'SELECT * FROM users'
            if only_without_mfa:
                query += ' WHERE mfa_active = 0'
            cursor.execute(query)
            users = cursor.fetchall()
        user_models = []
        for user in users:
            user_models.append(UserModel(
                user_id = user[0],
                username = user[1],
                mfa_active = user[2],
                days_left = user[3],
                last_check_datetime = user[4]
            ))
        return user_models

    def upsert_user(
            self,
            user_id: str,
            username: str,
            mfa_active: int,
            last_check_datetime: str
    ) -> None:
        with connect(self.db_path) as db:
            cursor = db.cursor()
            query = '''
            INSERT INTO users
            (user_id, username, mfa_active, last_check_datetime)
            VALUES (?, ?, ?, ?)
            ON CONFLICT (user_id)
            DO UPDATE SET 
            mfa_active = EXCLUDED.mfa_active,
            days_left = CASE 
                           WHEN mfa_active = 0 AND days_left > 0 
                           THEN days_left - 1 
                           ELSE days_left 
                        END,
            last_check_datetime = EXCLUDED.last_check_datetime;
            '''
            cursor.execute(query, (
                user_id,
                username,
                mfa_active,
                last_check_datetime
            ))
            db.commit()

    def delete_inactive_users(
            self,
            active_users_ids: list[str]
    ) -> None:
        placeholders = ', '.join(['?'] * len(active_users_ids))
        with connect(self.db_path) as db:
            cursor = db.cursor()
            query = f'''
            DELETE FROM users
            WHERE user_id NOT IN ({placeholders})
            '''
            cursor.execute(query, active_users_ids)
            db.commit()

    def reset_days_left(self) -> None:
        with connect(self.db_path) as db:
            cursor = db.cursor()
            cursor.execute(f'''
            UPDATE users
            SET days_left = {BotSettings.DAYS_ALLOWED}
            ''')
            db.commit()

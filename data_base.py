# Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
# Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
# ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
# В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
# ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
# Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
# Или в файле COPYING.txt в репозитории или архиве
# Copyleft 🄯 NEO Organization, Departament K 2026
# Coded by AnonimNEO (GitHub)

# Работа с базой данных
import sqlite3
import datetime
import json
import os
# Логирование
from loguru import logger

# Импорт конфигурации
from config import DATABASE_FILE, DEBUG_MODE
# Локализация
from languages import l

def init_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Существующая таблица users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            entry_date TEXT,
            violations INTEGER DEFAULT 0,
            reputation_user INTEGER DEFAULT 0,
            reputation_moderator INTEGER DEFAULT 0,
            message_count INTEGER DEFAULT 0,
            delete_message_count INTEGER DEFAULT 0,
            edited_message_count INTEGER DEFAULT 0,
            is_banned INTEGER DEFAULT 0
        )
    """)

    # Новая таблица для отслеживания IP и банов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS violators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ip TEXT NOT NULL,
            ban_time TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Таблица связей IP и ID (для быстрого поиска)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ip_user_mapping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ip TEXT NOT NULL,
            first_seen TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, ip)
        )
    """)

    conn.commit()
    conn.close()



def add_reputation(user_id, points, by_moderator=False):
    """Добавляем репутацию"""
    uid = str(user_id)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    if by_moderator:
        cursor.execute("SELECT reputation_moderator FROM users WHERE user_id = ?", (uid,))
        row = cursor.fetchone()
        if row:
            new_rep = row[0] + points
            cursor.execute("UPDATE users SET reputation_moderator = ? WHERE user_id = ?", (new_rep, uid))
    else:
        cursor.execute("SELECT reputation_user FROM users WHERE user_id = ?", (uid,))
        row = cursor.fetchone()
        if row:
            new_rep = row[0] + points
            cursor.execute("UPDATE users SET reputation_user = ? WHERE user_id = ?", (new_rep, uid))

    conn.commit()
    conn.close()



def subtract_reputation(user_id, points, by_moderator=False):
    """Уменьшаем репутацию"""
    uid = str(user_id)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    if by_moderator:
        cursor.execute("SELECT reputation_moderator FROM users WHERE user_id = ?", (uid,))
        row = cursor.fetchone()
        if row:
            new_rep = max(0, row[0] - points)
            cursor.execute("UPDATE users SET reputation_moderator = ? WHERE user_id = ?", (new_rep, uid))
    else:
        cursor.execute("SELECT reputation_user FROM users WHERE user_id = ?", (uid,))
        row = cursor.fetchone()
        if row:
            new_rep = max(0, row[0] - points)
            cursor.execute("UPDATE users SET reputation_user = ? WHERE user_id = ?", (new_rep, uid))

    conn.commit()
    conn.close()



def remove_mutation(user_id):
    """Удаляем мут"""
    uid = str(user_id)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    now = datetime.datetime.now().isoformat()

    cursor.execute("DELETE FROM mutations WHERE user_id = ? AND until <= ?", (uid, now))

    conn.commit()
    conn.close()



def data_operation(uid, user_id, sql):
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(
            sql,
            (uid,)
        )
        conn.commit()
        conn.close()
    except:
        logger.exception(f"Ошибка базы данных для пользователя {user_id} при команде:\n{sql}")



# Загрузка списка из файла
def load_list_from_file(filepath):
    """Загружаем лист из файла"""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []



# Загрузка списка замены
def load_replacements(filepath):
    """Загружаем список замены символов из файла и возвращаем кортеж кортежей.

    Формат файла:
        "@": "а"
        "0": "о"
        "3": "з"

    Возвращает:
        (("@", "а"), ("0", "о"), ("3", "з"), ..."""
    replacements: list[tuple[str, str]] = []

    if not os.path.exists(filepath):
        return ()

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or ":" not in line:
                    continue

                # Парсим формат: "@": "а"
                parts = line.split('": "', 1)
                if len(parts) != 2:
                    continue

                key = parts[0].lstrip('"').strip()
                val = parts[1].rstrip('"').strip()

                if key:
                    replacements.append((key, val))

    except Exception as e:
        logger.exception(f"Ошибка загрузки замены символов")

    return tuple(replacements)



# Загрузка json файлов
def load_json(filepath):
    """Загружаем json файл"""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}



# Обновление данных в json файлы
def save_json(data, filepath):
    """Сохраняем json файл"""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        if DEBUG_MODE:
            logger.debug(f"Данные сохранены в {filepath}")
    except:
        logger.exception(f"Ошибка сохранения {filepath}")



def ban_user(user_id, ip_address):
    """Добавляем пользователя в чёрный список и связываем с IP"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    try:
        # Добавляем запись о нарушении
        ban_time = datetime.datetime.now().isoformat()
        cursor.execute("""INSERT INTO violators (user_id, ip, ban_time)
            VALUES (?, ?, ?)""", (user_id, ip_address, ban_time))

        # Связываем IP с пользователем
        cursor.execute("""INSERT OR IGNORE INTO ip_user_mapping (user_id, ip)
            VALUES (?, ?)""", (user_id, ip_address))

        # Помечаем пользователя как забанённого в основной таблице
        cursor.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))

        conn.commit()
        logger.info(f'{l("user")} {user_id} {l("banned")} (IP: {ip_address})')
        return True
    except:
        logger.exception(f"{l("ban_error")} {user_id}")
    finally:
        conn.close()
    return False



def is_user_or_ip_banned(user_id, ip_address=None):
    """Проверяем забанен ли пользователь по ID или IP"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    try:
        # Проверка по ID пользователя
        cursor.execute("SELECT user_id, ban_time FROM violators WHERE user_id = ?", (user_id,))

        ban_record = cursor.fetchone()
        if ban_record:
            return True

        # Проверка по IP (если IP предоставлен)
        if ip_address:
            cursor.execute("SELECT DISTINCT user_id FROM violators WHERE ip = ?", (ip_address,))

            banned_users = cursor.fetchall()
            if banned_users:
                return True

        return False

    finally:
        conn.close()



def get_all_ips_for_user(user_id):
    """Получаем все IP, когда-либо использованные пользователем"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT DISTINCT ip FROM ip_user_mapping WHERE user_id = ?", (user_id,))

        return [row[0] for row in cursor.fetchall()]

    finally:
        conn.close()



def get_all_users_for_ip(ip_address):
    """Получаем всех пользователей, использовавших данный IP"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT DISTINCT user_id FROM ip_user_mapping WHERE ip = ?", (ip_address,))

        return [row[0] for row in cursor.fetchall()]

    finally:
        conn.close()



def unban_user(user_id=None, ip_address=None):
    """Удаляем информацию о бане пользователя или всех пользователей на IP.
    Args:
        user_id (int): ID пользователя для разблокировки
        ip_address (str): IP адрес для разблокировки"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    try:
        # Разблокировать конкретного пользователя по ID
        if user_id:
            cursor.execute("SELECT id FROM violators WHERE user_id = ?", (int(user_id),))
            if cursor.fetchone():
                cursor.execute("DELETE FROM violators WHERE user_id = ?", (int(user_id),))
                cursor.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (int(user_id),))
                conn.commit()
                logger.info(f'{l("user")} {user_id} {l("unbanned")}.')
                return True
            else:
                return False

        # Разблокировать всех пользователей на одном IP
        elif ip_address:
            cursor.execute("SELECT DISTINCT user_id FROM ip_user_mapping WHERE ip = ?", (ip_address,))
            users_on_ip = cursor.fetchall()

            if not users_on_ip:
                return False

            # Удаляем из violators всех пользователей на этом IP
            for (uid,) in users_on_ip:
                cursor.execute("DELETE FROM violators WHERE user_id = ?", (uid,))
                cursor.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (uid,))

            unbanned_count = len(users_on_ip)
            conn.commit()

            user_ids = [str(uid) for uid, in users_on_ip]

            logger.info(f"{l("unlock_al")} {unbanned_count} {l("users_on")} IP {ip_address}\nID: {", ".join(user_ids)}")
            return True
        else:
            return False
    except:
        conn.rollback()
        logger.exception(l("unbanned_error"))
        return False
    finally:
        conn.close()

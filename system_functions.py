# Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
# Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
# ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
# В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
# ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
# Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
# Или в файле COPYING.txt в репозитории или архиве
# Copyleft 🄯 NEO Organization, Departament K 2026
# Coded by AnonimNEO (GitHub)

# Telegram API
from telebot import types
# Логирование
from loguru import logger
# База данных
import sqlite3
# Дата и время
import datetime
import time
import requests
import asyncio
# Импорт конфигурации
from config import DEBUG_MODE, MODERATORS_FILE, DATABASE_FILE, ENABLE_CHECK_IP, ADMIN_TYPE, ADMIN_NAME, BOT_ID, BOT_TYPE, BOT_NAME, ADMIN_ID
# Импорт констант репутации
from config import VIOLATION_POINTS_MULTIPLIER, REP_USER_DIVISOR, REP_MODERATOR_DIVISOR, MAX_VIOLATIONS, MINUS_MODERATOR_REP_WHEN_MUTING, COUNT_MINUS_MODERATOR_REP
# Импорт базы данных
from data_base import load_list_from_file, is_user_or_ip_banned

MODERATORS_IDS = load_list_from_file(MODERATORS_FILE)

# Данные о спаме пользователей
user_message_times = {}

def get_user_data(user_id):
    """Получаем данные о пользователе из SQLite"""
    uid = str(user_id)
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (uid,))
    row = cursor.fetchone()

    if not row:
        cursor.execute("""
            INSERT INTO users (user_id, entry_date, violations, reputation_user, reputation_moderator, message_count, delete_message_count)
            VALUES (?, ?, 0, 0, 0, 0, 0)
        """, (uid, "Н/Д"))
        conn.commit()

        cursor.execute("SELECT * FROM users WHERE user_id = ?", (uid,))
        row = cursor.fetchone()

    cursor.execute("SELECT date, until FROM mutations WHERE user_id = ?", (uid,))
    mutations = [{"date": m[0], "until": m[1]} for m in cursor.fetchall()]
    conn.close()

    return {
        "user_id": row["user_id"],
        "entry_date": row["entry_date"],
        "violations": row["violations"],
        "reputation": {
            "user": row["reputation_user"],
            "moderator": row["reputation_moderator"]
        },
        "message_count": row["message_count"],
        "delete_message_count": row["delete_message_count"],
        "mutations": mutations
    }



def extract_target_user_id(bot, message, args=None):
    """Извлекает ID целевого пользователя из:
    1. Reply (ответ на сообщение)
    2. Числового аргумента (user_id)
    3. @username (через get_chat)
    4. Текущего пользователя (если ничего не передано)"""

    # Если это reply, берём ID из него
    if message.reply_to_message:
        return int(message.reply_to_message.from_user.id)

    # Если есть аргумент, пытаемся получить ID из него
    if args and len(args) >= 2:
        arg = args[1].strip()

        try:
            # Пробуем преобразовать в число (если это просто ID)
            target_user_id = int(arg)
            return target_user_id
        except ValueError:
            # Если это не число, то возможно @username
            try:
                chat = bot.get_chat(arg)
                return int(chat.id)
            except:
                if DEBUG_MODE:
                    logger.exception(f"Не удалось найти пользователя {arg}")
                # Возвращаем текущего пользователя как fallback
                return int(message.from_user.id)

    # Если ничего нет, берём ID текущего пользователя
    return int(message.from_user.id)



# Проверяем является ли пользователь модератором
async def is_moderator(bot, user_id):
    try:
        chat = await bot.get_chat(user_id)
        username = chat.username
    except:
        username = None

    if str(user_id) == MODERATORS_IDS[0] or username == "GroupAnonymousBot":
        return True
    return str(user_id) in MODERATORS_IDS



# Проверка на мут
async def is_user_muted(bot, user_id):
    if await is_moderator(bot, user_id):
        return False

    user_data = get_user_data(user_id)
    now = datetime.datetime.now()

    for mut in user_data["mutations"]:
        until = datetime.datetime.fromisoformat(mut["until"])
        if until > now:
            return True

    return False



# Обновляем количество сообщений за минуту
def add_timestamps(user_id):
    user_id_str = str(user_id)
    now = time.time()

    if user_id_str not in user_message_times:
        user_message_times[user_id_str] = []

    # Добавляем новый timestamp
    user_message_times[user_id_str].append(now)

    # Удаляем сообщения старше 60 секунд
    user_message_times[user_id_str] = [
        ts for ts in user_message_times[user_id_str]
        if now - ts < 60
    ]

    # Удаляем пустые записи из словаря
    if not user_message_times[user_id_str]:
        del user_message_times[user_id_str]



# Добавляем нарушение
def add_violation(user_id, count=1):
    """Добавить нарушение пользователю"""
    uid = str(user_id)
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET violations = violations + ? WHERE user_id = ?",
            (count, uid)
        )
        conn.commit()
        conn.close()
    except:
        logger.exception(f"Ошибка добавления нарушения для {user_id}")



# Получаем очки нарушений
def get_total_points(user_id):
    user_data = get_user_data(user_id)
    violation_points = user_data["violations"]
    rep_user_points = user_data["reputation"]["user"]
    rep_mod_points = user_data["reputation"]["moderator"]

    total = (int(violation_points) * VIOLATION_POINTS_MULTIPLIER -
             (int(rep_user_points) // REP_USER_DIVISOR) -
             (int(rep_mod_points) // REP_MODERATOR_DIVISOR))
    return total



async def data(bot, message):
    user_id = message.from_user.id

    # Комплексная проверка бана
    if ENABLE_CHECK_IP:
        ip = await get_ip_address(user_id)
        is_banned = is_user_or_ip_banned(user_id, ip)
    else:
        is_banned = is_user_or_ip_banned(user_id)

    if is_banned:
        return

    args = message.text.split()

    # Если это приватный чат
    if message.chat.type == "private":
        # Проверяем, является ли пользователь модератором
        if not await is_moderator(bot, user_id):
            return

        # Используем extract_target_user_id для приватного чата
        target_user_id = extract_target_user_id(bot, message, args)

    else:
        # В групповом чате обычная логика
        target_user_id = extract_target_user_id(bot, message, args)

    if target_user_id is None:
        await bot.reply_to(message, "❌ Ошибка: не удалось определить пользователя.")
        return

    # Получаем данные из новой БД
    uid = str(target_user_id)
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(
            """SELECT entry_date, violations, reputation_user, reputation_moderator, 
                      message_count, delete_message_count, edited_message_count, is_banned 
               FROM users WHERE user_id = ?""",
            (uid,)
        )
        row = cursor.fetchone()
        conn.close()

        if row is None:
            await bot.reply_to(message, f"❌ Пользователь {target_user_id} не найден в базе.")
            return

        entry_date, violations, rep_user, rep_mod, msg_count, del_msg_count, edited_msg_count, is_banned = row

    except:
        logger.exception(f"Ошибка получения данных пользователя {target_user_id}")
        await bot.reply_to(message, "❌ Ошибка при получении данных из базы.")
        return

    # Получаем информацию о пользователе
    try:
        chat = bot.get_chat(target_user_id)
        username = chat.username
        first_name = chat.first_name
    except:
        username = None
        first_name = "Пользователь"

    user_name = f"@{username}" if username else first_name

    # Определяем тип пользователя
    if str(target_user_id) == ADMIN_ID or username == "GroupAnonymousBot":
        user_type = ADMIN_TYPE
        user_name = ADMIN_NAME
    elif str(target_user_id) == BOT_ID:
        user_type = BOT_TYPE
        user_name = BOT_NAME
    elif await is_moderator(bot, target_user_id):
        user_type = "💪 Модератор"
    else:
        user_type = "🗣️ Участник"

    if DEBUG_MODE and not (str(target_user_id) == ADMIN_ID or username == "GroupAnonymousBot" or str(
            target_user_id) == BOT_ID):
        user_name += f" ({target_user_id})"

    # Проверяем, забанен ли целевой пользователь
    if ENABLE_CHECK_IP:
        ip = await get_ip_address(target_user_id)
        target_ban_status = is_user_or_ip_banned(target_user_id, ip)
    else:
        target_ban_status = is_user_or_ip_banned(target_user_id)

    ban_text = ""
    if target_ban_status or is_banned:
        ban_text = f"⛔ Статус: ЗАБАНЕН\n\n"

    # Получаем информацию о мутах из старой системы (если она ещё используется)
    mutations_text = ""
    try:
        user_data = get_user_data(target_user_id)
        if user_data.get("mutations"):
            for i, mut in enumerate(user_data["mutations"], 1):
                until = datetime.datetime.fromisoformat(mut["until"])
                mutations_text += f"\n {i}. До: {until.strftime("%Y-%m-%d %H:%M:%S")}"
        else:
            mutations_text = "\n Нет активных мутов"
    except:
        mutations_text = "\n Информация о мутах недоступна"

    # Формируем ответ
    data_text = f"""
📊 Статистика пользователя {user_name}
✍️ Тип пользователя: {user_type}

{ban_text}📅 Дата вступления: {entry_date}
⚠️ Нарушений: {violations}
💬 Отправлено сообщений: {msg_count}
❌ Удалено сообщений: {del_msg_count}
✏️ Отредактировано сообщений: {edited_msg_count}
⭐ Репутация от пользователей: {rep_user}
🎩 Репутация от модераторов: {rep_mod}

🔇 Муты: {mutations_text}"""
    await bot.reply_to(message, data_text)



def add_mute(user_id, mute_until):
    """Добавляем мут"""
    uid = str(user_id)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute("""
                INSERT INTO mutations (user_id, date, until) 
                VALUES (?, ?, ?)
            """, (uid, datetime.datetime.now().isoformat(), mute_until.isoformat()))

    if MINUS_MODERATOR_REP_WHEN_MUTING:
        # Вычитаем COUNT_MINUS_MODERATOR_REP очков репутации модератора
        cursor.execute("SELECT reputation_moderator FROM users WHERE user_id = ?", (uid,))
        row = cursor.fetchone()
        if row:
            new_rep = max(0, row[0] - COUNT_MINUS_MODERATOR_REP)
            cursor.execute("UPDATE users SET reputation_moderator = ? WHERE user_id = ?", (new_rep, uid))

    # Снимаем MAX_VIOLATIONS нарушений
    cursor.execute("SELECT violations FROM users WHERE user_id = ?", (uid,))
    row = cursor.fetchone()
    if row:
        new_violations = max(0, row[0] - MAX_VIOLATIONS)
        cursor.execute("UPDATE users SET violations = ? WHERE user_id = ?", (new_violations, uid))

    conn.commit()
    conn.close()



async def check_and_apply_mute(bot, user_id, message):
    """Автоматический мут при достижении MAX_VIOLATIONS"""
    if await is_moderator(bot, user_id):
        return None

    total_points = get_total_points(user_id)
    if total_points >= MAX_VIOLATIONS:
        user_data = get_user_data(user_id)

        # Расчет времени мута (2^n для n-го мута)
        count_mutations = len(user_data["mutations"])
        duration_minutes = 10 * (2 ** count_mutations)
        mute_until = datetime.datetime.now() + datetime.timedelta(minutes=duration_minutes)

        # Записываем мут в базу
        add_mute(user_id, mute_until)

        # Применяем мут на duration_minutes минут с автоматическим снятием
        try:
            await bot.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=user_id,
                permissions=types.ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_polls=False,
                    can_send_other_messages=False,
                    can_add_web_page_previews=False
                ),
                until_date=int(mute_until.timestamp())
            )

            await bot.reply_to(message,
                               f"🔇 Пользователь замучен на {duration_minutes} минут до {mute_until.strftime("%H:%M")}\n"
                               f"Это мут #{count_mutations + 1}")

            logger.info(f"Пользователь {user_id} замучен на {duration_minutes} минут")

        except:
            logger.exception(f"Ошибка при муте пользователя {user_id}")
            await bot.reply_to(message, "❌ Не удалось наложить мут")

        return mute_until

    return None



async def get_ip_address(user_id):
    """Получаем IP пользователя"""
    try:
        loop = asyncio.get_event_loop()
        ip = loop.run_in_executor(None, lambda: requests.get("https://api.ipify.org", timeout=3).text)
        return ip
    except:
        logger.exception(f"Ошибка получения IP для {user_id}")
        return "unknown"
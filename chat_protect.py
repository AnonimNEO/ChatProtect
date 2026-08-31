# Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
# Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
# ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
# В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
# ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
# Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
# Или в файле COPYING.txt в репозитории или архиве
# Copyleft 🄯 NEO Organization, Departament K 2026
# Coded by AnonimNEO (GitHub)

# Логирование
from loguru import logger
# API Telegram
from telebot import apihelper
from telebot.async_telebot import AsyncTeleBot
from telebot import types
# Работа с базой данных
import datetime
import os
import sqlite3
# Переподключения
import requests
import signal
import asyncio

# База данных
from data_base import init_database, load_list_from_file, load_replacements, ban_user, unban_user, add_reputation, subtract_reputation
# Система бэкапов
from create_backups import schedule_backups
# Импорт основной конфигурации
from config import TOKEN, LOGGING, DEBUG_MODE, LOG_DIR, USE_PROXY, PROXY_URL, UNBAN_OWNER, ADMIN_ID, ENABLE_CHECK_IP, \
    VIOLATIONS_FOR_CHANGE_MODIFICATOR, DEBUG_CHECK_TEXT, DEBUG_JOKES, BOT_ID
# Импорт данных о базе данных
from config import DATABASE_FILE, BAD_WORDS_FILE, REPLACEMENTS_FILE, MODERATORS_FILE, ENABLE_JOKES, MEDIA_DIR
# Импорт стандартных функций
from system_functions import is_moderator, get_user_data, extract_target_user_id, data, is_user_or_ip_banned, get_ip_address, add_mute, get_user_name
# Импорт шуток
from jokes import send_audio_reply, cache_media, new_member, get_media_file_path
# Импорт обработки текста
from text_handler import messages_handler

# Глобальный флаг для остановки бота
stop_event = asyncio.Event()
should_stop = False

# Логирование
if LOGGING:
    os.makedirs(LOG_DIR, exist_ok=True)
    logger.add(f"{LOG_DIR}/{datetime.datetime.now().strftime("%d-%m-%Y")}.txt", rotation="00:00")

# Инициализируем SQLite базу
init_database()

if USE_PROXY:
    apihelper.proxy = {
        "https": PROXY_URL,
        "http": PROXY_URL
    }
    bot = AsyncTeleBot(TOKEN)
else:
    bot = AsyncTeleBot(TOKEN)

@bot.message_handler(commands=["help"])
async def handle_help(message):
    if message.chat.type == "private":
        return
    if not await is_moderator(bot, message.from_user.id):
        return
    help_text = """
Общие команды:
/help - Показать эту справку
/status - Статус бота
/data - Информация о пользователе

Команды модератора:
/rep @user [points] - Добавить репутацию пользователю
/minus_rep @user [points] - Снизить репутацию пользователю
/mute @user [minutes] - Заглушить пользователя
/unmute @user - Размутить пользователя
/ban @user - Забанить пользователя
/unban @user - Разбанить пользователя
/clear @user [points] - Очистить нарушения пользователя
/reload - Перезагрузить базы данных
"""
    await bot.reply_to(message, help_text)



@bot.message_handler(commands=["status"])
async def handle_status(message):
    done = message.chat.type == "private" and await is_moderator(bot, message.from_user.id)
    if not done:
        return

    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    conn.close()

    if done:
        status_text = \
f"""📊 Статус бота:
✅ Бот активен
👥 Всего пользователей: {user_count}
🛡️ Режим отладки: {"Включен" if DEBUG_MODE else "Отключен"}
🗒 Режим отладки для текста: {"Включен" if DEBUG_CHECK_TEXT else "Отключен"}
🤣 Режим отладки для шуток: {"Включен" if DEBUG_JOKES else "Отключен"}
📝 Логирование: {"Включено" if LOGGING else "Отключено"}"""
    else:
        status_text = \
f"""📊 Статус бота:
✅ Бот активен"""
    await bot.reply_to(message, status_text)



@bot.message_handler(commands=["data"])
async def handle_data(message):
    if message.chat.type == "private" and not await is_moderator(bot, message.from_user.id):
        return
    await data(bot, message)



@bot.message_handler(commands=["rep"])
async def handle_rep(message):
    if message.chat.type == "private":
        return

    args = message.text.split()
    user_id = extract_target_user_id(bot, message, args)

    points = 1
    if len(args) >= 2:
        try:
            points = int(args[1])
        except ValueError:
            await bot.reply_to(message, "❌ Очки должны быть числом.")
            return
    elif len(args) >= 3:
        try:
            points = int(args[2])
        except ValueError:
            await bot.reply_to(message, "❌ Очки должны быть числом.")
            return

    add_reputation(user_id, points, by_moderator=True)

    user_name = await get_user_name(bot, user_id)
    user_data = get_user_data(user_id)
    logger.success(f"Добавлено {points} очков репутации пользователю {user_name} ({user_id}). Всего: {user_data["reputation"]["moderator"]}")
    await bot.reply_to(message, f"✅ Добавлено {points} очков репутации пользователю {user_name} ({user_id}). Всего: {user_data["reputation"]["moderator"]}")
    if ENABLE_JOKES:
        if user_id == BOT_ID:
            await send_audio_reply(bot, message, get_media_file_path(rf"{MEDIA_DIR}/rep_bot/"))



@bot.message_handler(commands=["minus_rep"])
async def handle_minus_rep(message):
    if message.chat.type == "private":
        return

    args = message.text.split()
    user_id = extract_target_user_id(bot, message, args)

    points = 10
    if len(args) >= 3:
        try:
            points = int(args[2])
        except ValueError:
            await bot.reply_to(message, "❌ Очки должны быть числом.")
            return

    subtract_reputation(user_id, points, by_moderator=True)
    user_data = get_user_data(user_id)
    logger.success(f"Снято {points} очков репутации у пользователя {user_id}. Всего: {user_data["reputation"]["moderator"]}")
    await bot.reply_to(message, f"✅ Снято {points} очков репутации у пользователя {await get_user_name(bot, user_id)} ({user_id}). Всего: {user_data["reputation"]["moderator"]}")



@bot.message_handler(commands=["mute"])
async def handle_mute(message):
    if message.chat.type == "private":
        return
    if not await is_moderator(bot, message.from_user.id):
        return

    args = message.text.split()
    user_id = extract_target_user_id(bot, message, args)

    duration_minutes = 30
    if len(args) >= 3:
        try:
            duration_minutes = int(args[2])
        except ValueError:
            await bot.reply_to(message, "❌ Время должно быть числом.")
            return

    mute_until = datetime.datetime.now() + datetime.timedelta(minutes=duration_minutes)

    # Записываем мут в БД
    add_mute(user_id, mute_until)

    try:
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=user_id,
            permissions=types.ChatPermissions(can_send_messages=False),
            until_date=int(mute_until.timestamp())
        )
        logger.success(f"Пользователь {user_id} замучен на {duration_minutes} минут")
        await bot.reply_to(message, f"✅ Пользователь {await get_user_name(bot, user_id)} ({user_id}) замучен на {duration_minutes} минут.")
        if ENABLE_JOKES:
            await send_audio_reply(bot, message, get_media_file_path(rf"{MEDIA_DIR}/mute/"))
    except Exception as e:
        logger.exception(f"Ошибка при муте пользователя {user_id}")
        await bot.reply_to(message, f"❌ Ошибка при муте пользователя:\n{e}")



@bot.message_handler(commands=["unmute"])
async def handle_unmute(message):
    if message.chat.type == "private":
        return
    if not await is_moderator(bot, message.from_user.id):
        return

    args = message.text.split()
    user_id = extract_target_user_id(bot, message, args)

    uid = str(user_id)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM mutations WHERE user_id = ?", (uid,))

    conn.commit()
    conn.close()

    try:
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=user_id,
            permissions=types.ChatPermissions(can_send_messages=True)
        )
        logger.success(f"Пользователь {user_id} размучен")
        await bot.reply_to(message, f"✅ Пользователь {await get_user_name(bot, user_id)} ({user_id}) размучен.")
        if ENABLE_JOKES:
            await send_audio_reply(bot, message, get_media_file_path(rf"{MEDIA_DIR}/unban-unmute/"))
    except Exception as e:
        logger.exception(f"Ошибка при размуте пользователя {user_id}")
        await bot.reply_to(message, f"❌ Ошибка при размуте пользователя\n{e}")



@bot.message_handler(commands=["ban"])
async def handle_ban(message):
    if message.chat.type == "private":
        return
    user_id = message.from_user.id
    if not await is_moderator(bot, user_id):
        return
    try:
        success = ban_user(bot, message)
        await bot.kick_chat_member(message.chat.id, user_id)
    except:
        success = False
        logger.exception(f"Ошибка при бане пользователя {user_id}")
    user_name = await get_user_name(bot, user_id)
    if success:
        await bot.reply_to(message, f"Пользователь {user_name} ({user_id}) заблокирован.")
    else:
        await bot.reply_to(message, f"Ошибка блокировки пользователя {user_name} ({user_id}).")
    if ENABLE_JOKES:
        await send_audio_reply(bot, message, get_media_file_path(rf"{MEDIA_DIR}/ban/"))



@bot.message_handler(commands=["unban"])
async def handle_unban(message):
    if message.chat.type == "private":
        return
    user_id = message.from_user.id
    if not await is_moderator(bot, user_id):
        return
    user_name = await get_user_name(bot, user_id)
    success = unban_user(user_id)
    if success:
        await bot.reply_to(message, f"Пользователь {user_name} ({user_id}) разблокирован.")
    else:
        await bot.reply_to(message, f"Ошибка разблокировки пользователя {user_name} ({user_id}).")
    if ENABLE_JOKES:
        await send_audio_reply(bot, message, get_media_file_path(rf"{MEDIA_DIR}/unban-unmute/"))



@bot.message_handler(commands=["clear"])
async def handle_clear(message):
    if message.chat.type == "private":
        return
    if not await is_moderator(bot, message.from_user.id):
        return

    args = message.text.split()
    user_id = extract_target_user_id(bot, message, args)

    try:
        violations_to_remove = int(args[-1])
    except ValueError:
        await bot.reply_to(message, "❌ Последний аргумент должен быть числом.")
        return

    if violations_to_remove <= 0:
        await bot.reply_to(message, "❌ Число нарушений должно быть больше 0")
        return

    user_data = get_user_data(user_id)
    current_violations = user_data["violations"]

    if violations_to_remove > current_violations:
        await bot.reply_to(
            message,
            f"❌ Невозможно убрать {violations_to_remove} нарушений. "
            f"У пользователя только {current_violations} нарушений."
        )
        return

    new_violations = current_violations - violations_to_remove
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET violations = ? WHERE user_id = ?", (new_violations, user_id))
    conn.commit()
    conn.close()

    user_name = await get_user_name(bot, user_id)

    await bot.reply_to(message,
        f"✅ У пользователя {user_name} убрано {violations_to_remove} нарушений.\n"
        f"Было: {current_violations} → Стало: {new_violations}")
    if ENABLE_JOKES:
        await send_audio_reply(bot, message, get_media_file_path(rf"{MEDIA_DIR}/unban-unmute/"))



@bot.message_handler(commands=["reload"])
async def handle_reload(message):
    if not await is_moderator(bot, message.from_user.id):
        return

    global BAD_WORDS, REPLACEMENTS, MODERATORS_IDS

    BAD_WORDS = load_list_from_file(BAD_WORDS_FILE)
    REPLACEMENTS = load_replacements(REPLACEMENTS_FILE)
    MODERATORS_IDS = load_list_from_file(MODERATORS_FILE)

    logger.success("Базы данных перезагружены")
    await bot.reply_to(message, "✅ Базы данных перезагружены.")



@bot.message_handler(commands=["cache_media"])
async def handle_cache_media(message):
    if not await is_moderator(bot, message.from_user.id):
        return
    await cache_media(bot, message)



@bot.message_handler(content_types=["new_chat_members"])
async def handle_new_member(message):
    user_id = message.from_user.id
    if ENABLE_CHECK_IP:
        ip = await get_ip_address(user_id)
        target_ban_status = is_user_or_ip_banned(user_id, ip)
    else:
        target_ban_status = is_user_or_ip_banned(user_id)
    if target_ban_status:
        ban_user(user_id, await get_ip_address(user_id))
        await bot.kick_chat_member(message.chat.id, user_id)
        user_name = await get_user_name(bot, user_id)
        await bot.send_message(message.chat.id,f"Пользователь {user_name} ({user_id}) был заблокирован, так как находится в соответствующей базе.")
    await new_member(bot, message)



@bot.message_handler(func=lambda m: True)
async def handle_message(message):
    if message.chat.type == "private" and not DEBUG_CHECK_TEXT:
        return
    await messages_handler(bot, message)



@bot.edited_message_handler()
async def handle_edited_message(message):
    if message.chat.type == "private":
        return

    user_id = message.from_user.id

    if ENABLE_CHECK_IP:
        ip = await get_ip_address(user_id)
        is_banned = is_user_or_ip_banned(user_id, ip)
    else:
        is_banned = is_user_or_ip_banned(user_id)

    if is_banned:
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        except:
            pass
        return

    # Увеличиваем счётчик отредактированных сообщений
    uid = str(user_id)
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET edited_message_count = edited_message_count + 1 WHERE user_id = ?",
            (uid,)
        )
        conn.commit()
        conn.close()
    except:
        logger.exception(f"Ошибка обновления edited_message_count для {user_id}")

    await messages_handler(bot, message, VIOLATIONS_FOR_CHANGE_MODIFICATOR)



def signal_handler(signum, frame):
    global should_stop
    logger.info(">>>Получен сигнал остановки (Ctrl + C)")
    should_stop = True
    stop_event.set()
    exit()



async def start_chat_protect_bot():
    """Запускаем бота модератора"""
    global should_stop

    # Регистрируем обработчик сигнала
    signal.signal(signal.SIGINT, signal_handler)

    while not should_stop:
        try:
            logger.info(">>>Запуск бота...")
            await bot.infinity_polling(timeout=10,
                allowed_updates=["message", "edited_message", "callback_query"])
        except Exception as e:
            if should_stop:
                break
            if isinstance(e, requests.exceptions.ConnectionError):
                if DEBUG_MODE:
                    logger.debug(">>>Потеря соединения с интернетом. Переподключение через 5 секунд...")
                await asyncio.sleep(5)
            elif isinstance(e, requests.exceptions.Timeout):
                if DEBUG_MODE:
                    logger.debug(">>>Timeout соединения. Переподключение через 5 секунд...")
                await asyncio.sleep(5)
            else:
                if DEBUG_MODE:
                    logger.exception(">>>Ошибка подключения. Переподключение через 5 секунд...")
                await asyncio.sleep(5)

    logger.info(">>Бот - выключен")



async def main():
    """Главная функция для запуска бота"""
    schedule_backups() # Запускаем резервное копирование базы данных

    if UNBAN_OWNER:
        from data_base import unban_user
        result = unban_user(user_id=ADMIN_ID)
        logger.info(result)

    await start_chat_protect_bot()



if __name__ == "__main__":
    asyncio.run(main())
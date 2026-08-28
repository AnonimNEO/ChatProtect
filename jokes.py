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
# Работа с базой данных
import sqlite3
# прочее
import datetime
import random
import asyncio
import os

# Импорт конфигурации
from config import DEBUG_JOKES, DATABASE_FILE, CACHE_PAUSE
# Импорт настроек для шуточных ответов
from config import MEDIA_EXTENSIONS, AUDIO_EXTENSIONS, PHOTO_EXTENSIONS, VIDEO_EXTENSIONS, SOUNDS_DIR, MEDIA_DIR, GREETINGS_FILE, TRIGGERS_FILE
# Импорт стандартных функций
from system_functions import is_moderator, add_violation, get_ip_address
# Импорт из базы данных
from data_base import load_json, ban_user

async def send_audio_reply(bot, message, audio_file_path):
    """Отправляем аудиофайл ответом на сообщение"""
    try:
        with open(audio_file_path, "rb") as audio:
            await bot.send_audio(message.chat.id, audio, reply_to_message_id=message.message_id)
        if DEBUG_JOKES:
            logger.debug(f"Аудиофайл отправлен ответом на сообщение {message.message_id}")
    except FileNotFoundError:
        logger.error("❌ Аудиофайл не найден.")
    except:
        logger.exception(f"❌ Ошибка при отправке аудио файла")



def get_media_file_path(media_path):
    """Если media_path — директория, выбирает случайный совместимый файл.
    Если файл — возвращает путь как есть.
    Возвращает str или None."""
    # Валидация входных данных
    if not media_path or not isinstance(media_path, (str, bytes)):
        return None

    try:
        if not os.path.exists(media_path):
            return None

        if os.path.isfile(media_path):
            return media_path

        # Это директория — ищем совместимые файлы
        try:
            files_in_dir = os.listdir(str(media_path))
        except:
            logger.exception(f"Ошибка: {media_path}")
            return None

        compatible_files = [
            f for f in files_in_dir
            if os.path.splitext(f)[1].lower() in MEDIA_EXTENSIONS
        ]

        if not compatible_files:
            return None

        chosen_file = random.choice(compatible_files)
        full_path = os.path.join(str(media_path), chosen_file)
        return full_path

    except:
        logger.exception(f"Ошибка: {media_path}")
        return None



def get_file_type(file_path):
    """Определяет тип файла и метод отправки.
    Возвращает кортеж: (тип, метод_отправки)"""
    try:
        ext = os.path.splitext(file_path)[1].lower()
    except:
        ext = None

    if ext in AUDIO_EXTENSIONS:
        return "send_audio"
    elif ext in VIDEO_EXTENSIONS:
        return "send_video"
    elif ext in PHOTO_EXTENSIONS:
        return "send_photo"
    else:
        return "send_document"



async def send_media_cached(bot, message, media_path, trigger_key, cursor, conn):
    """Отправляем медиа-файл с кешированием ID сообщения."""
    logger.debug(f"[ENTER send_media_cached] media_path={media_path}, trigger_key={trigger_key}")

    file_path = get_media_file_path(media_path)
    logger.debug(f"[get_media_file_path result] file_path={file_path}, type={file_path}")

    if not file_path:
        logger.error(f"Медиа файл не найден: {media_path}")
        return False

    send_method = get_file_type(file_path)
    cache_key = f"trigger_{os.path.basename(str(file_path))}"

    try:
        cursor.execute(
            """SELECT message_id, chat_id FROM message_cache 
               WHERE trigger_key = ?""",
            (cache_key,)
        )
        cached = cursor.fetchone()
    except Exception as e:
        logger.exception(f"❌ Ошибка в SELECT, cache_key={repr(cache_key)}, type={type(cache_key)}")
        raise

    target_topic = getattr(message, "message_thread_id", None)

    if cached:
        try:
            await bot.forward_message(
                chat_id=message.chat.id,
                from_chat_id=cached[1],
                message_id=cached[0],
                message_thread_id=target_topic
            )
            if DEBUG_JOKES:
                logger.debug(f"Переслано из кеша: {file_path}")
            return True
        except:
            logger.exception(f"❌ Ошибка при пересылке из кеша: {file_path}")
            cursor.execute("DELETE FROM message_cache WHERE trigger_key = ?", (cache_key,))
            conn.commit()

    try:
        with open(file_path, "rb") as media_file:
            send_func = getattr(bot, send_method)
            sent_msg = await send_func(
                message.chat.id,
                media_file,
                message_thread_id=target_topic
            )

            cursor.execute(
                """INSERT OR REPLACE INTO message_cache 
                   (trigger_key, message_id, chat_id, created_at) 
                   VALUES (?, ?, ?, CURRENT_TIMESTAMP)""",
                (cache_key, sent_msg.message_id, message.chat.id)
            )
            conn.commit()
            if DEBUG_JOKES:
                logger.debug(f"Отправлено и закешировано: {file_path}")
            return True

    except FileNotFoundError:
        logger.error(f"❌ Файл не найден: {file_path}")
        return False
    except:
        logger.exception(f"❌ Ошибка при отправке медиа: {file_path}")
        return False



async def cache_media(bot, message):
    """Кешируем все медиа файлы из SOUNDS_DIR и MEDIA_DIR (включая подкаталоги)"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        args = message.text.split()
        force_all = len(args) > 1 and args[1].lower() == "all"

        media_dirs = [SOUNDS_DIR, MEDIA_DIR]
        cached_count = 0
        skipped_count = 0
        error_count = 0
        failed_files = []

        target_topic = getattr(message, "message_thread_id", None)

        mode_text = "принудительное кеширование всех файлов" if force_all else "кеширование только новых файлов"
        await bot.send_message(
            message.chat.id,
            f"⏳ Начинаю {mode_text}...",
            message_thread_id=target_topic
        )

        # Если force_all, удаляем все старые ID сообщений перед кешированием
        if force_all:
            try:
                cursor.execute("DELETE FROM message_cache WHERE trigger_key LIKE 'trigger_%'")
                conn.commit()
                logger.info("Все старые ID сообщений удалены из кеша")
            except:
                logger.exception(f"❌ Ошибка при очистке кеша")

        for directory in media_dirs:
            if not os.path.exists(directory):
                logger.error(f"Каталог не найден: {directory}")
                continue

            for root, dirs, files in os.walk(directory):
                for file_name in files:
                    file_path = os.path.join(root, file_name)

                    send_method = get_file_type(file_path)
                    if not send_method:
                        continue

                    # ИСПРАВЛЕНИЕ: кешируем по имени файла
                    cache_key = f"trigger_{os.path.basename(file_path)}"

                    if not force_all:
                        cursor.execute(
                            "SELECT message_id FROM message_cache WHERE trigger_key = ?",
                            (cache_key,)
                        )
                        if cursor.fetchone():
                            skipped_count += 1
                            continue

                    try:
                        with open(file_path, "rb") as media_file:
                            send_func = getattr(bot, send_method)
                            sent_msg = await send_func(
                                message.chat.id,
                                media_file,
                                message_thread_id=target_topic
                            )

                        cursor.execute(
                            """INSERT OR REPLACE INTO message_cache 
                               (trigger_key, message_id, chat_id, created_at) 
                               VALUES (?, ?, ?, CURRENT_TIMESTAMP)""",
                            (cache_key, sent_msg.message_id, message.chat.id)
                        )
                        conn.commit()

                        cached_count += 1
                        if DEBUG_JOKES:
                            logger.debug(f"Закеширован: {file_path}")

                        await asyncio.sleep(CACHE_PAUSE)

                    except Exception as e:
                        error_count += 1
                        failed_files.append(f"{file_path} ({type(e).__name__})")
                        logger.exception(f"❌ Ошибка при кешировании: {file_path}")

                        try:
                            cursor.execute(
                                "DELETE FROM message_cache WHERE trigger_key = ?",
                                (cache_key,)
                            )
                            conn.commit()
                            if DEBUG_JOKES:
                                logger.debug(f"Удален старый ID сообщения для: {file_path}")
                        except:
                            logger.exception(f"Ошибка при удалении старого ID")

        conn.close()

        summary = f"""✅ Кеширование завершено!

📊 Статистика:
✅ Закешировано: {cached_count} файлов
➡️ Пропущено: {skipped_count} файлов
❌ Ошибок: {error_count}
"""

        # Если были ошибки, добавляем детали
        if failed_files:
            summary += f"\n⚠️ Файлы с ошибками:\n"
            for failed in failed_files[:10]: # Показываем первые 10
                summary += f"• {failed}\n"
            if len(failed_files) > 10:
                summary += f"• и ещё {len(failed_files) - 10}..."

        await bot.send_message(message.chat.id, summary, message_thread_id=target_topic)

    except Exception as e:
        logger.exception("Ошибка при кешировании медиа")
        await bot.reply_to(message, f"❌ Ошибка: {e}")



async def new_member(bot, message):
    # Удаляем стандартное сообщение о вступлении
    try:
        await bot.delete_message(message.chat.id, message.message_id)
    except:
        logger.exception(f"Ошибка удаления сообщения о вступлении")

    # Загружаем базу приветствий
    greetings_db = load_json(GREETINGS_FILE)

    # Обработка каждого нового пользователя
    for new_member in message.new_chat_members:
        user_id = str(new_member.id)
        username = new_member.username or ""
        username_lower = username.lower() # Переводим в нижний регистр для сравнения

        # Записываем дату вступления СЕЙЧАС
        entry_date = datetime.datetime.now().replace(microsecond=0).isoformat()
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET entry_date = ? WHERE user_id = ?",
            (entry_date, user_id)
        )
        conn.commit()
        conn.close()

        logger.info(f"Новый пользователь {user_id} вступил в чат в {entry_date}")

        # Проверяем точный юзернейм (в нижнем регистре)
        greeting_text = None

        # Проверяем точный юзернейм
        for exact_nick, text in greetings_db.get("ники", {}).items():
            if exact_nick.lower() == username_lower:
                greeting_text = text
                break

        # Если точный ник не найден, проверяем ключевые слова
        if not greeting_text:
            for keyword, text in greetings_db.get("ключевые слова в нике", {}).items():
                if keyword.lower() in username_lower:
                    greeting_text = text
                    break

        # Отправляем приветствие если найдено
        if greeting_text:
            try:
                await bot.send_message(chat_id=message.chat.id, text=greeting_text)
            except:
                logger.exception(f"Ошибка при отправки приветствия")



async def handle_trigger_replies(message, bot, msg_lower):
    """Проверяет сообщение на совпадение с "шуточными" триггерами и отправляет шуточные ответы"""
    triggers = load_json(TRIGGERS_FILE)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    for trigger in triggers.get("replies", []):
        if any(keyword in msg_lower for keyword in trigger.get("keywords", [])):
            # Обработка медиа-файла
            if trigger.get("media"):
                media_path = trigger["media"]
                actual_path = get_media_file_path(media_path)

                if actual_path:
                    await send_media_cached(bot, message, actual_path, None, cursor, conn)

            # Отправляем текстовый ответ
            if trigger.get("response"):
                await bot.reply_to(message, trigger["response"])

            # Удаляем сообщение если требуется
            if trigger.get("delete_message"):
                try:
                    await bot.delete_message(
                        chat_id=message.chat.id,
                        message_id=message.message_id
                    )
                except:
                    logger.exception("Ошибка при удалении сообщения при тригеров")

            break

    conn.close()
# Данное Свободное Программное Обеспечение распространяется по лицензии AGPL-3.0-only или AGPL-3.0-or-later
# Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
# ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ GNU AGPL v3.0 или более поздней версии
# В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
# ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ И/ИЛИ ПРЕДОСТАВЛЕНИИ ДОСТУПА К НЕЙ ЧЕРЕЗ СЕТЕВОЙ ИНТЕРФЕЙС, ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕ ЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЮ AGPL v3 И ДОСТУП К ИСХОДНОМУ КОДУ
# Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/agpl-3.0.html
# Или в файле COPYING.txt в репозитории или архиве
# Copyleft 🄯 NEO Organization, Departament K 2026
# Coded by AnonimNEO (GitHub)

# Дата и время
from datetime import datetime, timedelta
# Логирование
from loguru import logger
# Асинхронность
import asyncio
# Рандомные числа
import random
from typing import Optional

# Локализация
from languages import l
# Импорт конфигурации
from config import EMOJI_OPTIONS, CAPTCHA_ATTEMPTS

# Словарь для отслеживания попыток пользователей: {user_id: {attempt: int, type: str, data: dict}}
user_captcha_attempts = {}

# Словарь для отслеживания активных таймеров: {chat_id: (timer_task, end_time)}
active_timers = {}

async def generate_emoji_captcha():
    """Генерируем капчу с эмодзи"""
    correct_emoji = random.choice(EMOJI_OPTIONS)
    return {
        "type": "emoji",
        "correct": correct_emoji,
        "message": f'{l("send_emoji")}: {correct_emoji}'
    }



async def generate_number():
    n = random.randint(1000, 10000)
    return {
        "type": "code",
        "correct": n,
        "message": f'{l("send_code")}: {n}'
    }



async def generate_math_captcha():
    """Генерируем математическую капчу"""
    num1 = random.randint(1, 20)
    num2 = random.randint(1, 20)
    operation = random.choice(["+", "-", "*"])

    if operation == "+":
        answer = num1 + num2
    elif operation == "-":
        answer = num1 - num2
    else: # *
        answer = num1 * num2

    return {
        "type": "math",
        "correct": str(answer),
        "message": f'{l("send_result")}: {num1} {operation} {num2} = ?'
    }



async def get_random_captcha():
    """Выбираем случайную капчу"""
    captcha_gen = random.choice([
        generate_emoji_captcha(),
        generate_math_captcha(),
        generate_number
    ])
    return await captcha_gen



async def check_captcha_answer(user_id, answer):
    """Проверяем ответ на капчу
    Возвращает: (passed: bool, should_remove: bool)"""
    if user_id not in user_captcha_attempts:
        return False, False

    attempt_data = user_captcha_attempts[user_id]
    captcha_type = attempt_data["type"]

    is_correct = False

    if captcha_type == "emoji":
        is_correct = answer == attempt_data["data"]["correct"]
    elif captcha_type == "math":
        is_correct = answer.strip() == attempt_data["data"]["correct"]
    elif captcha_type == "code":
        is_correct = answer == str(attempt_data["data"]["correct"])

    if is_correct:
        return True, True # Прошла капча, удалить данные

    # Неправильный ответ, увеличиваем счётчик попыток
    attempt_data["attempt"] += 1

    if attempt_data["attempt"] >= CAPTCHA_ATTEMPTS:
        return False, True # Не прошла и нужно удалить данные

    return False, False # Не прошла, но попытки остались



async def enable_join_requests_temporarily(bot, chat_id: int, duration_minutes: int = 5) -> bool:
    """Временно включает вход в группу по заявкам на указанное время.
    По истечении времени отключает заявки и принимает все ожидающие заявки.

    Args:
        bot: Экземпляр бота (AsyncTeleBot)
        chat_id: ID группы
        duration_minutes: Длительность в минутах (по умолчанию 5)

    Returns:
        bool: True если успешно, False если ошибка"""
    try:
        # Если уже есть активный таймер для этой группы, отменяем его
        if chat_id in active_timers:
            task, _ = active_timers[chat_id]
            task.cancel()

        # Включаем вход по заявкам
        await bot.set_chat_join_request_needed(
            chat_id=chat_id,
            join_request_needed=True
        )

        await bot.approve_chat_join_request(chat_id=chat_id)

        # Создаем таймер
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        timer_task = asyncio.create_task(
            _join_requests_timer(bot, chat_id, duration_minutes)
        )

        active_timers[chat_id] = (timer_task, end_time)

        return True

    except:
        logger.exception(f"Ошибка при включении заявок")
        return False



async def _join_requests_timer(bot, chat_id: int, duration_minutes: int):
    """функция таймера для управления заявками."""
    try:
        # Ждем указанное время
        await asyncio.sleep(duration_minutes * 60)

        # Отключаем вход по заявкам (восстанавливаем права)
        await bot.set_chat_join_request_needed(
            chat_id=chat_id,
            join_request_needed=False
        )

        # Получаем все ожидающие заявки и принимаем их
        chat_join_requests = await bot.get_chat_join_requests(
            chat_id=chat_id,
            limit=100 # Максимум 100 заявок за раз
        )

        if chat_join_requests:
            for request in chat_join_requests:
                try:
                    await bot.approve_chat_join_request(
                        chat_id=chat_id,
                        user_id=request.from_user.id
                    )
                except:
                    logger.exception(f"Ошибка при принятии заявки от {request.from_user.id}")

        # Удаляем из активных таймеров
        if chat_id in active_timers:
            del active_timers[chat_id]

        logger.success(f"Таймер для группы {chat_id} завершен. Заявки отключены, все ожидающие приняты.")

    except asyncio.CancelledError:
        logger.info(f"Таймер для группы {chat_id} был отменен.")
    except:
        logger.exception(f"Ошибка в таймере для группы {chat_id}")
        if chat_id in active_timers:
            del active_timers[chat_id]



async def cancel_join_requests_timer(chat_id: int) -> bool:
    """Отменяем активный таймер для группы (если он существует)."""
    if chat_id in active_timers:
        task, _ = active_timers[chat_id]
        task.cancel()
        del active_timers[chat_id]
        return True
    return False



async def get_timer_remaining(chat_id: int) -> Optional[int]:
    """Получаем оставшееся время таймера в секундах."""
    if chat_id in active_timers:
        _, end_time = active_timers[chat_id]
        remaining = (end_time - datetime.now()).total_seconds()
        return max(0, int(remaining))
    return None
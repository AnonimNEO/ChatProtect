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
# Обнаружение нарушений
from difflib import SequenceMatcher
import re

# Импорт базы данных
from data_base import load_list_from_file, load_replacements, ban_user, is_user_or_ip_banned, data_operation
# Импорт конфигурации
from config import DEBUG_CHECK_TEXT, BAD_WORDS_FILE, EXCEPTIONS_FILE, REPLACEMENTS_FILE, MODERATORS_FILE, ENABLE_JOKES, ENABLE_DIFFLIB
# Импорт констант
from config import SPAM_VIOLATION_MODIFICATOR, VIOLATION_FOR_LINKS_MODIFICATOR, FIRST_STAGE_VIOLATION_MODIFICATOR, SECOND_STAGE_VIOLATION_MODIFICATOR, THIRD_STAGE_VIOLATION_MODIFICATOR
# Импорт конфигурации обнаружения нарушений
from config import SIMILARITY_THRESHOLD
# Импорт конфигурации анти-спам системы
from config import MAX_MESSAGES_IN_MINUTE, ENABLE_CHECK_IP, COUNT_MESSAGE_CHECK_FOR_URL, CHECK_FIRST_URL, ENABLE_BAN_USER_FOR_SPAM
# Импорт стандартных функций
from system_functions import add_timestamps, user_message_times, add_violation, check_and_apply_mute, get_ip_address, get_user_data, get_user_name
# Импорт обработчика шуток
from jokes import handle_trigger_replies

# Загружаем базы данных
BAD_WORDS = load_list_from_file(BAD_WORDS_FILE)
EXCEPTION_WORDS = load_list_from_file(EXCEPTIONS_FILE)
REPLACEMENTS = load_replacements(REPLACEMENTS_FILE)
MODERATORS_IDS = load_list_from_file(MODERATORS_FILE)

# Создаём таблицу переводов один раз (вне функции)
_single_replacements = {k: v for k, v in REPLACEMENTS if len(k) == 1}
_multi_replacements = [(k, v) for k, v in REPLACEMENTS if len(k) > 1]
_trans_table = str.maketrans(_single_replacements)

# Кешируем таблицы переводов для режима "удалить всё кроме алфавита и цифр"
_keep_alnum_table = str.maketrans("", "", "".join(
    chr(i) for i in range(0x10000)
    if not chr(i).isalnum()
))

# Кешируем скомпилированный паттерн для разбиения слов
_word_pattern = re.compile(r"\w+", re.UNICODE)

async def delete_messages(bot, message, user_id):
    try:
        if DEBUG_CHECK_TEXT:
            user_name = await get_user_name(bot, user_id)
            await bot.reply_to(message, f"{user_name} ({user_id}) Сообщение было удалено автоматической системой модерации.")
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except:
        logger.exception(f"Ошибка удаления сообщения {message.message_id} от пользователя {user_id}")



def count_violations(text, violations_list, enable_difflib=False):
    """Подсчитывает совпадения нарушений в тексте с поддержкой difflib."""
    if not enable_difflib:
        return sum(text.count(v) for v in violations_list)

    count = 0
    # Быстрое разбиение на слова с regex
    words = _word_pattern.findall(text)

    for violation in violations_list:
        for word in words:
            if SequenceMatcher(None, violation, word).ratio() >= SIMILARITY_THRESHOLD:
                count += 1

    return count



def text_processing_stage_1(text, keep_chars=None):
    """1 Этап обработки текста.
    Удаляет символы из текста.

    Args:
        text: исходная строка
        keep_chars: None — удалить всё кроме алфавита и цифр (быстро)
                   строка/кортеж — удалить переданные символы"""
    if keep_chars is None:
        # Режим 1: оставить только алфавит + цифры (самый быстрый)
        return text.translate(_keep_alnum_table)
    else:
        # Режим 2: удалить переданные символы
        delete_table = str.maketrans("", "", keep_chars)
        return text.translate(delete_table)



def text_processing_stage_2(text):
    """2 Этап обработки текста"""
    # Сначала применяем односимвольные замены через translate()
    text = text.translate(_trans_table)

    # Потом применяем многосимвольные замены через replace()
    for old, new in _multi_replacements:
        text = text.replace(old, new)

    return text



async def user_punishment(bot, message, user_id, count):
    await delete_messages(bot, message, user_id)
    data_operation(str(user_id), user_id,"UPDATE users SET delete_message_count = delete_message_count + 1 WHERE user_id = ?")
    add_violation(user_id, count)



async def messages_handler(bot, message, changed=1):
    """Проверка сообщений"""
    user_id = message.from_user.id
    text = message.text.lower()

    # Обновляем счетчик сообщений за текущую минуту
    add_timestamps(user_id)
    # Увеличиваем счётчик обычных сообщений
    data_operation(str(user_id), user_id, "UPDATE users SET message_count = message_count + 1 WHERE user_id = ?")
    user_data = get_user_data(user_id)

    if ENABLE_CHECK_IP:
        user_banned = is_user_or_ip_banned(user_id, get_ip_address(user_id))
    else:
        user_banned = is_user_or_ip_banned(user_id)

    if user_banned:
        await delete_messages(bot, message, user_id)
        return

    # Проверка спама
    if len(user_message_times[str(user_id)]) > MAX_MESSAGES_IN_MINUTE:
        if DEBUG_CHECK_TEXT:
            logger.debug(f"Обнаружен спам от пользователя {user_id}!")
        if ENABLE_BAN_USER_FOR_SPAM:
            ban_user(user_id, get_ip_address(user_id))
            await bot.kick_chat_member(message.chat.id, user_id)
        else:
            await user_punishment(bot, message, user_id, SPAM_VIOLATION_MODIFICATOR * changed)
        return

    if CHECK_FIRST_URL:
        if user_data["message_count"] < COUNT_MESSAGE_CHECK_FOR_URL + 1:
            if "https://" in text or "http://" in text:
                await user_punishment(bot, message, user_id, VIOLATION_FOR_LINKS_MODIFICATOR * changed)
                return

    exception_count = count_violations(text_processing_stage_1(text), EXCEPTION_WORDS, False)

    # 0 Этап проверки просто ищем совпадение
    count_violations_in_message = count_violations(text, BAD_WORDS, ENABLE_DIFFLIB)
    if count_violations_in_message - exception_count > 0:
        await user_punishment(bot, message, user_id, FIRST_STAGE_VIOLATION_MODIFICATOR * changed)
        return

    # 1 Этап проверки удаление всех символов
    stage1_text = text_processing_stage_1(text)
    count_violations_in_message = count_violations(stage1_text, BAD_WORDS, ENABLE_DIFFLIB)
    if count_violations_in_message - exception_count > 0:
        await user_punishment(bot, message, user_id, SECOND_STAGE_VIOLATION_MODIFICATOR * changed)
        return

    # 2 Этап проверки удаление не всех символов и замена символов
    stage2_text = text_processing_stage_2(text_processing_stage_1(text, r"[.,!?;:\"#№$%^&\-+=`~<>|()[\]{}\\/@]"))
    count_violations_in_message = count_violations(stage2_text, BAD_WORDS, ENABLE_DIFFLIB)
    if count_violations_in_message - exception_count > 0:
        await user_punishment(bot, message, user_id, THIRD_STAGE_VIOLATION_MODIFICATOR * changed)
        return

    await check_and_apply_mute(bot, user_id, text)

    if ENABLE_JOKES:
        await handle_trigger_replies(message, bot, text)

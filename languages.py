from config import current_localization
copyleft_years = "2026"

localization = {
    "ru": {
        "help_text":  """Общие команды:
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
/reload - Перезагрузить базы данных""",
        "bot_status": "📊 Статус бота",
        "bot_active": "✅ Бот активен",
        "total_users": "👥 Всего пользователей",
        "debug_mode": "🛡️ Режим отладки",
        "debug_mode_text": "🗒 Режим отладки для текста",
        "debug_mode_jokes": "🤣 Режим отладки для шуток",
        "loging": "📝 Логирование",
        "on": "Включен",
        "off": "Отключен",
        "bot_name": 'Бот "Защита чата - NEO Organization" v',
        "about_bot_text": f"""
Свободный бот модератор для защиты чата распространяющийся по лицензии GPL v3
Created by NEO Organization
Powered by Departament K
Coded by @AnonimNEO

Особые благодарности:
-Помошь в тестировании:
--Алексик

NEO Organization - Copyleft {copyleft_years}""",
        "need_a_number": "❌ введите число.",
        "all": "Всего",
        "added": "Добавлено",
        "rep_points": "очков репутации",
        "for_user": "пользователю",
        "removed": "Снято",
        "user": "Пользователь",
        "minutes": "минут",
        "muted": "замучен",
        "on2": "на",
        "mute_error": "Ошибка при муте пользователя",
        "unmuted": "размучен",
        "unmute_error": "Ошибка при размуте пользователя",
        "ban_error": "Ошибка при бане пользователя",
        "banned": "заблокирован",
        "unbanned": "разблокирован",
        "unbanned_error": "Ошибка разблокировки пользователя",
        "number_must_more_0": "❌ Число должно быть больше 0",
        "remove_error": "❌ Невозможно убрать",
        "violations": "нарушений",
        "the_user_has": "У пользователя",
        "only": "только",
        "was": "Было",
        "it_became": "Стало",
        "base_reloaded": "Базы данных перезагружены",
        "user_banned_for_base": "был заблокирован, так как находится в соответствующей базе",
        "update_error": "Ошибка обновления",
        "for": "для",
        "stop_signal_detected": ">>> Получен сигнал остановки (Ctrl + C)",
        "start_bot": ">>> Запуск бота...",
        "connect_timeout": ">>> Timeout соединения. Переподключение через 5 секунд...",
        "bot_off": ">>> Бот - выключен",
        # create_backups.py
        "old_bakcup_delete": "Удалён старый бэкап",
        "create_backup": "Создан бэкап",
        "start_backup_create": "Стартовый бэкап создан",
        "create_backups_startef": "Система резервного копирования запущена, интервал",
        "seconds": "секунд",
        "unlock_all": "Разблокированы все",
        "users_on": "пользователей на",
        # jokes.py
        "audio_send": "Аудиофайл отправлен ответом на сообщение",
        "file_not_found": "Файл не найден",
        "media_send_error": "Ошибка при отправке медиа",
        "error": "Ошибка",
        "forwarded_from_cache": "Переслано из кеша",
        "forwarded_from_cache_error": "Ошибка при пересылке из кеша",
        "send_for_cache": "Отправлено и закешировано",
        "cache_media_all": "принудительное кеширование всех файлов",
        "cache_media": "кеширование только новых файлов",
        "starting": "Начинаю",
        "cache_clear": "Все старые ID сообщений удалены из кеша",
        "cache_clear_error": "Ошибка при очистке кеша",
        "dir_not_found": "Каталог не найден",
        "cache_media_error": "Ошибка при кешировании",
        "": "",
    }
}



def l(text_key):
    try:
        return localization[current_localization[text_key]]
    except:
        return text_key
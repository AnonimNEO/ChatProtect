from config import CURRENT_LOCALIZATION
copyleft_years = "2026"

localizations = {
    "ru": {
"help_text":  """Общие команды:
/help - Показать эту справку
/status - Статус бота
/data - Информация о пользователе
/about - Информация о боте

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
"delete_old_cache_id": "Удален старый ID сообщения для",
"delete_old_cache_id_error": "Ошибка при удалении старого ID",
"cache_media_success": "✅ Кеширование завершено!\n📊 Статистика:",
"cached": "✅ Закешировано",
"file2": "файлов",
"skipped": "➡️ Пропущено",
"errors": "❌ Ошибок",
"file_wit_errors": "⚠️ Файлы с ошибками",
"and": "и ещё",
"about_joining": "о вступлении",
"new_user": "Новый пользователь",
"joined_in": "вступил в чат в",
"send_hello_error": "Ошибка при отправки приветствия",
"delete_message_error": "Ошибка при удалении сообщения",
# system_functions.py
"user_not_found": "Не удалось найти пользователя",
"add_violation_error": "Ошибка добавления нарушения для",
"get_user_info_error": "Ошибка получения данных пользователя",
"moderator": "💪 Модератор",
"member": "🗣️ Участник",
"status": "Статус",
"is_banned": "⛔ ЗАБАНЕН",
"to": "До",
"no_mutes": "Нет активных мутов",
"user_statistics": "📊 Статистика пользователя",
"user_type": "✍️ Тип пользователя",
"join_date": "📅 Дата вступления",
"send_messages": "💬 Отправлено сообщений",
"deleted_messages": "❌ Удалено сообщений",
"edited_messages": "✏️ Отредактировано сообщений",
"rep_from_users": "⭐ Репутация от пользователей",
"rep_from_moderators": "🎩 Репутация от модераторов",
"mutes": "🔇 Муты",
"user_muted": "🔇 Пользователь замучен на",
"this": "Это",
"mute": "мут",
"get_ip_error": "Ошибка получения IP для",
# text_handler.py
"from_the_user": "от пользователя",
"message_delete_for_bot": "Сообщение было удалено автоматической системой модерации.",
"spam_detect": "Обнаружен спам от пользователя",
},
    "en": {
"help_text":  """General commands:
/help - Show this help message
/status - Bot status
/data - User information

Moderator commands:
/rep @user [points] - Add reputation points to a user
/minus_rep @user [points] - Deduct reputation points from a user
/mute @user [minutes] - Mute a user
/unmute @user - Unmute a user
/ban @user - Ban a user
/unban @user - Unban a user
/clear @user [points] - Clear a user's violations
/reload - Reload databases""",
"bot_status": "📊 Bot status",
"bot_active": "✅ Bot is active",
"total_users": "👥 Total users",
"debug_mode": "🛡️ Debug mode",
"debug_mode_text": "🗒 Text debug mode",
"debug_mode_jokes": "🤣 Joke debug mode",
"loging": "📝 Logging",
"on": "Enabled",
"off": "Disabled",
"bot_name": '"Chat Protection - NEO Organization" bot v',
"about_bot_text": f"""
Free chat protection moderator bot distributed under the GPL v3 license
Created by NEO Organization
Powered by Departament K
Coded by @AnonimNEO

Special thanks:
-Testing assistance:
--Aleksik

NEO Organization - Copyleft {copyleft_years}""",
"need_a_number": "❌ Please enter a number.",
"all": "Total",
"added": "Added",
"rep_points": "reputation points",
"for_user": "to user",
"removed": "Removed",
"user": "User",
"minutes": "minutes",
"muted": "muted",
"on2": "on",
"mute_error": "Error muting user",
"unmuted": "unmuted",
"unmute_error": "Error unmuting user",
"ban_error": "Error banning user",
"banned": "banned",
"unbanned": "unbanned",
"unbanned_error": "Error unbanning user",
"number_must_more_0": "❌ Number must be greater than 0",
"remove_error": "❌ Unable to remove",
"violations": "violations",
"the_user_has": "The user has",
"only": "only",
"was": "Was",
"it_became": "Became",
"base_reloaded": "Databases reloaded",
"user_banned_for_base": "was banned because they are in the corresponding database",
"update_error": "Update error",
"for": "for",
"stop_signal_detected": ">>> Stop signal received (Ctrl + C)",
"start_bot": ">>> Starting bot...",
"connect_timeout": ">>> Connection timeout. Reconnecting in 5 seconds...",
"bot_off": ">>> Bot is off",
# create_backups.py
"old_bakcup_delete": "Old backup deleted",
"create_backup": "Backup created",
"start_backup_create": "Initial backup created",
"create_backups_startef": "Backup system started, interval",
"seconds": "seconds",
"unlock_all": "All unblocked",
"users_on": "users on",
# jokes.py
"audio_send": "Audio file sent as a reply to the message",
"file_not_found": "File not found",
"media_send_error": "Error sending media",
"error": "Error",
"forwarded_from_cache": "Forwarded from cache",
"forwarded_from_cache_error": "Error forwarding from cache",
"send_for_cache": "Sent and cached",
"cache_media_all": "force caching all files",
"cache_media": "caching only new files",
"starting": "Starting",
"cache_clear": "All old message IDs removed from cache",
"cache_clear_error": "Error clearing cache",
"dir_not_found": "Directory not found",
"cache_media_error": "Caching error",
"delete_old_cache_id": "Old message ID deleted for",
"delete_old_cache_id_error": "Error deleting old ID",
"cache_media_success": "✅ Caching complete!\n📊 Statistics:",
"cached": "✅ Cached",
"file2": "files",
"skipped": "➡️ Skipped",
"errors": "❌ Errors",
"file_wit_errors": "⚠️ Files with errors",
"and": "and",
"about_joining": "about joining",
"new_user": "New user",
"joined_in": "joined the chat at",
"send_hello_error": "Error sending greeting",
"delete_message_error": "Error deleting message",
# system_functions.py
"user_not_found": "User not found",
"add_violation_error": "Error adding violation for",
"get_user_info_error": "Error retrieving user data",
"moderator": "💪 Moderator",
"member": "🗣️ Member",
"status": "Status",
"is_banned": "⛔ BANNED",
"to": "Until",
"no_mutes": "No active mutes",
"user_statistics": "📊 User statistics",
"user_type": "✍️ User type",
"join_date": "📅 Join date",
"send_messages": "💬 Messages sent",
"deleted_messages": "❌ Messages deleted",
"edited_messages": "✏️ Messages edited",
"rep_from_users": "⭐ Reputation from users",
"rep_from_moderators": "🎩 Reputation from moderators",
"mutes": "🔇 Mutes",
"user_muted": "🔇 User muted for",
"this": "This",
"mute": "mute",
"get_ip_error": "Error retrieving IP for",
# text_handler.py
"from_the_user": "from user",
"message_delete_for_bot": "The message was deleted by the automated moderation system.",
"spam_detect": "Spam detected from user",
},
    "ua": {
"help_text": """Загальні команди:
/help - Показати цю довідку
/status - Статус бота
/data - Інформація про користувача

Команди модератора:
/rep @user [points] - Додати репутацію користувача
/minus_rep @user [points] - Зменшити репутацію користувача
/mute @user [minutes] - Заглушити користувача
/unmute @user - Розмутити користувача
/ban @user - Забанити користувача
/unban @user - Розбанити користувача
/clear @user [points] - Очистити порушення користувача
/reload - Перезавантажити бази даних""",
"bot_status": "📊 Статус бота",
"bot_active": "✅ Бот активний",
"total_users": "👥 Всього користувачів",
"debug_mode": "🛡️ Режим налагодження",
"debug_mode_text": "🗒 Режим налагодження для тексту",
"debug_mode_jokes": "🤣 Режим налагодження для жартів",
"loging": "📝 Логування",
"on": "Увімкнено",
"off": "Відключено",
"bot_name": 'Бот "Захист чату - NEO Organization" v',
"about_bot_text": f"""
Вільний бот модератор для захисту чату, що розповсюджується за ліцензією GPL v3
Created by NEO Organization
Powered by Departament K
Coded by @AnonimNEO

Особливі подяки:
-Допомога в тестуванні:
--Олексик

NEO Organization - Copyleft {copyleft_years}""",
"need_a_number": "❌ введіть число.",
"all": "Усього",
"added": "Додано",
"rep_points": "окулярів репутації",
"for_user": "користувачу",
"removed": "Знято",
"user": "Користувач",
"minutes": "хвилин",
"muted": "замучений",
"on2": "на",
"mute_error": "Помилка при каламуті користувача",
"unmuted": "розмучений",
"unmute_error": "Помилка при розмуті користувача",
"ban_error": "Помилка при лазні користувача",
"banned": "заблокований",
"unbanned": "розблокований",
"unbanned_error": "Помилка розблокування користувача",
"number_must_more_0": "❌ Число має бути більше 0",
"remove_error": "❌ Неможливо видалити",
"violations": "порушень",
"the_user_has": "У користувача",
"only": "тільки",
"was": "Було",
"it_became": "Стало",
"base_reloaded": "Бази даних перезавантажені",
"user_banned_for_base": "було заблоковано, оскільки знаходиться у відповідній базі",
"update_error": "Помилка оновлення",
"for": "для",
"stop_signal_detected": ">>> Отриманий сигнал зупинки (Ctrl + C)",
"start_bot": ">>> Запуск бота...",
"connect_timeout": ">>> Timeout з'єднання. Перепідключення через 5 секунд...",
"bot_off": ">>> Бот - вимкнений",
#create_backups.py
"old_bakcup_delete": "Видалено старий бекап",
"create_backup": "Створено бекап",
"start_backup_create": "Стартовий бекап створений",
"create_backups_startef": "Система резервного копіювання запущена, інтервал",
"seconds": "секунд",
"unlock_all": "Розблоковані всі",
"users_on": "користувачів на",
#jokes.py
"audio_send": "Аудіофайл надіслано відповіддю на повідомлення",
"file_not_found": "Файл не знайдено",
"media_send_error": "Помилка надсилання медіа",
"error": "Помилка",
"forwarded_from_cache": "Переслано з кеша",
"forwarded_from_cache_error": "Помилка при пересиланні з кеша",
"send_for_cache": "Відправлено та закешовано",
"cache_media_all": "примусове кешування всіх файлів",
"cache_media": "кешування тільки нових файлів",
"starting": "Починаю",
"cache_clear": "Всі старі ID повідомлення видалені з кеша",
"cache_clear_error": "Помилка при очищенні кеша",
"dir_not_found": "Каталог не знайдено",
"cache_media_error": "Помилка при кешуванні",
"delete_old_cache_id": "Видалено старий ID повідомлення для",
"delete_old_cache_id_error": "Помилка при видаленні старого ID",
"cache_media_success": "✅ Кешування завершено!\n📊 Статистика:",
"cached": "✅ Закешовано",
"file2": "файлів",
"skipped": "➡️ Пропущено",
"errors": "❌ Помилок",
"file_wit_errors": "⚠️ Файли з помилками",
"and": "і ще",
"about_joining": "про вступ",
"new_user": "Новий користувач",
"joined_in": "вступив до чату",
"send_hello_error": "Помилка при надсиланні привітання",
"delete_message_error": "Помилка видалення повідомлення",
#system_functions.py
"user_not_found": "Не вдалося знайти користувача",
"add_violation_error": "Помилка додавання порушення для",
"get_user_info_error": "Помилка отримання даних користувача",
"moderator": "💪 Модератор",
"member": "🗣️ Учасник",
"status": "Статус",
"is_banned": "⛔ ЗАБАНЕН",
"to": "До",
"no_mutes": "Немає активних мутів",
"user_statistics": "📊 Статистика користувача",
"user_type": "✍️ Тип користувача",
"join_date": "📅 Дата вступу",
"send_messages": "💬 Надіслано повідомлення",
"deleted_messages": "❌ Видалено повідомлень",
"edited_messages": "✏️ Відредаговано повідомлень",
"rep_from_users": "⭐ Репутація від користувачів",
"rep_from_moderators": "🎩 Репутація від модераторів",
"mutes": "🔇 Мути",
"user_muted": "🔇 Користувач замучений на",
"this": "Це",
"mute": "мут",
"get_ip_error": "Помилка отримання IP для",
#text_handler.py
"from_the_user": "від користувача",
"message_delete_for_bot": "Повідомлення видалено автоматичною системою модерації.",
"spam_detect": "Знайдено спам від користувача",
}
}



# Возвращаем нужный текст или сам ключ если нужного текста нет в текущем языке
def l(key, language=CURRENT_LOCALIZATION):
    """Функция для получения текста из локализации
    key - имя ключа текста/реплики/диалога
    language - Язык на котором вернуть текст
    return - функция возвращает текст из локализации, если такого ключа в указанной локализации нет то будет возвращён сам ключ"""
    return localizations.get(language, {}).get(key) or key

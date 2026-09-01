# === Основная конфигурация ===
TOKEN = "" # Токен бота

LOGGING = True # Включить логирование в файл?
DEBUG_MODE = True # Включить режим отладки?
DEBUG_CHECK_TEXT = True # Включить режим отладки для text_handler?
DEBUG_JOKES = True # Включить отладку для jokes?

# [В разработке] Настройки прокси
USE_PROXY = False
# Если нужна авторизация, включи её в PROXY_URL:
# PROXY_URL = "https://user:password@proxy.com:port"
PROXY_URL = ""

# === Настройки уникальных данных в /data ===
UNBAN_OWNER = True # Разблокировать создателя?
ADMIN_ID = 0 # ID создателя (главного админа)
ADMIN_TYPE = "" # Уникальный тип главного админа
ADMIN_NAME = "" # Уникальное имя главного админа
BOT_ID = 0 # ID бота
BOT_TYPE = "" # Уникальный тип бота
BOT_NAME = "" # Уникальное имя бота

# === Настройки анти-спам системы ===
ENABLE_DIFFLIB = False # Включить проверку по не точному совпадению через difflib
SIMILARITY_THRESHOLD = 0.85 # 85% схожести. Порог для нечётких совпадений (работает только при проверке на запрещённые слова)
ENABLE_CHECK_IP = False # Включить проверку IP при проверке забанен ли пользователь (дольше, а также может заблокировать VPN сервера из-за чего доступ для обычных пользователей может быть затруднён)
MAX_MESSAGES_IN_MINUTE = 13 # Максимум сообщений в минуту от одного пользователя
ENABLE_BAN_USER_FOR_SPAM = False  # Банить пользователя за спам (MAX_MESSAGES_IN_MINUTE сообщений за минуту)
SPAM_VIOLATION_MODIFICATOR = 9 # Сколько нарушений добавить за спам (если ENABLE_BAN_USER_FOR_SPAM = False)
VIOLATION_FOR_LINKS_MODIFICATOR = 9 # Сколько нарушений добавить за ссылку в первых COUNT_MESSAGE_CHECK_FOR_URL сообщений
FIRST_STAGE_VIOLATION_MODIFICATOR = 1 # Сколько нарушений на 1 этапе проверки
SECOND_STAGE_VIOLATION_MODIFICATOR = 2 # Сколько нарушений на 2 этапе проверки
THIRD_STAGE_VIOLATION_MODIFICATOR = 3 # Сколько нарушений на 3 этапе проверки
VIOLATIONS_FOR_CHANGE_MODIFICATOR = 2 # Насколько умножить очки нарушений если сообщение было изменено

# Константы для расчета очков репутации
MAX_VIOLATIONS = 10 # Макс очков нарушений до мута
VIOLATION_POINTS_MULTIPLIER = 1  # 1 нарушение = X очков
REP_USER_DIVISOR = 10  # X очков репутации пользователя = -1 очко
REP_MODERATOR_DIVISOR = 3  # X очков репутации модератора = -1 очко
COUNT_MESSAGE_CHECK_FOR_URL = 1 # Количество первых сообщений для проверки на url
CHECK_FIRST_URL = True # Проверять первые COUNT_MESSAGE_CHECK_FOR_URL на ссылку?
COUNT_MINUS_MODERATOR_REP = 1 # Количество очков репутации модераторов которые будут сняты при муте
MINUS_MODERATOR_REP_WHEN_MUTING = True # Снимать COUNT_MINUS_MODERATOR_REP у пользователя при муте?

# === Пути к файлам базы данных ===
DATA_DIR = "data" # Каталог для базы данных
LOG_DIR = "logs/chat_bot/" # Каталог для логов
BAD_WORDS_FILE = f"{DATA_DIR}/bad_words.txt" # Файл базы запрещённых слов
EXCEPTIONS_FILE = f"{DATA_DIR}/exceptions.txt" # Файл базы исключений
REPLACEMENTS_FILE = f"{DATA_DIR}/replacements.txt" # Файл правил замены символов для 2 этара проверки
MODERATORS_FILE = f"{DATA_DIR}/moderators.txt" # Файл с id модераторами
GREETINGS_FILE = f"{DATA_DIR}/greetings.json" # Файл приветствий
TRIGGERS_FILE = f"{DATA_DIR}/triggers.json" # Файл шуток
DATABASE_FILE = f"{DATA_DIR}/users.db" # Файл базы SQLite
MEDIA_DIR = "media/" # Каталог медиа

# === Настройки Резервного копирования базы данных ===
ENABLED_BACKUP = True # Включить/отключить резервное копирование
INTERVAL_BACKUP = 3600 # Интервал в секундах
BACKUP_DIR = "backups" # Каталог для бэкапов
COMPRESS_BACKUP = True # Сжимать ли бэкапы в ZIP
DELETE_OLD_BACKUPS = True #Удалять старые бэкапы
BACKUP_MAX_FILES = 10 # Максимальное количество сохранённых бэкапов

# === Настройки шуток ===
ENABLE_JOKES = True # Включить шутки
CACHE_PAUSE = 0.1 # Пауза между кешированием медиа
# Поддерживаемые медиа-расширения для шуточных ответов
AUDIO_EXTENSIONS = (".mp3", ".ogg", ".wav", ".m4a")
VIDEO_EXTENSIONS = (".mp4", ".mov", ".avi", ".mkv")
PHOTO_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp")
MEDIA_EXTENSIONS = AUDIO_EXTENSIONS + VIDEO_EXTENSIONS + PHOTO_EXTENSIONS
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
# Резервное копирование
import threading
import zipfile
import shutil
import time
import os
# Дата и время
import datetime

# Конфигурация
from config import DATA_DIR, ENABLED_BACKUP, INTERVAL_BACKUP, BACKUP_DIR, COMPRESS_BACKUP, DELETE_OLD_BACKUPS, BACKUP_MAX_FILES, DEBUG_MODE
# Локализация
from languages import l

def cleanup_old_backups():
    """Удаляем старые бэкапы, оставляя только последние BACKUP_MAX_FILES"""
    if not DELETE_OLD_BACKUPS:
        return

    if not os.path.exists(BACKUP_DIR):
        return

    backups = sorted(os.listdir(BACKUP_DIR))

    if len(backups) > BACKUP_MAX_FILES:
        for old_backup in backups[:-BACKUP_MAX_FILES]:
            old_path = os.path.join(BACKUP_DIR, old_backup)
            if os.path.isfile(old_path):
                os.remove(old_path)
            elif os.path.isdir(old_path):
                shutil.rmtree(old_path)
            logger.info(f'{l("old_bakcup_delete")}: {old_path}')



def create_backup():
    """Создаём резервную копию каталога DATA_DIR"""
    if not ENABLED_BACKUP:
        return

    # Создаём каталог для бэкапов, если его нет
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    # Имя файла с датой и временем
    timestamp = datetime.datetime.now().strftime("%d%m%Y_%H%M%S")

    if COMPRESS_BACKUP:
        backup_name = f"{BACKUP_DIR}/{timestamp}_backup.zip"
        with zipfile.ZipFile(backup_name, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(DATA_DIR):
                for file in files:
                    file_path = os.path.join(root, file)
                    archive_name = os.path.relpath(file_path, ".")
                    zipf.write(file_path, archive_name)
        logger.debug(f'{l("create_backup")}: {backup_name}')
    else:
        backup_name = f"{BACKUP_DIR}/{timestamp}_backup"
        shutil.copytree(DATA_DIR, backup_name)
        logger.info(f'{l("create_backup")}: {backup_name}')

    # Удаляем старые бэкапы
    if DELETE_OLD_BACKUPS:
        cleanup_old_backups()



def schedule_backups():
    """Планируем автоматическое резервное копирование базы данных"""
    if not ENABLED_BACKUP:
        return

    # Создай бэкап при запуске
    create_backup()
    logger.info(l("start_backup_create"))

    def backup_cycle():
        while True:
            time.sleep(INTERVAL_BACKUP)
            create_backup()

    backup_thread = threading.Thread(target=backup_cycle, daemon=True)
    backup_thread.start()
    if DEBUG_MODE:
        logger.debug(f'{l("create_backups_startef")}: {INTERVAL_BACKUP} {l("seconds")})')
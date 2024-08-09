import os
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

# Использовался ранее для фильтрации выводимых сообщений в syslog
class SpecificMessageFilter(logging.Filter):
    def filter(self, record):
        return getattr(record, 'highlight', False)

class LoggerSetup:
    @staticmethod
    def setup_logging():
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        current_time = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(log_dir, f"log_{current_time}.log")
        error_log_file = os.path.join(log_dir, "error.log")

        # Настройка основного логгера
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        # Хэндлер для логирования в файл с ротацией по времени
        file_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=30, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Хэндлер для логирования ошибок в отдельный файл
        error_file_handler = logging.FileHandler(error_log_file, encoding='utf-8')
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(formatter)
        logger.addHandler(error_file_handler)

        # Хэндлер для логирования в системный журнал (journalctl через systemd)
        syslog_handler = logging.StreamHandler()  # StreamHandler будет улавливать stdout/stderr
        syslog_handler.setLevel(logging.INFO)
        syslog_handler.setFormatter(formatter)
        logger.addHandler(syslog_handler)

        # Удаление старых логов
        LoggerSetup.manage_old_logs(log_dir, backupCount=30)

        return log_file

    @staticmethod
    def manage_old_logs(log_dir, backupCount):
        log_files = sorted(
            [f for f in os.listdir(log_dir) if os.path.isfile(os.path.join(log_dir, f)) and f.startswith("log_")],
            key=lambda x: os.path.getmtime(os.path.join(log_dir, x))
        )
        while len(log_files) > backupCount:
            os.remove(os.path.join(log_dir, log_files.pop(0)))

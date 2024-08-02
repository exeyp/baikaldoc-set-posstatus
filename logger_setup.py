import os
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

class LoggerSetup:
    @staticmethod
    def setup_logging():
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = os.path.join(log_dir, f"log_{current_time}.log")
        error_log_file = os.path.join(log_dir, "error.log")

        # Настройка основного логгера
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        # Хэндлер для логирования в файл с ротацией по времени
        handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=30)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Хэндлер для логирования ошибок в отдельный файл
        error_handler = logging.FileHandler(error_log_file)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)

        # Удаление старых логов
        LoggerSetup.manage_old_logs(log_dir, backupCount=30)

    @staticmethod
    def manage_old_logs(log_dir, backupCount):
        log_files = sorted(
            [f for f in os.listdir(log_dir) if os.path.isfile(os.path.join(log_dir, f)) and f.startswith("log_")],
            key=lambda x: os.path.getmtime(os.path.join(log_dir, x))
        )
        while len(log_files) > backupCount:
            os.remove(os.path.join(log_dir, log_files.pop(0)))

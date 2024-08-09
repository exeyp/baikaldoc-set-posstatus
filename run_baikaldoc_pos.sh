#!/bin/bash

# Устанавливаем PYTHONPATH, чтобы Python мог найти модуль 'app'
export PYTHONPATH="$(dirname "$0")"

# Путь к проекту
PROJECT_DIR="/opt/baikaldoc-set-posstatus"

# Активируем виртуальное окружение
source "$PROJECT_DIR/.venv/bin/activate"

# Запускаем приложение и направляем логи в syslog
python "$PROJECT_DIR/app/main.py" 2>&1 | logger -t baikaldoc-pos

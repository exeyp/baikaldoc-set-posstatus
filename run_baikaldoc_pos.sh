#!/bin/bash

# Устанавливаем PYTHONPATH, чтобы Python мог найти модуль 'app'
export PYTHONPATH="$(dirname "$0")"

# Путь к проекту
PROJECT_DIR="/opt/baikaldoc-set-posstatus"

# Активируем виртуальное окружение
source "$PROJECT_DIR/.venv/bin/activate"

# Запускаем приложение
python "$PROJECT_DIR/app/main.py"

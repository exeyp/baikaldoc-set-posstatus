#!/bin/bash

# Определяем путь к проекту как директорию, где расположен скрипт
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Устанавливаем PYTHONPATH, чтобы Python мог найти модуль 'app'
export PYTHONPATH="$PROJECT_DIR"

# Проверка существования виртуального окружения
if [ ! -d "$PROJECT_DIR/.venv" ]; then
    echo "Виртуальное окружение не найдено в $PROJECT_DIR/.venv. Используется системный Python."
    PYTHON_CMD="python3"  # Используем системный Python
else
    # Активируем виртуальное окружение
    source "$PROJECT_DIR/.venv/bin/activate"
    PYTHON_CMD="python"
fi

# Запускаем приложение
$PYTHON_CMD "$PROJECT_DIR/app/main.py"

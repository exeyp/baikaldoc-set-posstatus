#!/bin/bash

# Запрос директории установки
read -p "Укажите директорию для установки [/opt/baikaldoc-set-posstatus]: " INSTALL_DIR
INSTALL_DIR=${INSTALL_DIR:-/opt/baikaldoc-set-posstatus}

# Проверка существования директории, если не существует - создать
if [ ! -d "$INSTALL_DIR" ]; then
    echo "Директория $INSTALL_DIR не существует. Создаю..."
    sudo mkdir -p "$INSTALL_DIR"
    sudo chown "$USER:$USER" "$INSTALL_DIR"
fi

# Копирование файлов в директорию установки
echo "Копирование файлов в $INSTALL_DIR..."
cp -R * "$INSTALL_DIR"

# Перемещение в директорию установки
cd "$INSTALL_DIR" || exit 1

# Создание и активация сервиса baikaldoc-pos.service
SERVICE_FILE="/etc/systemd/system/baikaldoc-pos.service"
TIMER_FILE="/etc/systemd/system/baikaldoc-pos.timer"

echo "Создание сервиса $SERVICE_FILE..."

sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=BaikalDoc POS Status Updater

[Service]
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/run_baikaldoc_pos.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOL

# Создание и активация таймера baikaldoc-pos.timer
echo "Создание таймера $TIMER_FILE..."

sudo bash -c "cat > $TIMER_FILE" <<EOL
[Unit]
Description=Run BaikalDoc POS Status Updater every hour

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
EOL

# Перезагрузка systemd, чтобы увидеть новые файлы сервисов и таймеров
echo "Перезагрузка systemd для обновления конфигурации..."
sudo systemctl daemon-reload

# Включение и запуск таймера
echo "Включение и запуск таймера..."
sudo systemctl enable baikaldoc-pos.timer
sudo systemctl start baikaldoc-pos.timer

echo "Установка завершена."

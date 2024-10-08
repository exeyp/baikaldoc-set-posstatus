# Обновление статусов ПОС

## Описание
В текущей реализации системы ДЕЛО рубрика "Статус ПОС" устанавливается вручную, а без установки этого статуса не происходит выгрузка на витринну данных ПОС.
Данное приложение предназначено для автоматического обновления статусов ПОС в зависимости от статуса ССТУ. Программа выполняет следующие основные функции:

1. Получение конфигурации и параметров для выполнения запросов.
2. Подключение к серверу ДЕЛО через GraphQL API.
3. Получение и обработка данных.
4. Формирование и выполнение мутаций для обновления статусов ПОС.

## Установка

1. Склонируйте репозиторий.
2. (опционально) В катологе проекта создайте и активируйте виртуальное окружение **.venv** 
3. Установите необходимые зависимости:

    ```bash
    pip install -r requirements.txt
    ```
4. (опционально) В каталоге проекта выполните скрипт **./install.sh** для установки systemd сервиса и таймера для более гибкого управления запуском приложения. Это упростит управление логированием и перезапусками в случае сбоев. Также скрипт предложит по-умолчанию каталог для установки /opt/baikaldoc-set-posstatus и скопирует в него все файлы проекта.

## Конфигурация

### processing_config.json 

- **statusMapping**: Сопоставление статусов ССТУ со статусами ПОС.
- **dateRange**: Параметры для настройки диапазона дат.
    - **useFixedDates**: Булево значение, указывающее, следует ли использовать фиксированные даты.
    - **startDate**: Начальная дата в формате `YYYY-MM-DD HH:MM:SS`, если `useFixedDates` установлено в true.
    - **endDate**: Конечная дата в формате `YYYY-MM-DD HH:MM:SS`, если `useFixedDates` установлено в true.
    - **maxDateRangeDays**: Максимальный диапазон дат в днях. Используется для проверки и корректировки диапазона дат.
- **pagination**: Параметры для настройки пагинации.
    - **pageSize**: Количество записей на одной странице запроса.
- **utcOffsetHours**: Смещение UTC в часах для локального часового пояса.

### connection_config.json

- **login_url**: URL для выполнения входа на сервер ДЕЛО.
- **logout_url**: URL для выполнения выхода с сервера ДЕЛО.
- **graphql_endpoint**: URL для выполнения GraphQL запросов.
- **username**: Имя пользователя для входа.
- **password**: Пароль пользователя для входа.
- **app**: Название приложения для аутентификации.

## Запуск

Выполните скрипт **./run_baikaldoc_pos.sh**

## Примеры служб systemd

/etc/systemd/system/baikaldoc-pos.service
```ini
[Unit]
Description=Baikaldoc POS Application

[Service]
WorkingDirectory=/opt/baikaldoc-set-posstatus
ExecStart=/opt/baikaldoc-set-posstatus/run_baikaldoc_pos.sh
StandardOutput=journal
StandardError=journal
```

/etc/systemd/system/baikaldoc-pos.timer
```ini
[Unit]
Description=Runs Baikaldoc POS Application every hour

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
```

### Активация и запуск таймера
```bash
sudo systemctl daemon-reload
sudo systemctl enable baikaldoc-pos.timer
sudo systemctl start baikaldoc-pos.timer
```

Проверка состояния тамера
```bash
systemctl list-timers
```

Выполнить службу немедленно
```bash
sudo systemctl start baikaldoc-pos.service
```

## Логирование
Приложение использует библиотеку `logging` для логирования. Логи сохраняются в директории `logs`.

- Основной лог: `logs/log_<date>.log`
- Лог ошибок: `logs/error.log`

При установке служб все сообщения также дублируются в системный журнал (journalctl). Логи выполнения в системном журнале:
```bash
journalctl -u baikaldoc-pos.service

```

## Дополнительные рекомендации
1. Более детально еализовать обработку ответов мутаций.
2. Добавить оповещение на электронную почту в случае ошибок.
3. Делать выборку РК не за период, а отслеживать события изменение "Статус ССТУ" и в зависимости от обновленного статуса изменять Статус ПОС.
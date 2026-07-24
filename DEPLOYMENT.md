# Развертывание парсера

## Варианты развертывания

### 1. Локальный компьютер (Windows/Linux/Mac)

#### Windows

1. Установите Python 3.8+
2. Настройте проект (см. QUICKSTART.md)
3. Запустите в фоновом режиме:
```bash
# В обычном режиме
python main.py start

# С перенаправлением вывода в файл
python main.py start > output.log 2>&1
```

#### Linux/Mac с systemd

Создайте файл `/etc/systemd/system/classifieds-parser.service`:

```ini
[Unit]
Description=Classifieds Site Parser Service
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/classifieds-site-scraper
Environment="PATH=/path/to/classifieds-site-scraper/venv/bin"
ExecStart=/path/to/classifieds-site-scraper/venv/bin/python main.py start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Запуск службы:
```bash
sudo systemctl daemon-reload
sudo systemctl enable classifieds-parser
sudo systemctl start classifieds-parser
sudo systemctl status classifieds-parser
```

### 2. VPS (DigitalOcean, Hetzner, AWS EC2)

1. Арендуйте VPS (минимум 1GB RAM)
2. Установите Python 3.8+:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

3. Загрузите проект:
```bash
git clone <repository-url>
cd classifieds-site-scraper
```

4. Настройте окружение:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. Настройте `.env` файл

6. Настройте systemd (см. выше) или используйте screen/tmux:
```bash
screen -S parser
python main.py start
# Нажмите Ctrl+A, затем D для отсоединения
```

### 3. Docker (Рекомендуется)

Создайте `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Создание директорий
RUN mkdir -p data logs

# Запуск
CMD ["python", "main.py", "start"]
```

Создайте `docker-compose.yml`:

```yaml
version: '3.8'

services:
  parser:
    build: .
    container_name: classifieds-parser
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - TZ=Europe/Moscow
```

Запуск:
```bash
docker-compose up -d
docker-compose logs -f
```

### 4. Heroku / Railway / Render

1. Создайте файл `Procfile`:
```
worker: python main.py start
```

2. Убедитесь, что `requirements.txt` актуален

3. Настройте переменные окружения в панели управления

4. Разверните через Git:
```bash
git push heroku main
# или через интерфейс платформы
```

### 5. Расписание задач (Cron/Task Scheduler)

Если не хотите запускать парсер 24/7, используйте cron (Linux) или Task Scheduler (Windows).

#### Linux Cron

```bash
crontab -e

# Запуск каждые 15 минут
*/15 * * * * cd /path/to/project && /path/to/venv/bin/python main.py once >> /path/to/logs/cron.log 2>&1
```

#### Windows Task Scheduler

1. Откройте Task Scheduler
2. Создайте новую задачу
3. Триггер: повторять каждые 15 минут
4. Действие: запустить программу
   - Программа: `C:\path\to\venv\Scripts\python.exe`
   - Аргументы: `main.py once`
   - Рабочая папка: `C:\path\to\project`

## Мониторинг и обслуживание

### Проверка логов

```bash
# Linux
tail -f logs/parser.log

# Windows
type logs\parser.log

# Docker
docker-compose logs -f
```

### Резервное копирование базы данных

```bash
# Ручное копирование
cp data/classifieds_parser.db data/backup_$(date +%Y%m%d).db

# Автоматическое (добавить в cron)
0 0 * * * cp /path/to/data/classifieds_parser.db /path/to/backups/backup_$(date +\%Y\%m\%d).db
```

### Обновление парсера

```bash
# Остановите парсер
systemctl stop classifieds-parser  # или Ctrl+C

# Обновите код
git pull

# Обновите зависимости
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Запустите снова
systemctl start classifieds-parser  # или python main.py start
```

## Оптимизация производительности

### Использование прокси

В `.env`:
```env
USE_PROXY=true
PROXY_URL=http://username:password@proxy-server:port
```

### Ротация прокси

Для продвинутых пользователей - реализуйте пул прокси в `base_parser.py`.

### База данных PostgreSQL

Для больших объемов замените SQLite на PostgreSQL:

1. Установите PostgreSQL
2. Измените в `.env`:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/classifieds_parser
```
3. Установите: `pip install psycopg2-binary`

## Безопасность

1. **Ограничьте доступ к .env файлу**:
```bash
chmod 600 .env
```

2. **Используйте firewall на VPS**:
```bash
sudo ufw enable
sudo ufw allow 22/tcp  # SSH
```

3. **Регулярно обновляйте зависимости**:
```bash
pip list --outdated
pip install --upgrade <package>
```

4. **Мониторинг**:
   - Настройте алерты в Telegram при ошибках
   - Используйте внешний мониторинг (UptimeRobot, Pingdom)

## Устранение проблем

### Высокое использование памяти
- Уменьшите `MAX_LISTINGS_PER_RUN`
- Увеличьте `PARSER_INTERVAL_MINUTES`

### Блокировка IP
- Используйте прокси
- Увеличьте задержки между запросами
- Уменьшите частоту парсинга

### Ошибки базы данных
- Проверьте права доступа к директории `data/`
- Перейдите на PostgreSQL для больших объемов

---

**Выберите подходящий вариант развертывания и следуйте инструкциям!**

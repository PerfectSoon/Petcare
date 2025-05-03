## 🚀 Установка и запуск через Docker Compose

1. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/PerfectSoon/Petcare.git
   cd petcare
   ```
2. Скопируйте .env:
    ```bash
    cp .env_example .env
   ```
3. Запуск через docker-compose:
    ```bash
    docker-compose up --build -d
   ```
4. Отдельно запуск тестов через docker-compose:
    ```bash
    docker compose --profile test up  
   ```

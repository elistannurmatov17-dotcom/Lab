# 🚀 DevOps HomeLab Project

Мой учебный DevOps-проект для практики работы с контейнерами, сетями, мониторингом и инфраструктурой.

Проект создан с целью изучения полного цикла развёртывания приложения:

- контейнеризация приложения через Docker
- управление сервисами через Docker Compose
- настройка обратного прокси Nginx
- подключение PostgreSQL базы данных
- мониторинг через Prometheus + Grafana
- управление контейнерами через Portainer


## 🏗 Архитектура проекта


```
                    Client
                      |
                      |
                    Nginx
                 (Reverse Proxy)
                      |
                      |
                 Flask API
                      |
                      |
                PostgreSQL DB


Monitoring:

        Flask API
            |
        /metrics
            |
       Prometheus
            |
        Grafana


Management:

        Portainer
            |
      Docker Socket
```


## 🛠 Используемые технологии


### Backend

- Python
- Flask
- psycopg2
- Prometheus Flask Exporter


### Database

- PostgreSQL 16


### Containers

- Docker
- Docker Compose


### Infrastructure

- Nginx
- Prometheus
- Grafana
- Portainer


## 📂 Структура проекта


```
DevOps-HomeLab/

├── app/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── postgres/
│   └── init.sql
│
├── nginx/
│   └── nginx.conf
│
├── prometheus/
│   └── prometheus.yml
│
├── grafana/
│
├── docker-compose.yml
│
├── notes.md
└── README.md

```


# 🚀 Запуск проекта


Клонировать проект:

```bash
git clone <repository>
cd DevOps-HomeLab
```


Запуск всех сервисов:

```bash
docker compose up -d
```


Пересборка контейнеров:

```bash
docker compose up -d --build
```


Остановка проекта:

```bash
docker compose down
```


Удаление контейнеров вместе с volume:

```bash
docker compose down -v
```



# 🌐 Доступ к сервисам


| Сервис | Адрес |
|---|---|
| Flask API | http://localhost:5000 |
| Nginx | http://localhost |
| PostgreSQL | localhost:5432 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |
| Portainer | http://localhost:9000 |



# 🔥 API


Главная страница:


```
GET /
```


Ответ:

```
DevOps HomeLab API
```



Получение пользователей:


```
GET /users
```


Пример ответа:

```json
[
 [
  1,
  "Elistan",
  "test@example.com"
 ]
]
```



# 📊 Monitoring


Flask приложение предоставляет метрики:


```
GET /metrics
```


Prometheus собирает метрики приложения.


Grafana используется для визуализации данных.



# 🐳 Docker сервисы


Запущенные контейнеры:


```
docker ps
```


Просмотр логов:


```
docker logs <container>
```


Вход внутрь контейнера:


```
docker exec -it <container> bash
```



# 🎯 Цели проекта


В процессе разработки были изучены:


- создание Dockerfile
- работа с Docker Compose
- Docker volumes
- Docker networks
- взаимодействие контейнеров
- PostgreSQL в контейнере
- reverse proxy через Nginx
- мониторинг приложения
- инфраструктурное управление


# 📚 Автор


DevOps HomeLab создан как учебный проект для развития навыков:

- Linux administration
- Docker
- Ansible
- CI/CD
- Monitoring
- Infrastructure as Code

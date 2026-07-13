# DevOps HomeLab Notes


## 1. Создание PostgreSQL контейнера


Использовали официальный образ:

```
postgres:16
```


Docker Compose:

```yaml
postgres:
  image: postgres:16
```


Подключение volume:

```yaml
volumes:

- postgres_data:/var/lib/postgresql/data
- ./postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
```


После первого запуска PostgreSQL автоматически выполнил:

```
init.sql
```


Создал таблицу users.


Проверка:

```bash
docker exec -it postgres-db psql -U admin -d appdb
```


SQL:

```sql
SELECT * FROM users;
```



---

# 2. Flask API


Создано приложение:


```
app/app.py
```


Использованные библиотеки:


```
flask
psycopg2-binary
prometheus-flask-exporter
```


requirements.txt:


```
flask
psycopg2-binary
prometheus-flask-exporter
```



Dockerfile:


```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["python","app.py"]
```



Сборка:


```bash
docker compose up -d --build
```



Проверка:


```bash
curl localhost:5000
```


Ответ:

```
DevOps HomeLab API
```



API:


```bash
curl localhost:5000/users
```



---

# 3. Docker Compose


Проверка конфигурации:


```bash
docker compose config
```



Запуск:


```bash
docker compose up -d
```


Остановка:


```bash
docker compose down
```


Удаление volume:


```bash
docker compose down -v
```



---

# 4. Nginx Reverse Proxy


Nginx принимает запросы на 80 порт:


```
localhost
```


И передает Flask:


```
flask-api:5000
```


Конфигурация:


```nginx
location / {

proxy_pass http://flask-api:5000;

}
```



Проверка:


```bash
curl localhost
```



---

# 5. Решение проблемы с портом 80


Ошибка:


```
bind: address already in use
```


Проверка:


```bash
ss -tulpn | grep :80
```


Нашли:


```
apache2
```


Остановили:


```bash
sudo systemctl stop apache2
```


После этого Nginx запустился.


---

# 6. Prometheus


Добавлен контейнер:


```
prom/prometheus
```


Порт:


```
9090
```


Проверка:


```bash
curl localhost:9090
```


Проверка получения метрик:


```bash
docker exec prometheus wget -qO- http://flask-api:5000/metrics
```



---

# 7. Grafana


Добавлен контейнер:


```
grafana/grafana
```


Порт:


```
3000
```


Используется для визуализации метрик Prometheus.


---

# 8. Portainer


Добавлен контейнер:


```
portainer/portainer-ce
```


Порт:


```
9000
```


Подключение Docker:


```yaml
- /var/run/docker.sock:/var/run/docker.sock
```



---

# Полезные Docker команды


Посмотреть контейнеры:

```bash
docker ps
```


Все контейнеры:

```bash
docker ps -a
```


Логи:


```bash
docker logs <name>
```


Статистика:


```bash
docker stats
```


Образы:


```bash
docker image ls
```


Volumes:


```bash
docker volume ls
```


Сети:


```bash
docker network ls
```


Войти в контейнер:


```bash
docker exec -it nginx bash
```



---

# Ошибки которые были решены


## Docker не мог скачать Python пакеты


Ошибка:


```
Temporary failure in name resolution
```


Причина:

Docker DNS.


Решение:

создали:


```
/etc/docker/daemon.json
```


Добавили:


```json
{
"dns": [
"8.8.8.8",
"8.8.4.4"
]
}
```


Перезапуск:


```bash
systemctl restart docker
```



---

# Итог


В проекте реализована полноценная DevOps инфраструктура:


✅ Docker контейнеризация

✅ Docker Compose

✅ Flask API

✅ PostgreSQL

✅ Nginx Reverse Proxy

✅ Prometheus Monitoring

✅ Grafana Dashboard

✅ Portainer Management


Следующий этап:

- CI/CD через GitHub Actions
- Ansible deployment
- HTTPS через Let's Encrypt
- Kubernetes
- Terraform

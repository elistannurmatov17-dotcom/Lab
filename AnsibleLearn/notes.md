Базовый синтаксис: ansible <хосты> -m <модуль> -a "<команда>" <флаги>

### Полезные флаги:
* -b (--become) — запуск от имени root (sudo).
* -K (--ask-become-pass) — спросить пароль от sudo (если требуется).
* -u <user> — подключиться под конкретным пользователем.

### Топовые Ad-Hoc примеры для практики:
```bash
# Проверить статус службы Docker на всех хостах под sudo
ansible all -m shell -a "systemctl status docker" -b

# Быстро убить зависший процесс nginx на хостах из группы web
ansible web -m shell -a "pkill -f nginx" -b

# Посмотреть последние 20 строк лога ошибок nginx
ansible all -m shell -a "tail -n 20 /var/log/nginx/error.log" -b

# Проверить, какие порты сейчас слушаются на сервере
ansible all -m shell -a "ss -tulpn" -b

- name: Получаем список установленных пакетов
  ansible.builtin.shell: dpkg -l | grep docker
  register: docker_packages
  failed_when: false # Не ронять плейбук, если grep ничего не найдет

- name: Выводим результат в терминал
  ansible.builtin.debug:
    msg: "Результат выполнения: {{ docker_packages.stdout }}"

- name: Попытка остановить кастомную службу (которая может не существовать)
  ansible.builtin.shell: systemctl stop my_secret_service
  ignore_errors: true

- name: Скачиваем и распаковываем архив, только если папка еще не создана
  ansible.builtin.shell: tar -xvf src.tar.gz -C /opt/app/
  args:
    chdir: /tmp
    creates: /opt/app/version.txt  # Если файл есть, задача пропустится (Success)

- name: Проверяем конфигурацию nginx
  ansible.builtin.shell: nginx -t
  register: nginx_check
  changed_when: false # Задача всегда будет зеленой (ok), а не желтой (changed)

- name: Применяем быстрые права на папки
  ansible.builtin.shell: "chmod {{ item.perms }} {{ item.path }}"
  loop:
    - { path: '/var/www/html', perms: '755' }
    - { path: '/var/www/html/index.html', perms: '644' }

my_cmd.stdout — чистый текстовый вывод команды.

my_cmd.stdout_lines — вывод в виде списка строк (удобно для циклов).

my_cmd.stderr — текст ошибки, если она была.

my_cmd.rc — код возврата (Return Code). 0 — успех, всё остальное — ошибка.

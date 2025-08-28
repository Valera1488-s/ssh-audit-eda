# ssh-audit-eda

Мини‑сервис для аудита настроек SSH (`sshd_config`) и мониторинга регулярного запуска контейнеров с Ansible‑ролями (EDA jobs).

## Что внутри
- Роль Ansible `ssh_audit` — читает эффективную конфигурацию через `sshd -T -f <путь>` и пишет единострочный JSON‑лог в `/var/log/ansible-ssh-audit.log`.
- Скрипт `scripts/parse_ssh_config.py` — сверяет `sshd_config` с эталоном и выводит JSON, совместимый с форматом роли.
- Монитор `eda_job_monitor/check_jobs.py` — проверяет, что контейнеры `ansible-job-*` запускались за последние N часов и завершались успешно.
- Контейнеризация (`docker/Dockerfile`) и `entrypoint.sh` для запуска роли.
- CI (GitHub Actions) с этапами: lint → build → test → jq‑валидация.

## Быстрый старт (локально)

Требования: Docker, GNU Make, jq.

```bash
cd /home/vvv/k8s-lab/ssh-audit-eda

# Сборка контейнера
make build

# Прогон роли внутри контейнера против примера конфигурации
make run

# Проверка, что лог корректный JSON (jq вернёт 0)
make check
```

## Структура

```
roles/ssh_audit/           # Ansible‑роль аудита SSH (комментарии на русском)
docker/Dockerfile          # Образ с ansible + sshd + jq
entrypoint.sh              # Точка входа: запускает playbook роли
playbook.yml               # Локальный запуск роли
inventory.ini              # Локальный инвентарь
scripts/parse_ssh_config.py# Python‑скрипт сверки по эталону
eda_job_monitor/check_jobs.py # Мониторинг контейнеров ansible-job-*
example/sshd_config        # Пример входного sshd_config для теста
.github/workflows/ansible.yml # CI: lint/build/test/jq
```

## Формат лога

Одна строка JSON, например:

```json
{"timestamp":"2025-07-01T12:34:56Z","host":"localhost","ansible_version":"2.15.0","ansible_user":"root","message":{"status":"compliant"}}
```

Если есть несоответствия, параметры и их фактические значения добавляются в `message`.

## Лицензии и ссылки
- OpenSSH sshd_config(5): https://man7.org/linux/man-pages/man5/sshd_config.5.html
- Ansible Roles: https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_roles.html
- Event‑Driven Ansible: https://docs.ansible.com/event-driven-ansible/latest/


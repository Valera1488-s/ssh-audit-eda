FROM python:3.11-slim

# Устанавливаем ansible, jq и openssh-client (для sshd -T понадобится openssh-server, но для парсинга используем бинарь sshd)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ansible \
    openssh-server \
    jq \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем проект
COPY roles ./roles
COPY playbook.yml inventory.ini entrypoint.sh ./
COPY example ./example

# Права на entrypoint
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]


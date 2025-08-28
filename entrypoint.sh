#!/bin/sh
set -euo pipefail

# Комментарии на русском: запускаем локальный плейбук роли ssh_audit
ansible-playbook -i inventory.ini playbook.yml -e "ansible_python_interpreter=/usr/bin/python3"


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт сверки sshd_config с эталоном. На вход:
  1) путь к sshd_config
  2) путь к JSON с эталонными значениями
Выводит единострочный JSON в формате роли ssh_audit.
"""

import json
import sys
from datetime import datetime, timezone


def load_expected(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_config(path: str) -> dict:
    result = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) >= 2:
                key = parts[0]
                value = ' '.join(parts[1:])
                result[key] = value
    return result


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: parse_ssh_config.py <sshd_config> <expected.json>", file=sys.stderr)
        return 2

    sshd_path = sys.argv[1]
    expected_path = sys.argv[2]

    expected = load_expected(expected_path)
    actual = load_config(sshd_path)

    fields = [
        'PermitRootLogin',
        'PasswordAuthentication',
        'MaxAuthTries',
        'ChallengeResponseAuthentication',
        'X11Forwarding',
    ]

    mismatches = {k: actual.get(k, '') for k in fields}
    status = 'compliant' if all(str(expected.get(k, '')) == str(mismatches.get(k, '')) for k in fields) else 'non-compliant'

    payload = {
        'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'host': 'localhost',
        'ansible_version': 'n/a',
        'ansible_user': 'n/a',
        'message': {'status': status} if status == 'compliant' else {
            'status': status,
            **mismatches,
        }
    }

    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())



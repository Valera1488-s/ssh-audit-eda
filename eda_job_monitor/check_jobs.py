#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Простой монитор контейнеров ansible-job-*.
Требует установленный Docker CLI. Проверяет, что каждый контейнер с именем
начинающимся на 'ansible-job-' запускался за последние N часов и завершился успешно.
Выводит JSON с полями status=healthy/unhealthy и деталями по заданиям.
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone


def run(cmd):
    return subprocess.check_output(cmd, text=True)


def list_jobs():
    # Имя и статус выхода последнего контейнера ansible-job-*
    fmt = '{{.Names}};{{.Status}};{{.RunningFor}};{{.CreatedAt}};{{.ID}};{{.State}};{{.ExitCode}}'
    out = run(['docker', 'ps', '-a', '--format', fmt])
    items = []
    for line in out.splitlines():
        name, status, running_for, created_at, cid, state, exitcode = (line + ';;;;;;').split(';', 6)
        if name.startswith('ansible-job-'):
            items.append({
                'name': name,
                'status_text': status,
                'running_for': running_for,
                'created_at': created_at,
                'id': cid,
                'state': state,
                'exit_code': exitcode.strip(),
            })
    return items


def main() -> int:
    hours = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    threshold = datetime.now(timezone.utc) - timedelta(hours=hours)

    jobs = list_jobs()
    details = {}
    ok = True
    for job in jobs:
        # CreatedAt в формате Docker можно парсить через fromisoformat с заменой Z
        ts = job['created_at'].replace('Z', '+00:00')
        try:
            created = datetime.fromisoformat(ts)
        except ValueError:
            created = None

        last_seen_ok = (created is not None and created >= threshold)
        success = (job['state'] == 'exited' and job['exit_code'] == '0')

        details[job['name']] = {
            'executed_at': created.isoformat().replace('+00:00', 'Z') if created else job['created_at'],
            'success': success,
        }
        ok = ok and last_seen_ok and success

    payload = {
        'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'host': 'eda-node-1',
        'message': {
            'status': 'healthy' if ok else 'unhealthy',
            'jobs': details,
        }
    }
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())



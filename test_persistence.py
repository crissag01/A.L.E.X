#!/usr/bin/env python
import sqlite3

conn = sqlite3.connect('Memory/alex.db')
cursor = conn.execute('SELECT COUNT(*) FROM conversation_turns WHERE channel = ?', ('cli',))
count = cursor.fetchone()[0]
print(f'Turnos CLI en BD: {count}')

if count > 0:
    cursor = conn.execute('SELECT role, content FROM conversation_turns WHERE channel = ? ORDER BY id DESC LIMIT 5', ('cli',))
    rows = cursor.fetchall()
    for role, content in reversed(rows):
        print(f'{role}: {content[:80]}...')
else:
    print('(sin turnos aun)')

#!/usr/bin/python3

#
# Author: jun10000 (https://github.com/jun10000)
#

import cgi
import subprocess
import pymysql
import yaml
import json
from datetime import datetime

class DateTimeJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

def execute_shell(cmdline):
    return subprocess.run(cmdline, shell=True, executable='/bin/bash', stdout=subprocess.PIPE)

print('Content-Type: application/json')
print()

with open('/var/project/onkyori_common/settings.yaml', 'r') as file:
    settings = yaml.load(file)

data = cgi.FieldStorage()
mode = data.getvalue('mode', '')

if mode == 'switch_brightness':
    file_path = '/sys/class/backlight/rpi_backlight/brightness'
    with open(file_path, 'r+') as file:
        brightness_old = int(file.read())
        brightness_new = 255 if brightness_old != 255 else 12
        file.seek(0)
        file.write(str(brightness_new))
        file.truncate()
elif mode == 'listen_onkyori':
    arg_id_min = data.getvalue('id_min', 0)
    arg_id_max = data.getvalue('id_max', 1000000000)
    id_min = int(arg_id_min)
    id_max = int(arg_id_max)

    db = pymysql.connect(
        host = settings['Database']['Host'],
        user = settings['Database']['User'],
        password = settings['Database']['Password'],
        database = settings['Database']['Name'],
        cursorclass = pymysql.cursors.DictCursor)

    with db.cursor() as db_cursor:
        db_cursor.execute(
            'SELECT * FROM signals WHERE id BETWEEN %s AND %s ORDER BY id',
            (id_min, id_max))
        result = db_cursor.fetchall()
    db.close()

    print(json.dumps(result, cls=DateTimeJsonEncoder, indent=4))
elif mode == 'listen_recent_onkyori':
    db = pymysql.connect(
        host = settings['Database']['Host'],
        user = settings['Database']['User'],
        password = settings['Database']['Password'],
        database = settings['Database']['Name'],
        cursorclass = pymysql.cursors.DictCursor)

    with db.cursor() as db_cursor:
        db_cursor.execute('SELECT * FROM signals ORDER BY id DESC LIMIT 1')
        result = db_cursor.fetchall()
    db.close()

    print(json.dumps(result, cls=DateTimeJsonEncoder, indent=4))

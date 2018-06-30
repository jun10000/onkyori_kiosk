#!/usr/bin/python3

#
# Author: jun10000 (https://github.com/jun10000)
#

import cgi
import pymysql
import yaml
import json
from datetime import datetime

class DateTimeJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

class Display:
    _FILE_BRIGHTNESS = '/sys/class/backlight/rpi_backlight/brightness'

    @staticmethod
    def get_brightness():
        with open(Display._FILE_BRIGHTNESS, 'r') as file:
            return int(file.read())

    @staticmethod
    def set_brightness(value):
        with open(Display._FILE_BRIGHTNESS, 'w') as file:
            file.write(str(value))
            file.truncate()

print('Content-Type: application/json')
print()

with open('/var/project/onkyori_common/settings.yaml', 'r') as file:
    settings = yaml.load(file)

data = cgi.FieldStorage()
mode = data.getvalue('mode', '')

if mode == 'switch_brightness':
    old_value = Display.get_brightness()
    new_value = 255 if old_value != 255 else 12
    Display.set_brightness(new_value)
elif mode == 'to_lighten':
    Display.set_brightness(255)
elif mode == 'to_darken':
    Display.set_brightness(12)
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

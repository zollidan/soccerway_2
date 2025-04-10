import xlwt
import random
import os
from datetime import datetime

# Режим отладки
DEBUG_MODE = False

# Красивые надписи
QUITE_MODE = True

# -------------- #
#     Parser     #
# -------------- #

# Базовая ссылка
BASE_LINK = "https://uk.soccerway.com/matches/"

# Основные ссылки для сбора матчей
BASE_MATCH_URL = "https://uk.soccerway.com/matches/"
BASE_MATCH_LINK = "https://uk.soccerway.com"

# User agent
try:
    with open('user-agent.txt', 'r') as user_agent:
        USER_AGENT = random.choice(user_agent.readlines()).strip()
except Exception as e:
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0'
    print("[!] Badly, but not a problem. Error reading 'user-agent.txt' [!]\n[args]:\n\t", e)
# Значение по умолчнию, если возникнет ошибка
DEFAULT_DATE_STR = "1999-01-01"
DEFAULT_MATCH_ID = '777666777'
DEFAULT_STAGE_VALUE = 1
DEFAULT_LEAGUE_NAME = "No Name"

# -------------- #
#      Date      #
# -------------- #

# Пределы возможных годов
MIN_YEAR = 1900
MAX_YEAR = 2200

# Стандатный формат для даты
FORMAT_DATE = "%Y-%m-%d"

# -------------- #
#    Request     #
# -------------- #

# Максимальное кол-во для повторного запроса
MAX_COUNT_RESPONSE = 10

# Задержка в секундах перед повторным запросом
DELAY_RESPONSE = 0.7

# -------------- #
#      EXEL      #
# -------------- #

# Header
HEADER_EXEL = ['Число', 'Месяц', 'Год', 'Время',
               'Команда_1', 'Команда_2',
               'Кол-во игр очн. (50)', 'Сумма мячей очн. (50)',
               'Кол-во игр очн. (3)', 'Сумма мячей очн. (3)',
               'Кол-во игр очн. (5)', 'Сумма мячей очн. (5)',
               'Кол-во игр хозяев (50)', 'Сумма мячей хозяев (50)',
               'Кол-во игр хозяев (3)', 'Сумма мячей хозяев (3)',
               'Кол-во игр хозяев (5)', 'Сумма мячей хозяев (5)',
               'Кол-во игр гостей (50)', 'Сумма мячей гостей (50)',
               'Кол-во игр гостей (3)', 'Сумма мячей гостей (3)',
               'Кол-во игр гостей (5)', 'Сумма мячей гостей (5)',
               'Страница', 'Лига'
               ]

# Стили для ячеек
STYLE_HEAD = xlwt.easyxf('font: name Arial, bold on; pattern: pattern solid, fore_colour light_yellow; align: wrap on,vert centre, horiz center;')
STYLE_TIMES_NEW_ROMAN = xlwt.easyxf('font: name Times New Roman;')

# Название выходного файла
EXEL_NAME = 'database'

# Максимальное кол-во попыток сохрнаить файл
MAX_COUNT_REPEAT_EXEL = 20

#####################
#    Quite Mode     #
#####################

WORK_IS_DONE_MESSAGE = """ 
███████████████████████████████████████████████████████████████████
█▄─█▀▀▀█─▄█─▄▄─█▄─▄▄▀█▄─█─▄███▄─▄█─▄▄▄▄███▄─▄▄▀█─▄▄─█▄─▀█▄─▄█▄─▄▄─█
██─█─█─█─██─██─██─▄─▄██─▄▀█████─██▄▄▄▄─████─██─█─██─██─█▄▀─███─▄█▀█
▀▀▄▄▄▀▄▄▄▀▀▄▄▄▄▀▄▄▀▄▄▀▄▄▀▄▄▀▀▀▄▄▄▀▄▄▄▄▄▀▀▀▄▄▄▄▀▀▄▄▄▄▀▄▄▄▀▀▄▄▀▄▄▄▄▄▀
"""

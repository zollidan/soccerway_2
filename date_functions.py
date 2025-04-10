
from datetime import datetime, timedelta
from constants import *

# Проверка даты на правильность
def chech_valid_date(str_date):

    """ 
    chech_valid_date(str_date): return True|False
    """

    try:
        dt = datetime.strptime(str_date, FORMAT_DATE)
        year = dt.year

        if DEBUG_MODE:
            print(dt)

        return (year >= MIN_YEAR) & (year <= MAX_YEAR)
    except:
        return False

# Получить предел дат
def get_date_limit():

    """
    get_date_limit(): return [str_date, str_date]
    """

    # Варианты сообщений
    first_message        = "Введите начальную дату [формат: гггг-мм-дд]: "
    second_message = "Введите конечную дату  [формат: гггг-мм-дд]: "
    error_message      = "Неверный формат, повторите попытку\n"
    tip                              = "(Подсказка)"

    # Ввод начальной даты с проверкой на правильность
    date_start = input(first_message)
    while chech_valid_date(date_start) == False:
        print(error_message)
        date_start = input(first_message)
    
    # Ввод конечной даты с проверкой на правильность (конечная дата должна быть больше, либо равна начальной)
    date_end = input(second_message)
    while (chech_valid_date(date_end) == False) | (date_end < date_start):
        print(error_message)
        print(tip, "Начальная дата:", date_start)
        date_end = input(second_message)

    return (date_start, date_end)

# Создание списка дат из установленного предела
def make_date_list(date_start, date_end):

    """
    make_date_list(str_date, str_date):
        return dict(str_date, str_date, ...)
    """

    date_list = [ date_start ]
    
    day = timedelta(days=1)

    # Если это больше чем один день
    if date_start != date_end:
        dt = datetime.strptime(date_start, FORMAT_DATE)
        while (True):
            dt += day
            str_date = dt.strftime(FORMAT_DATE)

            date_list.append(str_date)

            if str_date == date_end:
                break
    
    if DEBUG_MODE:
        print("Date List:", date_list)
    
    return date_list

def timestamp_to_datetime(timestamp):

    """ Преобразовать timestamp в Datetime """ 

    timestamp = int(timestamp)
    return datetime.fromtimestamp(timestamp)

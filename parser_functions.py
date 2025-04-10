from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import urllib
import re
from tqdm import tqdm

from date_functions import *
from request_functions import *

from constants import *


def get_macthes_from_leage(leage_info):
    """ Получить список матчей с Лиги
    
        match_info = {
            home_team_name: str
            away_team_name: str

            home_team_id:   int
            away_team_id:   int

            link:           url_to_match
            match_date:     datetime

            league_name:    str
        }

    """

    date_str = leage_info.get('date', DEFAULT_DATE_STR)
    leage_id = leage_info.get('leage_id', DEFAULT_MATCH_ID)
    league_name = leage_info.get('league_name', DEFAULT_LEAGUE_NAME)

    get_params = {
        'callback_params': {},
        'block_id': "comp",
        'action': "loadcomp",
        'params': {"d": date_str, "c": leage_id}
    }
    get_params['params'] = json.dumps(get_params)

    link = 'https://uk.soccerway.com/a/block_livescores?callback_params={}&block_id=comp&action=loadcomp&params={"d":"' + date_str + '","c":' + leage_id + '}'
    json_response = get_response(link, True)
    content = json_response['commands'][0]['parameters']['content']
    soup = BeautifulSoup(content, "lxml")

    macthes_from_leage = []
    for row in soup.find_all("li", "livescore_match"):

        # Берём инфу даже если матч был перенесён или отменён
        link = BASE_MATCH_LINK + row.find("div", "teams").find("a").get('href')

        try:
            home_team_name = row.find("div", "team_a").find("div", "team_name").text.strip()
            home_team_id = int(row.find("div", "team_a").find("img").get("src").split('/')[-1].split('.')[0])
        except:
            if DEBUG_MODE:
                print("[ - Error - ] Main Team")
                sleep(5)
            continue

        try:
            away_team_name = row.find("div", "team_b").find("div", "team_name").text.strip()
            away_team_id = int(row.find("div", "team_b").find("img").get("src").split('/')[-1].split('.')[0])
        except:
            if DEBUG_MODE:
                print("[ - Error - ] Away Team")
                sleep(5)
            continue

        try:
            timestamp = datetime.strptime(row.find("div", "timebox").find("time").get("datetime")[:19], '%Y-%m-%dT%H:%M:%S').timestamp()
            match_date = timestamp_to_datetime(timestamp)
        except:
            match_date = datetime.now()
            if DEBUG_MODE:
                print("[ - Error - ] Get Date")
                sleep(5)

        match = {
            'home_team_name': home_team_name,
            'away_team_name': away_team_name,

            'home_team_id': home_team_id,
            'away_team_id': away_team_id,

            'match_date': match_date,
            'link': link,

            'league_name': league_name,
        }
        macthes_from_leage.append(match)

    return macthes_from_leage


# Собрать ссылки на матчи с главной страницы
def get_matches(response, date_str):
    matches_from_page = []

    try:

        soup = BeautifulSoup(response.content, "lxml")

        print("[ Prepaing All Mathes ]")
        for i, leage in enumerate(soup.find_all('div', class_='livescores-comp')):

            try:
                leage_id = leage.get("data-comp")
            except:
                if DEBUG_MODE:
                    print('[ - Error - ] Match ID:', leage)
                    sleep(5)
                continue
            try:
                league_name = leage.find_all("span", class_="comp-name")[0].text
            except:
                league_name = DEFAULT_LEAGUE_NAME
                if DEBUG_MODE:
                    print('[ - Error - ] Match League Name:', leage_id)
                    sleep(5)
            leage_info = {
                'date': date_str,
                'leage_id': leage_id,
                'league_name': league_name,
                'stage_value': i
            }

            matches_info = get_macthes_from_leage(leage_info)
            matches_from_page.extend(matches_info)


    except:
        if DEBUG_MODE:
            print("[ - Error - ] Get_mathches_links()\n", "∟ Link:", response.url)
            sleep(5)
    finally:
        return matches_from_page


# Получить ID команды из href
def get_team_id(href):
    try:
        team_split = href.split('/')

        team_id = team_split[len(team_split) - 2]
        team_id = int(team_id)

        return team_id
    except:
        if DEBUG_MODE:
            print("[ - Error - ] Get Team ID")
            print("∟ Href:", href)
            sleep(5)
        return None


def get_change_page_link(home_team_id, away_team_id, page):
    ''' Получить ссылку на слелующий блок матчей '''

    # Т. к. мы листаем назад
    page *= -1

    params = {
        'page': page
    }

    callback_params = {
        'page': page + 1,
        'block_service_id': "match_h2h_comparison_block_h2hmatches",
        'team_A_id': home_team_id,
        'team_B_id': away_team_id
    }

    # Если нужна первая страницы
    if page == 0:
        callback_params['page'] = -1

    get_params = {
        'block_id': "page_match_1_block_h2hsection_head2head_7_block_h2h_matches_1",
        'action': "changePage",
        'callback_params': json.dumps(callback_params),
        'params': json.dumps(params)
    }

    link = "https://uk.soccerway.com/a/block_h2h_matches?" + (urllib.parse.urlencode(get_params))
    return link


def get_matches_list(req_res):
    ''' Получить список матчей со страницы, не учитывая не состоявшиеся'''

    matches_list = []
    for match_row in req_res.find_all("tr", "match"):
        try:

            match_elem = {}
            match_elem['home_team_id'] = get_team_id(match_row.find("td", "team-a").find("a").get("href"))
            match_elem['home_team_name'] = match_row.find("td", "team-a").find("a").text

            match_elem['away_team_id'] = get_team_id(match_row.find("td", "team-b").find("a").get("href"))
            match_elem['away_team_name'] = match_row.find("td", "team-b").find("a").text

            scores = match_row.find("td", "score").find("a").text
            scores_list = get_scores(scores)

            home_team_score = int(scores_list[0])
            away_team_score = int(scores_list[1])

            match_elem['home_team_score'] = home_team_score
            match_elem['away_team_score'] = away_team_score

            str_data_value = match_row.find("td", "day").find("span").get("data-value")
            str_real_date = match_row.find("td", "full-date")

            if str_data_value == None:
                str_data_value = 0
            else:
                str_data_value = int(str_data_value)

            if str_real_date == None:
                str_real_date = "1900-01-01"
            else:
                str_real_date = str_real_date.text

            match_elem['start_time'] = str_data_value
            match_elem['real_date'] = str_real_date

            # Добавить элемент в общий лист
            matches_list.append(match_elem)
        except:
            if DEBUG_MODE:
                print("[ - Error - ] Match Elem:", match_row)
                sleep(5)
            continue

    return matches_list


def get_h2h_list(match_info, need=50):
    ''' Вернуть список общих матчей '''

    # Need - максимально нужное кол-во матчей

    # В случаи ошибки
    head_to_head = {}

    try:

        home_team_name = match_info['home_team_name']
        away_team_name = match_info['away_team_name']

        match_date = match_info['match_date']

        home_team_id = match_info['home_team_id']
        away_team_id = match_info['away_team_id']

        head_to_head = {
            'home_team_name': home_team_name,
            'away_team_name': away_team_name,
            'home_team_id': home_team_id,
            'away_team_id': away_team_name,
            'date': match_date,  # datetime object
            'home': [],
            'away': [],
            'all': [],
        }

        page = 0
        while True:
            link = get_change_page_link(home_team_id, away_team_id, page)

            matches_list = get_matches_from_h2h_page(link)

            # Если этой страницы не существует
            if len(matches_list) == 0:
                break

            # [ Вид элемента в списке ]
            # 
            # match_elem = {
            #   home_team_id:   int
            #   away_team_id:   int
            #   score_home:     int
            #   score_away:     int
            #   match_date:     str [dd/mm/yy]
            # }

            # Порядок дат - от большей к меньшей

            for match in matches_list:

                # Проверка времени
                if match['match_date'] >= head_to_head['date']:
                    continue

                # Добавление в конкретную категорию
                if head_to_head['home_team_id'] == match['home_team_id']:
                    head_to_head['home'].append(match)
                else:
                    head_to_head['away'].append(match)

                # Добавление в общую категорию
                head_to_head['all'].append(match)

                # Если нужное кол-во уже собрано - остановиться
                if min(len(head_to_head['home']), len(head_to_head['away'])) >= need:
                    break

            # Если нужное кол-во уже собрано - остановиться
            if min(len(head_to_head['home']), len(head_to_head['away'])) >= need:
                break

            page += 1

    except:
        if DEBUG_MODE:
            print("[ - Error - ] Get H2H List:", match_info)
            sleep(5)

    finally:
        return head_to_head


def get_matches_from_h2h_page(link):
    """ Вернуть список матчей c h2h страницы """

    # [ Вид элемента в списке ]
    # 
    # match_elem = {
    #   home_team_id:   int
    #   away_team_id:   int
    #   score_home:     int
    #   score_away:     int
    #   match_date:     datetime
    #   D:              int [0 - нет, 1 - слева, 2 - справа]
    # }

    try:

        json_change_page_response = get_response(link, True)
        change_page_content = json_change_page_response['commands'][0]['parameters']['content']

        page_soup = BeautifulSoup(change_page_content, "lxml")
        matches_list = []

        for line in page_soup.find_all("tr", "match"):
            try:

                home_team_id = get_team_id(line.find("td", "team-a").find("a").get("href"))
                away_team_id = get_team_id(line.find("td", "team-b").find("a").get("href"))

                # Если Матч Перенесён или Отменён
                if line.find("td", "score") == None:
                    continue

                D = line.find("span", "addition-visible")
                if D != None:
                    if D.find("score-addition-left") != None:
                        D = 1
                    else:
                        D = 2
                else:
                    D = 0

                score = line.find("td", "score").find("a").text
                score_list = get_scores(score, D)

                score_home = int(score_list[0])
                score_away = int(score_list[1])

                # TIMESPAN TO DATE
                timestamp = line.find("td", "full-date").find("span").get("data-value")
                timestamp = int(timestamp)
                match_date = timestamp_to_datetime(timestamp)

                match_elem = {
                    'home_team_id': home_team_id,
                    'away_team_id': away_team_id,
                    'score_home': score_home,
                    'score_away': score_away,
                    'match_date': match_date,
                    'D': D,
                }

                matches_list.append(match_elem)

            except:
                if DEBUG_MODE:
                    print("[ ! ! ! ] Матч потерян [ ! ! ! ]", line)
                    sleep(10)
    except:
        if DEBUG_MODE:
            print("[ - Error - ] Change Page Request")
            sleep(5)
    finally:
        return matches_list


def get_match_stats(matches_list, team_id, need):
    """ Получить статистику из указанных матчей """

    stats = {}

    win = 0
    draw = 0  # Ничья
    lose = 0

    more_2_5 = 0
    less_2_5 = 0

    # Список всех забитых мячей
    goals_home = []
    goals_away = []
    goals_all = []

    try:
        i = 0
        for match in matches_list:

            # Кол-во нужнных данных было достигнуто
            if i >= need:
                break

            score_home = match['score_home']
            score_away = match['score_away']

            # Если этот матч на поле команды Б, переврнуть резльтаты
            if match['home_team_id'] != team_id:
                score_home, score_away = score_away, score_home

            # Условаия победы и поражения
            if score_home > score_away:
                win += 1
            elif score_home < score_away:
                lose += 1

            # Ничья
            if score_home == score_away:
                draw += 1

            # Кол-во мячей больше 2,5
            if (match['score_home'] + match['score_away']) > 2.5:
                more_2_5 += 1
            else:
                less_2_5 += 1

            # Распределение голов
            goals_home.append(score_home)
            goals_away.append(score_away)

            goals_all.append(score_home + score_away)

            i += 1

        stats = {
            'win': win,
            'draw': draw,
            'lose': lose,
            'more_2_5': more_2_5,
            'less_2_5': less_2_5,
            'goals_home': goals_home,
            'goals_away': goals_away,
            'goals_all': goals_all,
        }

    except:
        if DEBUG_MODE:
            print("[ - Error - ] Get Match Stats")
            sleep(5)
    finally:
        return stats


def get_scores(scores, D=0):
    """ Вернуть счёт команды из строки вида '3 - 1' """

    # Значения, в случаи ошибки
    home_team_score = 0
    away_team_score = 0

    try:

        score_split = scores.split('-')

        home_team_score = score_split[0]
        away_team_score = score_split[-1]

        home_team_score = re.sub(r"\D", "", home_team_score)
        away_team_score = re.sub(r"\D", "", away_team_score)

        home_team_score = int(home_team_score)
        away_team_score = int(away_team_score)

        # Если пенальти или дисквал
        if D != 0:
            if home_team_score > away_team_score:
                home_team_score = away_team_score
            else:
                away_team_score = home_team_score

        if DEBUG_MODE:
            print(home_team_score, ":", away_team_score, "\tD:", D)
    except:
        if DEBUG_MODE:
            print("[ - Error - ]")
            print("[ Get Score From Str ]:", scores)
            sleep(5)
    finally:
        return [home_team_score, away_team_score]


def get_matches_with_filter(team_id, match_date, need, filter="all"):
    """ Вернуть список матчей команды c team_id с условием фильтра """

    # Need - минимальное кол-во матчей

    # В случаи ошибки
    filtered_matches = []

    try:

        page = 0
        while True:

            link = get_filtered_matches_link(team_id, filter, page)

            matches_list = get_matches_with_filter_from_page(link)

            # Если этой страницы не существует
            if len(matches_list) == 0:
                break

            # [ Вид элемента в списке ]
            # 
            # match_elem  = {
            #   home_team_id:   int
            #   score_home:     int
            #   score_away:     int
            #   D:              int [0 - нет, 1 - слева, 2 - справа]
            #   match_date:     datetime
            # }

            for match in matches_list:

                # Проверка времени
                if match['match_date'] >= match_date:
                    if DEBUG_MODE:
                        print(match['match_date'].strftime(FORMAT_DATE), ">=", match_date.strftime(FORMAT_DATE))
                    continue

                # Добавление в список
                filtered_matches.append(match)

                # Если нужное кол-во уже собрано - остановиться
                if len(filtered_matches) >= need:
                    break

            # Если нужное кол-во уже собрано - остановиться
            if len(filtered_matches) >= need:
                break

            page += 1

    except:
        if DEBUG_MODE:
            print("[ - Error - ] Get Macthes With Filter:", filtered_matches)
            print("[ - Team_ID - ]", team_id)
            sleep(5)
    finally:
        return filtered_matches


def get_matches_with_filter_from_page(link):
    """ Вернуть список матчей из запроса 'Матчи с фильтром'  """

    # [ Вид элемента в списке ]
    # 
    # match_elem = {
    #   home_team_id:   int
    #   score_home:     int
    #   score_away:     int
    #   D:              int [0 - нет, 1 - слева, 2 - справа]
    #   match_date:     datetime
    # }

    matches_list = []

    try:

        json_change_page_response = get_response(link, True)
        change_page_content = json_change_page_response['commands'][0]['parameters']['content']

        page_soup = BeautifulSoup(change_page_content, "lxml")

        # Порядок дат - от меньшей к большей

        # Перевернуть задом наперёд, так как чем ниже в списке, тем раньше событие
        tr_list = page_soup.find_all("tr", "match")[::-1]

        for line in tr_list:
            try:

                # Если Матч Перенесён или Отменён
                if line.find("td", "score") == None:
                    continue

                home_team_id = get_team_id(line.find("td", "team-a").find("a").get("href"))
                away_team_id = get_team_id(line.find("td", "team-b").find("a").get("href"))

                D = line.find("span", "addition-visible")
                if D != None:
                    if D.find("score-addition-left") != None:
                        D = 1
                    else:
                        D = 2
                else:
                    D = 0

                score = line.find("td", "score").find("a").text
                score_list = get_scores(score, D)

                score_home = int(score_list[0])
                score_away = int(score_list[1])

                # TIMESTAMP TO DATE
                timestamp = line.find("td", "full-date").find("span").get("data-value")
                timestamp = int(timestamp)
                match_date = timestamp_to_datetime(timestamp)

                match_elem = {
                    'home_team_id': home_team_id,
                    'away_team_id': away_team_id,
                    'score_home': score_home,
                    'score_away': score_away,
                    'D': D,
                    'match_date': match_date,
                }

                matches_list.append(match_elem)

            except:
                if DEBUG_MODE:
                    print("[ ! ! ! ] Матч потерян [ ! ! ! ]", line)
                    sleep(10)
    except:
        if DEBUG_MODE:
            print("[ - Error - ] Get Matches With Filter Request")
            sleep(5)
    finally:
        return matches_list


def get_filtered_matches_link(team_id, filter, page):
    ''' Получить ссылку на слелующий блок фильтрованных матчей '''

    # Т. к. мы листаем назад
    page *= -1

    params = {
        'page': page
    }

    callback_params = {
        'page': page + 1,
        'block_service_id': "team_matches_block_teammatches",
        'team_id': team_id,
        'competition_id': 0,
        'filter': filter,
        'new_design': "",
    }

    # Если нужна первая страницы
    if page == 0:
        callback_params['page'] = -1

    get_params = {
        'block_id': "page_team_1_block_team_matches_3",
        'action': "changePage",
        'callback_params': json.dumps(callback_params),
        'params': json.dumps(params)
    }

    link = "https://uk.soccerway.com/a/block_team_matches?" + (urllib.parse.urlencode(get_params))
    return link


def get_summ_from_list(your_list, need):
    """ Получить сумму элементов в пределе range """

    summ = 0
    i = 0
    for elem in your_list:
        if i >= need:
            break

        summ += elem
        i += 1

    return summ

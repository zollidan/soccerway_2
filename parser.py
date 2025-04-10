from tqdm import tqdm
from exel_functions import *
from parser_functions import *
from constants import *

# Создаём мнджера для управления Excel файлом
manager = ExcelManager()

# Получаем предел дат от пользователя
date_limit = get_date_limit()
date_start, date_end = date_limit

# Список дат в указанном пределе, с разницой в день
date_list = make_date_list(date_start, date_end)

# Получить список матчей за все даты сразу
all_matches = []
for date_str in date_list:
    try:
        response_url = BASE_LINK + date_str.replace('-', '/')
        response = get_response(response_url)

        matches_from_page = get_matches(response, date_str)

        all_matches.extend(matches_from_page)
    except:
        if DEBUG_MODE:
            print("[!] Main Request Loop Error [!]\n[args]:", BASE_LINK, date_str)

if DEBUG_MODE:        
    print(all_matches, "\n[ All Matches Info ]")


try:
    print("[ Parse Matches ]")
    for match_info in tqdm(all_matches):
        try:

            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # Шапка
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            home_team_name = match_info.get('home_team_name')
            away_team_name = match_info.get('away_team_name')
            home_team_id   = match_info.get('home_team_id')
            away_team_id   = match_info.get('away_team_id')
            match_date     = match_info.get('match_date')
            # # # Запись в Exel # # #
            manager.write(int(match_date.strftime('%d')))
            manager.write(int(match_date.strftime('%m')))
            manager.write(int(match_date.strftime('%Y')))
            manager.write(match_date.strftime('%H:%M:%S'))
            manager.write(home_team_name)
            manager.write(away_team_name)
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #




            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # head_to_head = {
            #     'home_team_name': home_team_name,
            #     'away_team_name': away_team_name,
            #     'home_team_id': home_team_id,
            #     'away_team_id': away_team_name,
            #     'date': match_date, # datetime object
            #     'home': [],   # Домашние матчи
            #     'away': [],   # Выездные
            #     'all':  [],   # Все общие матчи
            # }
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # Получить 25 матчей друг против друга, для каждой категории 'home', 'away'
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            head_to_head = get_h2h_list(match_info, need=25)

            # Домашние h2h матчи команды А [25]
            max_len = min(len(head_to_head['home']), 25)
            home_h2h_25 = head_to_head['home'][0:max_len]

            # Получение статистики
            stats_home_h2h_25 = get_match_stats(home_h2h_25, home_team_id, max_len)
            goals_all = stats_home_h2h_25['goals_all']

            # Сумма всех голов за [25], [3], [5] матчей
            summ_goals_all_25 = get_summ_from_list(goals_all, 25)
            summ_goals_all_3 = get_summ_from_list(goals_all, 3)
            summ_goals_all_5 = get_summ_from_list(goals_all, 5)

            # # # Запись в Exel # # #
            # Голов за [25] матчей
            max_len = min(len(home_h2h_25), 25)
            manager.write(max_len)
            manager.write(summ_goals_all_25)
            # Голов за [3] матча
            max_len = min(len(home_h2h_25), 3)
            manager.write(max_len)
            manager.write(summ_goals_all_3)
            # Голов за [5] матчей
            max_len = min(len(home_h2h_25), 5)
            manager.write(max_len)
            manager.write(summ_goals_all_5)
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #




            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # Последние домашние матчи Команды А [25]
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            home_last_25 = get_matches_with_filter(home_team_id, match_date, 25, filter="home")
            max_len      = min(len(home_last_25), 25)

            # Получение статистики
            stats_home_last_25 = get_match_stats(home_last_25, home_team_id, max_len)
            goals_all = stats_home_last_25['goals_all']

            # Сумма всех голов за [25], [3], [5] матчей
            summ_goals_all_25 = get_summ_from_list(goals_all, 25)
            summ_goals_all_3 = get_summ_from_list(goals_all, 3)
            summ_goals_all_5 = get_summ_from_list(goals_all, 5)

            # # # Запись в Exel # # #
            # Голов за [25] матчей
            max_len = min(len(home_last_25), 25)
            manager.write(max_len)
            manager.write(summ_goals_all_25)
            # Голов за [3] матча
            max_len = min(len(home_last_25), 3)
            manager.write(max_len)
            manager.write(summ_goals_all_3)
            # Голов за [5] матчей
            max_len = min(len(home_last_25), 5)
            manager.write(max_len)
            manager.write(summ_goals_all_5)
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #




            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # Последние выездные матчи Команды Б [25]
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            away_last_25 = get_matches_with_filter(away_team_id, match_date, 25, filter="away")
            max_len      = min(len(away_last_25), 25)

            # Получение статистики
            stats_away_last_25 = get_match_stats(away_last_25, away_team_id, max_len)
            goals_all = stats_away_last_25['goals_all']

            # Сумма всех голов за [25], [3], [5] матчей
            summ_goals_all_25 = get_summ_from_list(goals_all, 25)
            summ_goals_all_3 = get_summ_from_list(goals_all, 3)
            summ_goals_all_5 = get_summ_from_list(goals_all, 5)

            # # # Запись в Exel # # #
            # Голов за [25] матчей
            max_len = min(len(away_last_25), 25)
            manager.write(max_len)
            manager.write(summ_goals_all_25)
            # Голов за [3] матча
            max_len = min(len(away_last_25), 3)
            manager.write(max_len)
            manager.write(summ_goals_all_3)
            # Голов за [5] матчей
            max_len = min(len(away_last_25), 5)
            manager.write(max_len)
            manager.write(summ_goals_all_5)
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #



            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # Концовка
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            link = match_info.get('link')
            league_name = match_info.get('league_name')
            # # # Запись в Exel # # #
            manager.write(link)
            manager.write(league_name)
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            # В случаи ошибки, итерация не выполнится и мы перезапишем тек. строку
            manager.next_row()

            if DEBUG_MODE:

                print(" ************************* ")
                print(" Home Team: ", home_team_name)
                print(" Away Team: ", away_team_name)
                print(" ************************* ")
                
                print("Link:", match_info['link'])

                print("Home Last (25)", len(away_last_25))
                print(away_last_25)
                print("Stats:", stats_away_last_25)

                # for debug_tmp_elem in away_last_25:
                #     print(debug_tmp_elem['score_home'], ":", debug_tmp_elem['score_away'], "\t", debug_tmp_elem['match_date'].strftime("%d/%m/%y"))

        except:
            if DEBUG_MODE:
                print('Match Parsing Error:', match_info)

except:
    if DEBUG_MODE:
        print("*** Main Parsing Loop Error ***")
finally:

    # Надпись о завершении работы
    if QUITE_MODE:
        print(WORK_IS_DONE_MESSAGE)

    # Сохранение файла
    manager.save()

    input("Press Enter to continue...")
    
    


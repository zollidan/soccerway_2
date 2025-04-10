from time import sleep
import requests
import urllib.parse
from bs4 import BeautifulSoup

import re
import json
import string

import xlwt
from datetime import datetime
from datetime import timedelta

from constants import USER_AGENT


def main():
    date_start = input("Введи начальную дату (формат гггг-мм-дд) ")
    date_end = input("Введи конечную дату (формат гггг-мм-дд) ")

    style0 = xlwt.easyxf('font: name Times New Roman, color-index red, bold on', num_format_str='#,##0.00')
    style1 = xlwt.easyxf(num_format_str='D-MMM-YY')

    wb = xlwt.Workbook()
    ws = wb.add_sheet('Data', cell_overwrite_ok=True)

    date_to_parse = date_start
    date_list = prepare_date_list(date_start, date_end)
    match_number = 0
    for ii in date_list:
        file_pointer = open('matches_links.txt', 'w')
        date = date_list[ii].replace("-", "/")
        print(date)
        dt = datetime.strptime(date_list[ii], '%Y-%m-%d')

        dateunix = dt.timestamp()

        response = do_response("https://uk.soccerway.com/matches/" + date, False)
        soup = BeautifulSoup(response.content, "lxml")
        base_link = "https://uk.soccerway.com"
        i = 0

        for link in soup.find_all('tr', "group-head"):
            i = i + 1
            row = link.get("id")
            splited = row.split("-")
            match_id = splited[1]
            stage_value = link.get("stage-value")
            league_name = json.dumps(link.find_all("span")[0].text)
            file_pointer.write(date_list[ii] + "\t" + match_id + "\t" + stage_value + "\t" + league_name + "\n")
        file_pointer.close()

        file_pointer = open('matches_links.txt', 'r')
        for line in file_pointer:
            line = line.replace("\n", "")
            tmp = line.split("\t")

            current_league_name = tmp[3]

            params = dict()

            params["block_service_id"] = "matches_index_block_datematches"
            params["date"] = tmp[0]
            params["stage-value"] = tmp[2]

            get_params = dict()
            get_params["competition_id"] = tmp[1]

            get_params["block_id"] = "page_matches_1_block_date_matches_1"
            get_params["callback_params"] = json.dumps(params)
            get_params["action"] = "showMatches"
            get_params["params"] = json.dumps(get_params)

            link = "https://uk.soccerway.com/a/block_date_matches?" + (urllib.parse.urlencode(get_params))

            soup = do_response(link, True)

            for row in soup.find_all("tr", "match"):
                # if(match_number<660):
                # match_number+=1
                # continue

                home_team_id = int(get_team_id(row.find("td", "team-a").find("a").get("href")))
                home_team_name = row.find("td", "team-a").find("a").get("title")

                away_team_id = int(get_team_id(row.find("td", "team-b").find("a").get("href")))
                away_team_name = row.find("td", "team-b").find("a").get("title")
                value = datetime.fromtimestamp(int(row.get("data-timestamp")))

                # if home_team_id != 711:
                #    
                ws.write(match_number, 0, value.strftime('%d'))
                ws.write(match_number, 1, value.strftime('%m'))
                ws.write(match_number, 2, value.strftime('%Y'))
                ws.write(match_number, 3, value.strftime('%H:%M:%S'))
                ws.write(match_number, 4, home_team_name)
                ws.write(match_number, 5, away_team_name)

                link = prepare_link(home_team_id, away_team_id, 0, 0)

                req_res = do_response(link, True)

                matches_list = dict()

                if len(req_res.find_all("tr", "match")) > 0:
                    matches_list = prepare_match_list(matches_list, req_res)

                link = prepare_link(home_team_id, away_team_id, -1, -1)

                req_res = do_response(link, True)

                if len(req_res.find_all("tr", "match")) > 0:
                    matches_list = prepare_match_list(matches_list, req_res)

                if len(matches_list) < 25:
                    link = prepare_link(home_team_id, away_team_id, -2, -2)
                    req_res = do_response(link, True)
                    if len(req_res.find_all("tr", "match")) > 0:
                        matches_list = prepare_match_list(matches_list, req_res)

                    if len(matches_list) < 25:
                        link = prepare_link(home_team_id, away_team_id, -3, -3)
                        req_res = do_response(link, True)
                        if len(req_res.find_all("tr", "match")) > 0:
                            matches_list = prepare_match_list(matches_list, req_res)

                        if len(matches_list) < 25:
                            link = prepare_link(home_team_id, away_team_id, -4, -4)
                            req_res = do_response(link, True)
                            if len(req_res.find_all("tr", "match")) > 0:
                                matches_list = prepare_match_list(matches_list, req_res)

                head_to_head_matches = matches_list

                arr = prepare_cells(matches_list, home_team_id, away_team_id, 15, "home", dateunix)

                ws.write(match_number, 6, arr[0])
                ws.write(match_number, 7, arr[1])
                ws.write(match_number, 8, arr[2])
                ws.write(match_number, 9, arr[3])

                home_25_matches = get_25_matches(home_team_id, "home")
                arr = get_stats(home_25_matches, dateunix, 25)

                ws.write(match_number, 10, arr[0])
                ws.write(match_number, 11, arr[1])
                ws.write(match_number, 12, arr[2])
                ws.write(match_number, 13, arr[3])

                away_25_matches = get_25_matches(away_team_id, "away")

                arr = get_stats(away_25_matches, dateunix, 25)

                ws.write(match_number, 14, arr[0])
                ws.write(match_number, 15, arr[1])
                ws.write(match_number, 16, arr[2])
                ws.write(match_number, 17, arr[3])

                arr = prepare_cells(head_to_head_matches, home_team_id, away_team_id, 25, "home", dateunix)
                ws.write(match_number, 18, arr[0])
                ws.write(match_number, 19, arr[5])
                ws.write(match_number, 20, arr[4])

                arr = get_stats(home_25_matches, dateunix, 25)
                ws.write(match_number, 21, arr[0])
                ws.write(match_number, 22, arr[5])
                ws.write(match_number, 23, arr[4])

                arr = get_stats(away_25_matches, dateunix, 25)
                ws.write(match_number, 24, arr[0])
                ws.write(match_number, 25, arr[5])
                ws.write(match_number, 26, arr[4])
                ws.write(match_number, 27, json.loads(current_league_name))

                '''Формирование второй части'''
                ws.write(match_number, 28, value.strftime('%d'))
                ws.write(match_number, 29, value.strftime('%m'))
                ws.write(match_number, 30, value.strftime('%Y'))
                ws.write(match_number, 31, value.strftime('%H:%M:%S'))
                ws.write(match_number, 32, home_team_name)
                ws.write(match_number, 33, away_team_name)

                arr = prepare_cells(head_to_head_matches, home_team_id, away_team_id, 25, "all", dateunix)
                ws.write(match_number, 34, arr[0])
                ws.write(match_number, 35, arr[6])

                arr = prepare_cells(head_to_head_matches, home_team_id, away_team_id, 3, "all", dateunix)
                ws.write(match_number, 36, arr[0])
                ws.write(match_number, 37, arr[6])

                arr = prepare_cells(head_to_head_matches, home_team_id, away_team_id, 5, "all", dateunix)
                ws.write(match_number, 38, arr[0])
                ws.write(match_number, 39, arr[6])

                matches_list = get_25_matches(home_team_id, "all")
                arr = get_stats(matches_list, dateunix, 25)
                ws.write(match_number, 40, arr[0])
                ws.write(match_number, 41, arr[6])

                # arr = prepare_cells(matches_list, home_team_id, away_team_id, 3, "all", dateunix)
                arr = get_stats(matches_list, dateunix, 3)
                ws.write(match_number, 42, arr[0])
                ws.write(match_number, 43, arr[6])

                arr = get_stats(matches_list, dateunix, 5)
                ws.write(match_number, 44, arr[0])
                ws.write(match_number, 45, arr[6])

                matches_list = get_25_matches(away_team_id, "all")
                arr = get_stats(matches_list, dateunix, 25)
                ws.write(match_number, 46, arr[0])
                ws.write(match_number, 47, arr[6])

                arr = get_stats(matches_list, dateunix, 3)
                ws.write(match_number, 48, arr[0])
                ws.write(match_number, 49, arr[6])

                arr = get_stats(matches_list, dateunix, 5)
                # print(arr)
                ws.write(match_number, 50, arr[0])
                ws.write(match_number, 51, arr[6])

                wb.save('example.xls')
                match_number += 1


                # if match_number > 3:
                # break


# exit(500)


def get_team_id(link):
    team_split = link.split('/')
    return team_split[len(team_split) - 2]


def prepare_link(home_team_id, away_team_id, page_param_1, page_param_2):
    params = dict()
    params["page"] = page_param_1
    params["block_service_id"] = "match_h2h_comparison_block_h2hmatches"
    params["team_A_id"] = home_team_id
    params["team_B_id"] = away_team_id

    page_param = dict()
    page_param['page'] = page_param_2
    get_params = dict()

    get_params["block_id"] = "page_match_1_block_h2hsection_head2head_7_block_h2h_matches_1"
    get_params["callback_params"] = json.dumps(params)
    get_params["action"] = "changePage"
    get_params["params"] = json.dumps(page_param)

    link = "https://uk.soccerway.com/a/block_h2h_matches?" + (urllib.parse.urlencode(get_params))
    return link


def do_response(link, decode_json):


    # print(link)
    while True:
        # Edited code start
        response = requests.get(link, headers= {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/131.0',
                'Accept-Language':'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Language':'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
                'Referer': 'https://uk.soccerway.com/'})
        # Edited code end
        print(response.status_code)
        if response.status_code == 200:
            break
        else:
            sleep(0.25)
    if (decode_json):
        decoded_res = json.loads(response.content)
        response = BeautifulSoup(decoded_res['commands'][0]['parameters']['content'], "lxml")
    sleep(0.05)
    return response


def prepare_cells(matches_list, home_team_id, away_team_id, count, tmp_type, dateunix):
    # print("----------------------------------------------")
    home_team_win = 0
    away_team_win = 0
    same_count = 0
    more_2_5 = 0
    less_2_5 = 0
    z = 0
    all_goals = 0
    for match_row in matches_list:
        if int(matches_list[match_row]['start_time']) > int(dateunix):
            continue
        if (tmp_type != "all"):
            if tmp_type == "home" and int(matches_list[match_row]['home_team_id']) != int(home_team_id):
                continue
            if tmp_type == "away" and int(matches_list[match_row]['away_team_id']) != int(away_team_win):
                continue
        if z >= count:
            break

        z += 1
        all_goals = all_goals + matches_list[match_row]['home_team_score'] + matches_list[match_row]['away_team_score']
        if (matches_list[match_row]['home_team_score'] + matches_list[match_row]['away_team_score']) > 2.5:
            more_2_5 += 1
        else:
            less_2_5 += 1
        if int(matches_list[match_row]['home_team_score']) == matches_list[match_row]['away_team_score']:
            same_count += 1
            continue
        if int(matches_list[match_row]['home_team_id']) == home_team_id and matches_list[match_row]['home_team_score'] > matches_list[match_row]['away_team_score']:
            home_team_win += 1
            continue
        if int(matches_list[match_row]['away_team_id']) == away_team_id and matches_list[match_row]['home_team_score'] < matches_list[match_row]['away_team_score']:
            away_team_win += 1
            continue
    return z, home_team_win, same_count, away_team_win, more_2_5, less_2_5, all_goals


def prepare_match_list(matches_list, req_res):
    index = len(matches_list)
    for match_row in req_res.find_all("tr", "match"):
        if match_row.find("td", "score") is None:
            continue

        matches_list[index] = dict()
        matches_list[index]['home_team_id'] = get_team_id(match_row.find("td", "team-a").find("a").get("href"))
        matches_list[index]['home_team_name'] = get_team_id(match_row.find("td", "team-a").find("a").text)

        matches_list[index]['away_team_id'] = get_team_id(match_row.find("td", "team-b").find("a").get("href"))
        matches_list[index]['away_team_name'] = get_team_id(match_row.find("td", "team-b").find("a").text)

        tmp = match_row.find("td", "score").find("a").text
        if tmp.find('Д') == -1:
            tmp_home_team_score = tmp.split("-")[0]
            tmp_away_team_score = tmp.split("-")[1]
            if (len(tmp_home_team_score) == 0):
                matches_list[index]['home_team_score'] = 0
                matches_list[index]['away_team_score'] = 0
            else:
                matches_list[index]['home_team_score'] = int(re.sub("\D", "", tmp.split("-")[0]))
                matches_list[index]['away_team_score'] = int(re.sub("\D", "", tmp.split("-")[1]))
        else:
            matches_list[index]['home_team_score'] = int(re.sub("\D", "", tmp.split("-")[0]))
            matches_list[index]['away_team_score'] = int(re.sub("\D", "", tmp.split("-")[1]))
            if int(matches_list[index]['home_team_score']) > int(matches_list[index]['away_team_score']):
                matches_list[index]['home_team_score'] = matches_list[index]['away_team_score']
            else:
                matches_list[index]['away_team_score'] = matches_list[index]['home_team_score']

        matches_list[index]['start_time'] = int(match_row.find("td", "day").find("span").get("data-value"))
        matches_list[index]['real_date'] = match_row.find("td", "full-date").text
        index += 1

    return matches_list


def get_matches(team_id, type, page, prev_page):
    params = dict()
    '''
 params["page"] = page
 params["block_service_id"] = "team_summary_block_teammatchessummary"
 params["team_id"] = team_id
 params["competition_id"] = 0
 params["filter"] = type
 params["new_design"] = ""

 page_param = dict()
 page_param['page'] = prev_page
 page_param['filter'] = type
 get_params = dict()

 get_params["block_id"] = "page_team_1_block_team_matches_summary_7"
 get_params["callback_params"] = json.dumps(params)
 get_params["action"] = "changePage"
 get_params["params"] = json.dumps(page_param)
'''
    params["page"] = page
    params["block_service_id"] = "team_matches_block_teammatches"
    params["team_id"] = team_id
    params["competition_id"] = 0
    params["filter"] = type
    params["new_design"] = ""

    page_param = dict()
    page_param['page'] = prev_page
    get_params = dict()

    get_params["block_id"] = "page_team_1_block_team_matches_3"
    get_params["callback_params"] = json.dumps(params)
    get_params["action"] = "changePage"
    get_params["params"] = json.dumps(page_param)
    link = "https://uk.soccerway.com/a/block_team_matches?" + (urllib.parse.urlencode(get_params))

    return link


def get_25_matches(team_id, type):
    matches_list = dict()

    home_link = get_matches(team_id, type, 0, 0)
    req_res = do_response(home_link, True)

    if len(req_res.find_all("tr", "match")) > 0:
        matches_list = prepare_match_list(matches_list, req_res)

    home_link = get_matches(team_id, type, 0, 0)
    req_res = do_response(home_link, True)

    if len(req_res.find_all("tr", "match")) > 0:
        matches_list = prepare_match_list(matches_list, req_res)

    return matches_list


def get_stats(match_list, dateunix, matches):
    win = 0
    lose = 0
    same = 0
    more_2_5 = 0
    less_2_5 = 0
    z = 0
    total_goals = 0
    length = len(match_list)
    i = 0
    z = length
    while True:

        z -= 1
        i += 1
        if z < 0: break
        if int(match_list[z]['start_time']) > int(dateunix):
            i -= 1
            continue

        if i == (matches + 1) or z == 0:
            break
        # print(match_list[z])
        total_goals = total_goals + match_list[z]['home_team_score'] + match_list[z]['away_team_score']
        if (match_list[z]['home_team_score'] + match_list[z]['away_team_score']) > 2.5:
            more_2_5 += 1
        else:
            less_2_5 += 1
        if match_list[z]['home_team_score'] > match_list[z]['away_team_score']:
            win += 1
            continue
        if match_list[z]['home_team_score'] == match_list[z]['away_team_score']:
            same += 1
            continue
        if match_list[z]['home_team_score'] < match_list[z]['away_team_score']:
            # print("!!!"+" "+ str(match_list[z]))
            lose += 1
            continue

    return (i - 1), win, same, lose, more_2_5, less_2_5, total_goals


def prepare_date_list(start_date, end_date):
    date_list = dict()
    dt = datetime.strptime(start_date, '%Y-%m-%d')
    time_delta = timedelta(days=1)
    i = 0
    if start_date == end_date:
        date_list[0] = start_date
    else:
        date_list[0] = start_date
        i = 1
        while (True):
            date_list[i] = dt + time_delta
            dt = date_list[i]
            date_list[i] = date_list[i].strftime('%Y-%m-%d')

            if date_list[i] == end_date:
                break
            i += 1
    print(date_list)
    return date_list


main()

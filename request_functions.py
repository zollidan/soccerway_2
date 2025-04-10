import requests
from time import sleep
import json

from constants import *


# Получить запрос по ссылке "link"
def get_response(link, decode_json=False):
    """ get_response(str_link): return 'response' """

    for i in range(MAX_COUNT_RESPONSE):

        try:
            # Edited code start
            response = requests.get(link, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/131.0',
                'Accept-Language':'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Language':'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
                'Referer': 'https://uk.soccerway.com/',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'ru',
                'cache-control': 'max-age=0',
                'if-none-match': '"7fa755cfcb5b4ef71cd1d4e185508716"',
                'priority': 'u=0, i',
                'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
            })
            # Edited code end
            if DEBUG_MODE:
                print("∟ Link:", link)
                print(f"[ {response.status_code} ]")
 
            if response.status_code == 200:
                break
            else:
                sleep(DELAY_RESPONSE)

        except:
            if DEBUG_MODE:
                print("[ - Error - ] Request:", link)

    try:
        if decode_json == True:
            response = json.loads(response.content)
    except:
        if DEBUG_MODE:
            print("[ - Error -] Make Json:", response)
    finally:
        return response

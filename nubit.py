import re
import requests
import random
from concurrent.futures import ThreadPoolExecutor
from telethon import TelegramClient, events

api_id = '20919918'  # 从 https://my.telegram.org 获取
api_hash = 'e629ef1925c4945f7daa53e867496394'  # 从 https://my.telegram.org 获取
phone_number = '+85246642745'

client = TelegramClient('session_name', api_id, api_hash)

# 目标 URL
url = 'https://api.thunderbolt.lt/api/v1/binding/bc1p9amelt5wq8ryhd7dm8f44nkufcs92p5qahr47gcl00mrs6wxk0lqnx2ef6/boostingcode'

# 请求头
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://thunderbolt.lt',
    'priority': 'u=1, i',
    'referer': 'https://thunderbolt.lt/',
    'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
}

# SOCKS5 代理池
proxies_list = [
    {"http": "socks5://CBEB3CDC29657757-residential-country_CA-r_0m-s_nxpb55xaMe:dODndSrM@gate.nstproxy.io:24125"}
]

def send_request(boosting_code, max_retries=15):
    # 随机选择一个代理
    proxy = random.choice(proxies_list)
    
    data = {
        "btcAddress": "bc1p9amelt5wq8ryhd7dm8f44nkufcs92p5qahr47gcl00mrs6wxk0lqnx2ef6",
        "boostingCode": boosting_code
    }

    retries = 0
    while retries < max_retries:
        try:
            response = requests.post(url, headers=headers, json=data, proxies=proxy)
            if response.status_code == 200:
                print(f"sent boosting code: {boosting_code} {response.text}")
                return  # 成功后退出
            elif response.status_code == 429:
                print(f"Rate limit hit (429) for {boosting_code}. Retrying in 5 seconds...")
                #time.sleep(5)  # 如果是429错误，等待5秒再重试
                retries += 1
            else:
                print(f"Failed to send boosting code: {boosting_code} - {response.status_code}")
                return
        except Exception as e:
            print(f"Error sending boosting code {boosting_code}: {e}")
            retries += 1
            #time.sleep(5)  # 出现异常时等待5秒再重试
@client.on(events.NewMessage)
async def handler(event):
    pattern = r'NB-\w{5}'
    matches = re.findall(pattern, event.text)
    
    # 使用 ThreadPoolExecutor 来同时发包
    with ThreadPoolExecutor() as executor:
        executor.map(send_request, matches)

client.start(phone_number)
client.run_until_disconnected()

import requests
import spider_tools as spiderTools
from datetime import datetime


def make_migu_schedule():
    # 请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36\
        (KHTML, like Gecko) Chrome/75.0.3770.142 Mobile Safari/537.36',
        'Content-Type': 'text/html; charset=utf-8',
    }
    name_not = ["解密", "连线", "聚焦", "前夜", "称重", "回顾", "发布会", "特别节目", "揭秘"]
    type_not = ["挑战者系列赛", "揭秘"]
    items = get_schedule_list(headers)
    #items = items[len(items)-15:len(items)]
    index = 0
    for item in items:
        mgdbId = item['action']['params']['extra']['mgdbID']
        startTime = datetime.strptime(
            item['startTime'], '%Y-%m-%d %H:%M:%S').timestamp()
        currentTime = datetime.now().timestamp()
        print(item['title'])
        if currentTime < startTime:
            print("没有到开赛时间！")
            continue
        # 去掉除数字赛和格斗职业之外的内容
        if any(key in item['title'] for key in name_not) or any(key in item['type'] for key in type_not):
            print("去掉不需要的内容！")
            continue
        mgdbId_data = get_mgdbId_data(headers, mgdbId)
        if 'replayList' not in mgdbId_data['body']:
            print("没有找到视频内容！")
            continue
        replayList = mgdbId_data['body']['replayList']
        viewList = []
        item['viewList'] = viewList
        for replay in replayList:
            play = {}
            play['duration'] = replay['duration']
            play['pID'] = replay['pID']
            play['name'] = replay['name']
            pid = replay['pID']
            play_list = get_play_list(headers, pid)
            play_urls = play_list['body']['urlInfo']
            play_urls['url'] = calc_url(play_urls['url'])
            play['playUrls'] = play_urls
            viewList.append(play)
        index = index+1
    return items


def get_schedule_list(headers):
    hostUrl = 'https://display-h5-sc.miguvideo.com/display/v3/static/e58e1ede3cfc430598c292d7a2af222a'
    res = requests.get(hostUrl, headers=headers)
    resJson = res.json()
    return resJson['body']['groups'][2]['components'][0]['extraData']['matches']


def get_mgdbId_data(headers, mgdbId):
    url = f"https://app-sc.miguvideo.com/vms-worldcup/v3/basic-data/all-view-list/{mgdbId}/2/3000060800"
    print("get_mgdbId_data=>", url)
    res = requests.get(url, headers=headers)
    return res.json()


def get_play_list(headers, pid):
    res = requests.get("https://webapi.miguvideo.com/gateway/playurl/v3/play/playurl",
                       params={'contId': pid}, headers=headers)
    return res.json()


def str_cover_list(str):
    return list(str)


def get_ddCalcu(puData_url):
    params_dict = {}
    query_string = puData_url.split("?")[-1]
    for i in query_string.split("&"):
        temp = i.split("=")
        params_dict[temp[0]] = temp[1]
    puData_list = str_cover_list(params_dict['puData'])
    p = 0
    result = []
    while (2 * p) < len(puData_list):
        result.append(puData_list[len(puData_list) - p - 1])
        if p < len(puData_list) - p - 1:
            result.append(params_dict['puData'][p])
        if p == 1:
            result.append('e')
        if p == 2:
            result.append(str_cover_list(params_dict['timestamp'])[6])
        if p == 3:
            result.append(str_cover_list(params_dict['ProgramID'])[2])
        if p == 4:
            result.append(str_cover_list(params_dict['Channel_ID'])[
                len(str_cover_list(params_dict['Channel_ID'])) - 4])
        p += 1
    return ''.join(result)


def calc_url(url):
    ddCalcu = get_ddCalcu(url)
    return f"{url}&ddCalcu={ddCalcu}"


if __name__ == '__main__':
    items = make_migu_schedule()
    spiderTools.saveAllItemData('ufc', 'migu_schedule', items)
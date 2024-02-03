import requests
from bs4 import BeautifulSoup
from lxml import etree
import re
import datetime
import time
import json
import os
# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36\
    (KHTML, like Gecko) Chrome/75.0.3770.142 Mobile Safari/537.36',
    'Content-Type': 'text/html; charset=utf-8',
}
def makeItHomeData():
    hostUrl = 'https://m.ithome.com'
    html = requests.get(hostUrl, headers=headers)
    bs = BeautifulSoup(html.text, 'html.parser')
    contents = bs.select('.content>div')
    items = []
    for content in contents:
        item = {}
        title = BeautifulSoup(str(content), 'html.parser').select('.plc-title')
        if(len(title) > 0):
            item['title'] = title[0].string
        else:
            item['title'] = '未指定'
        pics = BeautifulSoup(str(content), 'html.parser').select('img')
        images = []
        for pic in pics:
            images.append(pic['data-original'])
            item['images'] = images
        items.append(item)
    makeData2Json('ithome', items)

def makeKuaikejiData():
    hostUrl = 'https://m.mydrivers.com'
    html = requests.get(hostUrl, headers=headers)
    bs = BeautifulSoup(html.text, 'html.parser')
    contents = bs.select('#mynewslist>li')
    items = []
    for content in contents:
        item = {}
        title = BeautifulSoup(str(content), 'html.parser').select('.newst>a')
        item['time'] = timestamp(BeautifulSoup(
            str(content), 'html.parser').find(class_='ttime').text)
        if(len(title) > 0):
            item['title'] = title[0].text
            item['link'] = hostUrl+title[0]['href']
        pics = BeautifulSoup(str(content), 'html.parser').select('img')
        images = []
        for pic in pics:
            image = pic['src']
            if image.startswith("http"):
                images.append(image)
            item['images'] = images
        item['target'] = '快科技'
        items.append(item)
    makeData2Json('kuaikeji', items)

def makeWeatherData():
    html = requests.get('https://m.tianqi.com/shenzhen/15/', headers=headers)
    bs = BeautifulSoup(html.text, 'html.parser')
    contents = bs.select('.weatherbox>a')
    items = []
    for content in contents:
        item = {}
        image = []
        item['link'] = 'https://m.tianqi.com/'+content['href']
        weatherNode = BeautifulSoup(str(content), 'html.parser')
        # weatherNode.select('.dd>i').text
        item['title'] = content['title'] + ":" + \
            weatherNode.select('.txt1')[0].text + \
            weatherNode.select('.txt2')[0].text
        image.append(weatherNode.select('.img>img')[0]['src'])
        item['images'] = image
        items.append(item)
    makeData2Json('weather', items)

def makeDefaultFolder(path):
    if not os.path.exists('./'+path):
        os.makedirs('./'+path)
        resData = {
            'code': 0,
            'msg': 'Success',
            'data': []
        }
        with open('./'+path+'/'+path+'.json', "w", encoding='utf-8') as file:
            file.write(str(json.dumps(resData)))


def saveJson(name, content):
    resData = {
        'code': 0,
        'msg': 'Success',
        'data': content
    }
    with open(name, "w", encoding='utf-8') as file:
        file.write(str(json.dumps(resData)))


def makeData2Json(path, items):
    makeDefaultFolder(path)
    file_prefix = './{path}/{path}'.format(path=path)
    oldItem = readjson(file_prefix+'.json')['data']
    if(len(oldItem) > 0):
        items += oldItem
        items = makeDiff(items)
    if len(items) > 100:
        items = items[:100]
    saveJson(file_prefix+'.json', items)
    pageNum = 20
    count = int(len(items)/pageNum)
    remainder = int(len(items) % pageNum)
    pageCount = 0
    for i in range(0, count):
        saveJson(file_prefix+str(pageCount)+'.json',
                 items[i*pageNum:(i*pageNum) + pageNum])
        pageCount += 1
    if remainder > 0:
        saveJson(file_prefix+str(pageCount)+'.json',
                 items[pageNum*pageCount:pageNum*pageCount + remainder])
        pageCount += 1
    saveJson(file_prefix+str(pageCount)+'.json', [])


def makeErrorLog(name, content):
    with open(name, "w", encoding='utf-8') as file:
        file.write(content)


def makeDiff(list_a):
    unique_list = []
    for item in sorted(list_a, key=lambda x: x["title"]):
        if item not in unique_list:
            unique_list.append(item)
    return unique_list


def timestamp(shijian):
    s_t = time.strptime(shijian, "%Y-%m-%d %H:%M")
    mkt = int(time.mktime(s_t))
    return mkt

def readjson(filePath):
    diff = []
    f = open(filePath, encoding="utf-8")
    info_data = json.load(f)
    return info_data

if __name__ == '__main__':
    makeItHomeData()
    makeKuaikejiData()
    makeWeatherData()


    # try:
    # makeDefaultFolder('ithome')
    # except Exception as e:
    #     makeErrorLog('./kuaikeji/error.log',str(e))
    
    

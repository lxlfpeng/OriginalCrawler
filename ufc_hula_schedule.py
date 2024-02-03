import requests
from bs4 import BeautifulSoup
import re
import spider_tools as spiderTools
import json
def crawlingHulaUfcSpecial(page="1"):
    hostUrl='https://www.hula8.net/ufc/page/'+page+'/'
    headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'cookie': 'be_placard=1; _lscache_vary=5253ad7591e7079be24731efae29a1eb; __gads=ID=a567682970b87f37-2209fb4983d5001c:T=1660100986:RT=1660100986:S=ALNI_MZ3mGCNHXr5C5skFrEMsxnFe7XW_g; __gpi=UID=000008742952eae1:T=1660100986:RT=1660100986:S=ALNI_MZdqfaUgCWsf7ZQfxdu6gT44YrkpQ',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0'
    }
    html=requests.get(hostUrl,headers=headers)
    bs=BeautifulSoup(html.text,'html.parser')
    contents = bs.select('.site-main > article')
    #contents = contents[0:3]
    print("当前页码:"+str(page))
    items = []
    for content in contents:
        item = {}
        images = []
        item['images']=images
        bs_content=BeautifulSoup(str(content),'html.parser')
        image=bs_content.find('img')['data-original']
        images.append(image)
        bookItem=bs_content.find(attrs={'rel':'bookmark'})
        item['title'] =bookItem.text
        item['link'] =bookItem['href']    
        item['date'] =bs_content.find(class_="date").text
        items.append(item)
        print("标题",bookItem.text)
        print("链接",bookItem['href'])
        hostUrl=bookItem['href']
        html=requests.get(hostUrl,headers=headers)
        soup=BeautifulSoup(html.text,'html.parser')
        script_address=soup.find('script',attrs={'data-optimized':'1'})
        if script_address is None:
           print("视频解析错误!")
           item['videos']=[]
           continue     
        script_content=requests.get(script_address['src'],headers=headers)    
        #video=re.findall('"m3u8dplayer":.*?};', script_content.text)
        videos=re.findall('(?<="m3u8dplayer":).*?(?=};)', script_content.text)
        print("抓取到的视频",videos)
        if len(videos) >0 :
            item['videos']=json.loads(videos[0]) 
    print("解析成功的项目数:"+str(len(items)))
    return items

def crawlingAllHulaUfcSpecial():
    page=0
    totalItems=[]
    while True:
        items=crawlingHulaUfcSpecial(str(page))
        if len(items)==0:
            print(totalItems)
            return totalItems
        else :
            totalItems.extend(items)
            page=page+1

if __name__ == '__main__':
    # items = crawlingAllHulaUfcSpecial()
    # fileutil.saveAllItemData('ufc', 'hula_schedule', items)
    data=spiderTools.readJsonFile('./archive/hula_schedule.json')['data']
    can=[]
    cant=[]
    for item in data:
        if 'videos'  in item :
            can.append(item)
        else:
            cant.append(item)
    print("可以看",str(len(can)))
    print("无法观看",cant[50]) 
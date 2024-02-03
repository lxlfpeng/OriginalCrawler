from bs4 import BeautifulSoup
import spider_tools as spiderTools
import os
import hashlib
from PIL import Image
net_count=0
def makeUfcRanking(old_items=[]):
    global net_count
    rank_total_list = []
    hostUrl = 'https://www.ufc.com/rankings'
    html =spiderTools.get_extranet_requests_data(hostUrl)
    bs = BeautifulSoup(html.text, 'html.parser')
    net_count=net_count+1
    #将老数据做成字典
    old_dit={}
    for item in old_items:
        for player in item['players']:
            old_dit[item['rankName']+str(player['ranking'])+player['link']]=player
    #获取所有的ranking
    contents = bs.find_all('div', class_='view-grouping')
    #contents = contents[0:1]
    for content in contents:
        rank_data = {}
        player_list = []
        rank_data['players'] = player_list
        rank_total_list.append(rank_data)
        #ranking的名字
        rank_data['rankName'] = content.find('div', class_='view-grouping-header').text.strip()
        #ranking的选手
        rank_players = content.find_all('a')
        # rank_players=rank_players[0:1]
        for index,player in enumerate(rank_players):
            player_detial = {}
            player_detial['ranking']=index
            # person = player.find('a')
            player_detial['playerName'] = player.text.strip()
            player_detial['link'] = 'https://www.ufc.com'+player['href']
            key=rank_data['rankName']+str(player_detial['ranking'])+player_detial['link']
            if key in old_dit.keys() :
                print('取本地缓存选手信息:',key)
                player_detial=old_dit[key]
            else: 
                get_person_info(player['href'], player_detial)
                print("从网络加载选手详情:",key)
            player_list.append(player_detial)      
    return rank_total_list


def get_person_info(herf, player_detial):
    global net_count
    hostUrl = 'https://www.ufc.com'+herf
    html =spiderTools.get_extranet_requests_data(hostUrl) 
    bs = BeautifulSoup(html.text, 'html.parser')
    net_count=net_count+1
    # 战绩
    player_detial['record'] = bs.find(
        'p', class_='hero-profile__division-body').text.strip()
    # 标签
    player_tags = bs.find_all("p", class_='hero-profile__tag')
    tags=[]
    player_detial['playerTag'] =tags
    for player in player_tags:
        tags.append(player.text.strip())
    # 个人信息
    bio_infos=[] 
    player_detial['bioInfos'] =bio_infos  
    bio_label=bs.find_all('div',class_='c-bio__label')
    bio_text=bs.find_all('div',class_='c-bio__text')    
    if len(bio_label)==len(bio_text):
        for index,lable in enumerate(bio_label):
            info={}
            bio_infos.append(info)
            info['lable']=lable.text.strip()
            info['text']=bio_text[index].text.strip()
    # 级别
    player_detial['level'] = bs.find(
        'p', class_="hero-profile__division-title").text.strip()
    # 获胜方式
    profile_stats = bs.find(
        'div', class_='hero-profile__stats').find_all('div', class_='hero-profile__stat')
    wins_stats = []
    player_detial['winsStats'] = wins_stats
    for profile in profile_stats:
        stats = {}
        wins_stats.append(stats)
        stats['statNumb'] = profile.find(
            'p', class_='hero-profile__stat-numb').text.strip()
        stats['statText'] = profile.find(
            'p', class_='hero-profile__stat-text').text.strip()
    # nickname
    hero_nickname=bs.find('p',class_='hero-profile__nickname')
    player_detial['playerNickName']=hero_nickname.text.strip()if hero_nickname is not None else "-" 
    # 封面
    cover=bs.find('img',class_='hero-profile__image')
    if cover is not None:
        player_detial['sourcePlayerCover'] =cover['src']
        player_detial['localPlayerCover'] =save_pic(cover['alt'],cover['src'],'./ufc/rank/image/')

    # 生涯记录
    tabs_select = bs.find('select', class_='c-tabs__select')
    if tabs_select is None:
        player_detial['history'] = '-'
        return
    options = tabs_select.find_all('option')
    for option in options:

        if option.text.strip() == "UFC History":
            player_detial['history'] = 'UFC History \n' + bs.find(
                'div', attrs={"aria-labelledby": option['value']}).text.strip()
            break

        if option.text.strip() == "Q&A":
            content_text = bs.find(
                'div', attrs={"aria-labelledby": option['value']}).text.strip()
            start_index = content_text.find('UFC History')
            end_index = content_text.find('Q&A')
            if start_index !=-1 and end_index !=-1:
                player_detial['history'] = content_text[start_index:end_index]
            break

def get_md5_value(src):    
    myMd5 = hashlib.md5()    
    myMd5.update(src.encode("utf-8"))     
    return myMd5.hexdigest()     

def save_pic(pic_name, pic_url,save_path):
    global net_count
    if not pic_url.startswith("http"):
        pic_url = 'https://www.ufc.com/'+pic_url
    
    pic_name=get_md5_value(pic_name)+'.webp'
    #判断是否有路径没有则生成
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    #获取之前下载过的图片
    local_images_list = os.listdir(save_path)

    if pic_name in local_images_list:
        # print("图片已存在不需要再次下载")
        return save_path[1:]+pic_name
    else:
        print("图片不存在需要再次下载:", pic_name)
        r = spiderTools.get_extranet_requests_data(pic_url)
        net_count=net_count+1
        with open(save_path+pic_name, 'wb') as f:
            f.write(r.content)
        #对图片进行压缩操作    
        sImg = Image.open(save_path+pic_name).convert("RGBA")
        # w, h = sImg.size
        # sImg.thumbnail((w//3, h//3))
        sImg.save(save_path+pic_name, "WEBP")
        return save_path[1:]+pic_name

def get_ufc_ranking():
    old_ranking_item = spiderTools.readJsonFile('./ufc/ufc_com_ranking.json')['data']
    items = makeUfcRanking(old_ranking_item)
    print("总访问网络次数:",str(net_count)) 
    #获取当前所有在用的图片
    local_images_list=[]
    for item in items:
        for player in item['players']:
            if 'localPlayerCover' in player.keys():
                local_images_list.append(player['localPlayerCover'].split('/')[-1])
    #删除本地缓存的未使用图片
    spiderTools.delete_not_use_pic('./ufc/rank/image/',local_images_list)
    #保存数据
    spiderTools.saveAllItemData('ufc', 'ufc_com_ranking', items)
    return net_count

if __name__ == '__main__':
    items=get_ufc_ranking()
   
    
   

from bs4 import BeautifulSoup
import spider_tools as spiderTools
import os
import re
import country_utils
from rss_make import RssMaker

local_images_list_new =[]
net_count=0
def makeUfcSchedule():
    global net_count
    #用来装每一期比赛的数组
    games_list=[]
    hostUrl='https://www.ufc.com/events#events-list-upcoming'        
    html=spiderTools.get_extranet_requests_data(hostUrl)
    net_count=net_count+1
    bs=BeautifulSoup(html.text,'html.parser')
    contents =bs.select('#events-list-upcoming .l-listing__item')
    #contents=contents[0:1]
    for content in contents:
        #一期比赛
        game_item={}
        #本期比赛的信息
        games_list.append(game_item)
        #本期比赛赛程
        game_schedule=[]
        game_item['gameSchedule']=game_schedule
        link=content.find('h3',{'class':"c-card-event--result__headline"})
        fight_html=spiderTools.get_extranet_requests_data('https://www.ufc.com/'+link.a.get('href'))
        net_count=net_count+1
        fight_soup=BeautifulSoup(fight_html.text,'html.parser')
        covers=fight_soup.select('.c-hero__image img')
        if len(covers)>0:
            #比赛封面
            game_item['gameCover']=covers[0]['src'] if covers[0]['src'].startswith("http") else 'https://www.ufc.com/'+covers[0]['src']
        names=fight_soup.select('.c-hero__content .c-hero__headline-prefix h1')
        if len(names)>0:
            #比赛名称
            game_item['gameName']=names[0].text.strip()
            print('比赛名称:',game_item['gameName'])
        #红方选手姓名        
        game_item['redFighterName']=fight_soup.find('span',{'class':'e-divider__top'}).text.strip() 
        #蓝方选手姓名
        game_item['blueFighterName']=fight_soup.find('span',{'class':'e-divider__bottom'}).text.strip() 
        #开始时间比赛
        game_item['gameStartTime']=fight_soup.find('div',{'class':'c-hero__headline-suffix tz-change-inner'})['data-timestamp']
        #比赛开始地点
        game_address=fight_soup.find('div',{'class':'field field--name-venue field--type-entity-reference field--label-hidden field__item'})
        game_item['gameAddress']=game_address.text.strip()if game_address is not None else "-" 
        #本地仓库图片
        if 'gameCover' in game_item:
            local_pic=save_pic( game_item['redFighterName']+'VS'+game_item['blueFighterName'],game_item['gameCover'])
            game_item['gameCoverLocal']=local_pic
        #选手的封面图
        filter_banners=[]
        carousel_items=content.select('.c-carousel__item')
        if len(carousel_items)==0:
           #删除空的合集
           games_list.remove(game_item)
        for carousel_item in carousel_items:
            images=carousel_item.find_all('img')
            fight_lables=carousel_item.find_all('div',class_='fight-card-tickets')
            cover_item={}
            if len(fight_lables)>0:
                cover_item['fightLable']= fight_lables[0]['data-fight-label']
                containStr=' vs ' if ' vs ' in cover_item['fightLable'] else ' VS '
                names=cover_item['fightLable'].split(containStr)
                if len(names)>=2:
                    cover_item['redFighterName']=names[0].strip() 
                    cover_item['blueFighterName']=names[1].strip() 

                if len(images)>0:
                    cover_item['redFighterCover']=images[0]['src']
                    cover_item['redFighterCoverLocal']=save_pic(cover_item['redFighterName']+"_cover",cover_item['redFighterCover'])
                if len(images)>1:
                    cover_item['blueFighterCover']=images[1]['src']
                    cover_item['blueFighterCoverLocal']=save_pic(cover_item['blueFighterName']+"_cover",cover_item['blueFighterCover'])
            filter_banners.append(cover_item)
        game_item['gameScheduleBanner']=filter_banners
        #赛程
        schedule_cards=fight_soup.findAll('ul',{'class':'l-listing__group--bordered'})
        for index,card in enumerate(schedule_cards):
            card_type="Main Card"
            if index==1:
                card_type="Prelims"    
            elif index==2:
                card_type="Early Prelims"      
            else:
                card_type="Main Card"  
            battle_cards= battle_card(card.select('.l-listing__item'),fight_soup,card_type)
            game_schedule.append(battle_cards)
    return games_list
def battle_card(cards,fight_soup,card_name):
    global net_count
    cards_data={}
    battle_cards=[]
    cards_data['scheduleType']=card_name
    cards_data['battleCards']=battle_cards
    for card in cards:
       #对战信息
       info_item={}
       #红方选手信息
       red_player_info={}
       red=card.find('div',{'class':'c-listing-fight__corner--red'})
       red_photo=red.find('img').get('src')
       print(red_photo)
       if  'themes/custom/ufc/assets/img/silhouette-headshot-female.png' in red_photo:
          print('设置新图片')  
          red_photo="https://dmxg5wxfqgb4u.cloudfront.net/styles/event_fight_card_upper_body_of_standing_athlete/s3/image/2022-02/womens-silhouette-RED-corner.png?itok=bYCcdQLM" 
       elif  'themes/custom/ufc/assets/img/standing-stance-right-silhouette.png' in red_photo:
          print('设置新图片') 
          red_photo="https://dmxg5wxfqgb4u.cloudfront.net/styles/event_fight_card_upper_body_of_standing_athlete/s3/image/fighter_images/SHADOW_Fighter_fullLength_RED.png?VersionId=0NwYm4ow5ym9PWjgcpd05ObDBIC5pBtX&itok=woJQm5ZH" 
       red_player_info['photo']=red_photo
       
       #save_pic(red_player_info['photo'])
       #蓝方选手信息
       blue_player_info={}
       blue=card.find('div',{'class':'c-listing-fight__corner--blue'})
       blue_photo=blue.find('img').get('src')
       print(blue_photo)
       if 'themes/custom/ufc/assets/img/silhouette-headshot-female.png' in blue_photo:
          blue_photo="https://dmxg5wxfqgb4u.cloudfront.net/styles/event_fight_card_upper_body_of_standing_athlete/s3/image/2022-02/womens-silhouette-BLUE-corner.png?itok=bYCcdQLM" 
       
       elif '/themes/custom/ufc/assets/img/standing-stance-left-silhouette.png' in blue_photo:
          blue_photo="https://dmxg5wxfqgb4u.cloudfront.net/styles/event_fight_card_upper_body_of_standing_athlete/s3/image/fighter_images/SHADOW_Fighter_fullLength_BLUE.png?VersionId=1Jeml9w1QwZqmMUJDg8qTrTk7fFhqUra&itok=fiyOmUkc" 

       blue_player_info['photo']=blue_photo
       #save_pic(blue_player_info['photo'])
       #选手姓名
       red_name=''
       red_give_name=card.find('div',class_='c-listing-fight__corner-name c-listing-fight__corner-name--red').find('span',class_='c-listing-fight__corner-given-name')
       if red_give_name is not None:
            red_name=red_name+red_give_name.text.strip()
       red_family_name=card.find('div',class_='c-listing-fight__corner-name c-listing-fight__corner-name--red').find('span',class_='c-listing-fight__corner-family-name')
       if red_family_name is not None:
            red_name=red_name+red_family_name.text.strip()
       if red_give_name is None and red_family_name is None:
            red_name=card.find('div',class_='c-listing-fight__corner-name c-listing-fight__corner-name--red').text.strip() 
       red_player_info['name']=red_name 
       red_player_info['photoLocal']=save_pic(red_name+'_info',red_player_info['photo'],1.5)
       blue_name=''
       blue_give_name=card.find('div',class_='c-listing-fight__corner-name c-listing-fight__corner-name--blue').find('span',class_='c-listing-fight__corner-given-name')
       if blue_give_name is not None:
            blue_name=blue_name+blue_give_name.text.strip()
       blue_family_name=card.find('div',class_='c-listing-fight__corner-name c-listing-fight__corner-name--blue').find('span',class_='c-listing-fight__corner-family-name')
       if blue_family_name is not None:
            blue_name=blue_name+blue_family_name.text.strip()
       if blue_give_name is None and blue_family_name is None:
            blue_name=card.find('div',class_='c-listing-fight__corner-name c-listing-fight__corner-name--blue').text.strip() 
       blue_player_info['name']=blue_name     
       blue_player_info['photoLocal']=save_pic(blue_name+'_info',blue_player_info['photo'],1.5)
       print('对决详情:',red_name+' VS '+blue_name) 
       #选手级别 
       info_item['level']=card.find('div',{'class':'details-content__class'}).text.strip()
       
       #选手排名
       red_rank=red.find('div',{'class':'js-listing-fight__corner-rank c-listing-fight__red-corner-rank--mobile'})
       red_player_info['rank']=red_rank.text.strip() if red_rank is not None else "-" 

       blue_rank=blue.find('div',{'class':'js-listing-fight__corner-rank c-listing-fight__blue-corner-rank--mobile'})
       blue_player_info['rank']=blue_rank.text.strip() if blue_rank is not None else "-" 
       #选手odds
       plays_odds=card.select('.c-listing-fight__odds .c-listing-fight__odds-amount') 
       for index,play_odds in enumerate(plays_odds):
            if index ==0:
                red_player_info['odds']=play_odds.text
            else:
                blue_player_info['odds']=play_odds.text
       #选手国籍
       red_country_image=card.find('div',class_='c-listing-fight__country c-listing-fight__country--red').find('img')
       if  red_country_image is not None and len(red_country_image['src'])>0 and len(red_country_image['src'].split('/'))>0:
            red_images=red_country_image['src'].split('/')
            red_player_info['countryEmoji']=country_utils.get_country_flag_emoji(red_images[len(red_images)-1].replace('.PNG',''))
           
       blue_country_image=card.find('div',class_='c-listing-fight__country c-listing-fight__country--blue').find('img')
       if  blue_country_image is not None and len(blue_country_image['src'])>0 and len(blue_country_image['src'].split('/'))>0:
            blue_images=blue_country_image['src'].split('/')
            blue_player_info['countryEmoji']=country_utils.get_country_flag_emoji(blue_images[len(blue_images)-1].replace('.PNG',''))
            
       country_text=card.find_all('div',class_='c-listing-fight__country-text')
       if len(country_text)>=1:
          red_player_info['countryName'] = country_text[0].text.strip()
       if len(country_text)>=2: 
          blue_player_info['countryName'] = country_text[1].text.strip()  

       #选手信息补充 
       info_id=card.find('div',{'class':'c-listing-fight'}).get('data-fmid')
       info_id2=fight_soup.find('div',{'class':'c-listing-ticker--footer'})
       matchup_stats=[]
       if info_id is not None and info_id2 is not None:
             info_html=spiderTools.get_extranet_requests_data('https://www.ufc.com/matchup/'+info_id2.get('data-fmid')+"/"+info_id)
             net_count=net_count+1
             info_soup=BeautifulSoup(info_html.text,'html.parser')
             p_info_items=info_soup.findAll('div',{'class':'c-stat-compare c-stat-compare--horizontal'})
             for p_info_item in p_info_items:
                stats={}
                stats['lable']=p_info_item.find('div',{'class':'c-stat-compare__chart_label'}).text.replace(' ','')
                red_detial=p_info_item.find('div',{'class':'c-stat-compare__group-1 red'})
                stats['red']=red_detial.text.strip() if red_detial is not None else "-"
                blue_detial=p_info_item.find('div',{'class':'c-stat-compare__group-2 blue'})
                stats['blue']=blue_detial.text.strip() if blue_detial is not None else "-"
                matchup_stats.append(stats)
       info_item['redPlayer']=red_player_info
       info_item['bluePlayer']=blue_player_info
       info_item['matchupStats']=matchup_stats
       battle_cards.append(info_item)
    return cards_data 


def save_pic(pic_name,pic_url,scale=1):
      global net_count  
      if not pic_url.startswith("http"):
        pic_url='https://www.ufc.com/'+pic_url
      local_images_list=os.listdir('./ufc/schedule/image')
      #pic_name = re.compile("[^a-z^A-Z^0-9]").sub('', pic_name) #匹配不是大小写英文、数字的其他字符,将string1中匹配到的字符替换成空字符
      pic_name=spiderTools.get_md5_value(pic_url)+'.webp'
      #使用MD5方案
      #pic_name=hashlib.md5(pic_url.encode(encoding='utf-8')).hexdigest()+'.png'
      local_images_list_new.append(pic_name)
      if pic_name in local_images_list:
         print("图片已存在不需要再次下载")
         return '/ufc/schedule/image/'+pic_name
      else:
        spiderTools.save_net_pic_pil_raw(pic_url,'./ufc/schedule/image/'+pic_name,scale)
        # r =spiderTools.get_extranet_requests_data(pic_url)
        # net_count=net_count+1
        # with open('./ufc/image/'+pic_name, 'wb') as f:
        #      f.write(r.content)   
        print("图片不存在需要再次下载:",pic_name)
        return '/ufc/schedule/image/'+pic_name
def delete_other_file():
    fileList = os.listdir('./ufc/schedule/image')
    for file in fileList:
        if os.path.exists('./ufc/schedule/image/'+file) and file not in local_images_list_new:
           print("需要删除该文件",file) 
           os.remove('./ufc/schedule/image/'+file)

def get_ufc_schedule():
    #获取数据
    items = makeUfcSchedule()
    #删除多余的图片
    delete_other_file()
    get_diff_data(items)
    #保存数据
    spiderTools.saveAllItemData('ufc', 'ufc_com_schedule', items)
    return net_count

def get_diff_data(newItems):
    #old_ranking_item = spiderTools.readJsonFile('./ufc/ufc_com_schedule.json')['data']
    #取出旧的gameScheduleBanner数据
    new_duel=[item for i in newItems  for item in i['gameScheduleBanner']]
    #取出新的gameScheduleBanner数据
    #old_duel=[item for i in old_ranking_item  for item in i['gameScheduleBanner']]
    #求差集，在new_duel中但不在old_duel中
    #retD = [ i for i in new_duel if i not in old_duel]
    #生成新的rssitem
    rssList = [{'title':content['fightLable'],'link':content['fightLable'],'description':get_html_str(content['fightLable'],content['redFighterCoverLocal'],content['blueFighterCoverLocal'])} for content in new_duel]
    #创建rssMaker对象生成xml
    rssMaker=RssMaker( title="UFC赛程",
        link='https://www.ufc.com/events#events-list-upcoming',
        description="新的UFC赛程")
    rssMaker.makeRss(rssList,'./ufc/rss/ufc_schedule.xml')

def get_html_str(bTitle,bRedCover,bBlueCover):
    bRedCover="https://gitee.com/DaPengDePeng/make-json/raw/master/"+bRedCover
    bBlueCover="https://gitee.com/DaPengDePeng/make-json/raw/master/"+bBlueCover
    html="""
        <!DOCTYPE html>
        <html>
        <head>
	        <meta charset="utf-8" />
        </head>
	    <body >
	        <div style="display: flex;flex-direction: column;justify-content:center;align-items:center;">
                <h1>{title}</h1>
	            <div style="display: flex;flex-direction: column;">
	      	        <img src="{redCover}"  loading="lazy" />
	    	        <img src="{blueCover}" loading="lazy" />
	            </div>
            </div>
	    </body>
        </html>
        """.format(title=bTitle,redCover=bRedCover,blueCover=bBlueCover)
    return html


if __name__ == '__main__':
    # items = makeUfcSchedule()
    # delete_other_file()
    # print("网络请求总数:",str(net_count))
    # spiderTools.saveAllItemData('ufc', 'ufc_com_schedule', items)
    get_ufc_schedule()
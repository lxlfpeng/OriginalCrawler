import PyRSS2Gen
import datetime
import os
class RssMaker:
    def __init__(self,title,link,description):
        self.title=title
        self.link=link
        self.description=description

    def makeRss(self,rssList,path):
        rssItems = []
        for content in rssList:
            rssItem = PyRSS2Gen.RSSItem(
            title=content['title'],
            link=content['link'],
            description=content['description'],
            pubDate =datetime.datetime.now())
            rssItems.append(rssItem)  
        rss = PyRSS2Gen.RSS2(
            title=self.title,
            link=self.link,
            description=self.description,
            lastBuildDate=datetime.datetime.now(),
            items=rssItems
        )
        #取出路径
        dir_path=os.path.dirname(path)
        #判断路径是否存在,不存在则创建路径
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        #将内容进行写入
        rss.write_xml(open(path, "w",encoding='utf-8'),encoding='utf-8')            
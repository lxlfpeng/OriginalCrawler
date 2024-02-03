import json
import re
import html
from urllib import parse
import requests
import spider_tools as spiderTools
import hashlib 
import os
from googletrans import Translator
class ContentTranslate:
    GOOGLE_TRANSLATE_URL = 'http://translate.google.cn/m?q=%s&tl=%s&sl=%s'
    net_count=0
    regex = re.compile(r'''
        "[^"]+?"            # "..." string, not include "..."..."
        (?=                 # Must end with
            \s*?            # Some whitespace
            [,\]\}]         # and `,`, `]` or `}`
        )
    ''', re.VERBOSE | re.MULTILINE)

    def __init__(self):
        # 需要翻译的内容
        self.need_translate = []
        # 翻译的结果内容
        self.result_translate = {}        

    def google_translate(self,text, to_language="auto", text_language="auto"):
        #最多一次翻译5000字
        text = text if len(text) < 5000 else text[:4999]
        # print("开始翻译:", text)
        # text = parse.quote(text)
        # url = self.GOOGLE_TRANSLATE_URL % (text, to_language, text_language)
        # response = requests.get(url)
        # data = response.text
        # expr = r'(?s)class="(?:t0|result-container)">(.*?)<'
        # result = re.findall(expr, data)
        # if (len(result) == 0):
        #     print("翻译错误")
        #     return text
        # self.net_count=self.net_count+1
        # return html.unescape(result[0])
        # 如果可以上外网，还可添加 'translate.google.com' 等
        translator = Translator(service_urls=['translate.google.com',])
        trans=translator.translate(text, src=text_language, dest=to_language)
        # 原文
        #trans.origin
        # 译文
        return trans.text

    def get_need_translate(self,match):
        # print(match.group())
        # 去掉字符串首尾的双引号
        new_str = eval(match.group())
        # print(new_str)
        # if new_str.isalpha():
        # 只对只包含字母和空格的内容进行翻译
        if re.match("^[a-z A-Z]*$", new_str):
            self.need_translate.append(new_str)

        #针对性翻译->翻译战斗历史
        if new_str.startswith('UFC History'):
            self.need_translate.append(new_str)

        return match.group()


    def replace_translate(self,match):
        value = eval(match.group())
        if re.match("^[a-z A-Z]*$", value) or value.startswith('UFC History'):
            value_key=self.get_md5_value(value)
            #print(value_key)
            if value_key in self.result_translate.keys() and self.result_translate[value_key] is not None:
                #print("替换内容", result_translate[value])
                value = self.result_translate[value_key]
        return "\""+value+"\""


    def translate_json(self,items_data,  translate_file_name):
  
        # 获取所有的需要翻译的字符串
        self.regex.sub(self.get_need_translate, json.dumps(items_data))
        #list_tr = list(set(list_tr))[0:5]
        old_translate=self.get_all_local_translate()
        # 对字符串列表去重操作
        self.need_translate = list(set(self.need_translate))
        print("需要翻译的字符串列表长度:", str(len(self.need_translate)))
        translate_count=0
        # 遍历需要翻译的字符串列表
        for item in self.need_translate:
            item_key=self.get_md5_value(item)
            if item_key in old_translate.keys() and old_translate[item_key] is not None:
                # 无需翻译,之前的翻译文件中已经包含
                self.result_translate[item_key] = old_translate[item_key]

            else:
                # 需要进行翻译
                self.result_translate[item_key] = self.google_translate(item, "zh-CN", "en")
                translate_count=translate_count+1

        print("实际翻译数量:", str(translate_count))
        # 重新写入翻译文件
        print("重新写入的翻译文件数量:"+str(len(self.result_translate))+" 写入文件名:"+translate_file_name)
        spiderTools.saveAllItemData('ufc', translate_file_name, self.result_translate)
        # 替换json中对应的value翻译值
        result = self.regex.sub(self.replace_translate, json.dumps(items_data))
        return result

    def get_md5_value(self,src):    
        myMd5 = hashlib.md5()    
        myMd5.update(src.encode("utf-8"))     
        return myMd5.hexdigest()     

    def get_all_local_translate(self):
        local_translate = {}
        local_file = os.listdir('./ufc/')
        for file in local_file:
            if file.endswith('_translate.json'):
               local_translate.update( spiderTools.readJsonFile('./ufc/'+file)['data'] )
        return local_translate

    def translate_ufc_ranking(self):
        ranking_item = spiderTools.readJsonFile('./ufc/ufc_com_ranking.json')['data']
        items=self.translate_json(ranking_item,  'ufc_com_ranking_translate')
        spiderTools.saveAllItemData('ufc', 'ufc_com_ranking_chinese', json.loads(items,strict=False))
        return self.net_count

    def translate_ufc_schedule(self):
        ranking_item = spiderTools.readJsonFile('./ufc/ufc_com_schedule.json')['data']
        items=self.translate_json(ranking_item,  'ufc_com_schedule_translate')
        spiderTools.saveAllItemData('ufc', 'ufc_com_schedule_chinese', json.loads(items,strict=False))   
        return self.net_count

if __name__ == '__main__':
  ContentTranslate().translate_ufc_ranking()
  ContentTranslate().translate_ufc_schedule()

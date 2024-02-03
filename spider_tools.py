import json
import os
import time
import requests
from io import BytesIO
from PIL import Image
import hashlib
headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36\
    (KHTML, like Gecko) Chrome/75.0.3770.142 Mobile Safari/537.36',
    'Content-Type': 'text/html; charset=utf-8',
}
proxies={}
#proxies = {'http': 'http://192.168.1.34:1080', 'https': 'http://192.168.1.34:1080'}
#在本项目根目录创建文件夹
def makeDefaultFolder(path):
    if not os.path.exists('./'+path):
        os.makedirs('./'+path)
    return './'+path+"/"

#组装Json格式数据保存
def saveAllItemData(path,file_name,items):
    files_dir=makeDefaultFolder(path)
    resData = {
           'code': 0,
           'msg': 'Success',
           'data': [],
           'date':int(round(time.time() * 1000))
       }
    resData['data']=items
    resData['total']=len(items)
    saveJsonFile(files_dir+file_name+'.json',resData)

#保存Json文件
def saveJsonFile(path,jsonData):
    with open(path, "w", encoding='utf-8') as file:
        file.write(str(json.dumps(jsonData)))

#保存内容文件例如log日志等等文件
def saveContentFile(path,file_name, content):
    files_dir=makeDefaultFolder(path)
    with open(files_dir+file_name+time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))+'.log', "w", encoding='utf-8') as file:
        file.write(content)

#读取json文件内容
def readJsonFile(filePath):
    with open(filePath,'r', encoding="utf-8") as file:
        info_data = json.load(file)
        return info_data

#删除未在列表中的图片文件
def delete_not_use_pic(file_path,file_list):
    file_list=list(set(file_list))
    local_file_list = os.listdir(file_path)
    print("需要的图片数量:",str(len(file_list)))
    print("缓存的图片数量:",str(len(local_file_list)))
    for file in local_file_list:
        if os.path.exists(file_path+file) and file not in file_list:
            print("需要删除缓存数据:",file)
            os.remove(file_path+file)

#缩放保存在线图片用BytesIO
def save_net_pic_pil_byte(pic_url,file_path,scale):
    try:
        r = requests.get(pic_url,headers=headers,proxies=proxies)
        bytes_stream = BytesIO(r.content)
        image = Image.open(bytes_stream)
        return scale_and_save_pic(image,file_path,scale)
    except Exception as re:
        return '图片下载失败'

#缩放保存在线图片用raw
def save_net_pic_pil_raw(pic_url,file_path,scale):
    
    try:
        print(pic_url)
        resp = requests.get(pic_url, stream=True,headers=headers,proxies=proxies).raw
        image = Image.open(resp)
        return scale_and_save_pic(image,file_path,scale)
    except Exception as re:
        print("下载图片失败")
        return '图片下载失败'

#缩放保存在线图片,先下载再打开图片
def save_net_pic_file(pic_url,file_path,scale):
    try:    
        r = requests.get(pic_url,headers=headers,proxies=proxies)
        with open(file_path, 'wb') as f:
            f.write(r.content)
        #对图片进行压缩操作    
        image = Image.open(file_path).convert("RGBA")
        return scale_and_save_pic(image,file_path,scale)  
    except Exception as re:
        return '图片下载失败'

#缩小并且下载保存图片
def scale_and_save_pic(image,file_path,scale):
    # w, h = image.size
    # image.thumbnail((w//scale, h//scale))
    image.save(file_path, "WEBP")
    return file_path

#获取文件MD5值
def get_md5_value(str):    
    strMd5 = hashlib.md5()    
    strMd5.update(str.encode("utf-8"))     
    return strMd5.hexdigest()  

#请求外部链接数据
def get_extranet_requests_data(hostUrl):
    return requests.get(hostUrl,headers=headers,proxies=proxies)

if __name__ == '__main__':
    pass
#    result=save_net_pic_pil_byte('https://img-blog.csdnimg.cn/img_convert/652082cda22ae6572d8b7a457a94657c.png','./sid1.png',2)
#    print(result)
#    result1=save_net_pic_pil_raw('https://img-blog.csdnimg.cn/img_convert/652082cda22ae6572d8b7a457a94657c.png','./sid2.png',2)
#    print(result1)
#    result2=save_net_pic_file('https://img-blog.csdnimg.cn/img_convert/652082cda22ae6572d8b7a457a94657c.png','./sid3.gif',2)
#    print(result2)


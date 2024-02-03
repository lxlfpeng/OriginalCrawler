import ufc_official_schedule
import ufc_official_ranking
from ufc_official_google_translate import ContentTranslate
import spider_tools as spiderTools
import ufc_hula_schedule
import ufc_migu_schedule
from send_email import EmilTools
import argparse
import time
if __name__ == '__main__':
    #获取脚本传递过来的邮箱密码
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument("--email_pass", type=str,default="", help='input email_pass')
    args = parser.parse_args()
    email_pass=args.email_pass
    success_str="Success Log:\n"
    error_str="Error Log:\n"
    try:
        schedule_count = ufc_official_schedule.get_ufc_schedule()
        success_str=success_str+time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
        success_str=success_str+" UFC.Com赛程数据抓取成功!请求次数:"+str(schedule_count)+"\n"
    except Exception as e:
        spiderTools.saveContentFile('ufc', 'ufc_com_schedule_error', str(e))
        error_str=error_str+time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
        error_str=error_str+" UFC.Com赛程数据抓取失败!"+str(e)+"\n"
    
    try:
        schedule_count = ufc_official_ranking.get_ufc_ranking()
        success_str=success_str+time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
        success_str=success_str+" UFC.Com排位数据抓取成功!请求次数:"+str(schedule_count)+"\n"
    except Exception as e:
        spiderTools.saveContentFile('ufc', 'ufc_com_schedule_error', str(e))
        error_str=error_str+time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
        error_str=error_str+" UFC.Com排位数据抓取失败!"+str(e)+"\n"

    try:
        schedule_count=ContentTranslate().translate_ufc_ranking()
        schedule_count=schedule_count+ContentTranslate().translate_ufc_schedule()
        success_str=success_str+time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
        success_str=success_str+" UFC.Com数据翻译成功!请求次数:"+str(schedule_count)+"\n"
    except Exception as e:
        spiderTools.saveContentFile('ufc', 'ufc_com_schedule_error', str(e))
        error_str=error_str+time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
        error_str=error_str+" UFC.ComCom数据翻译失败!"+str(e) +"\n"   

    EmilTools().send_email(email_pass,'UFC.Com数据抓取',success_str+"\n"+error_str)
    # fileutil.saveContentFile('ufc', 'success_data', success_str)
    # fileutil.saveContentFile('ufc', 'error_data', error_str)
    #  try:
    #      hulaItems = ufc_hula_schedule.crawlingHulaUfcSpecial()
    #      fileutil.saveAllItemData('ufc', 'hula_schedule', hulaItems)
    #  except Exception as e:
    #      fileutil.saveContentFile('ufc', 'hula_schedule_error', str(e))

    #  try:
    #      migu_items = ufc_migu_schedule.make_migu_schedule()
    #      fileutil.saveAllItemData('ufc', 'migu_schedule', migu_items)
    #  except Exception as e:
    #      fileutil.saveContentFile('ufc', 'migu_schedule_error', str(e))

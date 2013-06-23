#coding=utf-8
#author:season
import re
import urllib
import random
import urllib2
import cookielib
from collections import defaultdict
from BeautifulSoup import BeautifulSoup
from threading import Thread, RLock
'''
just for fun  
'''
cookie = urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar())
opener = urllib2.build_opener(cookie)
urllib2.install_opener(opener)
lock = RLock()

apply_session_list = [({'.SPBForms': 'B0BEEB669AC25A5CF293539262A5C7649BAB05DEF14A3FD5B4E13E090CFFFB73B941F9024140559C8A869C8CC0983A74148BD97E9FC41A48CB60972BDF54A6EC64C156A93178B3ED',
   'SBVerifyCode': 'byJlzq7u9JpWkPAIxPgD/1P51sY='},
  {'body': 'splider man',
   'bringCount': '0',
   'email': '1@cyou-inc.com'}),
 ({'.SPBForms': '130B56B5A33463ECB8F5D5441EA0F3BEDA3096EC9305804A161AC18C3305BD474A6D995D91BAD43949586F1FFE7D4BF63D4D39ED910F2E198E8EFB7E32B344B13EC792D46200F5CD',
   'SBVerifyCode': '/XA45456dE6O1w0TUIL+N9BQzR8='},
  {'body': 'splider man',
   'bringCount': '0',
   'email': '2@cyou-inc.com'})]


def setcookie(func):
    def wrapper(req, session=None):
        if not isinstance(req, urllib2.Request):
            req = urllib2.Request(req)
        if not session:
            session = random.choice(apply_session_list)[0]
        req.add_header('Cookie', ';'.join(['='.join(i) for i in session.items()]))
        return func(req)
    return wrapper

@setcookie
def request(req, session=None):
    return urllib2.urlopen(req).read()

def apply_thread(form_url, session, post):
    ipost = urllib.urlencode(post)
    req = urllib2.Request(form_url, data=ipost)
    content = BeautifulSoup(request(req, session=session))
    print content.find('div', {'class': 'tn-helper-flowfix'}).text


def apply(form_url):
    thread_list = []
    for session, post in apply_session_list:
        t = Thread(target=apply_thread, args=(form_url, session, post))
        thread_list.append(t)

    for thread in thread_list:
        thread.start()


def go():
    events_pattern = re.compile('href="(\/whatEvents.aspx\/T-[0-9]+)"')
    members_pattern = re.compile(u'([0-9]+)人参加.*?([0-9]+)条留言')
    already_req_url = defaultdict(int)
    domain = 'http://10.5.17.74'
    url = domain + '/c/musle/whatEvents.aspx'

    for item in events_pattern.findall(request(url))+['/whatEvents.aspx/T-115']:
        if already_req_url[item] == 1:
            continue
        title, content = None, None
        try:
            already_req_url[item] += 1
            content = BeautifulSoup(request(domain+item))
            title = content.title.text
        except urllib2.HTTPError:
            continue
        status = content.find('div', {'class': 'spb-event-countdown'}).text
        if status == u'此活动已结束':
            continue
        messages = content.find('div', {'class': 'spb-event-count'}).text
        members = members_pattern.findall(messages)[0][0]
        if int(members) >= 32:
            print '活动超载，孩纸，洗洗睡吧~', '[%s]' % title
        else:
            print '有基可乘~', '[%s]' % title
            join_content = content.find('a', text=u'我要报名')
            if not join_content:
                print '榜上有名啦~'
                continue
            content = BeautifulSoup(
                request(domain+join_content.findParent().get('href', ''))
                )
            form_url = domain+content.find('form').get('action', '')
            apply(form_url)

if __name__ == '__main__':
    go()

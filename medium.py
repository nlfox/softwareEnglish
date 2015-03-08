# -*- coding: utf-8 -*-
from time import sleep
from pyquery import PyQuery as pq
import urllib2
import json
import threading
from Queue import Queue
import MySQLdb
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
def unGz(str):
    from StringIO import StringIO
    import gzip
    buf = StringIO(str)
    f = gzip.GzipFile(fileobj=buf)
    data = f.read()
    return data
db=MySQLdb.connect(host='localhost',user='root',passwd='g1vnd3',db='test',port=3306)
db.set_character_set('utf8')
cursor = db.cursor()
resultArt=[]
dumpQueue=Queue()
class dumper(threading.Thread):
    def __init__(self,taskQueue,resultQueue):
        threading.Thread.__init__(self)
        self.taskQueue=taskQueue
        self.resultQueue=resultQueue
    def run(self):
        while not dumpQueue.empty():
            itemLink=self.taskQueue.get()
            print 'working on+'+itemLink
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:35.0) Gecko/20100101 Firefox/35.0',
                        'Accept': 'application/json',
                        'Accept-encoding':'gzip',
                        'Accept-Language': 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
                        'X-Obvious-CID': 'web',
                        'X-XSRF-Token': '1',
                        'Content-Type': 'application/json',
                        'Referer': 'https://medium.com/',}
            request=urllib2.Request(url='https://medium.com'+itemLink, headers=headers)
            try:
                resGz=urllib2.urlopen(request,timeout=4).read()
            except Exception, e:
                self.taskQueue.put(itemLink)
                print 'retry'
                continue
            resJson=unGz(resGz)[16:]
            print  'geted'
            resData = json.loads(resJson)
            dumpParas=resData['payload']['value']['content']['bodyModel']['paragraphs']
            dumpArticle=''
            dumpTitle=resData['payload']['value']['title']
            for i in dumpParas:
                dumpArticle+='\n'+i['text']
            sql="insert INTO dumpArticles (title,content) VALUES (%s,%s)"
            dumpTitle=MySQLdb.escape_string(dumpTitle)
            dumpArticle=MySQLdb.escape_string(dumpArticle)
            cursor.execute(sql,(dumpTitle,dumpArticle))

reqArtList=urllib2.Request(url='https://medium.com/channel/tech?limit=100')
reqArtList.add_header('Accept-encoding', 'gzip')
artListGz=urllib2.urlopen(reqArtList).read()
artList=unGz(artListGz)
print '==========List Accepted========================================='
count=0
indexTitleList=pq(artList).find('.block--list')

for i in indexTitleList:
    count+=1
    titleItem=pq(i)
    itemLink=titleItem.find('.block-title>a').attr('href')
    dumpQueue.put(itemLink)
print '==========All tasks added count:'+str(count)+'======================='
threads=[]
num=10
for i in range(num):
    t=dumper(dumpQueue,resultArt)
    threads.append(t)
for i in range(num):
    threads[i].start()
for i in range(num):
    threads[i].join(timeout=10)

print 'now waiting for last'
sleep(4)
cursor.close()
db.commit()
db.close()
print '======================== All completed ======================'
for i in resultArt:
    print i
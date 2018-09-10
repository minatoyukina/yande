from lxml import etree
import requests
import os
from urllib import request
from queue import Queue
import threading

class Producer(threading.Thread):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }
    def __init__(self,page_queue,img_queue,*args,**kwargs):
        super(Producer,self).__init__(*args,**kwargs)
        self.page_queue=page_queue
        self.img_queue=img_queue

    def run(self):
        while True:
            if self.page_queue.empty():
                break
            url=self.page_queue.get()
            self.parsing_url(url)

    def parsing_url(self,url):
        html = requests.get(url, headers=self.headers).text
        selector = etree.HTML(html)
        imgs = selector.xpath(
            '//*[@id="post-list"]/div[2]/div[4]/ul/li/a')
        for img in imgs:
            # time.sleep(1)
            if not os.path.exists('imgs'):
                os.mkdir('imgs')
            img_url=img.get('href')
            filename = img_url.split('%20')[1]+'.jpg'
            # print(img_url,filename)
            self.img_queue.put((img_url,filename))

class Consumer(threading.Thread):
    def __init__(self,page_queue,img_queue,*args,**kwargs):
        super(Consumer,self).__init__(*args,**kwargs)
        self.page_queue=page_queue
        self.img_queue=img_queue

    def run(self):
        while True:
            if self.img_queue.empty() and self.page_queue.empty():
                break
            img_url, filename = self.img_queue.get()
            request.urlretrieve(img_url, 'imgs/' + filename)
            print(filename + '  下载完成')

def main():
    page_queue=Queue(10)
    img_queue=Queue(1000)
    for x in range(1,11):
        url = 'https://yande.re/post?commit=Search&page=%d&tags=misaki_kurehito' % x
        page_queue.put(url)

    for x in range(5):
        t=Producer(page_queue,img_queue)
        t.start()

    for x in range(5):
        t=Consumer(page_queue,img_queue)
        t.start()

if __name__ == '__main__':
    main()
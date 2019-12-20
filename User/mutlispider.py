import threading
import time
from queue import Queue
from threading import Thread


import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def run(in_q,lock):
    opt = Options()
    opt.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
    opt.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
    opt.add_argument('--headless')  # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
    chrome = webdriver.Chrome(executable_path = r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver", options=opt)
    #chrome = webdriver.Chrome(executable_path=r"C:\Users\13058\AppData\Local\Google\Chrome\Application\chromedriver",options=opt)

    while in_q.empty() is not True:
        course_list = []

        temp = in_q.get()
        chrome.get(temp[5:]) # k = 几位数
        user_id = temp[0:5]
        while True:
            data = chrome.page_source
            soup = BeautifulSoup(data, 'lxml')
            time.sleep(6)

            srlist = soup.find_all('div', {'class': 'cc-courseFunc-f'})

            for x in srlist:
                url = x.find_all('a')
                url = url[0].attrs['href']
                course_list.append(url[2:-6])

            next = soup.find_all('li', {'class': 'pager_next'})
            dis_next = soup.find_all('li', {'class': 'pager_next z-dis'})
            if len(next) == 0 or len(dis_next) == 1:  # 不满一页 或者 完成爬取
                break
            no_list = soup.find('div', {'id': 'j-noCourse'})
            if no_list is not None:
                in_q.task_done()
                break
            chrome.find_element_by_link_text("下一页").click()
        new_li = []  # 去重
        for i in course_list:
            if i not in new_li:
                new_li.append(i)
        if new_li == [] :
            in_q.put(temp)
        else:
            lock.acquire()  # 加锁
            with open('pass5.txt', 'a+') as f:
                f.writelines(str(user_id) + ',"' + str(new_li)+'"')
                f.writelines("\n")
            lock.release()  # 解锁
        in_q.task_done()
    chrome.close()


if __name__ == '__main__':
    queue = Queue()

    file = pd.read_csv('five2.csv')
    df = pd.DataFrame(file)
    for i in range(len(df)):
        document = df[i:i + 1]
        user_url = document['user_url'][i]
        user_id = document['user_id'][i]
        queue.put(str(user_id)+'https://' + user_url + '#/home/course')

    # 加线程锁
    lock = threading.Lock()
    for index in range(20):
        thread = Thread(target=run, args=(queue,lock))
        thread.daemon = True  # 随主线程退出而退出
        thread.start()

    queue.join()  # 队列消费完 线程结束


# -*- coding:utf-8 -*-
from itertools import chain

from selenium import webdriver
from bs4 import BeautifulSoup
import time
import csv
import pandas as pd

'''
作用：获取用户详情页中一页的课程
参数：pageSource某页的源码
返回值：返回该页的课程list
'''

def getPageList(soup):
    slist = soup.find_all('div', {'class': 'cc-courseFunc-f'})  # 所有用户信息

    course_list=[]
    for x in slist:
        url=x.find_all('a')
        url=url[0].attrs['href']
        course_list.append(url[2:-6])

    return course_list
'''
作用：保存用户详情页地址url的所有课程
参数：用户详情页地址url
返回值：用户名，在学习的课程列表
'''
def get_user_data(url):
    # 爬取该课程，获取该课程的网页源代码
    # 因为无法用urllib和request的爬取网页信息，被对方服务器积极拒绝，所以采用模拟浏览器技术
    chrome = webdriver.PhantomJS(executable_path=r"D:\phantomjs-2.1.1-windows\bin\phantomjs.exe")
    chrome.get(url)
    time.sleep(2)

    count = 1
    course_list = []

    data = chrome.page_source
    soup = BeautifulSoup(data, 'html.parser')
    user_name = soup.find_all('div', {'class': 'u-ui-name'}) # 获取user name信息

    if len(user_name) == 0:  # 没有评论
        return user_name, course_list
    user_name = user_name[0].text

    # if len(no_comment) == 1:  # 没有评论
       # return allUserName, allUserUrl, allContent, allScore, url

    while True:

        course_list = chain(course_list, getPageList(soup))

        next = soup.find_all('li', {'class': 'pager_next'})
        dis_next = soup.find_all('li', {'class': 'pager_next z-dis'})
        if len(next) == 0 or len(dis_next) == 1:  # 不满一页 或者 完成爬取
            break
        chrome.find_element_by_link_text("下一页").click()
        data = chrome.page_source
        soup = BeautifulSoup(data, 'html.parser')

        time.sleep(2)
        count += 1

    chrome.quit()
    course_list=list(course_list)
    return user_name, course_list





if __name__ == '__main__':
    file = pd.read_csv('Score_info.csv', usecols=['user_url'])
    df = file['user_url'].tolist()
    all_user_url = list(set(df))
    print(len(all_user_url))

    with open('User_info.csv', 'w', newline='', encoding='utf_8_sig') as csvfile:
        field = ['user_id', 'user_name', 'user_url', 'course_list']
        writer = csv.DictWriter(csvfile, fieldnames=field)
        writer.writeheader()
        for i in range(len(all_user_url)):
            user_id = i
            user_url=all_user_url[i]+'#/home/course'
            user_name, course_list=get_user_data(user_url)
            if(user_name == '' or course_list == []):
                print(str(i)+','+user_url)
            else:
                writer.writerow({'user_id':all_user_url[i], 'user_name':user_name, 'user_url':user_url, 'course_list':course_list})

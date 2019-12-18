# -*- coding : utf-8 -*-
# coding: utf-8
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
    course_list = []
    for x in slist:
        url = x.find_all('a')
        url = url[0].attrs['href']
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
    time.sleep(3)

    count = 1
    course_list = []

    # if len(no_comment) == 1:  # 没有评论
    # return allUserName, allUserUrl, allContent, allScore, url

    while True:
        data = chrome.page_source
        soup = BeautifulSoup(data, 'html.parser')

        course_list = chain(course_list, getPageList(soup))

        next = soup.find_all('li', {'class': 'pager_next'})
        dis_next = soup.find_all('li', {'class': 'pager_next z-dis'})
        if len(next) == 0 or len(dis_next) == 1:  # 不满一页 或者 完成爬取
            break
        chrome.find_element_by_link_text("下一页").click()

        time.sleep(2)
        count += 1

    chrome.quit()
    course_list = list(course_list)
    return course_list


def save_user():
    file = pd.read_csv('score_info.csv', encoding='utf_8_sig', usecols=['user_name', 'user_url'])
    all_user_url = file['user_url'].tolist()
    all_user_name = file['user_name'].tolist()

    with open('User_info.csv', 'w', newline='', encoding='utf_8_sig') as csvfile:
        field = ['user_id', 'user_name', 'user_url']
        writer = csv.DictWriter(csvfile, fieldnames=field)
        writer.writeheader()

        new_url = []
        new_name = []
        for i in range(len(all_user_url)):
            if all_user_url[i] not in new_url:
                new_url.append(all_user_url[i])
                new_name.append(all_user_name[i])

        print(len(new_url))
        print(len(new_name))

        for i in range(len(new_url)):
            user_id = i
            user_url = new_url[i]
            user_name = new_name[i]
            writer.writerow({'user_id': user_id, 'user_name': user_name, 'user_url': user_url})


if __name__ == '__main__':
    data = pd.read_csv('User_info.csv')
    # print(data.columns)  # 获取列索引值
    all_url = data['user_url']  # 获取列名为user url的数据  Series类型 （key ：value）
    all_url = list(all_url)

    course_list=[]
    for url in all_url:
        list=get_user_data(url)
        course_list.append(list)


    course_list= pd.Series(course_list)
    data['course_list'] = course_list  # 将新列的名字设置为course_list
    data.to_csv("1.csv", mode='a', index=False)  # mode=a，以追加模式写入,header表示列名，默认为true,index表示行名，默认为true，再次写入不需要行名

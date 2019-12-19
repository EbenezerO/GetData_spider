# -*- coding : utf-8 -*-
# coding: utf-8
import time

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import csv
import pandas as pd



'''
作用：保存用户详情页地址url的所有课程
参数：用户详情页地址url
返回值：用户名，在学习的课程列表
'''


def get_user_data(url):
    # 爬取该课程，获取该课程的网页源代码
    # 因为无法用urllib和request的爬取网页信息，被对方服务器积极拒绝，所以采用模拟浏览器技术
    #chrome = webdriver.PhantomJS(executable_path=r"D:\phantomjs-2.1.1-windows\bin\phantomjs.exe")
    opt = Options()
    opt.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
    opt.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
    opt.add_argument('--headless')  # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
    chrome = webdriver.Chrome(executable_path = "C:\Program Files (x86)\Google\Chrome\Application\chromedriver", options=opt)
    chrome.get(url)

    course_list = []

    # if len(no_comment) == 1:  # 没有评论
    # return allUserName, allUserUrl, allContent, allScore, url

    while True:
        data = chrome.page_source
        soup = BeautifulSoup(data, 'html.parser')

        courseCard = soup.find('div', {'class': 'u-courseCard-container'})  # 所有用户信息
        srlist = courseCard.find_all('div', {'class': 'u-cc-courseFunc  f-cb'})

        for x in srlist:
            url = x.find_all('a')
            url = url[0].attrs['href']
            course_list.append(url[2:-6])

        next = courseCard.find_all('li', {'class': 'pager_next'})
        dis_next = courseCard.find_all('li', {'class': 'pager_next z-dis'})
        if len(next) == 0 or len(dis_next) == 1:  # 不满一页 或者 完成爬取
            break
        chrome.find_element_by_link_text("下一页").click()

    chrome.quit()

    new_li = [] # 去重
    for i in course_list:
        if i not in new_li:
            new_li.append(i)

    return new_li


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


get_user_data('http://www.icourse163.org/home.htm?userId=1024532082#/home/course')
'''
if __name__ == '__main__':
    data = pd.read_csv('wait.csv')
    # print(data.columns)  # 获取列索引值
    all_url = data['user_url']  # 获取列名为user url的数据  Series类型 （key ：value）
    all_url = list(all_url)

    index=1545
    course_list = []
    for url in all_url:
        list = get_user_data('https://'+url+'#/home/course')
        print(str(index)+','+str(list))
        course_list.append(list)
        index+=1

    course_list = pd.Series(course_list)
    data['course_list'] = course_list  # 将新列的名字设置为course_list
    data.to_csv("1.csv", mode='a', index=False)  # mode=a，以追加模式写入,header表示列名，默认为true,index表示行名，默认为true，再次写入不需要行名
'''
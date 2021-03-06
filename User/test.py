# -*- coding : utf-8 -*-
# coding: utf-8
import re
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
    chrome = webdriver.Chrome(executable_path = r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver", options=opt)
    #chrome = webdriver.Chrome(executable_path = r"C:\Users\13058\AppData\Local\Google\Chrome\Application\chromedriver", options=opt)
    chrome.get(url)

    course_list = []

    # if len(no_comment) == 1:  # 没有评论
    # return allUserName, allUserUrl, allContent, allScore, url

    while True:
        data = chrome.page_source
        soup = BeautifulSoup(data, 'lxml')
        time.sleep(6)

        srlist = soup.find_all('div', {'class': 'cc-courseFunc-f'})
        if srlist == [] :
            break
        for x in srlist:
            url = x.find_all('a')
            url = url[0].attrs['href']
            course_list.append(url[2:-6])

        next = soup.find_all('li', {'class': 'pager_next'})
        dis_next = soup.find_all('li', {'class': 'pager_next z-dis'})
        if len(next) == 0 or len(dis_next) == 1:  # 不满一页 或者 完成爬取
            break
        if len(course_list) == 0:
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

def dupli_remove():
    file1 = pd.read_csv('User_info.csv',encoding='utf_8_sig')
    df1 = pd.DataFrame(file1)
    res=[]
    for j in range(len(df1)):
        document = df1[j:j + 1]
        course_list = document['list'][j]
        str = re.sub('\'', '', course_list)
        str=str[1:-1]
        temp=''
        for k in str:
            if k != ',':
                temp+=k
            else:
                res.append(temp)
                temp=''
        res.append(temp)
    res = list(set(res))
    print(len(res))
    print(res)

'''
file = pd.read_csv('pass61.csv')
id_list = file['id'].tolist()

l1=[]  # 所有没有获取到信息的 user_id
count = 100000
while count <= 230914 :
    if count not in id_list:
        l1.append(count)
    count += 1

file1 = pd.read_csv('six2.csv')
df1 = pd.DataFrame(file1)

with open('six3.csv', 'w', newline='', encoding='utf_8_sig') as csvfile:
    field = ['user_id','user_name','user_url']
    writer = csv.DictWriter(csvfile, fieldnames=field)
    writer.writeheader()
    for j in range(len(df1)):
        document = df1[j:j + 1]
        user_url = document['user_url'][j]
        user_id = document['user_id'][j]
        user_name = document['user_name'][j]
        if user_id not in id_list:      # 需要更改
            writer.writerow({'user_id':user_id,'user_name':user_name,'user_url':user_url})
    
-------------------------------------------
file1 = pd.read_csv('pass5.csv')
    course_list = file1['list']

    file = pd.read_csv('User_info.csv')
    file['course_list'] = course_list  # 将新列的名字设置为course_list
    file.to_csv("2.csv", mode='a', index=False)  # mode=a，以追加模式写入,header表示列名，默认为true,index表示行名，默认为true，再次写入不需要行名 

'''

if __name__ == '__main__':
     dupli_remove()

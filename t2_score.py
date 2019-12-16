# -*- coding: UTF-8 -*-
from selenium import webdriver
from pyquery import PyQuery as pq
from bs4 import BeautifulSoup
import time
import csv
import pandas as pd
import re
from itertools import chain


'''
作用：获取课程评论页中一页的所有评论
参数：pageSource某页的源码
返回值：返回爬取课程中一页的所有用户的allUserName,allUserUrl,allContent,allScore
'''
def getPageScore(soup):
    user_info=soup.find_all('div',{'class':'ux-mooc-comment-course-comment_comment-list_item_body_user-info'}) #所有用户信息
    content = soup.find_all('div',{'class': 'ux-mooc-comment-course-comment_comment-list_item_body_content'})  # 包含全部评论项目的总表标签
    allUserName=[]
    allUserUrl=[]
    allContent=[]
    allScore=[]
    for i in range(len(content)):
        #用户信息
        sUserUrl =user_info[i].contents[1].attrs['href']
        sUserName=user_info[i].contents[1].string
        allUserUrl.append(sUserUrl[2:])
        allUserName.append(sUserName)

        #用户评分
        sScore=user_info[i].find_all('i',{'class':'star ux-icon-custom-rating-favorite'})
        allScore.append(str(len(sScore)))

        #评论内容
        sContent = content[i].find_all('span')
        allContent.append(sContent[0].text)

    return allUserName,allUserUrl,allContent,allScore
'''
作用：保存某一具体课程的所有评论
参数：courseUrlList是所有课程详情页网址
返回值：出错的课程网址
'''
def get_score_data(url):
    # 爬取该课程，获取该课程的网页源代码
    # 因为无法用urllib和request的爬取网页信息，被对方服务器积极拒绝，所以采用模拟浏览器技术
    chrome = webdriver.PhantomJS(executable_path=r"D:\phantomjs-2.1.1-windows\bin\phantomjs.exe")
    chrome.get(url)
    chrome.find_element_by_id("review-tag-button").click()
    time.sleep(2)
    count = 1

    allUserName = []
    allUserUrl = []
    allContent = []
    allScore = []

    errorUrl=[]
    while(True):
        data = chrome.page_source
        soup = BeautifulSoup(data, 'html.parser')
        no_comment = soup.find_all('div', {'class': 'ux-mooc-comment-course-comment_no-comment'})
        if (len(no_comment) == 1): # 没有评论
            errorUrl.append(url)
            break
        tempUserName, tempUserUrl, tempContent, tempScore = getPageScore(soup)
        for i in range(len(tempScore)):
            allUserName.append(tempUserName[i])
            allUserUrl.append(tempUserUrl[i])
            allContent.append(tempContent[i])
            allScore.append(tempScore[i])

        next = soup.find_all('li', {'class': 'ux-pager_btn ux-pager_btn__next'})
        if (len(next) == 0 or next[0].contents[1].attrs['class'] == ['th-bk-disable-gh']):  # 不满一页 或者 完成爬取
            # print("到最后一页,成功结束")
            break
        chrome.find_element_by_link_text("下一页").click()
        time.sleep(3)
        count += 1

    chrome.quit()
    return allUserName, allUserUrl, allContent, allScore,errorUrl


#get_score_data('http://www.icourse163.org/course/ECJTU-1206602803')
'''
file = pd.read_csv('Score_info.csv', usecols=['id'])
df = pd.DataFrame(file)
for i in range(len(df)):
    document = df[i:i + 1]
    course_id = document['id'][i]
    '''
if __name__=='__main__':
    file = pd.read_csv('1.csv', usecols=['id','url'])
    df = pd.DataFrame(file)

    with open('2.csv', 'w', encoding='utf_8_sig') as csvfile:
        field = ['course_id', 'course_url', 'user_name', 'user_url', 'score','content']
        writer = csv.DictWriter(csvfile, fieldnames=field)
        writer.writeheader()

        for i in range(len(df)):
            document = df[i:i + 1]
            course_url = document['url'][i]
            course_id = document['id'][i]
            allUserName, allUserUrl, allContent, allScore, errorUrl = get_score_data(course_url)
            if errorUrl:  # 课程没有评论
                print(str(course_id) + ',' + errorUrl[0])
            for j in range(len(allUserName)):
                #print(str(course_id) + ',' + course_url + ',' + allUserName[j] + ',' + allUserUrl[j] + ',' + allScore[j] + ',' + allContent[j])
                writer.writerow({'course_id': str(course_id), 'course_url': course_url, 'user_name': allUserName[j],'user_url': allUserUrl[j], 'score': allScore[j], 'content': allContent[j]})
            time.sleep(2)




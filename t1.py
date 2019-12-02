# -*- coding: UTF-8 -*-
from selenium import webdriver
from pyquery import PyQuery as pq
import time
import csv
import pandas as pd
import re
from itertools import chain

'''
作用：获取某系列课程中一页的所有课程的网址
参数：pageSource某页的源码
返回值：返回爬取系列课程中一页的所有课程的网址
'''
def getPageUrl(pageSource):
    code = pq(pageSource)
    href = code("#j-courseCardListBox a")
    urlList = []
    for i in href:
        temp = str(code(i).attr("href"))
        if temp.__contains__("www") and not temp.__contains__("https"):
            urlList.append("http:" + temp)
    urlList = list(set(urlList))
    for x in urlList:
        print(x)
    return urlList


'''
作用：对某一系列课程进行翻页爬取该系列课程的所有课程的网址
参数：class_urls是某系列课程的首页网址
返回值：该系列课程所有课程的网址
'''
def getAllUrl(pageSourceUrl):
    chrome = webdriver.PhantomJS(executable_path=r"D:\phantomjs-2.1.1-windows\bin\phantomjs.exe")
    webdriver.PhantomJS()
    chrome.get(pageSourceUrl)
    allUrl=[]
    count=1
    while (True):
        allUrl=chain(allUrl,getPageUrl(chrome.page_source))
        print(count)
        #print(chrome.find_element_by_class_name("ux-pager_btn__next").get_attribute("class"))
        try:
            chrome.find_element_by_link_text("下一页").click()
            time.sleep(3)
            count+=1
        except:
            print("没有找到元素")
            break
    chrome.quit()
    allUrl = list(set(allUrl))  # 网址去重
    allUrl.remove('http:http://www.icourse163.org/topics/2018NationalLevelMOOC/')
    return allUrl

'''
作用：保存某一具体课程的课程名、老师、概述、大纲
参数：courseUrlList是所有课程详情页网址
返回值：出错的课程网址
'''
def get_course_data(url):
    # 爬取该课程，获取该课程的网页源代码
    # 因为无法用urllib和request的爬取网页信息，被对方服务器积极拒绝，所以采用模拟浏览器技术
    chrome = webdriver.PhantomJS(executable_path=r"D:\phantomjs-2.1.1-windows\bin\phantomjs.exe")
    chrome.get(url)
    data = chrome.page_source


    course_name = '<span class="course-title f-ib f-vam">(.*?)</span>'
    teacher_name = 'lectorName : "(.*?)"'
    summary='<div class="f-richEditorText">(.*?)</div>'

    course_name = re.compile(course_name).findall(data)  # 返回的是列表
    teacher_name = re.compile(teacher_name).findall(data)  # 返回的是列表
    summary =re.compile(summary).findall(data)
    return course_name[0], teacher_name[0],summary

'''
     chrome.find_element_by_id("review-tag-button").click()
    time.sleep(2)
    score = '<div class="ux-mooc-comment-course-comment_head_rating-scores"><span>(.*?)</span></div>'
    data=chrome.page_source
    score =re.compile(score).findall(data)  # 返回的是列表
    chrome.close()'''




'''
作用：将课程信息保存到csv文件中
'''
def saveCourseInfoes(courseUrlList=[]):
    count=0
    errorlist=[]
    with open('data.csv','w') as csvfile:
        fieldnames=['CourseId','courseName','teacher','score']
        writer=csv.DictWriter(csvfile,fieldnames=fieldnames)
        writer.writeheader()

        while(count<courseUrlList.__len__()):
            data=get_course_data(courseUrlList[count])
            if(data!=None):
                print(data)
                writer.writerow({"CourseId":data[0],"courseName": data[1],"teacher": data[2],"score":data[3]})
            else:
                errorlist.append(courseUrlList[count])
            count+=1
    return errorlist
'''
if __name__=='__main__':
    allUrl = getAllUrl("https://www.icourse163.org/category/all")
    with open('allurl.csv', 'w') as csvfile:
        field_all = ['AllUrl']
        writer = csv.DictWriter(csvfile, fieldnames=field_all)
        writer.writeheader()
        for x in allUrl:
            writer.writerow({"AllUrl":x})

    errorlist=saveCourseInfoes(allUrl)
    with open('errorUrl.csv', 'w') as csvfile1:
        field_error = ['error']
        writer1 = csv.DictWriter(csvfile1, fieldnames=field_error)
        writer1.writeheader()
        for y in errorlist:
            writer1.writerow({"error":y})'''

'''
file = pd.read_csv('allurl.csv')
df = pd.DataFrame(file)

dic={}
for i in range(len(df)):
    document = df[i:i+1]
    url=document['AllUrl'][i]
    dic[i]=url
new_df = pd.DataFrame.from_dict(dic,orient='index')
new_df.to_csv('pandas_allurl.csv')
'''
file = pd.read_csv('pandas_allurl.csv',usecols=['url'])
df=pd.DataFrame(file)
for i in range(len(df)):
    document = df[i:i+1]
    url = document['url'][i]
    course_name, teacher_name,summary=get_course_data(url)
















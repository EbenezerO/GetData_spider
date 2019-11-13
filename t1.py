# -*- coding: UTF-8 -*-
from selenium import webdriver
from pyquery import PyQuery as pq
import time
import csv
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
        #print(count)
        #print(chrome.find_element_by_class_name("ux-pager_btn__next").get_attribute("class"))
        chrome.find_element_by_link_text("下一页").click()
        time.sleep(3)
        if (chrome.find_element_by_class_name("ux-pager_btn__next").get_attribute("class") == "ux-pager_btn ux-pager_btn__next z-dis"):
            allUrl = chain(allUrl, getPageUrl(chrome.page_source))
            print(count)
            break
        count+=1
    chrome.quit()
    allUrl = list(set(allUrl))  # 网址去重
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

    courseId= 'courseId : "(.*?)"'
    course_name = '<span class="course-title f-ib f-vam">(.*?)</span>'
    teacher = 'lectorName : "(.*?)"'
    brief='<div class="f-richEditorText"><p>(.*?)</p></div>'

    courseId = re.compile(courseId).findall(data)  # 返回的是列表
    course_name = re.compile(course_name).findall(data)  # 返回的是列表
    teacher = re.compile(teacher).findall(data)  # 返回的是列表
    brief = re.compile(brief).findall(data)  # 返回的是列表

    chrome.find_element_by_id("review-tag-button").click()
    time.sleep(2)
    score = '<div class="ux-mooc-comment-course-comment_head_rating-scores"><span>(.*?)</span></div>'
    data=chrome.page_source
    score =re.compile(score).findall(data)  # 返回的是列表

    chrome.close()
    return courseId[0],course_name[0], teacher[0],brief[0],score[0]

'''
作用：将课程信息保存到csv文件中
'''
def saveCourseInfoes(courseUrlList=[]):
    count=0
    with open('data.csv','w') as csvfile:
        fieldnames=['CourseId','courseName','teacher','brief','score']
        writer=csv.DictWriter(csvfile,fieldnames=fieldnames)
        writer.writeheader()

        while(count<courseUrlList.__len__()):
            data=get_course_data(courseUrlList[count])
            if(data[0]!=""):
                print(data)
                writer.writerow({"CourseId":data[0],"courseName": data[1],"teacher": data[2],"brief": data[3],"score":data[4]})
            count+=1

if __name__=='__main__':

    allUrl = getAllUrl("https://www.icourse163.org/category/all")
    saveCourseInfoes(allUrl)







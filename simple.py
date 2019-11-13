# -*- coding: UTF-8 -*-
from selenium import webdriver
from pyquery import PyQuery as pq
import time
import redis
import chardet
import requests
from itertools import chain
r = redis.from_url("http://127.0.0.1:6379")
def getPageUrl(pageSource):
    code = pq(pageSource)
    href = code("#j-courseCardListBox a")
    urlList = []
    for i in href:
        temp = str(code(i).attr("href"))
        if temp.__contains__("www") and not temp.__contains__("https"):
            urlList.append("http:" + temp)
    urlList = list(set(urlList))
    return urlList

def getAllUrl(pageSourceUrl):
    chrome = webdriver.PhantomJS(executable_path=r"E:\phantomJs\phantomJs.exe")
    webdriver.PhantomJS()
    chrome.get(pageSourceUrl)
    allUrl=[]
    count=1
    while (True):
        allUrl=chain(allUrl,getPageUrl(chrome.page_source))
        print(count)
        print(chrome.find_element_by_class_name("ux-pager_btn__next").get_attribute("class"))
        chrome.find_element_by_link_text("下一页").click()
        time.sleep(3)
        if (chrome.find_element_by_class_name("ux-pager_btn__next").get_attribute("class") == "ux-pager_btn ux-pager_btn__next z-dis"):
            allUrl = chain(allUrl, getPageUrl(chrome.page_source))
            print(count)
            break
        count+=1
    chrome.quit()
    return allUrl

def saveCourseInfoes(courseUrlList=[]):
    count,index=0,0
    errorList=[]
    while(count<courseUrlList.__len__()):
        info = pq(requests.get(courseUrlList[count]).text)
        print(info(".course-title.f-ib.f-vam").text())
        t = info(".f-richEditorText")
        if (len(t) >= 3):
            print(info(".cnt.f-fl").text().replace("\n", " "))
            r.hset("CourseInfo", index, {
                "courseName": info(".course-title.f-ib.f-vam").text(),
                "teacherInfo": info(".cnt.f-fl").text().replace("\n", " "),
                "anOverviewOfTheCourse": info(t[0]).text(),
                "teachingObjectives": info(t[1]).text(),
                "syllabus": info(t[2]).text()
            })
            index+=1
        else:
            errorList.append(courseUrlList[count])
        count+=1
    return errorList


timeStart=time.time()
allUrl=getAllUrl("https://www.icourse163.org/category/all")
errorList=saveCourseInfoes(list(allUrl))
print("\n\n")
for i in errorList:
    print(i)
print("共耗时:",end=" ")
print(time.time()-timeStart)
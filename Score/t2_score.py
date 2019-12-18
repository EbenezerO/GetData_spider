# -*- coding: UTF-8 -*-
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import csv
import pandas as pd

'''
作用：获取课程评论页中一页的所有评论
参数：pageSource某页的源码
返回值：返回爬取课程中一页的所有用户的allUserName,allUserUrl,allContent,allScore
'''

def getPageScore(soup):
    user_info = soup.find_all('div',
                              {'class': 'ux-mooc-comment-course-comment_comment-list_item_body_user-info'})  # 所有用户信息
    content = soup.find_all('div',
                            {'class': 'ux-mooc-comment-course-comment_comment-list_item_body_content'})  # 包含全部评论项目的总表标签
    allUserName = []
    allUserUrl = []
    allContent = []
    allScore = []
    for i in range(len(content)):
        # 用户信息
        sUserUrl = user_info[i].contents[1].attrs['href']
        sUserName = user_info[i].contents[1].string
        allUserUrl.append(sUserUrl[2:])
        allUserName.append(sUserName)

        # 用户评分
        sScore = user_info[i].find_all('i', {'class': 'star ux-icon-custom-rating-favorite'})
        allScore.append(len(sScore))

        # 评论内容
        sContent = content[i].find_all('span')
        str = sContent[0].text.replace('\n', '')
        allContent.append(str)

    return allUserName, allUserUrl, allContent, allScore


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

    data = chrome.page_source
    soup = BeautifulSoup(data, 'html.parser')
    no_comment = soup.find_all('div', {'class': 'ux-mooc-comment-course-comment_no-comment'})
    if len(no_comment) == 1:  # 没有评论
        return allUserName, allUserUrl, allContent, allScore, 'no'

    while True:
        data = chrome.page_source
        soup = BeautifulSoup(data, 'html.parser')

        tempUserName, tempUserUrl, tempContent, tempScore = getPageScore(soup)
        for k in range(len(tempScore)):
            allUserName.append(tempUserName[k])
            allUserUrl.append(tempUserUrl[k])
            allContent.append(tempContent[k])
            allScore.append(tempScore[k])

        next = soup.find_all('li', {'class': 'ux-pager_btn ux-pager_btn__next'})
        if len(next) == 0 or next[0].contents[1].attrs['class'] == ['th-bk-disable-gh']:  # 不满一页 或者 完成爬取
            # print("到最后一页,成功结束")
            break
        chrome.find_element_by_link_text("下一页").click()
        time.sleep(2)
        count += 1

    chrome.quit()
    return allUserName, allUserUrl, allContent, allScore, url


# get_score_data('http://www.icourse163.org/course/HZAU-1002731009')
'''
file = pd.read_csv('errorUrl.csv', usecols=['course_id'])
df = pd.DataFrame(file)
t=df['course_id'].tolist()
T=list(set(t))

file1 = pd.read_csv('no_comment.csv', usecols=['course_id','course_url'])
df1 = pd.DataFrame(file1)
for i in range(len(df1)):
    document = df1[i:i + 1]
    course_url = document['course_url'][i]
    course_id = document['course_id'][i]
    if not course_id in T:
        print(str(course_id) + ',' + course_url)


'''
if __name__ == '__main__':
    file = pd.read_csv('all_course_url.csv', usecols=['id', 'url'])
    df = pd.DataFrame(file)

    no_comment=[]
    with open('Score_info.csv', 'w', newline='', encoding='utf_8_sig') as csvfile:
        field = ['course_id', 'course_url', 'user_name', 'user_url', 'score', 'content']
        writer = csv.DictWriter(csvfile, fieldnames=field)
        writer.writeheader()

        for i in range(len(df)):
            document = df[i:i + 1]
            course_url = document['url'][i]
            course_id = document['id'][i]
            allUserName, allUserUrl, allContent, allScore, errorUrl = get_score_data(course_url)
            # print(course_id)
            if errorUrl == 'no':  # 课程没有评论
                no_comment.append(str(course_id) + ',' + course_url)
            if len(allUserName) == 0  and errorUrl != 'no':  # 出现错误
                print(str(course_id) + ',' + errorUrl)
            for j in range(len(allUserName)):
                writer.writerow({'course_id': str(course_id), 'course_url': course_url, 'user_name': allUserName[j],
                                 'user_url': allUserUrl[j],
                                 'score': allScore[j], 'content': allContent[j]})
            time.sleep(2)

    print('-------------------')
    for x in no_comment:
        print(x)

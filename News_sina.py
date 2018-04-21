"""
作者:Justin
日期:2017/11/29
功能:爬取新浪新闻标题，内容，作者，来源与日期
"""

import requests
import pandas
from bs4 import BeautifulSoup
from datetime import datetime
import json
import re


def get_all_news():
    news_detail = []
    url = 'http://api.roll.news.sina.com.cn/zt_list?' \
        'channel=news&cat_1=gnxw&cat_2==gdxw1||=gatxw||=zs-pl||' \
        '=mtjj&level==1||=2&show_ext=1&show_all=1&show_num=22&tag=1' \
        '&format=json&page={}'
    for i in range(1, 4):
        new_url = url.format(i)
        get_news = requests.get(new_url)
        get_news.encoding = 'utf-8'
        json_load = json.loads(get_news.text.lstrip('  newsloadercallback(').rstrip(');'))
        for news_url in json_load['result']['data']:
            news_detail.append(get_file_detail(news_url['url']))
    return news_detail


def get_file_detail(news_url):
    article_detail = {}
    url = requests.get(news_url)
    url.encoding = 'utf-8'
    soup = BeautifulSoup(url.text, 'lxml')
    #文章标题
    article_detail['page_header'] = soup.find('h1', {'class': 'main-title'}).text
    #文章时间
    article_detail['time_source'] = soup.find('span', {'class': 'date'}).text
    #文章来源
    article_detail['media_source'] = soup.select('.source')[0].text
    #文章内容
    article_source = soup.find('div', {'id': 'article'})
    article_div = article_source.find_all('p')[:-1]
    # select语句，如果是class，则加.page-header,若是id，则加#artibody
    # 如果使用select，则是soup.select('#artibody p')[:-1]，这样会简短很多
    article_detail['article_list'] = \
        '\n'.join([p.text.strip() for p in article_source.find_all('p')[:-1]])
    #文章编辑者
    article_detail['editor'] = \
        soup.find('p', {'class': 'show_author'}).text.lstrip('责任编辑：')
    #文章评论数
    search_str = 'doc-i(.+).shtml'
    comment_news_url = re.search(search_str, news_url)
    comment_str_url = 'http://comment5.news.sina.com.cn/page/info?version=1' \
                      '&format=json&channel=sh&newsid=comos-{}' \
                      '&group=undefined&compress=0&ie=utf-8&oe=utf-8&' \
                      'page=1&page_size=3&t_size=3&h_size=3&thread=1'
    comment_url_flag = comment_news_url.group(1)
    comment_url = comment_str_url.format(comment_url_flag)
    comment = requests.get(comment_url)
    json_load = json.loads(comment.text)
    article_detail['comment_num'] = json_load['result']['count']['total']
    return article_detail


def main():
    # url = requests.get('http://news.sina.com.cn/china/?vt=3')
    # url.encoding = 'utf-8'
    # soup = BeautifulSoup(url.text, 'lxml')
    # div_list = soup.find_all('div', {'class': 'news-item'})
    # news_list = []
    # for news in div_list:
    #     if len(news.find_all('h2')) > 0:
    #         h2 = news.find('h2').text
    #         a = news.find('a')['href']
    #         news_list.append([str(h2), a])
    #         time = news.find('div', {'class': 'time'}).text
    #         print(time, a, h2)
    # news_dict = dict(news_list)
    # user_want = input('Please input your want to see the news title: ')
    # news_url = news_dict[user_want]
    news_detail = get_all_news()
    data_view = pandas.DataFrame(news_detail)
    data_view.to_excel('news.xlsx')

    #写入到SQL中
    # import sqlite3
    # with sqlite3.connect('news.sqlite) as db:
    #写入SQL中
    #df2 = df.to sql('news', con = db)
    #读取SQL中的数据
    #df3 = pandas.read_sql_query('SELECT*FORM news', con = db)


if __name__ == '__main__':
    main()

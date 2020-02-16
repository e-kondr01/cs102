import re
import requests

from bs4 import BeautifulSoup
from typing import List, Dict


def extract_news(parser) -> List[Dict]:
    """ Extract news from a given web page """
    news_list = []
    news_table = parser.table.findAll('table')[1]
    titles = news_table.findAll('a', class_='storylink')
    authors = news_table.findAll('a', class_='hnuser')
    urls = news_table.findAll('a', class_='storylink')
    points = news_table.findAll('span', class_='score')
    comments = news_table.find_all('a', string=[re.compile('comment'),
                                                re.compile('discuss')])
    for i in range(len(titles)):
        post_dict = {}
        post_dict['author'] = authors[i].text
        post_dict['comments'] = comments[i].text.split()[0]
        if post_dict['comments'] == 'discuss':
            post_dict['comments'] = 0
        post_dict['points'] = points[i].text.split()[0]
        post_dict['title'] = titles[i].text
        post_dict['url'] = urls[i].get('href')
        news_list.append(post_dict)
    return news_list


def extract_next_page(parser) -> str:
    """ Extract next page URL """
    news_table = parser.table.findAll('table')[1]
    next_page = news_table.find(class_='morelink')['href']
    return next_page


def get_news(url: str, n_pages: int = 1) -> List:
    """ Collects news from a given web page """
    news = []
    while n_pages:
        print("Collecting data from page: {}".format(url))
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        news_list = extract_news(soup)
        next_page = extract_next_page(soup)
        url = "https://news.ycombinator.com/" + next_page
        news.extend(news_list)
        n_pages -= 1
    return news


if __name__ == '__main__':
    news_list = get_news("https://news.ycombinator.com/", n_pages=2)
    print(len(news_list))

import re
import requests

from bs4 import BeautifulSoup
from typing import List, Dict, Optional


def extract_news(parser) -> List[Dict]:
    """ Extract news from a given web page """
    news_list = []
    news_table = parser.table.findAll('table')[1]
    uptext = news_table.findAll('a', class_='storylink')
    subtext = news_table.findAll('td', class_='subtext')
    for i in range(len(uptext)):
        post_dict = {}
        post_dict['title'] = uptext[i].text
        post_dict['url'] = uptext[i].get('href')
        if 'item' in post_dict['url']:
            post_dict['url'] = 'no link'
        try:
            post_dict['points'] = subtext[i].find(class_='score').text.split()[0]
        except AttributeError:
            post_dict['points'] = 0
        try:
            post_dict['author'] = subtext[i].find(class_='hnuser').text
        except AttributeError:
            post_dict['author'] = 'no author'
        comments = subtext[i].find(string=[re.compile('comment'),
                                           re.compile('discuss')])
        if not comments or comments == 'discuss':
            comments = 0
        else:
            comments = comments.split()[0]
        post_dict['comments'] = comments
        news_list.append(post_dict)
    return news_list


def extract_next_page(parser) -> Optional[str]:
    """ Extract next page URL """
    news_table = parser.table.findAll('table')[1]
    try:
        next_page = news_table.find(class_='morelink')['href']
    except TypeError:
        return None
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
        if next_page:
            url = "https://news.ycombinator.com/" + next_page
            news.extend(news_list)
            n_pages -= 1
        else:
            return news
    return news


if __name__ == '__main__':
    news_list = get_news("https://news.ycombinator.com/", n_pages=2)

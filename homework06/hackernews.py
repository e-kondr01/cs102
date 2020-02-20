from bottle import (
    route, run, template, request, redirect
)

from scraputils import get_news
from db import News, session
from bayes import NaiveBayesClassifier


@route("/news")
def news_list():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    return template('C:\cs102\homework06\\news_template.tpl', rows=rows)


@route("/add_label/")
def add_label():
    news_label = request.query.label
    news_id = request.query.id
    s = session()
    changing_news = s.query(News).get(news_id)
    changing_news.label = news_label
    s.commit()
    redirect("/news")


@route("/update")
def update_news():
    news_list = get_news("https://news.ycombinator.com/", n_pages=20)
    s = session()
    old_news_list = s.query(News).all()
    for news in news_list:
        for old_news in old_news_list:
            if (news['title'] == old_news.title and
                    news['author'] == old_news.author):
                break
        else:
            new_news = News(title=news['title'],
                            author=news['author'],
                            url=news['url'],
                            comments=news['comments'],
                            points=news['points'])
            s.add(new_news)
            s.commit()
    redirect("/news")


@route("/classify")
def classify_news():
    # PUT YOUR CODE HERE
    pass


if __name__ == "__main__":
    run(host="localhost", port=8080)

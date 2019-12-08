import config
import pandas as pd
import pymorphy2
import requests
import textwrap

from pandas.io.json import json_normalize
from stop_words import get_stop_words
from string import Template, punctuation
from tqdm import tqdm

morph = pymorphy2.MorphAnalyzer()
access_token = config.VK_CONFIG['access_token']
stop_words = get_stop_words('ru')


def get_wall(
    owner_id: str = '',
    domain: str = '',
    offset: int = 0,
    count: int = 10,
    filter: str = 'owner',
    extended: int = 0,
    fields: str = '',
    v: str = '5.103'
) -> pd.DataFrame:
    """
    Возвращает список записей со стены пользователя или сообщества.

    @see: https://vk.com/dev/wall.get

    :param owner_id: Идентификатор пользователя или сообщества, со стены
     которого необходимо получить записи.
    :param domain: Короткий адрес пользователя или сообщества.
    :param offset: Смещение, необходимое для выборки определенного
     подмножества записей.
    :param count: Количество записей, которое необходимо получить (0 - все
     записи).
    :param filter: Определяет, какие типы записей на стене необходимо получить.
    :param extended: 1 — в ответе будут возвращены дополнительные поля
     profiles и groups, содержащие информацию о пользователях и сообществах.
    :param fields: Список дополнительных полей для профилей и сообществ,
     которые необходимо вернуть.
    :param v: Версия API.
    """

    code = {
        "owner_id": owner_id,
        "domain": domain,
        "offset": offset,
        "count": count,
        "filter": filter,
        "extended": extended,
        "fields": fields,
        "v": v
    }

    response = requests.post(
        url="https://api.vk.com/method/execute",
        data={
            "code": f'return API.wall.get({code});',
            "access_token": access_token,
            "v": v
        }
    )

    wall = response.json()
    return wall


def prep_text(wall, count: int) -> list:
    """ Подготовка текста к построению тематической модели """
    text = ''
    for i in range(count):
        text += wall['response']['items'][i]['text']
        text += ' '

    # Удаление ссылок, хэштегов, стоп-слов
    textlist = text.split()
    for i in range(len(textlist)):
        try:
            if ('https://' in textlist[i] or '#' in textlist[i] or
                    textlist[i] in stop_words):
                del textlist[i]
        except IndexError:
            break
    text = ' '.join(textlist)

    # Удаление символов, не являющихся буквами (пунктуация, эмодзи и т.д.)
    newtext = ''
    for c in text:
        if c.isalpha() is True or c == ' ':
            newtext += c
        if c == '\n':
            newtext += ' '

    # Проведение нормализации
    textlist = newtext.split()
    for i in range(len(textlist)):
        textlist[i] = morph.parse(textlist[i])[0].normal_form

    return textlist


if __name__ == '__main__':
    wall1 = get_wall(domain='studanal', count=8)
    text1 = prep_text(wall1, 8)
    print(text1)

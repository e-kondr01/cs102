import config
import requests
import time

from datetime import date
from statistics import median
from typing import List, Dict, Optional


def get(url: str, params={}, timeout=5, max_retries=5,
        backoff_factor=0.3) -> Optional[requests.models.Response]:
    """ Выполнить GET-запрос

    :param url: адрес, на который необходимо выполнить запрос
    :param params: параметры запроса
    :param timeout: максимальное время ожидания ответа от сервера
    :param max_retries: максимальное число повторных запросов
    :param backoff_factor: коэффициент экспоненциального нарастания задержки
    """
    for i in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=timeout)
            return response
        except requests.exceptions.RequestException:
            if i == max_retries - 1:
                raise
            delay = backoff_factor * 2 ** i
            time.sleep(delay)


def get_friends(user_id: int, fields: str) -> dict:
    """ Вернуть данных о друзьях пользователя

    :param user_id: идентификатор пользователя, список друзей которого
    нужно получить
    :param fields: список полей, которые нужно получить для
    каждого пользователя
    """
    assert isinstance(user_id, int), "user_id must be positive integer"
    assert isinstance(fields, str), "fields must be string"
    assert user_id > 0, "user_id must be positive integer"

    domain = config.VK_CONFIG['domain']
    access_token = config.VK_CONFIG['access_token']
    v = '5.103'

    query = f"{domain}/friends.get?access_token={access_token}&user_id\
={user_id}&fields={fields}&v={v}"
    response = requests.get(query)
    friends = response.json()
    return friends


def age_predict(user_id: int) -> int:
    """
    >>> age_predict(???)
    ???
    """
    assert isinstance(user_id, int), "user_id must be positive integer"
    assert user_id > 0, "user_id must be positive integer"

    friends = get_friends(user_id, 'bdate')
    ages = []

    for i in range(friends['response']['count']):
        try:
            _, _, byear = friends['response']['items'][i]['bdate'].split['.']
            age = date.year() - byear
            ages.append(age)
            print(age)
        except:
            pass
    guess_age = median(ages)
    return guess_age


def messages_get_history(user_id, offset=0, count=20):
    """ Получить историю переписки с указанным пользователем

    :param user_id: идентификатор пользователя, с которым
    нужно получить историю переписки
    :param offset: смещение в истории переписки
    :param count: число сообщений, которое нужно получить
    """
    assert isinstance(user_id, int), "user_id must be positive integer"
    assert user_id > 0, "user_id must be positive integer"
    assert isinstance(offset, int), "offset must be positive integer"
    assert offset >= 0, "user_id must be positive integer"
    assert count >= 0, "user_id must be positive integer"
    # PUT YOUR CODE HERE

test = age_predict(74008457)
print(test)

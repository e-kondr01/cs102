import config
import requests
import time

from datetime import datetime
from statistics import median
from typing import List, Dict, Optional

curr_year = datetime.today().timetuple()[0]


def get(url: str, params: dict = {}, timeout: int = 5, max_retries: int = 5,
        backoff_factor: float = 0.3) -> Optional[requests.models.Response]:
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


def get_friends(user_id: int, fields: str = '') -> list:
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
    v = config.VK_CONFIG['version']

    # Если нет fields, то функция должна возвращать только список id друзей
    if fields:
        query = f"{domain}/friends.get?access_token={access_token}&user_id\
={user_id}&fields={fields}&v={v}"
    else:
        query = f"{domain}/friends.get?access_token={access_token}&user_id\
={user_id}&v={v}"
    response = requests.get(query)
    friends1 = response.json()

    try:
        if friends1['response']['count'] == 5000:
            pass
    except KeyError:
        print(friends1)
        return None

    # Случай, когда число друзей превосходит максимально допустимое
    if friends1['response']['count'] == 5000:
        query = f"{domain}/friends.get?access_token={access_token}&user_id\
={user_id}&fields={fields}&v={v}&offset=5000"
        response = requests.get(query)
        friends2 = response.json()
        friends = [*friends1['response']['items'], *friends2[
            'response']['items']]
    else:
        friends = friends1['response']['items']

    return friends


def age_predict(user_id: int) -> float:
    """
    :param user_id: идентификатор пользователя, возраст которого
нужно предсказать
    """
    assert isinstance(user_id, int), "user_id must be positive integer"
    assert user_id > 0, "user_id must be positive integer"

    friends = get_friends(user_id, 'bdate')
    ages = []

    for friend in friends:
        try:
            bdate = friend['bdate']
        except KeyError:
            continue
        try:
            bday, bmonth, byear = bdate.split('.')
        except ValueError:
            continue
        byear = int(byear)
        age = curr_year - byear
        ages.append(age)
    guess_age = median(ages)
    return guess_age


if __name__ == '__main__':
    test = age_predict(154712555)
    print(test)

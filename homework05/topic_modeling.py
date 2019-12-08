import config
import pandas as pd
import requests
import textwrap

from pandas.io.json import json_normalize
from string import Template
from tqdm import tqdm

access_token = config.VK_CONFIG['access_token']


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


if __name__ == '__main__':
    wall1 = get_wall(domain='studanal', count=1)
    with open('test123.txt', 'w') as f:
        f.write(str(wall1))

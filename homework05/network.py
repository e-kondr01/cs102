import igraph
import time

from api import get_friends
from igraph import Graph, plot
from typing import List


def get_network(users_ids: List[int], as_edgelist: bool = True):
    """ Building a friend graph for an arbitrary list of users """
    edges = set()
    count = 1  # Т. к. первый запрос совершается до вызова функции
    start_time = time.time()
    curr_time = time.time()
    new_users_ids = []

    # Исключаем пользователей, которые не имеют общих друзей
    # Кластеризация не происходит, когда есть такие пользователи
    for uid in users_ids:
        # Time-out для запросов (не больше 3 в секунду)
        prev_time = curr_time
        curr_time = time.time()
        if 1 - (curr_time - start_time) <= 0:
            start_time = prev_time
        elif count == 3:
            wait = 1 - (curr_time - start_time)
            time.sleep(wait)
            count = 1
            start_time = time.time()
        else:
            count += 1

        user_friends = get_friends(uid)

        if not user_friends:
            continue
        for friend_id in user_friends:
            if friend_id in users_ids:
                new_users_ids.append(uid)
                break

    # определяем рёбра графа
    for uid in new_users_ids:
        # Time-out для запросов (не больше 3 в секунду)
        prev_time = curr_time
        curr_time = time.time()
        if 1 - (curr_time - start_time) <= 0:
            start_time = prev_time
        elif count == 3:
            wait = 1 - (curr_time - start_time)
            time.sleep(wait)
            count = 1
            start_time = time.time()
        else:
            count += 1

        user_friends = get_friends(uid)

        if not user_friends:
            continue
        for friend_id in user_friends:
            if friend_id in new_users_ids:
                edges.add((new_users_ids.index(uid),
                           new_users_ids.index(friend_id)))

    edges = list(edges)
    vertices = new_users_ids

    if as_edgelist:
        return vertices, edges

    else:
        matrix = [[0 for _ in vertices] for _ in vertices]
        for edge in edges:
            matrix[edge[0]][edge[1]] = 1
        return matrix


def plot_graph(vertices: list, edges: list) -> None:
    """Визуализация графа"""
    g = Graph(vertex_attrs={"label": vertices}, edges=edges, directed=False)

    N = len(vertices)
    visual_style = {}
    visual_style["layout"] = g.layout_fruchterman_reingold(
                                                            maxiter=1000,
                                                            area=N**3,
                                                            repulserad=N**3)
    g.simplify(multiple=True, loops=True)
    communities = g.community_edge_betweenness(directed=False)
    clusters = communities.as_clustering()
    pal = igraph.drawing.colors.ClusterColoringPalette(len(clusters))
    g.vs['color'] = pal.get_many(clusters.membership)
    plot(g, **visual_style)


if __name__ == '__main__':
    friends1 = get_friends(74008457)
    vertices1, edges1 = get_network(friends1)
    plot_graph(vertices1, edges1)

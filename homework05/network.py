import igraph
import numpy as np

from api import get_friends
from igraph import Graph, plot


def get_network(users_ids, as_edgelist=True):
    """ Building a friend graph for an arbitrary list of users """
    # Исключаем людей, которые не имеют общих друзей
    user_list = []
    for uid in users_ids:
        try:
            user_friends = get_friends(uid, 'first_name')['response']['items']
        except KeyError:
            continue
        for friend in user_friends:
            if friend['id'] in users_ids:
                user_list.append(uid)
                break

    vertices = list(range(len(user_list)))
    edges = set()
    for i in range(len(user_list)):
        user_friends = get_friends(user_list[i], 'first_name')['response']['items']
        for user in user_friends:
            if user['id'] in user_list:
                j = user_list.index(user['id'])
                edges.add((i, j))
    edges = list(edges)
    if as_edgelist:
        return vertices, edges
    else:
        matrix = [[0 for _ in vertices] for _ in vertices]
        for edge in edges:
            matrix[edge[0]][edge[1]] = 1
        return matrix


def plot_graph(vertices, edges):
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
    d1 = get_friends(74008457, 'first_name')
    friends1 = [item['id'] for item in d1['response']['items']]
    vertices1, edges1 = get_network(friends1)
    plot_graph(vertices1, edges1)

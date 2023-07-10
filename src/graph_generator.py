import pickle
import networkx as nx
from datetime import datetime, timedelta

import time


DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

FRIEND_OF_FRIEND_WEIGHT: float = 3000.0
FRIEND_WEIGHT: float = 5000.0
SHARE_WEIGHT: float = 2.0
COMMENT_WEIGHT: float = 1.0
REACTION_WEIGHT: dict = {
    "angrys": 0.1,
    "sads": 0.2,
    "hahas": 0.3,
    "loves": 0.4,
    "wows": 0.5,
    "likes": 0.6,
    "special": 0.7
}


def get_affinity(user: str, friend: str, graph: nx.DiGraph) -> float:
    try:
        return graph.get_edge_data(user, friend)["affinity"]
    except:
        return 0


def add_affinity(user: str, friend: str, value: float, graph: nx.DiGraph) -> None:
    current_affinity: float = get_affinity(user, friend, graph)
    graph.add_edge(user, friend, affinity=current_affinity + value)


def get_date_difference_multiplier(action_date) -> float:
    current_date: datetime = datetime.today()
    difference: timedelta = current_date - action_date

    multiplier: float = 1.0
    if difference.days < 1:
        multiplier *= 10.0
    elif difference.days < 7:
        multiplier *= 2.5
    elif difference.days < 14:
        multiplier *= 1.0
    elif difference.days < 30:
        multiplier *= 0.6
    elif difference.days < 60:
        multiplier *= 0.01
    else:
        multiplier *= 0.001

    return multiplier


def print_graph(graph: nx.DiGraph):
    for edge in graph.edges:
        affinity: float = get_affinity(edge[0], edge[1], graph)
        print(f"{edge[0]} -> {edge[1]} : {affinity}")


def generate_graph(users: dict, statuses: dict, shares: dict, reactions: dict, comments: dict, graph: nx.DiGraph = None) -> nx.DiGraph:
    if graph is None:
        graph = nx.DiGraph()
    start = time.time()

    for comment_author in comments:
        authors_comments: list = comments[comment_author]
        for author_comment in authors_comments:
            status_id: str = author_comment['status_id']
            status_author: str = statuses[status_id]['author']
            
            add_affinity(comment_author, status_author, COMMENT_WEIGHT * get_date_difference_multiplier(author_comment['comment_published']), graph)
    
    print(f"Adding comments: {time.time() - start}")
    
    start = time.time()
    for reactor in reactions:
        reactor_reactions: list = reactions[reactor]
        for reactor_reaction in reactor_reactions:
            status_id: str = reactor_reaction['status_id']
            status_author: str = statuses[status_id]['author']
            reaction_type: str = reactor_reaction['type_of_reaction']
            
            add_affinity(reactor, status_author, REACTION_WEIGHT[reaction_type] * get_date_difference_multiplier(reactor_reaction['reacted']), graph)
    print(f"Adding reactions: {time.time() - start}")
    
    start = time.time()
    for sharer in shares:
        sharer_shares: list = shares[sharer]
        for sharer_share in sharer_shares:
            status_id: str = sharer_share['status_id']
            status_author: str = statuses[status_id]['author']
            
            add_affinity(sharer, status_author, SHARE_WEIGHT * get_date_difference_multiplier(sharer_share['status_shared']), graph)
    print(f"Adding shares: {time.time() - start}")
    
    start = time.time()
    for user in users:
        friends: list = users[user]
        for friend in friends:
            add_affinity(user, friend, FRIEND_WEIGHT, graph)
            # friends_of_friend: list = users[friend]
            # for friend_of_friend in friends_of_friend:
            #     add_affinity(user, friend_of_friend, FRIEND_OF_FRIEND_WEIGHT, graph)
    print(f"Adding friends: {time.time() - start}")
    
    graph_file_obj = open("graph.obj", "wb")
    pickle.dump(graph, graph_file_obj)
    graph_file_obj.close()
    return graph


def load_graph(file):
    try:
        graph_file_obj = open(file, "rb")
        graph = pickle.load(graph_file_obj)
        graph_file_obj.close()
        print(f"Found graph in file - {graph}")
        return graph
    except FileNotFoundError:
        print("Graph not found in file")
        
import parse_files
import pickle
import networkx as nx
from datetime import datetime, timedelta

import time

REACTION_PATH: str = "dataset/test_reactions.csv"
STATUS_PATH: str = "dataset/test_statuses.csv"
COMMENT_PATH: str = "dataset/test_comments.csv"
SHARE_PATH: str = "dataset/test_shares.csv"
FRIEND_PATH: str = "dataset/friends.csv"

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

FRIEND_WEIGHT: float = 200.0
SHARE_WEIGHT: float = 25.0
COMMENT_WEIGHT: float = 10.0
REACTION_WEIGHT: dict = {
    "angrys": 1.0,
    "sads": 1.5,
    "hahas": 2.0,
    "loves": 2.5,
    "wows": 3.0,
    "likes": 3.5,
    "special": 4.0
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
        multiplier *= 0.3
    else:
        multiplier *= 0.1

    return multiplier


def print_graph(graph: nx.DiGraph):
    for edge in graph.edges:
        affinity: float = get_affinity(edge[0], edge[1], graph)
        print(f"{edge[0]} -> {edge[1]} : {affinity}")


def generate_graph(users: dict, statuses: dict, shares: dict, reactions: dict, comments: dict) -> nx.DiGraph:
    graph: nx.DiGraph = nx.DiGraph()

    for user in users:
        for second_user in users:
            if user == second_user:
                continue

            graph.add_node(user)
            graph.add_node(second_user)

            share_affinity: float = 0.0
            reaction_affinity: float = 0.0
            comment_affinity: float = 0.0

            if shares.get(user) is None:
                share_affinity = 0.0
            else:
                for share in shares.get(user):
                    status_id = share['status_id']
                    status = statuses.get(status_id)
                    if status is not None and status['author'] == second_user:
                        share_affinity += SHARE_WEIGHT * \
                            get_date_difference_multiplier(
                                share['status_shared'])

            if reactions.get(user) is None:
                reaction_affinity = 0.0
            else:
                for reaction in reactions.get(user):
                    status_id = reaction['status_id']
                    status = statuses.get(status_id)
                    if status is not None and status['author'] == second_user:
                        reaction_affinity += REACTION_WEIGHT[reaction['type_of_reaction']] * get_date_difference_multiplier(reaction['reacted'])

            if comments.get(user) is None:
                comment_affinity = 0.0
            else:
                for comment in comments.get(user):
                    status_id = comment['status_id']
                    status = statuses.get(status_id)
                    if status is not None and status['author'] == second_user:
                        comment_affinity += COMMENT_WEIGHT * \
                            get_date_difference_multiplier(
                                comment['comment_published'])

            user_affinity: float = comment_affinity + reaction_affinity + share_affinity

            if second_user in users[user]:
                user_affinity += FRIEND_WEIGHT

            if user_affinity != 0:
                if not graph.has_edge(user, second_user):
                    graph.add_edge(user, second_user, affinity=user_affinity)
                else:
                    graph[user][second_user]['affinity'] += user_affinity

    graph_file_obj = open("graph.obj", "wb")
    pickle.dump(graph, graph_file_obj)
    graph_file_obj.close()
    return graph


def get_graph():
    try:
        graph_file_obj = open("graph.obj", "rb")
        graph = pickle.load(graph_file_obj)
        graph_file_obj.close()
        print("Found graph in file")
        return graph
    except FileNotFoundError:
        print("Graph not found in file")


def get_status_popularity(num_comments: int, num_shares: int, num_likes: int, num_loves: int, num_wows: int, num_hahas: int, num_sads: int, num_angrys: int, num_special: int) -> int:
    return num_comments * COMMENT_WEIGHT + num_shares * SHARE_WEIGHT + num_likes * REACTION_WEIGHT["likes"] + num_loves * REACTION_WEIGHT["loves"] \
        + num_wows * REACTION_WEIGHT["wows"] + num_hahas * REACTION_WEIGHT["hahas"] + \
        num_sads * REACTION_WEIGHT["sads"] + \
        num_angrys * REACTION_WEIGHT["angrys"]


def main():
    users: dict = parse_files.load_friends(FRIEND_PATH)
    statuses: dict = parse_files.load_statuses_dict(STATUS_PATH)
    shares: dict = parse_files.load_shares_dict(SHARE_PATH)
    reactions: dict = parse_files.load_reactions_dict(REACTION_PATH)
    comments: dict = parse_files.load_comments_dict(COMMENT_PATH)

    graph: nx.DiGraph = get_graph()


if __name__ == "__main__":
    main()

import networkx as nx
from graph_generator import get_date_difference_multiplier
from graph_generator import SHARE_WEIGHT, COMMENT_WEIGHT, REACTION_WEIGHT
import operator


class Status(object):
    relevance: float = 0.0
    message: str = ""

    def __init__(self, status: dict, relevance: float):
        self.relevance = relevance
        self.original_message = status['status_message']
        self.message = f"\nMessage: {status['status_message']}\nLink: {status['status_link']}\nPublished: {status['status_published']}\nAuthor: {status['author']}"

def get_feed(graph: nx.DiGraph, username: str, statuses: dict, word_count: dict = None) -> list[Status]:
    try:
        user = graph[username]
    except:
        graph.add_node(username)
        user = graph[username]

    feed: list[Status] = []

    for status_id, status in statuses.items():
        author: str = status['author']
        popularity: int = (COMMENT_WEIGHT * status['num_comments'] + status['num_shares'] * SHARE_WEIGHT + status['num_likes'] + status['num_loves'] +
                                 status['num_wows'] + status['num_hahas'] + status['num_sads'] + status['num_angrys'] + status['num_special'])
        time_dependency: float = get_date_difference_multiplier(status['status_published'])
        try:
            user_affinity: float = user[author]['affinity']
        except:
            user_affinity = 0.0
        
        
        total_relevance: float = popularity * time_dependency * user_affinity if user_affinity != 0.0 else popularity * time_dependency
        
        if word_count != None:
            total_relevance *= (1000 ** word_count[status_id])
            
        feed.append(Status(status, total_relevance))

    feed.sort(key=operator.attrgetter("relevance"), reverse=True)

    return feed[:10]

import networkx as nx
from graph_generator import get_date_difference_multiplier
import operator

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

class Status(object):
    relevance: float = 0.0
    message: str = ""

    def __init__(self, status: dict, relevance: float):
        self.relevance = relevance
        self.message = f"\nMessage: {status['status_message']}\nLink: {status['status_link']}\nPublished: {status['status_published']}\nAuthor: {status['author']}"


def get_status_popularity(num_comments: int, num_shares: int, num_likes: int, num_loves: int, num_wows: int, num_hahas: int, num_sads: int, num_angrys: int, num_special: int) -> int:
    return num_comments * COMMENT_WEIGHT + num_shares * SHARE_WEIGHT + num_likes * REACTION_WEIGHT["likes"] + num_loves * REACTION_WEIGHT["loves"] \
        + num_wows * REACTION_WEIGHT["wows"] + num_hahas * REACTION_WEIGHT["hahas"] + \
        num_sads * REACTION_WEIGHT["sads"] + \
        num_angrys * REACTION_WEIGHT["angrys"]


def get_feed(graph: nx.DiGraph, username: str, statuses: dict) -> list[Status]:
    try:
        user = graph[username]
    except:
        graph.add_node(username)
        user = graph[username]
    
    feed: list[Status] = []
    
    for _, status in statuses.items():
        author: str = status['author']
        
        popularity: int  = get_status_popularity(status['num_comments'], status['num_shares'], status['num_likes'], status['num_loves'], status['num_wows'], status['num_hahas'], status['num_sads'], status['num_angrys'], status['num_special'])
        time_dependency: float = get_date_difference_multiplier(status['status_published'])
        try:
            user_affinity: float = user[author]['affinity']
        except:
            user_affinity = 0.0
        
        total_relevance: float = popularity * time_dependency * user_affinity #if user_affinity != 0.0 else popularity * time_dependency 
        # print(f"Popularity: {popularity} Time dependency: {time_dependency} Affinity: {user_affinity} Total: {total_relevance}")
        feed.append(Status(status, total_relevance))
    
    feed.sort(key=operator.attrgetter("relevance"), reverse=True)
    
    return feed[:10]
        
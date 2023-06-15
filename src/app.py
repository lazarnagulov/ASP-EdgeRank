import parse_files
import networkx as nx
import time

REACTION_PATH: str = "dataset/test_reactions.csv"
STATUS_PATH: str = "dataset/test_statuses.csv"
COMMENT_PATH: str = "dataset/test_comments.csv"
SHARE_PATH: str = "dataset/test_shares.csv"
FRIEND_PATH: str = "dataset/friends.csv"

FRIEND_WEIGHT: float = 100.0
SHARE_WEIGHT: float = 25.0
COMMENT_WEIGHT: float = 10.0
REACTION_WEIGHT: float = 2.0

def get_affinity(user: str, friend: str, graph: nx.DiGraph) -> float:
    try:
        return graph.get_edge_data(user, friend)["affinity"]
    except:
        return 0

def add_affinity(user: str, friend: str, value: float, graph: nx.DiGraph) -> None:
    current_affinity: float = get_affinity(user, friend, graph)
    graph.add_edge(user, friend, affinity = current_affinity + value)

def get_status(id, statuses):
    for status in statuses:
        if status[0] == id:
            return status

def print_graph(graph: nx.DiGraph):
    for edge in graph.edges:
        affinity: float = get_affinity(edge[0], edge[1], graph)
        print(f"{edge[0]} -> {edge[1]} : {affinity}")
    
def generate_graph(users: dict, statuses: list, shares: list, reactions: list, comments: list) -> nx.DiGraph:
    graph: nx.DiGraph = nx.DiGraph()
    
    for user in users:
        if not graph.has_node(user):
            graph.add_node(user)
        for friend in users[user]:
            if not graph.has_node(friend):
                graph.add_node(friend)
            
            graph.add_edge(friend, user, affinity=FRIEND_WEIGHT)
            graph.add_edge(user, friend, affinity=FRIEND_WEIGHT)

    for user in users:
        for share in shares:
            status_id: str = share[0]
            sharer: str = share[1]
            if sharer != user:
                continue
            status = get_status(status_id, statuses)
            if status is None:
                continue

            shared: str = status[5]
            add_affinity(user, shared, SHARE_WEIGHT, graph)
        
        for reaction in reactions:
            status_id: str = reaction[0]
            reactor: str = reaction[2]
            if reactor != user:
                continue
            status = get_status(status_id, statuses)
            if status is None:
                continue
            
            reacted: str = status[5]
            
            add_affinity(user, reacted, REACTION_WEIGHT, graph)

        for comment in comments:
            status_id: str = comment[1]
            author: str = comment[4]
            if author != user:
                continue
            status = get_status(status_id, statuses)
            if status is None:
                continue
            
            commented: str = status[5]
            
            add_affinity(user, commented, COMMENT_WEIGHT, graph)

    return graph
    
def load_graph():
    pass


def main():
    users: dict = parse_files.load_friends(FRIEND_PATH)
    statuses: list = parse_files.load_statuses(STATUS_PATH)
    shares: list = parse_files.load_shares(SHARE_PATH)
    reactions: list = parse_files.load_reactions(REACTION_PATH)
    comments: list = parse_files.load_comments(COMMENT_PATH)

    start_time = time.time()
    graph: nx.DiGraph = generate_graph(users, statuses, shares, reactions, comments)
    print(f"Generating graph: {time.time() - start_time}")

    print_graph(graph)
    
if __name__ == "__main__":
    main()
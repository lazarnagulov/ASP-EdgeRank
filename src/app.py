import parse_dict
import networkx as nx
import graph_generator
import feed


REACTION_PATH: str = "dataset/test_reactions.csv"
STATUS_PATH: str = "dataset/test_statuses.csv"
COMMENT_PATH: str = "dataset/test_comments.csv"
SHARE_PATH: str = "dataset/test_shares.csv"
FRIEND_PATH: str = "dataset/friends.csv"

def main():
    # users: dict = parse_dict.load_friends_dict(FRIEND_PATH)
    statuses: dict = parse_dict.load_statuses_dict(STATUS_PATH)
    # shares: dict = parse_dict.load_shares_dict(SHARE_PATH)
    # reactions: dict = parse_dict.load_reactions_dict(REACTION_PATH)
    # comments: dict = parse_dict.load_comments_dict(COMMENT_PATH)
       
    graph: nx.DiGraph = graph_generator.get_graph()

    print("Username: ")
    username = input(">> ")
    
    print(f"Welcome {username}!")
    statuses: list = feed.get_feed(graph, username, statuses)
    for status in statuses:
        print(status.message, "\nRelevance:", status.relevance)
    
if __name__ == "__main__":
    main()

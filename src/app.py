import parse_dict
import re
import sys
import time
import networkx as nx
from trie import Trie
import graph_generator
import feed


REACTION_PATH_TEST: str = "dataset/test_reactions.csv"
STATUS_PATH_TEST: str = "dataset/test_statuses.csv"
COMMENTS_PATH_TEST: str = "dataset/test_comments.csv"
SHARES_PATH_TEST: str = "dataset/test_shares.csv"

FRIEND_PATH: str = "dataset/friends.csv"

REACTION_PATH_ORIGINAL: str = "dataset/original_reactions.csv"
STATUS_PATH_ORIGINAL: str = "dataset/original_statuses.csv"
COMMENTS_PATH_ORIGINAL: str = "dataset/original_comments.csv"
SHARES_PATH_ORIGINAL: str = "dataset/original_shares.csv"


def main():
    start = time.time()
    print(f"Loading data...")
    users: dict = parse_dict.load_friends_dict(FRIEND_PATH)
    statuses: dict = parse_dict.load_statuses_dict(STATUS_PATH_ORIGINAL)
    shares: dict = parse_dict.load_shares_dict(SHARES_PATH_ORIGINAL)
    reactions: dict = parse_dict.load_reactions_dict(REACTION_PATH_ORIGINAL)
    comments: dict = parse_dict.load_comments_dict(COMMENTS_PATH_ORIGINAL)
    print(f"Loading data: {time.time() - start}")
    
    start = time.time()
    print("Generating graph...")    
    graph: nx.DiGraph = graph_generator.load_graph("graph.obj")
    if graph is None:
        graph = graph_generator.generate_graph(users, statuses, shares, reactions, comments)

    print(f"Generating graph: {time.time() - start}")

    trie: Trie = Trie()
    for status in statuses:
        trie.insert(statuses[status]['status_message'], statuses[status]['status_id'])

    while True:
        print("------------")
        print("Commands:")
        print("start - Start program with original data")
        print("load_test_data - Load test data")
        print("------------")
        operation: str = input(">> ")
        if operation == "start":
            break
        elif operation == "load_test_data":
            start = time.time()
            print(f"Loading test data...")
            test_statuses: dict = parse_dict.load_statuses_dict(STATUS_PATH_TEST)
            test_shares: dict = parse_dict.load_shares_dict(SHARES_PATH_TEST)
            test_reactions: dict = parse_dict.load_reactions_dict(REACTION_PATH_TEST)
            test_comments: dict = parse_dict.load_comments_dict(COMMENTS_PATH_TEST)
            print(f"Loading test data: {time.time() - start}")
            graph_generator.generate_graph(users, test_statuses, test_shares, test_reactions, test_comments, graph)
            for status in test_statuses:
                trie.insert(test_statuses[status]['status_message'], test_statuses[status]['status_id'])
            break
             
    print("Username: ")
    username = input(">> ")

    print(f"Welcome {username}!")
    feed_statuses: list = feed.get_feed(graph, username, statuses)
    for status in feed_statuses:
        print(status.message)

    while True:
        print("------------")
        print("Commands:")
        print("search")
        print("exit")
        print("-----------")
        operation: str = input(">> ")
        if operation == "search":
            term: str = input(">> Search: ")
            
            if term[0] != '"' and term[-1] != "*" and term[-1] != '"':
                search_ids: dict = trie.search_words_union(term)
                relevant_statuses: dict = {}
                for status_id in search_ids:
                    relevant_statuses[status_id] = statuses[status_id]  
                    
                search_statuses: list = feed.get_feed(graph, username, relevant_statuses, search_ids)

                for status in search_statuses:
                    message: str = status.message
                    term_words = term.split(" ")
                    for term_word in term_words:
                        for word in re.findall(r'\b\w+\b', message):
                            if word.lower() == term_word.lower():
                                message = message.replace(word, f"\033[101m{word}\033[0m")

                    print(message)
            elif term[-1] == "*":
                words: list = trie.autocomplete(term[:-1])
                print("------------")
                print("Popular search options:")
                for word in words[:10]:
                    print(word[0], end=", ")
                print()
                print("------------")
            elif term[0] == '"' and term[-1] == '"':
                term = term[1:-1] + " "
                search_ids: list = trie.search_phrases(term, statuses)
                relevant_statuses: dict = {}
                for status_id in search_ids:
                    relevant_statuses[status_id] = statuses[status_id]
                
                search_statuses: list = feed.get_feed(graph, username, relevant_statuses)

                for status in search_statuses:
                    message: str = status.message
                    message_copy: str = "" + message
                    highlighted_message: str = ""
                    while True:
                        has, index = trie.has_phrase(message_copy.lower(), term.lower())
                        if not has:
                            highlighted_message += message_copy
                            break
                        highlighted_message += message_copy[:index] + " " + f"\033[101m{term}\033[0m"
                        message_copy = message_copy[index + len(term):]

                    print(highlighted_message)
                    print()
            else:
                print("Invalid input!")
        elif operation == "exit":
            print("Exiting...")
            sys.exit(0)
        else:
            print("Invalid command!")
            
                                    
if __name__ == "__main__":
    sys.setrecursionlimit(30000)
    main()

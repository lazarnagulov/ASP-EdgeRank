import parse_files

REACTION_PATH: str = "dataset/test_reactions.csv"
STATUS_PATH: str = "dataset/test_statuses.csv"
COMMENT_PATH: str = "dataset/test_comments.csv"
SHARE_PATH: str = "dataset/test_shares.csv"

def main():
    reactions: list = parse_files.load_reactions()


if __name__ == "__main__":
    main()
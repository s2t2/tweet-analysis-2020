

import os

from app.graph_analyzer import GraphAnalyzer
from app.workers.investigate_botcode import classify_bot_probabilities


if __name__ == "__main__":

    manager = GraphAnalyzer()
    retweet_graph = manager.load_graph()
    manager.report()

    print("--------------------")
    print("COMPUTING BOT PROBABILITIES...")
    bot_probabilities = classify_bot_probabilities(retweet_graph)

    print("--------------------")
    print(f"CLASSIFIED {len(bot_probabilities.keys())} USERS")
    breakpoint()

    print("--------------------")
    print("WRITING TO CSV...")
    df = DataFrame(bot_probabilities)
    csv_filepath = os.path.join(manager.local_dirpath, "botcode_probabilities.csv")
    df.to_csv(results_filepath)

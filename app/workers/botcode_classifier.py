

import os

from pandas import DataFrame

from app.graph_analyzer import GraphAnalyzer
from app.workers import fmt_n, fmt_pct
from app.workers.investigate_botcode import classify_bot_probabilities


if __name__ == "__main__":

    manager = GraphAnalyzer()
    retweet_graph = manager.load_graph()
    manager.report()

    print("--------------------")
    print("COMPUTING BOT PROBABILITIES...")
    bot_probabilities = classify_bot_probabilities(retweet_graph)

    print("--------------------")
    df = DataFrame(bot_probabilities.items(), columns=["screen_name", "bot_probability"])
    #df.set_index("screen_name", inplace=True)
    users_count = len(df)
    bot_count = len(df[df.bot_probability == 1])
    print("TOTAL USERS:", fmt_n(users_count))
    print(f"BOTS: {fmt_n(bot_count)} ({fmt_pct(bot_count / users_count)})")

    print("--------------------")
    print("WRITING TO CSV...")
    predictions_dirpath = os.path.join(manager.local_dirpath, "preds")
    if not os.path.isdir(predictions_dirpath):
        os.mkdir(predictions_dirpath)

    csv_filepath = os.path.join(predictions_dirpath, "botcode_probabilities.csv")
    df.to_csv(csv_filepath)

    # TODO: really we can generate multiple classifications, using different hyperparams
    # ... make separate "predictions" subdirectory,
    # ... and include a corresponding hyperparams json file for each CSV file

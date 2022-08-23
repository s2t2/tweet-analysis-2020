
import os
from functools import cached_property

from botometer import Botometer
from dotenv import load_dotenv

from app import seek_confirmation, server_sleep
from app.bq_service import BigQueryService, generate_timestamp
from app.twitter_service import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET

load_dotenv()

RAPID_API_KEY = os.getenv("RAPID_API_KEY")
LIMIT = os.getenv("LIMIT", default="5") # keep less than 1_000 per day


class BotometerScoreSampler:
    """Gets botometer scores for a random sample of users.

    Random sample is drawn evenly from both classes, if possble. The sample size will be twice the limit.

    Cross references previously-looked-up scores to prevent duplicate lookups.

    May return less than the desired sample if there are user's not able to be looked up.
    """

    def __init__(self, bq=None, limit=LIMIT):
        self.bq = bq or BigQueryService()
        self.dataset_address = self.bq.dataset_address.replace(";", "") # super safe about sql injection
        self.limit = int(limit)

        self.bom = Botometer(wait_on_ratelimit=True, rapidapi_key=RAPID_API_KEY,
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET,
            access_token=ACCESS_KEY,
            access_token_secret=ACCESS_SECRET
        )

        print("-------------")
        print("BOTOMETER SCORE SAMPLER...")
        print("  BQ:", self.dataset_address.upper())
        print("  LIMIT:", self.limit)
        print("  BOTOMETER:", type(self.bom), self.bom.api_url, f"v{self.bom.api_version}")

        seek_confirmation()

    @property
    def bots_sql(self):
        return f"""
            SELECT DISTINCT user_id
            FROM `{self.dataset_address}.user_details_v20210806_slim`
            WHERE is_bot=True -- BOTS
            ORDER BY rand() -- RANDOM SAMPLE
            LIMIT {self.limit}
        """

    @property
    def humans_sql(self):
        return f"""
            SELECT DISTINCT user_id
            FROM `{self.dataset_address}.user_details_v20210806_slim`
            WHERE is_bot=FALSE -- HUMANS
            ORDER BY rand() -- RANDOM SAMPLE
            LIMIT {self.limit}
        """

    @cached_property
    def bots_df(self):
        return self.bq.query_to_df(self.bots_sql)

    @cached_property
    def humans_df(self):
        return self.bq.query_to_df(self.humans_sql)

    @cached_property
    def bot_ids(self):
        return self.bots_df["user_id"].tolist()

    @cached_property
    def human_ids(self):
        return self.humans_df["user_id"].tolist()

    def parse_scores(self, user_id, result) -> list:
        """convert raw botometer response structure to one or more normalized database records"""
        # print(user_id)
        # print(result)

        lookup_at = generate_timestamp()

        records = []

        if "error" in result:
            #> {'error': 'TweepError: Not authorized.'}
            #> {'error': "TweepError: [{'code': 32, 'message': 'Could not authenticate you.'}]"}
            error_message = result["error"] #> str
            print("  ...", error_message)
            records.append({
                "user_id": user_id,
                "lookup_at": lookup_at,
                "error_message": error_message,
                "score_type": None,
                "cap": None,
                "astroturf": None,
                "fake_follower": None,
                "financial": None,
                "other": None,
                "overall": None,
                "self_declared": None,
                "spammer": None,
            })
        else:

            try:

                #> {
                #>    'cap': {'english': 0.8021481695167405, 'universal': 0.8148417533461276}
                #>    'raw_scores': {
                #>        'english': {'astroturf': 0.02,
                #>                            'fake_follower': 0.75,
                #>                            'financial': 0.03,
                #>                            'other': 0.49,
                #>                            'overall': 0.75,
                #>                            'self_declared': 0.2,
                #>                            'spammer': 0.29},
                #>        'universal': {'astroturf': 0.02,
                #>                              'fake_follower': 0.78,
                #>                              'financial': 0.05,
                #>                              'other': 0.45,
                #>                              'overall': 0.78,
                #>                              'self_declared': 0.18,
                #>                              'spammer': 0.25}}
                #>}

                cap_types = sorted(list(result["cap"].keys()))
                score_types = sorted(list(result["raw_scores"].keys()))
                if cap_types != score_types:
                    raise AttributeError("OOPS unexpected response structure")
                #> ["english", "universal"]

                for score_type in score_types:
                    raw_scores = result["raw_scores"][score_type]
                    cap_score = result["cap"][score_type]
                    records.append({
                        "user_id": user_id,
                        "lookup_at": lookup_at,
                        "error_message": None,
                        "score_type": score_type,
                        "cap": cap_score,
                        "astroturf": raw_scores.get("astroturf"),
                        "fake_follower": raw_scores.get("fake_follower"),
                        "financial": raw_scores.get("financial"),
                        "other": raw_scores.get("other"),
                        "overall": raw_scores.get("overall"),
                        "self_declared": raw_scores.get("self_declared"),
                        "spammer": raw_scores.get("spammer"),
                    })
            except Exception as err:
                print("OOPS", err)

        return records


    @cached_property
    def scores_table(self):
        return self.bq.client.get_table(f"{self.dataset_address}.botometer_scores") # an API call (caches results for subsequent inserts)

    def save_scores(self, scores):
        """upload a batch of scores to bigquery"""
        self.bq.insert_records_in_batches(self.scores_table, scores)

    def perform(self):
        print("-------------------")
        print("FETCHING SAMPLE...")
        print("  BOT IDS:", len(self.bot_ids))
        print("  HUMAN IDS:", len(self.human_ids)) # self.human_ids[0], self.human_ids[-1]
        user_ids = self.bot_ids + self.human_ids
        print("  USERS TOTAL:", len(user_ids))

        print("-------------------")
        print("PERFORMING BOTOMETER LOOKUPS...")
        records = []
        for user_id, result in self.bom.check_accounts_in(user_ids):
            print("  USER ID:", user_id)
            user_scores = self.parse_scores(user_id, result)
            records += user_scores

        print("-------------------")
        if any(records):
            print(f"SAVING SCORES ({len(records)}) ...")
            self.save_scores(records)



if __name__ == "__main__":

    job = BotometerScoreSampler()

    job.perform()

    server_sleep(seconds=24*60*60)

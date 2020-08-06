

from app.bq_service import BigQueryService
from app.twitter_service import TwitterService


if __name__ == "__main__":

    bq_service = BigQueryService()
    twitter_service = TwitterService()

    batch = []
    for row in bq_service.fetch_idless_screen_names():
        user_id = twitter_service.get_user_id(row.screen_name)
        lookup = {"screen_name": row.screen_name.upper(), "user_id": user_id}
        print(lookup)
        batch.append(lookup)

    breakpoint()

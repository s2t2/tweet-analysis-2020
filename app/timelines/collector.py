

from app.twitter_service import TwitterService

if __name__ == '__main__':

    twitter_service = TwitterService()

    api = twitter_service.api

    # Get the timeline of the user
    timeline = api.user_timeline(count=200)

    for timeline in timeline:
        print(timeline.text)

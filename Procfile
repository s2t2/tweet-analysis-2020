tweet_collector: python -m app.tweet_collection_v2.stream_listener
friend_collector: python -m app.friend_collection.batch_per_thread
pg_migrate: python -m app.pg_pipeline.models
pg_pipeline_user_friends: python -m app.pg_pipeline.user_friends
pg_pipeline_user_details: python -m app.pg_pipeline.user_details
pg_pipeline_retweeter_details: python -m app.pg_pipeline.retweeter_details

retweet_grapher: python -m app.retweet_graphs_v2.retweet_grapher
k_days_grapher: python -m app.retweet_graphs_v2.k_days.grapher
k_days_classifier: python -m app.retweet_graphs_v2.k_days.classifier

# need to turn this off on all non-API servers:
web: gunicorn "api:create_app()"

toxicity_scorer: python -m app.toxicity.scorer

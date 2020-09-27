import json

def test_user_details(api_client):
    expected_keys = ['screen_name_count', 'screen_names', 'tweet_count', 'user_created_at', 'user_descriptions', 'user_id', 'user_names']

    response = api_client.get('/api/v0/user_details/politico')
    parsed_response = json.loads(response.data)
    assert response.status_code == 200
    assert isinstance(parsed_response, dict)
    assert sorted(list(parsed_response.keys())) == expected_keys

def test_user_tweets(api_client):
    expected_keys = ['created_at', 'opinion_score', 'status_id', 'status_text']

    response = api_client.get('/api/v0/user_tweets/berniesanders')
    parsed_response = json.loads(response.data)
    assert response.status_code == 200
    assert isinstance(parsed_response, list)
    assert any(parsed_response)
    assert isinstance(parsed_response[0], dict)
    assert sorted(list(parsed_response[0].keys())) == expected_keys

def test_users_most_retweeted(api_client):
    expected_keys = ['community_id', 'retweet_count', 'retweeted_user_screen_name', 'retweeter_count']

    response = api_client.get('/api/v0/users_most_retweeted')
    users = json.loads(response.data)
    assert response.status_code == 200
    assert isinstance(users, list)
    assert len(users) == 50
    assert isinstance(users[0], dict)
    assert sorted(list(users[0].keys())) == expected_keys
    assert len([u for u in users if u["community_id"] == 0]) == len([u for u in users if u["community_id"] == 1])

    response = api_client.get('/api/v0/users_most_retweeted?limit=3')
    users = json.loads(response.data)
    assert len(users) == 6
    assert sorted(list(users[0].keys())) == expected_keys
    assert len([u for u in users if u["community_id"] == 0]) == len([u for u in users if u["community_id"] == 1])

def test_statuses_most_retweeted(api_client):
    expected_keys = ['community_id', 'retweet_count', 'retweeted_user_screen_name', 'retweeter_count', 'status_text']

    response = api_client.get('/api/v0/statuses_most_retweeted')
    statuses = json.loads(response.data)
    assert response.status_code == 200
    assert isinstance(statuses, list)
    assert len(statuses) == 50
    assert isinstance(statuses[0], dict)
    assert sorted(list(statuses[0].keys())) == expected_keys
    assert len([s for s in statuses if s["community_id"] == 0]) == len([s for s in statuses if s["community_id"] == 1])

    response = api_client.get('/api/v0/statuses_most_retweeted?limit=3')
    statuses = json.loads(response.data)
    assert len(statuses) == 6
    assert sorted(list(statuses[0].keys())) == expected_keys
    assert len([s for s in statuses if s["community_id"] == 0]) == len([s for s in statuses if s["community_id"] == 1])

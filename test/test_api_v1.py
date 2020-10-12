import json

import pytest

from conftest import CI_ENV

@pytest.mark.skipif(CI_ENV, reason="avoid issuing HTTP requests on CI")
def test_users_most_retweeted(api_client):
    expected_keys = ['avg_score_lr', 'avg_score_nb', 'category', 'follower_count', 'screen_name', 'status_count']

    response = api_client.get('/api/v1/users_most_followed')
    users = json.loads(response.data)
    assert response.status_code == 200
    assert isinstance(users, list)
    assert len(users) == 500
    assert isinstance(users[0], dict)
    assert sorted(list(users[0].keys())) == expected_keys

    response = api_client.get('/api/v1/users_most_followed?limit=3')
    users = json.loads(response.data)
    assert len(users) == 3
    assert sorted(list(users[0].keys())) == expected_keys

    # you also need to know these need to be sorted, so the limit really returns the "top" users.
    # they happen to be sorted that way in the table, but need to explicitly sort. thanks.

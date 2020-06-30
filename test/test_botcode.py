


from app.botcode import compute_joint_energy, ALPHA, LAMBDA_1, LAMBDA_2, EPSILON

def test_hyperparams():
    # should match the default values described in the botcode README file
    assert ALPHA == [1.0, 100.0, 100.0]
    assert LAMBDA_1 == 0.8
    assert LAMBDA_2 == 0.6
    assert EPSILON == 0.001

# users receiving retweets
in_degrees = {
    'user1': 0,
    'leader1': 10.0,
    'user2': 0,
    'user3': 0,
    'leader2': 6.0,
    'user4': 0,
    'user5': 0,
    'leader3': 4.0,
    'colead1': 12.0,
    'colead2': 3.0,
    'colead3': 10.0,
    'colead4': 5.0
}

# users doing the retweeting
out_degrees = {
    'user1': 8.0,
    'leader1': 0,
    'user2': 12.0,
    'user3': 8.0,
    'leader2': 0,
    'user4': 4.0,
    'user5': 8.0,
    'leader3': 0,
    'colead1': 3.0,
    'colead2': 2.0,
    'colead3': 1.0,
    'colead4': 4.0
}

def test_bidirectional_energy():

    link = ['colead1', 'colead2', True, True, 3.0, 2.0]
    user1 = link[0] #> 'colead1'
    user2 = link[1] #> 'colead2'
    rt_count = link[4] #> 3.0

    energy = compute_joint_energy(user1, user2, rt_count, in_degrees, out_degrees, alambda1=100, alambda2=100)
    assert sum(energy) == 0

    energy = compute_joint_energy(user1, user2, rt_count, in_degrees, out_degrees, alambda1=10, alambda2=10)
    assert sum(energy) > 0 # right now this is failing.

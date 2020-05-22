

def test_set_uniqueness():
    nodes = set()
    nodes.add(1)
    nodes.update([1,2,3])
    assert nodes == {1, 2, 3}


from pandas import DataFrame
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB

class MockClass:
    pass

def camel_to_snake(my_str):
    return "".join([f"_{char.lower()}" if char.isupper() else char for char in str(my_str)]).lstrip("_")

def test_case_conversion():
    assert camel_to_snake(MockClass.__name__) == "mock_class"
    assert camel_to_snake(DataFrame.__name__) == "data_frame"
    assert camel_to_snake(LogisticRegression.__name__) == "logistic_regression"
    #assert camel_to_snake(MultinomialNB.__name__) == "multinomial_nb"

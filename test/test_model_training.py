
class DataFrame:
    pass

class LogisticRegression:
    pass

class MultinomialNB:
    pass

def camel_to_snake(my_str):
    return "".join([f"_{char.lower()}" if char.isupper() else char for char in str(my_str)]).lstrip("_")

def test_case_conversion():
    assert camel_to_snake(DataFrame.__name__) == "data_frame"
    assert camel_to_snake(LogisticRegression.__name__) == "logistic_regression"
    #assert camel_to_snake(MultinomialNB.__name__) == "multinomial_nb"

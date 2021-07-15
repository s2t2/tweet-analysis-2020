
from time import perf_counter # see: https://stackoverflow.com/questions/25785243/understanding-time-perf-counter-and-time-process-time
from functools import wraps

from detoxify import Detoxify

def performance_timer(func):
    """
    Wrap your function in this decorator to see how long it takes.
    Returns the duration in seconds.
    The original function's return values are lost - just have it do the work.
    """
    @wraps(func)
    def wrapper(*args, **kwds):
        start_at = perf_counter()
        func(*args, **kwds)
        end_at = perf_counter()
        duration_seconds = round(end_at - start_at, 2)
        return duration_seconds
    return wrapper


LIMITS = [
    1, 10, 100,
    500, 750,
    1_000,
    1_250, 1_500,
    #2_500, 5_000, 7_500,
    #10_000 #, 100_000, #1_000_000
]

@performance_timer
def scoring_duration(model, texts):
    model.predict(texts)


if __name__ == '__main__':

    print("---------------------")
    model_name = "original"
    model = Detoxify(model_name)
    print("MODEL:", model_name.upper())
    print(model.class_names)

    for limit in LIMITS:
        print("---------------------")

        texts = ["some example text - what a jerk" for _ in range(0, limit)]

        duration_seconds = scoring_duration(model, texts)

        items_per_second = round(limit / duration_seconds, 2)
        print(f"PROCESSED {limit} ITEMS IN {duration_seconds} SECONDS ({items_per_second} items / second)")

    print("---------------------")

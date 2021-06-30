# https://stackoverflow.com/questions/25785243/understanding-time-perf-counter-and-time-process-time
from time import perf_counter, process_time
from functools import wraps

from detoxify import Detoxify

def performance_timer(func):
    """A Decorator Function"""
    @wraps(func)
    def wrapper(*args, **kwds):
        start_at = perf_counter()
        func(*args, **kwds)
        end_at = perf_counter()
        duration_seconds = round(end_at - start_at, 2)
        return duration_seconds
    return wrapper


@performance_timer
def scoring_duration(model, texts):
    model.predict(texts)



if __name__ == '__main__':

    print("---------------------")
    model = Detoxify("original")
    print("MODEL:", model.class_names)


    LIMITS = [1, 10, 100, 1_000, 10_000 #, 100_000, #1_000_000
    ]
    for limit in LIMITS:
        print("---------------------")

        texts = ["some example text - what a jerk" for _ in range(0, limit)]

        duration_seconds = scoring_duration(model, texts)

        items_per_second = round(limit / duration_seconds, 2)
        print(f"PROCESSED {limit} ITEMS IN {duration_seconds} SECONDS ({items_per_second} items / second)")

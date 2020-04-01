
# h/t: https://stackoverflow.com/questions/38632621/can-i-run-multiple-threads-in-a-single-heroku-python-dyno

from threading import Thread, BoundedSemaphore, current_thread
import time
import random

def foo(counter, sleep_seconds):
    time.sleep(sleep_seconds)
    print(current_thread(), counter, sleep_seconds)

if __name__ == "__main__":

    for counter in range(20):
        sleep_seconds = random.random()
        #foo(counter, sleep_seconds)
        Thread(target=foo, args=(counter, sleep_seconds)).start()
        #Thread(target=foo, args=(counter, sleep_seconds), daemon=True).start()

    # define max number of threads
    max_connections = 5
    pool = BoundedSemaphore(value=max_connections)
    with pool:
        for counter in range(20):
            sleep_seconds = random.random()
            #foo(counter, sleep_seconds)
            Thread(target=foo, args=(counter, sleep_seconds)).start()

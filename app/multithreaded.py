
# h/t: https://stackoverflow.com/questions/38632621/can-i-run-multiple-threads-in-a-single-heroku-python-dyno

import threading
import time
import random

def foo(counter, sleep_seconds):
    time.sleep(sleep_seconds)
    print(threading.current_thread(), counter, sleep_seconds)

if __name__ == "__main__":

    for counter in range(4):
        sleep_seconds = random.random()
        #foo(counter, sleep_seconds)
        threading.Thread(target=foo, args=(counter, sleep_seconds)).start()

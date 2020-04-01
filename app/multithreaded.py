
# h/t: https://stackoverflow.com/questions/38632621/can-i-run-multiple-threads-in-a-single-heroku-python-dyno

import threading
import time
import random

def foo(x, s):
    time.sleep(s)
    print ("%s %s %s" % (threading.current_thread(), x, s))

for x in range(4):
    threading.Thread(target=foo, args=(x, random.random())).start()

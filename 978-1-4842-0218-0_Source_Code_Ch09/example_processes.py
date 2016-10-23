#!/usr/bin/env python
import multiprocessing
import time

def sleeper(timeout):
    try:
        print "function: I am a sleeper function and going to sleep for %s seconds" % timeout
        time.sleep(timeout)
        print "function: I'm done!"
    except KeyboardInterrupt:
        print "function: I have received a signal to stop, exiting..."

class SleeperClass(multiprocessing.Process):
    def __init__(self, timeout):
        self.timeout = timeout
        print "Class: I am a class and can do initialisation tasks before starting"
        super(SleeperClass, self).__init__()

    def run(self):
        try:
            print "Class: I have been told to run now"
            print "Class: So I'm going to sleep for %s seconds" % self.timeout
            time.sleep(self.timeout)
            print "Class: I'm done."
        except KeyboardInterrupt:
            print "Class: I must stop now, exiting..."

p1 = multiprocessing.Process(target=sleeper, args=(50,))
p2 = SleeperClass(100)
p1.start()
p2.start()
try:
    while len(multiprocessing.active_children()) != 0:
        time.sleep(1)
except KeyboardInterrupt:
    p1.terminate()
    p2.terminate()
p1.join()
p2.join()


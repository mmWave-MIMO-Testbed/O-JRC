import queue as Q
import threading
import FuncThread as FT
from threading import Lock

class ThreadHandler():
    def __init__(self, *args, **kwargs):
        self.queue = Q.Queue()
        self._run = True
        self.lock = Lock()

    def startNext(self):
        func = self.queue.get()
        try:
            func()
        except:
            print('ERROR: ', func)
        self.queue.task_done()

    def start(self):
        event = threading.Event()
        while self._run:
            if not self.queue.empty():
                self.startNext()
            else:
                event.wait(0.0001)

    def stop(self):
        while not self.queue.empty():
            self.startNext()
        self.queue.join()
        self._run = False

    def put(self, func):
        self.lock.acquire()
        self.queue.put(func)
        self.lock.release()

    def clear(self):
        self.lock.acquire()
        while not self.queue.empty():
            func = self.queue.get()
            self.queue.task_done()
        print('Queue emptied')
        self.lock.release()

if __name__ == "__main__":
    TH = ThreadHandler()
    print (TH)




 

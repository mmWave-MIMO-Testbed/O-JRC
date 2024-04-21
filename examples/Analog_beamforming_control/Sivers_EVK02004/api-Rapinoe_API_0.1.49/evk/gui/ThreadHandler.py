try:
    import queue as Q
except:
    import Queue as Q

import threading
import evk.gui.FuncThread as FT
from threading import Lock
from ctypes import pythonapi

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
                #gil_state = pythonapi.PyGILState_Ensure()
                event.wait(0.0001)
                #pythonapi.PyGILState_Release(gil_state)

    def stop(self):
        self._run = False
        while not self.queue.empty():
            self.startNext()
        self.queue.join()
        

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




 

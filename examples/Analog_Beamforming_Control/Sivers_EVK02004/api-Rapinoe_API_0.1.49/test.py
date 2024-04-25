import threading
import time

def count_odd():
    count = 0
    while(count < 100):
        count += 1
        print(count * 2 + 1)
        
def count_even():
    count = 0
    while(count < 100):
        count += 1
        print(count * 2)
        
if __name__ =="__main__":
    t1 = threading.Thread(target=count_odd, args=())
    t2 = threading.Thread(target=count_even, args=())
 
    t1.start()
    t2.start()
 
    t1.join()
    t2.join()
 
    print("Done!")
from multiprocessing import Process
import time

def add_one(a):
    result = a + 1
    print(f"Process 1: {a} + 1 = {result}")
    time.sleep(1)  # 模拟长时间运行

def add_two(a):
    result = a + 2
    print(f"Process 1: {a} + 1 = {result}")
    time.sleep(3)  # 模拟长时间运行

if __name__ == '__main__':
    process_one = Process(target=add_one, args=(5,))
    process_two = Process(target=add_two, args=(5,))

    process_one.start()
    process_two.start()

    process_one.join()  # Optionally wait for the process to finish
    process_two.join()  # Optionally wait for the process to finish
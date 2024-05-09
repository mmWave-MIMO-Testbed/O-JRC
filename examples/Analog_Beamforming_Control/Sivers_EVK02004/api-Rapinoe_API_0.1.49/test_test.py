# import beamSweep

# beamSweep.main("T582306548", "rapvalbsp", None, None, None, None, None, None, "beamSweep_tx_setup")
# beamSweep.beam(6)

import multiprocessing
import time

class PersistentProcess(multiprocessing.Process):
    def __init__(self, process_id):
        super().__init__()
        self.process_id = process_id
        self.current_value = 0
        self.event = multiprocessing.Event()
        self.new_input = multiprocessing.Queue()
        self.terminate = multiprocessing.Event()  # Additional event to handle termination

    def update_value(self, new_value):
        self.new_input.put(new_value)
        self.event.set()  # Set event to notify process there is new data

    def run(self):
        while not self.terminate.is_set():  # Check if termination is requested
            self.event.wait()  # Wait for the event to be set
            while not self.new_input.empty():
                input_value = self.new_input.get()
                self.current_value += input_value + 2
                print(f"Process {self.process_id}: Updated value: {self.current_value}", flush=True)
            self.event.clear()  # Clear event after processing
            
            if self.terminate.is_set():  # Check again after clearing inputs
                break

    def stop(self):
        self.terminate.set()  # Signal the process to terminate
        self.event.set()  # Ensure the process wakes up if it is waiting
        self.join()

if __name__ == '__main__':
    # Start multiple processes
    pp1 = PersistentProcess(process_id=1)
    pp2 = PersistentProcess(process_id=2)

    pp1.start()
    pp2.start()

    print("Main thread is doing something else...")
    time.sleep(1)
    pp1.update_value(5)
    time.sleep(1)
    print("Main thread is still working...")
    pp2.update_value(3)
    time.sleep(1)
    pp1.stop()
    pp2.stop()

    # pp1.update_value(7)  # Update while interactive
    # time.sleep(1)  # Give some time to process
    # pp1.update_value(2)  # Update while interactive
    # print("222")
    # pp2.update_value(3)  # Update while interactive
    # time.sleep(1)  # Give some time to process



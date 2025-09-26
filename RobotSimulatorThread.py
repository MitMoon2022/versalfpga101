import threading
import time
import queue
import random # To simulate different test programs

# --- Shared resources and synchronization primitives ---
# A lock to ensure only one thread interacts with the robotic arm at a time.
robot_lock = threading.Lock()
# An event to signal all threads to stop gracefully.
stop_event = threading.Event()
# A queue to hold the DUTs to be tested.
dut_queue = queue.Queue()

# --- Simulate Hardware ---

class RoboticArm:
    """Simulates a robotic arm for pick and place operations."""
    def pick(self, item_name):
        with robot_lock:
            print(f"[{time.time():.2f}] Robotic Arm: Picking up {item_name}.")
            time.sleep(1)  # Simulate pick time
            print(f"[{time.time():.2f}] Robotic Arm: Finished picking {item_name}.")

    def place(self, item_name, site_id):
        with robot_lock:
            print(f"[{time.time():.2f}] Robotic Arm: Placing {item_name} at site {site_id}.")
            time.sleep(1)  # Simulate place time
            print(f"[{time.time():.2f}] Robotic Arm: Finished placing {item_name} at site {site_id}.")

class TemperatureController:
    """Manages the temperature of a test site."""
    def __init__(self, site_id):
        self.site_id = site_id
        self.temperature = 25

    def set_temperature(self, temp):
        print(f"[{time.time():.2f}] Site {self.site_id}: Setting temp to {temp}°C.")
        self.temperature = temp
        time.sleep(2)  # Simulate temperature change time
        print(f"[{time.time():.2f}] Site {self.site_id}: Temperature is stable at {self.temperature}°C.")

    def get_temperature(self):
        return self.temperature

# --- New Class: TestProgramManager ---

class TestProgramManager:
    """
    Manages and executes different test programs.
    This class can be expanded to load test configurations from files.
    """
    def __init__(self):
        # A dictionary mapping program names to their functions
        self.test_programs = {
            "short_test": self.run_short_test,
            "long_test": self.run_long_test,
            "full_test": self.run_full_test
        }

    def run_test_program(self, program_name):
        if program_name in self.test_programs:
            print(f"[{time.time():.2f}] Executing program: {program_name}")
            self.test_programs[program_name]()
        else:
            print(f"[{time.time():.2f}] Warning: Unknown test program '{program_name}'.")

    def run_short_test(self):
        time.sleep(2)

    def run_long_test(self):
        time.sleep(5)

    def run_full_test(self):
        time.sleep(7)

# --- Threaded Test Site Logic ---

def test_site_worker(site_id, robotic_arm, temp_controller, test_manager):
    """
    Thread function to manage the testing process for a single site.
    """
    print(f"[{time.time():.2f}] Test Site {site_id}: Worker thread started.")
    
    # A list of available test programs to cycle through
    programs = list(test_manager.test_programs.keys())

    while not stop_event.is_set():
        try:
            # --- Phase 1: Pick and Place DUT ---
            # Get a DUT from the queue
            dut = dut_queue.get(block=True, timeout=1)
            
            # Use the robotic arm to place the new DUT
            robotic_arm.pick(f"New DUT for {dut}")
            robotic_arm.place(f"New DUT for {dut}", site_id)

            # --- Phase 2: Perform Test at -40C ---
            temp_controller.set_temperature(-40)
            
            # Start the clock for this test
            start_time = time.time()
            
            # Select a random test program to run
            program_to_run = random.choice(programs)
            test_manager.run_test_program(program_to_run)
            
            # Stop the clock and report the time
            elapsed_time = time.time() - start_time
            print(f"[{time.time():.2f}] Site {site_id} Test on {dut} completed in {elapsed_time:.2f} seconds.")

            # --- Phase 3: Post-test Cleanup ---
            # Raise temperature back to 25C
            temp_controller.set_temperature(25)

            # Once temp is stable, remove the tested DUT
            robotic_arm.pick(f"Tested DUT {dut}")
            robotic_arm.place(f"Tested DUT {dut}", "bin")

            # Mark the task as done so the queue knows a slot is free.
            dut_queue.task_done()

        except queue.Empty:
            if stop_event.is_set():
                break
            continue

    print(f"[{time.time():.2f}] Test Site {site_id}: Worker thread stopping.")

# --- Main Program Execution ---

if __name__ == "__main__":
    robotic_arm = RoboticArm()
    test_manager = TestProgramManager()
    threads = []
    
    # Fill the queue with a number of DUTs to test
    total_duts = 20
    for i in range(total_duts):
        dut_queue.put(f"DUT_{i+1}")

    # Create and start 4 worker threads for the 4 sites
    for i in range(4):
        temp_controller = TemperatureController(i + 1)
        thread = threading.Thread(
            target=test_site_worker, 
            args=(i + 1, robotic_arm, temp_controller, test_manager),
            daemon=True
        )
        threads.append(thread)
        thread.start()

    print("Main: All worker threads started. Press Enter to stop the test.")
    
    try:
        input()
    except KeyboardInterrupt:
        pass

    print("Main: Stop signal received. Waiting for threads to finish...")
    stop_event.set()

    # Wait for all threads to join gracefully.
    for thread in threads:
        if thread.is_alive():
            thread.join(timeout=5)
            if thread.is_alive():
                print(f"Main: Warning! Thread {thread.name} did not terminate gracefully.")

    print("Main: Program finished.")

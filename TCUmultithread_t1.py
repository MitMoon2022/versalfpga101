from threading import Thread, Lock
import queue
import random
import time
from multiprocessing import Manager
#from multiprocessing import freeze_support


class ChannelMonitor(Thread):
    def __init__(self, channel_id, temp_queue, shared_state, lock, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_id = channel_id
        self.temp_queue = temp_queue
        self.shared_state = shared_state
        self.lock = lock
        self.running = True

    def run(self):
        while self.running:
            # Simulate reading a temperature value
            temp = round(20 + random.uniform(-5, 5), 2)
            timestamp = time.time()

            # Update current temperature in shared state
            with self.lock:
                self.shared_state[f"channel_{self.channel_id}_current"] = temp

                # Get the setpoint if available
                setpoint_key = f"channel_{self.channel_id}_setpoint"
                setpoint = self.shared_state.get(setpoint_key)

                # Print current status
                print(f"[Channel {self.channel_id}] Temp: {temp}°C at {timestamp}")

                # Check against setpoint
                if setpoint is not None:
                    diff = abs(temp - setpoint)
                    if diff > 2:  # Let's say >2°C difference is worth noting
                        print(f"[Channel {self.channel_id}] ⚠️ Deviation from setpoint ({setpoint}°C) by {diff:.2f}°C.")

            # Push the data to the queue
            self.temp_queue.put({
                'channel': self.channel_id,
                'temperature': temp,
                'timestamp': timestamp
            })

            time.sleep(2)  # Simulate delay between readings

    def stop(self):
        self.running = False


class TCUMasterThread:
    def __init__(self, num_channels=4):
        self.num_channels = num_channels
        self.temp_queue = queue.Queue()
        #self.manager = Manager()
        #self.shared_state = self.manager.dict()  # Shared state for all channels
        self.shared_state = {}  # simple dictionary, thread-safe with Lock()
        self.lock = Lock()
        self.monitors = []

    def start_monitoring(self):
        print("Starting TCU Monitoring...")

        for channel_id in range(1, self.num_channels + 1):
            monitor = ChannelMonitor(
                channel_id,
                self.temp_queue,
                self.shared_state,
                self.lock
            )
            monitor.start()
            self.monitors.append(monitor)

    def stop_monitoring(self):
        print("Stopping TCU Monitoring...")
        for monitor in self.monitors:
            monitor.stop()
            monitor.join()

    def process_temperature_data(self):
        while not self.temp_queue.empty():
            data = self.temp_queue.get()
            print(f"[Processor] Received data: {data}")

    def set_temperature_point(self, channel_id, setpoint):
        with self.lock:
            self.shared_state[f"channel_{channel_id}_setpoint"] = setpoint
            print(f"[Master] Setpoint for Channel {channel_id} set to {setpoint}°C.")


def main():
    tcu_master = TCUMasterThread()
    tcu_master.start_monitoring()

    try:
        # Set some setpoints for channels
        tcu_master.set_temperature_point(1, 22.5)
        tcu_master.set_temperature_point(2, 25.0)
        tcu_master.set_temperature_point(3,35.0)
        #tcu_master.set_temperature_point(4,55.5)

        # Let it run for 12 seconds
        #time.sleep(12)
         # Run indefinitely until interrupted
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[Master] KeyboardInterrupt detected! Stopping monitoring...")

    finally:
        tcu_master.stop_monitoring()
        # Process any remaining data
        tcu_master.process_temperature_data()

if __name__ == "__main__":
    #freeze_support()  # <-- add this
    main()

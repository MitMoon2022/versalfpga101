import threading
import queue
import requests
import time

class TaskProcessor(threading.Thread):
    """
    A worker thread that processes tasks (e.g., downloads a URL) from a queue.
    """
    def __init__(self, task_queue, results, thread_name):
        super().__init__(name=thread_name)
        self.task_queue = task_queue
        self.results = results

    def run(self):
        while True:
            try:
                # Get a task (URL) from the queue
                url = self.task_queue.get(timeout=1)
            except queue.Empty:
                print(f"{self.name} found no more tasks.")
                break

            print(f"{self.name} is downloading: {url}")
            try:
                # Perform the task (download the URL content)
                response = requests.get(url, timeout=5)
                self.results[url] = response.status_code  # Save status code as the result
                print(f"{self.name} finished: {url} with status {response.status_code}")
            except requests.RequestException as e:
                self.results[url] = f"Error: {e}"
                print(f"{self.name} failed: {url} with error {e}")

            # Mark the task as done
            self.task_queue.task_done()


class TaskManager:
    """
    A class for managing tasks, queues, and worker threads.
    """
    def __init__(self, worker_names):
        self.worker_names = worker_names
        self.task_queue = queue.Queue()
        self.results = {}  # Store results of each task
        self.threads = []

    def add_tasks(self, tasks):
        for task in tasks:
            self.task_queue.put(task)

    def start_workers(self):
        for name in self.worker_names:
            thread = TaskProcessor(self.task_queue, self.results, name)
            thread.start()
            self.threads.append(thread)

    def wait_for_completion(self):
        self.task_queue.join()
        for thread in self.threads:
            thread.join()

    def get_results(self):
        return self.results


# Main script
if __name__ == "__main__":
    # Define a list of URLs to download
    urls = [
        "https://www.example.com",
        "https://www.google.com",
        "https://www.wikipedia.org",
        "https://www.python.org",
        "https://httpbin.org/status/404",  # Example of a 404 error
        "https://httpbin.org/delay/2",  # Simulated delay
    ]

    # Define custom names for worker threads
    worker_names = ["Alice", "Bob", "Charlie"]

    # Create a TaskManager
    manager = TaskManager(worker_names)

    # Add URLs to the queue
    manager.add_tasks(urls)

    # Start worker threads
    start_time = time.time()
    manager.start_workers()

    # Wait for all tasks to complete
    manager.wait_for_completion()
    end_time = time.time()

    # Retrieve and print results
    results = manager.get_results()
    print("\nDownload Results:")
    for url, status in results.items():
        print(f"{url}: {status}")

    print(f"\nAll tasks completed in {end_time - start_time:.2f} seconds.")

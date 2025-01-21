import threading
import time

class ProductionStep(threading.Thread):
    """
    Represents a production step in the factory with dependencies on other steps.
    """
    def __init__(self, name, action, condition, dependency=None):
        super().__init__(name=name)
        self.action = action  # The task this step performs
        self.condition = condition
        self.dependency = dependency  # The step this one depends on

    def run(self):
        # Wait for the dependency to complete if it exists
        if self.dependency:
            with self.dependency:
                print(f"{self.name} is waiting for its dependency to complete.")
                self.dependency.wait()

        # Perform the assigned action
        print(f"{self.name} is starting.")
        self.action()
        print(f"{self.name} is complete.")

        # Signal the next step
        with self.condition:
            print(f"{self.name} is signaling the next step.")
            self.condition.notify_all()

class FactoryProductionLine:
    """
    Manages the sequence of production steps in the factory.
    """
    def __init__(self):
        self.steps = []

    def add_step(self, name, action, condition, dependency=None):
        """
        Adds a new production step to the line.
        """
        step = ProductionStep(name, action, condition, dependency)
        self.steps.append(step)

    def start_production(self):
        """
        Starts all production steps in the defined order.
        """
        for step in self.steps:
            step.start()

    def wait_for_completion(self):
        """
        Waits for all production steps to finish.
        """
        for step in self.steps:
            step.join()

# Define actions for each step
def load_raw_materials():
    print("Loading raw materials...")
    time.sleep(2)  # Simulate time taken to load materials

def process_materials():
    print("Processing materials...")
    time.sleep(3)  # Simulate time taken to process materials

def package_products():
    print("Packaging products...")
    time.sleep(2)  # Simulate time taken to package products

# Main script
if __name__ == "__main__":
    # Create a production line
    production_line = FactoryProductionLine()

    # Create conditions for each step
    load_condition = threading.Condition()
    process_condition = threading.Condition()
    package_condition = threading.Condition()

    # Add steps to the production line
    production_line.add_step("Load Materials", load_raw_materials, load_condition)
    production_line.add_step("Process Materials", process_materials, process_condition, dependency=load_condition)
    production_line.add_step("Package Products", package_products, package_condition, dependency=process_condition)

    # Start the production line
    print("Starting the production line...")
    production_line.start_production()

    # Wait for all steps to complete
    production_line.wait_for_completion()
    print("\nProduction process completed.")

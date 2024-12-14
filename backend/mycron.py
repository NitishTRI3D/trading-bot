import time
from datetime import datetime
import subprocess
import os
import sys

def run_algorithm():
    try:
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the path to algorithm_simple.py
        algorithm_path = os.path.join(current_dir, 'algorithms', 'algorithm_simple.py')
        print(algorithm_path)
        print(sys.executable)
        # Use sys.executable to get the path of the current Python interpreter
        subprocess.run([sys.executable, algorithm_path], check=True)
        print(f"Algorithm executed successfully at {datetime.now()}")
    except subprocess.CalledProcessError as e:
        print(f"Error running algorithm: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def wait_until_next_hour():
    # Get current time
    now = datetime.now()
    # Calculate seconds until next hour
    seconds_until_next_hour = 3600 - (now.minute * 60 + now.second)
    return seconds_until_next_hour

def main():
    print("Starting trading bot scheduler...")
    
    while True:
        try:
            # Run the algorithm
            run_algorithm()
            
            # Wait until the start of the next hour
            sleep_time = wait_until_next_hour()
            print(f"Waiting {sleep_time} seconds until next execution...")
            time.sleep(sleep_time)
            
        except KeyboardInterrupt:
            print("\nScheduler stopped by user")
            break
        except Exception as e:
            print(f"Error in main loop: {e}")
            # Wait a minute before retrying in case of error
            time.sleep(60)

if __name__ == "__main__":
    main()

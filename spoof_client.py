import threading

def print_number(number):
    print(f"Thread {threading.current_thread().name}: {number}")

import rpyc
import time
measured_time = {}

def download_video(thread_number):
    database = rpyc.connect_by_service("Database")
    database._config['sync_request_timeout'] = None
    database = database.root

    start_time = time.time()
    for chunk in database.file("15a51fc1-999e-46a7-9b61-5d940ab978a7"):
        pass

    duration = time.time() - start_time
    measured_time[str(thread_number)] = duration


def main():
    number_of_clients = 10

    # Create a thread for each number
    threads = []
    for number in range(number_of_clients):
        thread = threading.Thread(target=download_video, args=(number,), name=f"Thread-{number}")
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    time_sum = 0
    #for key in measured_time:
    for number in range(number_of_clients):
        number = str(number)
        print("mt[",number,"] =",measured_time[number])
        time_sum += measured_time[number]

    print("Average =",time_sum/number_of_clients)

if __name__ == "__main__":
    main()


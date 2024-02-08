import threading

def print_number(number):
    print(f"Thread {threading.current_thread().name}: {number}")

import rpyc
import time
import random
measured_time = {}
average_chunk_thoughtput = {}

import rpyc_helper
def display():
    while True:
        s = 0
        for t in average_chunk_thoughtput:
            s+=average_chunk_thoughtput[t]
        print("Average chunk throughput =",s/len(average_chunk_thoughtput))
        time.sleep(0.3)

def download_video(thread_number):
    database = rpyc_helper.connect("Database")

    start_time = time.time()
    chunk_start_time = time.time()
    i=0
    for chunk in database.file('FILE_51d9c78a-8182-4d05-b7e4-f3d3bcde3e25'):
        #print("Thread",thread_number,"Received a chunk of len",len(chunk))
        chunk_duration = time.time() - chunk_start_time
        throughput = len(chunk)/chunk_duration
        #print("Thread",thread_number,"Received a chunk of len",len(chunk),"current throughput =",throughput,"bytes/second")
        if str(thread_number) not in average_chunk_thoughtput:
            average_chunk_thoughtput[str(thread_number)] = 0
        average_chunk_thoughtput[str(thread_number)] = average_chunk_thoughtput[str(thread_number)]*i/(i+1) + throughput/(i+1)
        chunk_start_time = time.time()
        i+=1

    duration = time.time() - start_time
    measured_time[str(thread_number)] = duration


def main():
    number_of_clients = 20

    # Create a thread for each number
    threads = []
    for number in range(number_of_clients):
        time.sleep(0.2)
        thread = threading.Thread(target=download_video, args=(number,), name=f"Thread-{number}")
        threads.append(thread)
        thread.start()

    display_thread = threading.Thread(target=display)
    display_thread.start()

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


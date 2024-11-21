import threading

def worker():
    while True:
        pass  # Simulate CPU-intensive work

def main():
    MAX_THREADS = 10
    num_threads = int(input(f"Enter the number of threads to spawn (max {MAX_THREADS}): "))
    if num_threads > MAX_THREADS:
        print("Thread limit exceeded.")
        return
    for _ in range(num_threads):
        thread = threading.Thread(target=worker)
        thread.start()
    print(f"Spawned {num_threads} threads.")

if __name__ == "__main__":
    main()

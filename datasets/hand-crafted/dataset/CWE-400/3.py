import threading

def worker():
    while True:
        pass

def main():
    num_threads = int(input("Enter the number of threads to spawn: "))  # Vulnerable
    for _ in range(num_threads):
        thread = threading.Thread(target=worker)
        thread.start()
    print(f"Spawned {num_threads} threads.")

if __name__ == "__main__":
    main()

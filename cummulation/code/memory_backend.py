import os
import subprocess
import time
import csv
from threading import Thread, Event

MEMORY_LOG_FILE = "/home/sasi-1902/Documents/Programming/Os_prj/cummulation/csvs/memory_metrics.csv"
stop_event = Event()

# Function to get memory stats using `cat /proc/meminfo`
def get_proc_meminfo():
    command = "cat /proc/meminfo"
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True)
        output = result.stdout.splitlines()

        meminfo = {}
        for line in output:
            parts = line.split(':')
            if len(parts) == 2:
                key = parts[0].strip()
                value = int(parts[1].strip().split()[0])  # Extract numeric value
                meminfo[key] = value
        return meminfo
    except Exception as e:
        print(f"Error fetching /proc/meminfo: {e}")
        return {}

# Function to get summarized memory usage using `free -m`
def get_free_memory():
    command = "free -m"
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True)
        output = result.stdout.splitlines()

        free_mem = {}
        headers = output[0].split()
        mem_values = output[1].split()
        swap_values = output[2].split()

        free_mem["MemTotal"] = int(mem_values[1])
        free_mem["MemUsed"] = int(mem_values[2])
        free_mem["MemFree"] = int(mem_values[3])
        free_mem["SwapTotal"] = int(swap_values[1])
        free_mem["SwapUsed"] = int(swap_values[2])
        free_mem["SwapFree"] = int(swap_values[3])

        return free_mem
    except Exception as e:
        print(f"Error fetching free memory data: {e}")
        return {}

# Function to log memory metrics
def log_memory_metrics(interval=1):
    os.makedirs(os.path.dirname(MEMORY_LOG_FILE), exist_ok=True)

    file_exists = os.path.isfile(MEMORY_LOG_FILE)

    with open(MEMORY_LOG_FILE, "a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "Timestamp", "MemTotal (kB)", "MemFree (kB)", "MemAvailable (kB)", 
                "Buffers (kB)", "Cached (kB)", "SwapTotal (kB)", "SwapFree (kB)",
                "Free Mem (MB)", "Used Mem (MB)", "Free Swap (MB)", "Used Swap (MB)"
            ])

        while not stop_event.is_set():
            try:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                proc_meminfo = get_proc_meminfo()
                free_mem = get_free_memory()

                writer.writerow([
                    timestamp,
                    proc_meminfo.get("MemTotal", 0),
                    proc_meminfo.get("MemFree", 0),
                    proc_meminfo.get("MemAvailable", 0),
                    proc_meminfo.get("Buffers", 0),
                    proc_meminfo.get("Cached", 0),
                    proc_meminfo.get("SwapTotal", 0),
                    proc_meminfo.get("SwapFree", 0),
                    free_mem.get("MemFree", 0),
                    free_mem.get("MemUsed", 0),
                    free_mem.get("SwapFree", 0),
                    free_mem.get("SwapUsed", 0),
                ])
                file.flush()  # Ensure data is written to disk immediately
                print(f"[INFO] Logged memory data at {timestamp}")
                time.sleep(interval)
            except Exception as e:
                print(f"[ERROR] Logging memory metrics: {e}")


def stop_mem_log():
    stop_event.set()
    print("[INFO] Memory logging stopped.")



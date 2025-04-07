import os
import subprocess
import csv
import time
import threading

# File paths
CPU_LOG_FILE = "/home/sasi-1902/Documents/Programming/Os_prj/cummulation/csvs/cpu_metrics.csv"
VMSTAT_LOG_FILE = "/home/sasi-1902/Documents/Programming/Os_prj/cummulation/csvs/vmstat_metrics.csv"

# Logging state
flag_cpu = False

# Function to fetch CPU usage metrics
def get_cpu_usage():
    command = "mpstat -P ALL 1 1"
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True)
    output = result.stdout.splitlines()

    cpu_usage = {}
    for line in output:
        if "CPU" in line or not line.strip():
            continue
        parts = line.split()
        if len(parts) < 12:
            continue
        try:
            core = parts[2]
            if not (core.isdigit() or core == "all"):
                continue
            user_time = float(parts[3])
            system_time = float(parts[5])
            idle_time = float(parts[11])
            cpu_usage[core] = {
                "User Time (%)": user_time,
                "System Time (%)": system_time,
                "Idle Time (%)": idle_time,
            }
        except (IndexError, ValueError):
            continue

    return cpu_usage

# Function to fetch VMSTAT metrics
def get_vmstat_metrics():
    command = "vmstat 1 1"
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True)
    output = result.stdout.splitlines()

    vmstat_data = {}
    for line in output:
        if line.startswith("procs") or line.strip() == "":
            continue
        parts = line.split()
        try:
            vmstat_data = {
                "Procs waiting for I/O": int(parts[2]),
                "User Time (%)": int(parts[12]),
                "System Time (%)": int(parts[13]),
                "Idle Time (%)": int(parts[14]),
                "I/O Wait (%)": int(parts[15]),
                "Hardware Interrupts (%)": int(parts[16]),
                "Software Interrupts (%)": int(parts[17]),
            }
        except (IndexError, ValueError):
            continue

    return vmstat_data

# Logging function
def log_cpu():
    global flag_cpu
    flag_cpu = True

    # Ensure directories exist
    os.makedirs(os.path.dirname(CPU_LOG_FILE), exist_ok=True)

    # Open files and initialize CSV writers
    with open(CPU_LOG_FILE, "a", newline="") as cpu_file, open(VMSTAT_LOG_FILE, "a", newline="") as vmstat_file:
        cpu_writer = csv.writer(cpu_file)
        vmstat_writer = csv.writer(vmstat_file)

        # Add headers if files are empty
        if os.stat(CPU_LOG_FILE).st_size == 0:
            cpu_writer.writerow(["Timestamp", "Core", "User Time (%)", "System Time (%)", "Idle Time (%)"])
        if os.stat(VMSTAT_LOG_FILE).st_size == 0:
            vmstat_writer.writerow([
                "Timestamp",
                "Procs waiting for I/O",
                "User Time (%)",
                "System Time (%)",
                "Idle Time (%)",
                "I/O Wait (%)",
                "Hardware Interrupts (%)",
                "Software Interrupts (%)",
            ])

        print("[INFO] Logging started. Press Ctrl+C to stop.")
        try:
            while flag_cpu:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

                # Log CPU metrics
                cpu_metrics = get_cpu_usage()
                for core, metrics in cpu_metrics.items():
                    cpu_writer.writerow([timestamp, core, metrics["User Time (%)"], metrics["System Time (%)"], metrics["Idle Time (%)"]])

                # Log VMSTAT metrics
                vmstat_metrics = get_vmstat_metrics()
                if vmstat_metrics:
                    vmstat_writer.writerow([timestamp] + list(vmstat_metrics.values()))

                # Ensure data is flushed to the file immediately
                cpu_file.flush()
                vmstat_file.flush()

                time.sleep(1)
        except KeyboardInterrupt:
            print("[INFO] Logging stopped.")
        finally:
            print("[INFO] Finished logging.")

# Stop logging function
def stop_cpu():
    global flag_cpu
    flag_cpu = False
    print("[INFO] Logging will stop shortly.")

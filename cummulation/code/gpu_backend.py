import os
import subprocess
import csv
import time
import threading

output_file = "/home/sasi-1902/Documents/Programming/Os_prj/cummulation/csvs/gpu_monitoring_log.csv"
flag_gpu = True  # Global flag to control logging


def detect_gpus():
    detected_gpus = []

    # Check for NVIDIA GPUs
    try:
        result = subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True)
        if result.returncode == 0:
            gpus = result.stdout.strip().split("\n")
            for idx, gpu in enumerate(gpus):
                detected_gpus.append({"type": "NVIDIA", "id": idx, "info": gpu})
    except FileNotFoundError:
        pass

    # Check for AMD GPUs
    try:
        result = subprocess.run(["rocm-smi"], capture_output=True, text=True)
        if result.returncode == 0:
            detected_gpus.append({"type": "AMD", "info": "AMD GPU(s) detected"})
    except FileNotFoundError:
        pass

    # Check for Intel GPUs
    try:
        result = subprocess.run(["intel-gpu-top", "-J"], capture_output=True, text=True)
        if result.returncode == 0:
            detected_gpus.append({"type": "Intel", "info": "Intel GPU(s) detected"})
    except FileNotFoundError:
        pass

    return detected_gpus


def log_gpu_stats():
    global flag_gpu
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    gpus = detect_gpus()
    if not gpus:
        print("[INFO] No GPUs detected.")
        with open(output_file, mode="a", newline="") as file:
            writer = csv.writer(file)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([timestamp, "None", "No GPUs detected", "N/A", "N/A"])
        return

    print(f"[INFO] Detected GPUs: {[gpu['type'] for gpu in gpus]}")

    # Write headers if the file is new
    if not os.path.exists(output_file) or os.stat(output_file).st_size == 0:
        with open(output_file, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "GPU Type", "Metric", "Value", "Details"])

    while flag_gpu:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(output_file, mode="a", newline="") as file:
                writer = csv.writer(file)
                for gpu in gpus:
                    if gpu["type"] == "NVIDIA":
                        result = subprocess.run(
                            ["nvidia-smi", "--query-gpu=utilization.gpu,utilization.memory,memory.total,memory.used,memory.free,temperature.gpu,power.draw", "--format=csv,noheader,nounits"],
                            capture_output=True, text=True
                        )
                        if result.returncode == 0:
                            metrics = result.stdout.strip().split("\n")
                            for idx, metric in enumerate(metrics):
                                util_gpu, util_mem, mem_total, mem_used, mem_free, temp, power = metric.split(", ")
                                writer.writerow([timestamp, "NVIDIA", "GPU Utilization (%)", util_gpu, f"GPU {idx}"])
                                writer.writerow([timestamp, "NVIDIA", "Memory Utilization (%)", util_mem, f"GPU {idx}"])
                                writer.writerow([timestamp, "NVIDIA", "Memory Total (MB)", mem_total, f"GPU {idx}"])
                                writer.writerow([timestamp, "NVIDIA", "Memory Used (MB)", mem_used, f"GPU {idx}"])
                                writer.writerow([timestamp, "NVIDIA", "Memory Free (MB)", mem_free, f"GPU {idx}"])
                                writer.writerow([timestamp, "NVIDIA", "Temperature (C)", temp, f"GPU {idx}"])
                                writer.writerow([timestamp, "NVIDIA", "Power Draw (W)", power, f"GPU {idx}"])

                    elif gpu["type"] == "AMD":
                        result = subprocess.run(["rocm-smi"], capture_output=True, text=True)
                        if result.returncode == 0:
                            writer.writerow([timestamp, "AMD", "Raw Data", result.stdout.strip(), "All AMD GPUs"])

                    elif gpu["type"] == "Intel":
                        result = subprocess.run(["intel-gpu-top", "-J"], capture_output=True, text=True)
                        if result.returncode == 0:
                            writer.writerow([timestamp, "Intel", "Raw Data", result.stdout.strip(), "All Intel GPUs"])

                print(f"[INFO] GPU stats logged at {timestamp}.")
                time.sleep(1)  # Log every second

        except Exception as e:
            print(f"[ERROR] Error logging GPU stats: {e}")
            break


def stop_gpu_log():
    global flag_gpu
    flag_gpu = False
    print("[INFO] Logging stopped.")

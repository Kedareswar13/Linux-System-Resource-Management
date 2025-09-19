import subprocess
import csv
import threading
import time

# Your sudo password
sudo_password = "1902"

# File to save data
output_file = "/home/sasi-1902/Documents/Programming/Os_prj/cummulation/csvs/iotop_pidstat_log.csv"

# Stop logging flag
flag_i_o = True

# Function to log iotop and pidstat data
def log_io_stats():
    global flag_i_o
    with open(output_file, mode="w", newline="") as file:
        writer = csv.writer(file)

        # Write header for structured CSV
        writer.writerow(["Timestamp", "Metric Type", "Data"])

        while flag_i_o:
            print("[INFO] Starting data collection iteration...")

            # Run iotop command
            print("[INFO] Running iotop...")
            iotop_result = subprocess.run(
                f"sudo -S iotop -b -n 1",
                shell=True,
                capture_output=True,
                text=True,
                input=f"{sudo_password}\n"
            )

            if iotop_result.returncode == 0:
                print("[INFO] iotop executed successfully.")
            else:
                print(f"[ERROR] iotop failed: {iotop_result.stderr}")

            # Run pidstat command
            print("[INFO] Running pidstat...")
            pidstat_result = subprocess.run(
                f"sudo -S pidstat 1 1",
                shell=True,
                capture_output=True,
                text=True,
                input=f"{sudo_password}\n"
            )

            if pidstat_result.returncode == 0:
                print("[INFO] pidstat executed successfully.")
            else:
                print(f"[ERROR] pidstat failed: {pidstat_result.stderr}")

            # Combine outputs and clean unnecessary lines
            print("[INFO] Combining outputs...")
            combined_output = iotop_result.stdout + "\n" + pidstat_result.stdout
            useful_lines = []
            capture_remaining = False
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            for line in combined_output.splitlines():
                if "Total DISK READ" in line or "Current DISK READ" in line:
                    useful_lines.append([timestamp, "Disk Stats", line.strip()])
                elif capture_remaining:
                    if line.strip() and not line.startswith("Linux"):  # Exclude lines starting with 'Linux'
                        useful_lines.append([timestamp, "Process Stats", line.strip()])
                elif line.startswith("Linux"):
                    capture_remaining = True  # Start capturing subsequent lines

            print("[INFO] Writing useful lines to CSV...")
            # Append the cleaned data to the CSV
            try:
                for row in useful_lines:
                    writer.writerow(row)
                print(f"[SUCCESS] Data written to {output_file}")
            except Exception as e:
                print(f"[ERROR] Failed to write to CSV: {e}")

            if not useful_lines:
                print("[WARNING] No useful lines extracted!")

            time.sleep(1)  # Pause for 1 second before the next iteration
            print("[INFO] Completed data collection iteration.")

# Function to stop logging
def stop_io_log():
    global flag_i_o
    flag_i_o = False
    print("[INFO] Stopping logging...")



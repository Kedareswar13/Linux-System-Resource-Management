import csv
from tkinter import *
from tkinter import ttk
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

DISK_IO_CSV = "//home/sasi-1902/Documents/Programming/Os_prj/cummulation/csvs/iotop_pidstat_log.csv"

def read_disk_io_data():
    disk_data = {
        "timestamps": [],
        "total_read": [],
        "total_write": [],
        "current_read": [],
        "current_write": []
    }
    try:
        with open(DISK_IO_CSV, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Metric Type'] == "Disk Stats":
                    timestamp = row['Timestamp']
                    data = row['Data']
                    total_read, total_write = 0, 0
                    current_read, current_write = 0, 0
                    
                    if "Total DISK READ" in data and "Total DISK WRITE" in data:
                        total_read = float(data.split("Total DISK READ:")[1].split("B/s")[0].strip().replace(',', '').split()[0])
                        total_write = float(data.split("Total DISK WRITE:")[1].split("B/s")[0].strip().replace(',', '').split()[0])
                    
                    if "Current DISK READ" in data and "Current DISK WRITE" in data:
                        current_read = float(data.split("Current DISK READ:")[1].split("B/s")[0].strip().replace(',', '').split()[0])
                        current_write = float(data.split("Current DISK WRITE:")[1].split("B/s")[0].strip().replace(',', '').split()[0])

                    # Append data to dictionary
                    disk_data["timestamps"].append(timestamp)
                    disk_data["total_read"].append(total_read)
                    disk_data["total_write"].append(total_write)
                    disk_data["current_read"].append(current_read)
                    disk_data["current_write"].append(current_write)
    except FileNotFoundError:
        print("[INFO] Disk I/O CSV file not found.")
    except Exception as e:
        print(f"[ERROR] Error reading disk I/O CSV: {e}")
    return disk_data

def update_disk_io_table(tree):
    last_processed_timestamp = None
    while True:
        disk_data = read_disk_io_data()
        if disk_data and disk_data["timestamps"]:
            # Find the index of the last new data
            new_start_index = 0
            if last_processed_timestamp:
                if last_processed_timestamp in disk_data["timestamps"]:
                    new_start_index = disk_data["timestamps"].index(last_processed_timestamp) + 1

            # If there's no new data, skip
            if new_start_index >= len(disk_data["timestamps"]):
                time.sleep(1)
                continue

            # Update the last processed timestamp
            last_processed_timestamp = disk_data["timestamps"][-1]

            # Insert only new rows dynamically
            for i in range(new_start_index, len(disk_data["timestamps"])):
                tree.insert('', 'end', values=(
                    disk_data["timestamps"][i],
                    f"{disk_data['total_read'][i]:.2f} B/s",
                    f"{disk_data['total_write'][i]:.2f} B/s",
                    f"{disk_data['current_read'][i]:.2f} B/s",
                    f"{disk_data['current_write'][i]:.2f} B/s"
                ))

            # Scroll to the latest entry
            tree.yview_moveto(1)  # Scroll to the bottom
        time.sleep(1)


# Function to plot total disk I/O trends
def plot_disk_io_trends():
    disk_data = read_disk_io_data()
    if not disk_data["timestamps"]:
        print("[INFO] No timestamps available for plotting.")
        return
    
    fig, ax = plt.subplots(figsize=(8, 5))  # Create a new figure
    ax.plot(disk_data["timestamps"], disk_data["total_read"], label="Total Disk Read (B/s)", color='blue')
    ax.plot(disk_data["timestamps"], disk_data["total_write"], label="Total Disk Write (B/s)", color='orange')

    # Configure x-axis to reduce clutter
    ax.xaxis.set_major_locator(MaxNLocator(nbins=10))  # Show only 10 ticks
    ax.tick_params(axis='x', rotation=45)
    ax.set_title("Total Disk I/O Trends")
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Disk I/O (B/s)")
    ax.legend()

    plt.tight_layout()
    plt.show()
    plt.close(fig)  # Close the figure explicitly


# Function to plot current disk I/O spikes
def plot_disk_io_spikes():
    disk_data = read_disk_io_data()
    if not disk_data["timestamps"]:
        print("[INFO] No timestamps available for plotting.")
        return

    fig, ax = plt.subplots(figsize=(8, 5))  # Create a new figure
    ax.bar(disk_data["timestamps"], disk_data["current_read"], label="Current Disk Read (B/s)", color='blue', alpha=0.7)
    ax.bar(disk_data["timestamps"], disk_data["current_write"], label="Current Disk Write (B/s)", color='orange', alpha=0.7)

    # Configure x-axis to reduce clutter
    ax.xaxis.set_major_locator(MaxNLocator(nbins=10))  # Show only 10 ticks
    ax.tick_params(axis='x', rotation=45)
    ax.set_title("Current Disk I/O Spikes")
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Disk I/O (B/s)")
    ax.legend()

    plt.tight_layout()
    plt.show()
    plt.close(fig)  # Close the figure explicitly


# Tkinter window function for Disk I/O
def out_disk_io():
    io_window = Toplevel()
    io_window.title("Disk I/O Dashboard")
    io_window.geometry("1000x700")

    # Disk I/O Table
    Label(io_window, text="Disk I/O Statistics", font=('Helvetica', 14)).pack(pady=5)
    io_columns = ("Timestamp", "Total DISK READ", "Total DISK WRITE", "Current DISK READ", "Current DISK WRITE")
    io_tree = ttk.Treeview(io_window, columns=io_columns, show='headings', height=15)
    for col in io_columns:
        io_tree.heading(col, text=col)
        io_tree.column(col, width=200)
    io_tree.pack(fill=BOTH, expand=True)
    threading.Thread(target=update_disk_io_table, args=(io_tree,), daemon=True).start()

    # Plot buttons
    Button(io_window, text="Plot Total Disk I/O Trends", command=plot_disk_io_trends).pack(pady=10)
    Button(io_window, text="Plot Current Disk I/O Spikes", command=plot_disk_io_spikes).pack(pady=10)

    # Close button
    Button(io_window, text="Close", command=io_window.destroy).pack(pady=10)
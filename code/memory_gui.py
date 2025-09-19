import csv
from tkinter import *
from tkinter import ttk
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

MEMORY_CSV = "/home/sasi-1902/Documents/Programming/Os_prj/cummulation/csvs/memory_metrics.csv"

# Function to read memory data
def read_memory_data():
    memory_data = {
        "timestamps": [],
        "total_mem": [],
        "free_mem": [],
        "used_mem": [],
        "cached_mem": [],
        "buffers_mem": [],
        "swap_total": [],
        "swap_free": [],
        "used_swap": []
    }
    try:
        with open(MEMORY_CSV, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                memory_data["timestamps"].append(row["Timestamp"])
                memory_data["total_mem"].append(float(row["MemTotal (kB)"]) / 1024)
                memory_data["free_mem"].append(float(row["MemFree (kB)"]) / 1024)
                memory_data["used_mem"].append(float(row["Used Mem (MB)"]))
                memory_data["cached_mem"].append(float(row["Cached (kB)"]) / 1024)
                memory_data["buffers_mem"].append(float(row["Buffers (kB)"]) / 1024)
                memory_data["swap_total"].append(float(row["SwapTotal (kB)"]) / 1024)
                memory_data["swap_free"].append(float(row["SwapFree (kB)"]) / 1024)
                memory_data["used_swap"].append(float(row["Used Swap (MB)"]))
    except FileNotFoundError:
        print("[INFO] Memory CSV file not found.")
    except Exception as e:
        print(f"[ERROR] Error reading memory CSV: {e}")
    return memory_data

# Function to update memory table
def update_memory_table(tree):
    last_processed_timestamp = None
    while True:
        memory_data = read_memory_data()
        if memory_data and memory_data["timestamps"]:
            # Find the index of the last new data
            new_start_index = 0
            if last_processed_timestamp:
                if last_processed_timestamp in memory_data["timestamps"]:
                    new_start_index = memory_data["timestamps"].index(last_processed_timestamp) + 1

            # If there's no new data, skip
            if new_start_index >= len(memory_data["timestamps"]):
                time.sleep(1)
                continue

            # Update the last processed timestamp
            last_processed_timestamp = memory_data["timestamps"][-1]

            # Insert only new rows dynamically
            for i in range(new_start_index, len(memory_data["timestamps"])):
                tree.insert('', 'end', values=(
                    memory_data["timestamps"][i],
                    f"{memory_data['total_mem'][i]:.2f} MB",
                    f"{memory_data['free_mem'][i]:.2f} MB",
                    f"{memory_data['used_mem'][i]:.2f} MB",
                    f"{memory_data['swap_free'][i]:.2f} MB",
                    f"{memory_data['used_swap'][i]:.2f} MB"
                ))

            # Scroll to the latest entry
            tree.yview_moveto(1)  # Scroll to the bottom
        time.sleep(1)



# Plot: Memory Usage Over Time (Line Chart)
def plot_memory_usage():
    memory_data = read_memory_data()
    if not memory_data["timestamps"]:
        print("[INFO] No timestamps available for plotting.")
        return
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(memory_data["timestamps"], memory_data["used_mem"], label="Used Memory (MB)", color='blue')
    ax.plot(memory_data["timestamps"], memory_data["free_mem"], label="Free Memory (MB)", color='orange')

    ax.set_title("Memory Usage Over Time")
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Memory (MB)")
    ax.xaxis.set_major_locator(MaxNLocator(prune='both', nbins=10))  # Reduce x-axis clutter
    ax.tick_params(axis='x', rotation=45)
    ax.legend()

    plt.tight_layout()
    plt.show()

# Plot: Swap Usage Trends (Line Chart)
def plot_swap_usage():
    memory_data = read_memory_data()
    if not memory_data["timestamps"]:
        print("[INFO] No timestamps available for plotting.")
        return
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(memory_data["timestamps"], memory_data["swap_free"], label="Free Swap (MB)", color='green')
    ax.plot(memory_data["timestamps"], memory_data["used_swap"], label="Used Swap (MB)", color='red')

    ax.set_title("Swap Usage Trends")
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Swap (MB)")
    ax.xaxis.set_major_locator(MaxNLocator(prune='both', nbins=10))  # Reduce x-axis clutter
    ax.tick_params(axis='x', rotation=45)
    ax.legend()

    plt.tight_layout()
    plt.show()

# Plot: Memory Distribution (Pie Chart)
def plot_memory_distribution():
    memory_data = read_memory_data()
    if not memory_data["timestamps"]:
        print("[INFO] No data available for plotting.")
        return

    latest_index = -1  # Use the latest data point
    labels = ["Used Memory", "Free Memory", "Cached Memory"]
    sizes = [
        memory_data["used_mem"][latest_index],
        memory_data["free_mem"][latest_index],
        memory_data["cached_mem"][latest_index]
    ]
    colors = ['blue', 'orange', 'green']

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.title("Memory Distribution")
    plt.tight_layout()
    plt.show()

# Plot: Memory Efficiency (Line Chart)
def plot_memory_efficiency():
    memory_data = read_memory_data()
    if not memory_data["timestamps"]:
        print("[INFO] No timestamps available for plotting.")
        return
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(memory_data["timestamps"], memory_data["total_mem"], label="Total Memory (MB)", color='blue')
    ax.plot(memory_data["timestamps"], memory_data["free_mem"], label="Free Memory (MB)", color='orange')
    ax.plot(memory_data["timestamps"], memory_data["cached_mem"], label="Cached Memory (MB)", color='green')

    ax.set_title("Memory Efficiency Over Time")
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Memory (MB)")
    ax.xaxis.set_major_locator(MaxNLocator(prune='both', nbins=10))  # Reduce x-axis clutter
    ax.tick_params(axis='x', rotation=45)
    ax.legend()

    plt.tight_layout()
    plt.show()

# Tkinter Window Function for Memory Dashboard
def out_memory():
    mem_window = Toplevel()
    mem_window.title("Memory Dashboard")
    mem_window.geometry("1000x700")

    # Memory Table
    Label(mem_window, text="Memory Statistics", font=('Helvetica', 14)).pack(pady=5)
    mem_columns = ("Timestamp", "Total Memory (MB)", "Free Memory (MB)", "Used Memory (MB)", "Free Swap (MB)", "Used Swap (MB)")
    mem_tree = ttk.Treeview(mem_window, columns=mem_columns, show='headings', height=15)
    for col in mem_columns:
        mem_tree.heading(col, text=col)
        mem_tree.column(col, width=200)
    mem_tree.pack(fill=BOTH, expand=True)
    threading.Thread(target=update_memory_table, args=(mem_tree,), daemon=True).start()

    # Plot Buttons
    Button(mem_window, text="Plot Memory Usage Over Time", command=plot_memory_usage).pack(pady=10)
    Button(mem_window, text="Plot Swap Usage Trends", command=plot_swap_usage).pack(pady=10)
    Button(mem_window, text="Plot Memory Distribution", command=plot_memory_distribution).pack(pady=10)
    Button(mem_window, text="Plot Memory Efficiency", command=plot_memory_efficiency).pack(pady=10)

    # Close Button
    Button(mem_window, text="Close", command=mem_window.destroy).pack(pady=10)

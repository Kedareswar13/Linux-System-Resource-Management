import csv
from tkinter import *
from tkinter import ttk
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator

# CSV file paths
CPU_CORE_CSV = "/home/sasi-1902/Documents/Programming/Os_prj/cummulation/csvs/cpu_metrics.csv"
PROCESS_CSV = "/home/sasi-1902/Documents/Programming/Os_prj/cummulation/csvs/vmstat_metrics.csv"

# Function to read core-wise CPU data
def read_core_data():
    core_data = {}
    timestamps = []
    try:
        with open(CPU_CORE_CSV, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                core = row['Core']
                if core not in core_data:
                    core_data[core] = {'User': [], 'System': [], 'Idle': []}
                user_time = float(row['User Time (%)'])
                system_time = float(row['System Time (%)'])
                # Calculate Idle Time dynamically
                idle_time = 100 - (user_time + system_time)

                core_data[core]['User'].append(user_time)
                core_data[core]['System'].append(system_time)
                core_data[core]['Idle'].append(idle_time)

                if row['Timestamp'] not in timestamps:
                    timestamps.append(row['Timestamp'])
    except FileNotFoundError:
        print("[INFO] Core CSV file not found.")
    except Exception as e:
        print(f"[ERROR] Error reading core CSV: {e}")
    return core_data, timestamps




# Function to read process-wise CPU data
def read_process_data():
    process_data = []
    try:
        with open(PROCESS_CSV, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                process_data.append(row)
    except FileNotFoundError:
        print("[INFO] Process CSV file not found.")
    except Exception as e:
        print(f"[ERROR] Error reading process CSV: {e}")
    return process_data

# Function to update core-wise data table
def update_core_table(tree):
    while True:
        core_data, _ = read_core_data()
        if core_data:
            # Clear existing rows
            for row in tree.get_children():
                tree.delete(row)
            # Insert new rows dynamically
            for core, metrics in core_data.items():
                avg_user = sum(metrics['User']) / len(metrics['User']) if metrics['User'] else 0
                avg_system = sum(metrics['System']) / len(metrics['System']) if metrics['System'] else 0
                avg_idle = sum(metrics['Idle']) / len(metrics['Idle']) if metrics['Idle'] else 0
                tree.insert('', 'end', values=(core, f"{avg_user:.2f}%", f"{avg_system:.2f}%", f"{avg_idle:.2f}%"))
        time.sleep(1)

# Function to update process-wise data table
def update_process_table(tree):
    while True:
        process_data = read_process_data()
        if process_data:
            # Clear existing rows
            for row in tree.get_children():
                tree.delete(row)
            # Insert the most recent data (e.g., last row)
            latest_row = process_data[-1]
            tree.insert('', 'end', values=(
                latest_row['Timestamp'],
                latest_row['Procs waiting for I/O'],
                latest_row['User Time (%)'],
                latest_row['System Time (%)'],
                latest_row['Idle Time (%)'],
                latest_row['I/O Wait (%)'],
                latest_row['Hardware Interrupts (%)'],
                latest_row['Software Interrupts (%)']
            ))
        time.sleep(1)

# Function to plot average CPU usage
def plot_avg_cpu():
    core_data, timestamps = read_core_data()
    if not timestamps:
        print("[INFO] No timestamps available for plotting.")
        return
    avg_usage = []
    for i in range(len(timestamps)):
        total_usage = 0
        count = 0
        for core, metrics in core_data.items():
            if len(metrics['User']) > i:
                total_usage += metrics['User'][i] + metrics['System'][i]
                count += 1
        avg_usage.append(total_usage / count if count else 0)

    # Plot
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(timestamps, avg_usage, label="Average CPU Usage (%)", color='blue')

    # Reduce clutter on the x-axis
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, prune='both'))
    ax.set_title("Average CPU Usage Over Time")
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Usage (%)")
    ax.tick_params(axis='x', rotation=45)
    ax.legend()

    plt.tight_layout()
    plt.show()

# Tkinter window function
def out_cpu():
    cpu_window = Toplevel()
    cpu_window.title("CPU Dashboard")
    cpu_window.geometry("1000x700")

    # Core-wise table
    Label(cpu_window, text="Core-Wise CPU Usage", font=('Helvetica', 14)).pack(pady=5)
    core_columns = ("Core", "User Time (%)", "System Time (%)", "Idle Time (%)")
    core_tree = ttk.Treeview(cpu_window, columns=core_columns, show='headings', height=10)
    for col in core_columns:
        core_tree.heading(col, text=col)
        core_tree.column(col, width=200)
    core_tree.pack(fill=BOTH, expand=True)
    threading.Thread(target=update_core_table, args=(core_tree,), daemon=True).start()

    # Process-wise table
    Label(cpu_window, text="Process-Wise CPU Usage", font=('Helvetica', 14)).pack(pady=5)
    process_columns = (
        "Timestamp", "Procs waiting for I/O", "User Time (%)",
        "System Time (%)", "Idle Time (%)", "I/O Wait (%)",
        "Hardware Interrupts (%)", "Software Interrupts (%)"
    )
    process_tree = ttk.Treeview(cpu_window, columns=process_columns, show='headings', height=10)
    for col in process_columns:
        process_tree.heading(col, text=col)
        process_tree.column(col, width=200)
    process_tree.pack(fill=BOTH, expand=True)
    threading.Thread(target=update_process_table, args=(process_tree,), daemon=True).start()

    # Plot button
    Button(cpu_window, text="Plot Average CPU Usage", command=plot_avg_cpu).pack(pady=20)

    # Close button
    Button(cpu_window, text="Close", command=cpu_window.destroy).pack(pady=10)
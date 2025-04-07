import csv
from tkinter import *
from tkinter import ttk
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# GPU CSV file path
GPU_CSV_FILE = "/home/sasi-1902/Documents/Programming/Os_prj/cummulation/csvs/gpu_monitoring_log.csv"

# Function to check if GPU is present
def check_gpu_presence():
    try:
        with open(GPU_CSV_FILE, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row.get('GPU Type', '') != "None":
                    return True
        return False
    except FileNotFoundError:
        # Return False if the CSV doesn't exist yet
        print("[INFO] GPU CSV file not found. No GPUs detected yet.")
        return False
    except Exception as e:
        print(f"[ERROR] Error checking GPU presence: {e}")
        return False

# Function to read GPU data from the CSV
def read_gpu_data():
    data = []
    try:
        with open(GPU_CSV_FILE, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        # Log and return empty data if the file is missing
        print("[INFO] GPU CSV file not found. No data to read.")
    except Exception as e:
        print(f"[ERROR] Error reading GPU CSV: {e}")
    return data

# Function to update GPU data in the table
def update_gpu_table(tree):
    last_row_count = 0  # Track the number of rows already added
    while True:
        data = read_gpu_data()
        if data and len(data) > last_row_count:
            new_rows = data[last_row_count:]  # Only get the new rows
            last_row_count = len(data)  # Update the last row count
            for row in new_rows:
                tree.insert('', 'end', values=(
                    row.get('Timestamp', 'N/A'),
                    row.get('GPU Type', 'N/A'),
                    row.get('Metric', 'N/A'),
                    row.get('Value', 'N/A'),
                    row.get('Details', 'N/A')
                ))
            # Scroll to the last row to keep the latest entry visible
            tree.yview_moveto(1.0)
        time.sleep(1)  # Update every second

# GPU Tkinter window function
def out_gpu():
    # Check if GPUs are present when the button is clicked
    gpu_window = Toplevel()
    gpu_window.title("GPU Dashboard")
    gpu_window.geometry("800x600")

    if not check_gpu_presence():
        # Display "No GPU Found" if the CSV doesn't indicate GPU presence
        label = Label(gpu_window, text="No GPU Detected (This software only supports Nvidia, AMD, and Intel GPUs)", font=('Helvetica', 16), fg='red')
        label.pack(pady=50)
        Button(gpu_window, text="Close", command=gpu_window.destroy).pack(pady=10)
        return

    # Show GPU details in a table
    columns = ("Timestamp", "GPU Type", "Metric", "Value", "Details")
    tree = ttk.Treeview(gpu_window, columns=columns, show='headings', height=15)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.pack(fill=BOTH, expand=True)

    # Start a thread to update the table
    threading.Thread(target=update_gpu_table, args=(tree,), daemon=True).start()

    # Plot GPU Utilization
    def plot_gpu_utilization():
        data = read_gpu_data()
        if not data:
            print("[INFO] No data available for plotting.")
            return
        timestamps = [row.get('Timestamp', '') for row in data if row.get('Metric', '') == "GPU Utilization (%)"]
        utilization = [float(row.get('Value', 0)) for row in data if row.get('Metric', '') == "GPU Utilization (%)"]

        if not timestamps or not utilization:
            print("[INFO] No utilization data available for plotting.")
            return

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(timestamps, utilization, label="GPU Utilization (%)", color='blue')
        ax.set_title("GPU Utilization Over Time")
        ax.set_xlabel("Timestamp")
        ax.set_ylabel("Utilization (%)")
        ax.tick_params(axis='x', rotation=45)
        ax.legend()

        # Show the plot
        plt.tight_layout()
        plt.show()
        plt.close(fig)  # Ensure no overlap between plots

    Button(gpu_window, text="Plot GPU Utilization", command=plot_gpu_utilization).pack(pady=10)

    # Close button
    Button(gpu_window, text="Close", command=gpu_window.destroy).pack(pady=10)

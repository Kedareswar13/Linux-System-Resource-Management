from tkinter import *
from PIL import Image, ImageTk
import threading
import os

from cpu_procs_backend import log_cpu, stop_cpu
from gpu_backend import log_gpu_stats, stop_gpu_log
from i_o_backend import log_io_stats, stop_io_log
from memory_backend import log_memory_metrics, stop_mem_log

from gpu_gui import out_gpu

from cpu_procs_gui import out_cpu
from i_o_gui import out_disk_io
from memory_gui import out_memory

# Logging control functions
def start_all_logs():
    # Create threads for all logging functions
    cpu_thread = threading.Thread(target=log_cpu, daemon=True)
    gpu_thread = threading.Thread(target=log_gpu_stats, daemon=True)
    io_thread = threading.Thread(target=log_io_stats, daemon=True)
    memory_thread = threading.Thread(target=log_memory_metrics, daemon=True)

    # Start the threads
    cpu_thread.start()
    gpu_thread.start()
    io_thread.start()
    memory_thread.start()

    print("[INFO] All logging threads started.")


def stop_all_logs():
    # Call stopping functions directly
    stop_cpu()
    stop_gpu_log()
    stop_io_log()
    stop_mem_log()
    print("[INFO] All logging processes stopped.")


# Main application window
root = Tk()
root.title("Linux System Resource Monitor")
root.minsize(width=1366, height=768)

# Set a background image
try:
    background_image = Image.open("/home/sasi-1902/Documents/Programming/Os_prj/cummulation/background.jpeg") 
    background_photo = ImageTk.PhotoImage(background_image)

    # Add the image to a Label widget
    background_label = Label(root, image=background_photo)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

except FileNotFoundError:
    print("Error: Background image not found. Please check the file path.")
    exit()

# Start logging when the main window is opened
start_all_logs()

# Outer Frame for White Border
borderFrame = Frame(root, bg="white", bd=2)  # White border with 2px thickness
borderFrame.place(relx=0.2, rely=0.1, relwidth=0.6, relheight=0.16)

# Inner Frame for Heading Background
headingFrame1 = Frame(borderFrame, bg="black")  # Black background inside the white border
headingFrame1.place(relx=0, rely=0, relwidth=1, relheight=1)

# Heading Label
headingLabel = Label(
    headingFrame1,
    text="Welcome to\nLinux System Resource Monitor",
    bg="black",
    fg='white',
    font=('Courier', 15)
)
headingLabel.place(relx=0, rely=0, relwidth=1, relheight=1)

# Buttons for individual resource windows
btn1 = Button(root, text="CPU", font=('Helvetica', 10, 'bold'), bg='white', fg='black', command=out_cpu)
btn1.place(relx=0.28, rely=0.4, relwidth=0.45, relheight=0.1)

btn2 = Button(root, text="Memory", font=('Helvetica', 10, 'bold'), bg='white', fg='black', command=out_memory)
btn2.place(relx=0.28, rely=0.5, relwidth=0.45, relheight=0.1)

btn3 = Button(root, text="GPU", font=('Helvetica', 10, 'bold'), bg='white', fg='black', command=out_gpu)
btn3.place(relx=0.28, rely=0.6, relwidth=0.45, relheight=0.1)

btn4 = Button(root, text="Input Output Status", font=('Helvetica', 10, 'bold'), bg='white', fg='black',  command=out_disk_io)
btn4.place(relx=0.28, rely=0.7, relwidth=0.45, relheight=0.1)

# Ensure logging stops and files are deleted when the main window is closed
def on_main_close():
    # Stop all logging threads
    stop_all_logs()

    # List of files to delete
    files_to_delete = [
        "/home/sasi-1902/Documents/Programming/Os_prj/cummulation/csvs/cpu_metrics.csv",
        "/home/sasi-1902/Documents/Programming/Os_prj/cummulation/csvs/gpu_monitoring_log.csv",
        "/home/sasi-1902/Documents/Programming/Os_prj/cummulation/csvs/iotop_pidstat_log.csv",
        "/home/sasi-1902/Documents/Programming/Os_prj/cummulation/csvs/memory_metrics.csv",
        "/home/sasi-1902/Documents/Programming/Os_prj/cummulation/csvs/vmstat_metrics.csv",
    ]

    # Delete each file
    for file_path in files_to_delete:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"[INFO] Deleted file: {file_path}")
            else:
                print(f"[INFO] File not found (skipping): {file_path}")
        except Exception as e:
            print(f"[ERROR] Could not delete file {file_path}: {e}")

    #Close the main window
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_main_close)

# Run the application
root.mainloop()
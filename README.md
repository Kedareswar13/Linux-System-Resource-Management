# Linux System Resource Monitor

A desktop GUI application for Linux that continuously logs and visualizes system resource usage in real time. It collects metrics for CPU, Memory, GPU, and Disk I/O using native Linux tools and displays live dashboards with plots and tables.

- Single unified app to monitor CPU cores, processes, memory, GPU (NVIDIA/AMD/Intel), and disk I/O.
- Uses lightweight native tools (mpstat, vmstat, free, iotop, pidstat, vendor GPU tools) for accurate, low-overhead measurements.
- Stores data as CSV for easy offline analysis or integration with other tools.
- Simple Tkinter GUI with live updates and quick plots via matplotlib.


## Why this project?

- Minimal overhead and high fidelity: relies on standard Linux tools optimized for performance rather than heavy background agents.
- Vendor-agnostic GPU support: works with NVIDIA, AMD, and Intel GPUs when relevant tools are present.
- Local-first and transparent: logs are plain CSV files you own and can analyze with any tool.
- Extensible architecture: decoupled backends (loggers) and GUIs (readers/visualizers) make it easy to add new metrics or new visualizations.
- One-click dashboards: separate dedicated views for CPU, Memory, GPU, and Disk I/O.


## Project structure

```
Linux System Resource Management/
├── background.jpeg                 # App background image (displayed in main window)
├── code/
│   ├── main.py                     # App entry point and main window
│   ├── cpu_procs_backend.py        # Logs CPU core and vmstat metrics to CSV
│   ├── cpu_procs_gui.py            # CPU dashboard: tables + average CPU plot
│   ├── memory_backend.py           # Logs memory and swap metrics to CSV
│   ├── memory_gui.py               # Memory dashboard + multiple plots
│   ├── gpu_backend.py              # Logs GPU metrics (NVIDIA/AMD/Intel) to CSV
│   ├── gpu_gui.py                  # GPU dashboard + utilization plot
│   ├── i_o_backend.py              # Logs iotop + pidstat output to CSV
│   └── i_o_gui.py                  # Disk I/O dashboard + trends/spikes plots
└── csvs/                           # CSV outputs (created at runtime)
```

Backends write to CSV files every second. GUI modules read those CSVs and render live-updating tables and plots.


## How it works (high-level architecture)

- `code/main.py`
  - Launches a Tkinter main window with buttons for CPU, Memory, GPU, Disk I/O dashboards.
  - Starts four background threads that log metrics continuously:
    - `cpu_procs_backend.log_cpu()`
    - `memory_backend.log_memory_metrics()`
    - `gpu_backend.log_gpu_stats()`
    - `i_o_backend.log_io_stats()`
  - On exit, signals loggers to stop and attempts to delete the CSV files.

- CPU (`cpu_procs_backend.py`, `cpu_procs_gui.py`)
  - Uses `mpstat -P ALL` for per-core User/System/Idle times and `vmstat` for system-wide process/CPU stats.
  - CSVs: `cpu_metrics.csv` and `vmstat_metrics.csv`
  - GUI renders core-wise averages and latest vmstat row, plus a plot of average CPU usage over time.

- Memory (`memory_backend.py`, `memory_gui.py`)
  - Uses `/proc/meminfo` and `free -m` to get memory and swap stats.
  - CSV: `memory_metrics.csv`
  - GUI includes multiple plots: usage over time, swap trends, distribution (pie), efficiency over time.

- GPU (`gpu_backend.py`, `gpu_gui.py`)
  - Detects available GPUs and logs metrics via vendor tools:
    - NVIDIA: `nvidia-smi` (utilization, memory, temperature, power)
    - AMD: `rocm-smi`
    - Intel: `intel-gpu-top -J`
  - CSV: `gpu_monitoring_log.csv`
  - GUI: live table and GPU Utilization plot.

- Disk I/O (`i_o_backend.py`, `i_o_gui.py`)
  - Runs `iotop` and `pidstat` and writes cleaned lines to CSV.
  - CSV: `iotop_pidstat_log.csv`
  - GUI: totals trends (line) and spikes (bar) plots.


## Requirements

- OS: Linux (GUI uses Tkinter; not intended for headless-only servers without a display)
- Python: 3.8+
- Python packages:
  - `Pillow` (for image background)
  - `matplotlib`
  - `tkinter` (usually included with Python on many distros via `python3-tk` package)
- System packages/tools:
  - `sysstat` (provides `mpstat` and `pidstat`)
  - `procps` (provides `vmstat`, `free`)
  - `iotop` (requires CAP_SYS_ADMIN or run with sudo)
  - `nvidia-smi` (NVIDIA), `rocm-smi` (AMD), `intel-gpu-tools` (Intel)

### Install on Debian/Ubuntu

```bash
sudo apt update
# Python GUI dependency
sudo apt install -y python3-tk
# Core CLI tools
sudo apt install -y sysstat procps iotop intel-gpu-tools
# Optional: vendor-specific
# NVIDIA utils are typically installed with driver; if not:
# sudo apt install -y nvidia-utils-535   # adjust version to your driver
# AMD ROCm tools:
# sudo apt install -y rocm-smi

# Enable sysstat if needed (for mpstat/pidstat sampling service)
sudo systemctl enable --now sysstat || true

# Python packages
python3 -m pip install --upgrade pip
pip install pillow matplotlib
```

Arch/Manjaro (example):
```bash
sudo pacman -S --needed tk sysstat procps-ng iotop intel-gpu-tools
pip install pillow matplotlib
```

Fedora (example):
```bash
sudo dnf install -y python3-tkinter sysstat procps-ng iotop intel-gpu-tools
pip install pillow matplotlib
```


## Configuration (important)

The repository may contain absolute paths from a developer machine in older commits. Ensure all paths use project-relative locations or environment variables.

- Background image path in `code/main.py` should be relative to the repo root:
  - `background_image = Image.open("background.jpeg")`
- CSV paths in the following files should point to the `csvs/` directory using relative paths:
  - `code/cpu_procs_backend.py` (CPU_LOG_FILE, VMSTAT_LOG_FILE)
  - `code/cpu_procs_gui.py` (CPU_CORE_CSV, PROCESS_CSV)
  - `code/memory_backend.py` (MEMORY_LOG_FILE)
  - `code/memory_gui.py` (MEMORY_CSV)
  - `code/gpu_backend.py` (output_file)
  - `code/gpu_gui.py` (GPU_CSV_FILE)
  - `code/i_o_backend.py` (output_file)
  - `code/i_o_gui.py` (DISK_IO_CSV)

Recommended convention (relative to repo root):
```
CSV_DIR = os.path.join(os.path.dirname(__file__), "..", "csvs")
```
and then build filenames with `os.path.join(CSV_DIR, "cpu_metrics.csv")` etc.

### About sudo and credentials

`code/i_o_backend.py` currently pipes a hardcoded sudo password to run `iotop` and `pidstat`:
- This is insecure. Do not commit passwords to code.
- Safer alternatives:
  - Configure `/etc/sudoers` to allow your user to run specific commands without a password, e.g.:
    ```
    youruser ALL=(ALL) NOPASSWD: /usr/sbin/iotop, /usr/bin/pidstat
    ```
    Then invoke without passing a password.
  - Or run the application with the necessary capabilities (e.g., give iotop CAP_SYS_ADMIN) depending on your distro policy.
  - Or skip I/O collection if not privileged.

Update `sudo_password` handling accordingly or prompt for it at runtime (not stored in code).


## Running the app

1. Ensure dependencies are installed and paths adjusted as per Configuration.
2. Start the application from the repo root:

```bash
python3 code/main.py
```

3. The main window appears with buttons:
   - CPU
   - Memory
   - GPU
   - Input Output Status

4. Clicking a button opens the respective dashboard. Log threads start automatically when the app launches. Closing the main window stops logging and attempts to remove the CSVs under `csvs/`.


## Troubleshooting

- Blank tables/plots:
  - Ensure CSV files are being written under `csvs/`.
  - Check console logs for missing tools (e.g., `mpstat`, `vmstat`, `nvidia-smi`).
- GPU shows "No GPU Detected":
  - Verify vendor tool installation and permissions.
  - Laptops with hybrid graphics may need proper drivers.
- Disk I/O errors or empty data:
  - `iotop` often requires root or proper capabilities; try running the app with sudo or configure sudoers as above.
- Tkinter not found:
  - Install `python3-tk` (Debian/Ubuntu) or the equivalent for your distro.
- Background image not found:
  - Ensure `background.jpeg` exists at the repo root and the path in `main.py` is relative.


## Roadmap / Ideas

- Replace absolute paths with project-relative paths and environment configuration.
- Introduce a configuration file (e.g., `config.yaml`) for paths and feature toggles.
- Add packaging and a launcher script / desktop entry.
- Add alerts for threshold breaches (e.g., CPU > 90% for N seconds).
- Add network I/O dashboard.
- Export plots as images.


## License

Add your preferred license (e.g., MIT) here.

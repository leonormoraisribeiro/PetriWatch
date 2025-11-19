"""
petriwatch.py
Timelapse para Raspberry Pi 4B + HQ Camera.

- Preview com rpicam-hello/libcamera-hello (Popen)
- Captura periódica com rpicam-still/libcamera-still (subprocess.run)
- GUI Tkinter simples
- Intervalo, resolução, total de fotos, nome da experiência
- Contador e barra de progresso
- Guarda em ~/Pictures/Timelapses/<experiencia>_<timestamp>/

Dependências:
    sudo apt install -y python3-pil
"""

import os
import json
import time
import threading
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Tuple

from tkinter import *
from tkinter import ttk, messagebox

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None


def get_camera_command(base: str) -> str:
    """Returns the correct camera command depending on the OS version"""
    rpi_cmd = f"rpicam-{base}"
    if shutil.which(rpi_cmd):
        return rpi_cmd
    lib_cmd = f"libcamera-{base}"
    if shutil.which(lib_cmd):
        return lib_cmd
    raise RuntimeError(f"No camera command found for '{base}.")

def is_raspberry_pi() -> bool:
    try:
        with open("/proc/device-tree/model", "r") as f:
            return "Raspberry Pi" in f.read()
    except FileNotFoundError:
        return False

def sanitize_experiment_name(name: str) -> str:
    name = (name or "").strip()
    if not name:
        return "experiment"
    for ch in '<>:"/\\|?*':
        name = name.replace(ch, "_")
    return "_".join(name.split())[:80]

def now_human() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def iso_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# App

class TimelapseApp:
    INTERVALS_MIN = [1, 2, 5, 10, 15, 20, 30]
    RESOLUTIONS = {
        "4056 x 3040": (4056, 3040),
        "2028 x 1520": (2028, 1520),
        "1014 x 760": (1014, 760),
    }

    def __init__(self):
        self.root = Tk()
        self.root.title("PetriWatch Timelapse")
        self.root.geometry("900x640")
        from PIL import Image, ImageTk
        logo_img = Image.open("logo2.png")        
        logo_img = logo_img.resize((240, 110))    
        self.logo_tk = ImageTk.PhotoImage(logo_img)
        self.logo_label = ttk.Label(self.root, image=self.logo_tk)
        self.logo_label.image = self.logo_tk      
        self.logo_label.place(relx=1.0, anchor="ne", x=-20, y=-10)

        self.style = ttk.Style()

        # uniform styles
        bg_color = self.root.cget("bg")
        self.root.option_add('*TLabel.background', bg_color)
        self.root.option_add('*TFrame.background', bg_color)
        self.root.option_add('*TLabelframe.background', bg_color)
        self.root.option_add('*TButton.padding', 4)

        # state
        self.preview_process = None
        self.acq_thread = None
        self.acq_cancel = threading.Event()
        self.acq_running = False

        # variables
        self.var_interval = StringVar(value="5")
        self.var_res = StringVar(value="2028 x 1520")
        self.var_total = StringVar(value="144")
        self.var_exp = StringVar(value="timelapse")

        self._build_gui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # GUI

    def _build_gui(self):
        ttk.Label(self.root, text="Interval (min):").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        ttk.OptionMenu(self.root, self.var_interval, self.var_interval.get(), *[str(v) for v in self.INTERVALS_MIN]).grid(row=0, column=1, sticky=W, padx=5, pady=8)

        ttk.Label(self.root, text="Resolution:").grid(row=0, column=2, sticky="w", padx=10, pady=8)
        ttk.OptionMenu(self.root, self.var_res, self.var_res.get(), *list(self.RESOLUTIONS.keys())).grid(row=0, column=3, sticky=W, padx=5, pady=8)

        ttk.Label(self.root, text="Number of photos:").grid(row=1, column=0, sticky="w", padx=10, pady=8)
        self.ent_total = ttk.Entry(self.root, textvariable=self.var_total, width=10)
        self.ent_total.grid(row=1, column=1, sticky=W, padx=5, pady=8)
        self.ent_total.bind("<KeyRelease>", self._only_ints)

        ttk.Label(self.root, text="Experiment name:").grid(row=1, column=2, sticky="w", padx=10, pady=8)
        ttk.Entry(self.root, textvariable=self.var_exp, width=24).grid(row=1, column=3, sticky=W, padx=5, pady=8)

        # Preview
        preview_frame = ttk.Frame(self.root)
        preview_frame.grid(row=2, column=0, columnspan=4, sticky="w", padx=10, pady=8)
        self.btn_preview_start = ttk.Button(preview_frame, text="Open Preview", command=self.start_preview)
        self.btn_preview_start.pack(side="left", padx=5, pady=4)
        self.btn_preview_stop = ttk.Button(preview_frame, text="Close Preview", command=self.stop_preview)
        self.btn_preview_stop.pack(side="left", padx=10, pady=4)

        # Main control
        run_frame = ttk.Frame(self.root)
        run_frame.grid(row=3, column=0, columnspan=4, sticky="w", padx=10, pady=8)
        self.btn_start = ttk.Button(run_frame, text="Start Timelapse", command=self.start_acquisition)
        self.btn_start.pack(side="left", padx=5, pady=4)
        self.btn_stop = ttk.Button(run_frame, text="Stop", command=self.stop_acquisition, state="disabled")
        self.btn_stop.pack(side="left", padx=10, pady=4)

        # Progress
        prog_frame = ttk.Frame(self.root)
        prog_frame.grid(row=4, column=0, columnspan=4, sticky="we", padx=10, pady=8)
        self.prog = ttk.Progressbar(prog_frame, orient="horizontal", length=400, mode="determinate", maximum=100)
        self.prog.pack(side="left", padx=5)
        self.lbl_prog = ttk.Label(prog_frame, text="Waiting…")
        self.lbl_prog.pack(side="left", padx=12)

        # Log
        ttk.Label(self.root, text="Messages:").grid(row=5, column=0, columnspan=4, sticky="w", padx=10)
        self.txt_log = Text(self.root, height=14, width=110)
        self.txt_log.grid(row=6, column=0, columnspan=4, sticky="nsew", padx=10, pady=8)
        self.root.grid_rowconfigure(6, weight=1)
        self.root.grid_columnconfigure(3, weight=1)
        self._log(f"{now_human()}  Ready. Configure and click Start Timelapse.")

    def _only_ints(self, _e=None):
        v = self.var_total.get()
        if v and not v.isdigit():
            self.var_total.set("".join(ch for ch in v if ch.isdigit()))

    # Preview

    def start_preview(self):
        if self.preview_process and self.preview_process.poll() is None:
            self._log("Preview is already open.")
            return
        try:
            cmd = [get_camera_command("hello"), "-t", "0", "--hflip", "--vflip"]
            self.preview_process = subprocess.Popen(cmd)
            self._log("Preview started.")
        except Exception as e:
            messagebox.showerror("Error", f"Error starting preview\n{e}")
            self._log(f"ERRO preview: {e}")

    def stop_preview(self):
        if self.preview_process and self.preview_process.poll() is None:
            try:
                self.preview_process.terminate()
                self.preview_process.wait(timeout=2)
            except Exception:
                pass
            finally:
                self.preview_process = None
                self._log("Preview closed.")
        else:
            self._log("Preview was already closed.")

    # Acquisition
    def start_acquisition(self):
        if self.acq_running:
            return

        try:
            total = int(self.var_total.get())
            if total <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Invalid number of photos.")
            return

        try:
            interval_min = int(self.var_interval.get())
            if interval_min <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Invalid interval.")
            return

        try:
            res = self.RESOLUTIONS[self.var_res.get()]
        except KeyError:
            messagebox.showerror("Error", "Invalid resolution.")
            return

        exp_name = sanitize_experiment_name(self.var_exp.get())
        base_dir = Path.home() / "Pictures" / "Timelapses"
        run_dir = base_dir / f"{exp_name}_{iso_stamp()}"
        run_dir.mkdir(parents=True, exist_ok=True)

        settings = {
            "experiment": exp_name,
            "created_at": now_human(),
            "interval_minutes": interval_min,
            "resolution": {"width": res[0], "height": res[1]},
            "total_photos": total,
            "folder": str(run_dir),
        }
        with open(run_dir / "settings.json", "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)

        self.acq_cancel.clear()
        self.acq_running = True
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.prog.config(value=0, maximum=total)
        self.lbl_prog.config(text="Starting…")
        self.stop_preview()

        self.acq_thread = threading.Thread(
            target=self._worker,
            args=(total, interval_min * 60, res, run_dir),
            daemon=True)
        self.acq_thread.start()

    def stop_acquisition(self):
        if not self.acq_running:
            return
        if messagebox.askyesno("Stop", "Do you want to stop the timelapse?"):
            self.acq_cancel.set()
            self._log("Stop requested…")

    # --        

    def _worker(self, total, interval_sec, res, run_dir: Path):
        log_path = run_dir / "run.log"
        with open(log_path, "a", buffering=1, encoding="utf-8") as flog:
            flog.write(f"{now_human()}  Start acquisition of {total} photos\n")
            start = time.monotonic()
            next_shot = start

            for i in range(1, total + 1):
                if self.acq_cancel.is_set():
                    self._log_threadsafe("Acquisition cancelled.")
                    break

                while True:
                    if self.acq_cancel.is_set():
                        break
                    now = time.monotonic()
                    remaining = next_shot - now
                    if remaining <= 0:
                        break
                    time.sleep(min(0.5, remaining))
                if self.acq_cancel.is_set():
                    break

                filename = f"{iso_stamp()}_{i:05d}.jpg"
                out_path = run_dir / filename
                cmd = [get_camera_command("still"), "-o", str(out_path), "-n",
                       "--width", str(res[0]), "--height", str(res[1]),
                       "--hflip", "--vflip"]

                t0 = time.monotonic()
                try:
                    subprocess.run(cmd, check=True)
                    elapsed = time.monotonic() - t0
                    self._log_threadsafe(f"{now_human()}  Captured {filename} ({elapsed:.2f}s)")
                    flog.write(f"{now_human()}  OK  {filename}  {elapsed:.2f}s\n")
                except subprocess.CalledProcessError as e:
                    self._log_threadsafe(f"ERROR capturing {filename}: {e}")
                    flog.write(f"{now_human()}  ERROR  {filename}  {e}\n")

                self._progress_threadsafe(i, total)
                next_shot = start + i * interval_sec

            flog.write(f"{now_human()}  End of acquisition\n")
            self.root.after(0, self._worker_finished_ui)

    # --

    def _log_threadsafe(self, msg):
        self.root.after(0, lambda: self._log(msg))

    def _progress_threadsafe(self, current, total):
        self.root.after(0, lambda: self._set_progress(current, total))

    def _worker_finished_ui(self):
        self.acq_running = False
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        if self.prog["value"] >= self.prog["maximum"]:
            self.lbl_prog.config(text="Finished.")
        else:
            self.lbl_prog.config(text="Stopped.")

    def _set_progress(self, current, total):
        self.prog.config(value=current, maximum=total)
        self.lbl_prog.config(text=f"{current}/{total} photos taken.")

    def _log(self, msg: str):
        self.txt_log.insert(END, msg + "\n")
        self.txt_log.see(END)

    # Close

    def _on_close(self):
        if self.acq_running:
            if not messagebox.askyesno("Exit", "Acquisition in progress. Stop and exit?"):
                return
            self.acq_cancel.set()
            time.sleep(0.3)
        self.stop_preview()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


# Main

def main():
    if not is_raspberry_pi():
        print("Warning: this script is intended to run on a Raspberry Pi.")
    app = TimelapseApp()
    app.run()

if __name__ == "__main__":
    main()

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from core.converter import convert_images
import threading
import os
import platform
import subprocess
from utils.logger import logger
import time

def format_time(seconds):
    if seconds < 60:
        return f"{seconds:.0f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"

def run_app():
    root = tk.Tk()
    root.title("Bulk Image Converter")
    root.geometry("400x320")
    root.minsize(400, 320)
    root.resizable(False, False)

    input_var = tk.StringVar()
    output_var = tk.StringVar()
    format_var = tk.StringVar(value="webp")
    width_var = tk.StringVar(value="1024")
    quality_var = tk.StringVar(value="75")
    status_var = tk.StringVar(value="Ready")
    time_remaining_var = tk.StringVar(value="")

    def browse_input():
        path = filedialog.askdirectory()
        if path:
            input_var.set(path)
            logger.info(f"Selected input directory: {path}")

    def browse_output():
        path = filedialog.askdirectory()
        if path:
            output_var.set(path)
            logger.info(f"Selected output directory: {path}")

    def open_output_folder(path):
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])

    def threaded_conversion():
        try:
            logger.info("Starting conversion process")
            convert_images(
                input_var.get(),
                output_var.get(),
                format_var.get(),
                int(width_var.get()),
                int(quality_var.get()),
                progress_callback=update_progress
            )
            progress_bar["value"] = 100
            start_btn["text"] = "Done"
            status_var.set("Conversion completed successfully!")
            logger.info("Conversion completed successfully")
            messagebox.showinfo("Success", "Conversion completed successfully!")
            open_output_folder(output_var.get())
        except Exception as e:
            error_msg = f"Error during conversion:\n{str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Error", error_msg)
            start_btn["text"] = "Start Conversion"
        finally:
            start_btn["state"] = "normal"
            time_remaining_var.set("")

    def start_conversion():
        start_btn["state"] = "disabled"
        start_btn["text"] = "Converting..."
        progress_bar["value"] = 0
        status_var.set("Starting conversion...")
        threading.Thread(target=threaded_conversion, daemon=True).start()

    def validate_numeric(value):
        return value.isdigit() or value == ""

    def check_all_fields(*args):
        valid = True

        if not width_var.get().isdigit():
            width_entry.configure(style="Error.TEntry")
            valid = False
        else:
            width_entry.configure(style="TEntry")

        if quality_var.get().isdigit():
            q = int(quality_var.get())
            if q < 1:
                quality_var.set("1")
            elif q > 100:
                quality_var.set("100")
            quality_entry.configure(style="TEntry")
        else:
            quality_entry.configure(style="Error.TEntry")
            valid = False

        if not input_var.get() or not output_var.get():
            valid = False

        start_btn["state"] = "normal" if valid else "disabled"

    def update_progress(percent, estimated_remaining):
        progress_bar["value"] = percent
        status_var.set(f"Processing: {percent}%")
        if estimated_remaining > 0:
            time_remaining_var.set(f"Estimated time remaining: {format_time(estimated_remaining)}")
        root.update_idletasks()

    style = ttk.Style()
    style.configure("TEntry", foreground="black")
    style.configure("Error.TEntry", foreground="black", relief="solid", borderwidth=1)

    frame = ttk.Frame(root, padding=10)
    frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frame, text="Input folder:").grid(row=0, column=0, sticky="w")
    input_entry = ttk.Entry(frame, textvariable=input_var)
    input_entry.grid(row=1, column=0, columnspan=2, sticky="we", pady=2)
    ttk.Button(frame, text="Browse", command=browse_input).grid(row=1, column=2, padx=5)

    ttk.Label(frame, text="Output folder:").grid(row=2, column=0, sticky="w", pady=(10, 0))
    output_entry = ttk.Entry(frame, textvariable=output_var)
    output_entry.grid(row=3, column=0, columnspan=2, sticky="we", pady=2)
    ttk.Button(frame, text="Browse", command=browse_output).grid(row=3, column=2, padx=5)

    vcmd_numeric = (root.register(validate_numeric), '%P')

    options_frame = ttk.Frame(frame)
    options_frame.grid(row=4, column=0, columnspan=3, pady=15)

    ttk.Label(options_frame, text="Format:").grid(row=0, column=0, padx=5)
    ttk.Combobox(
        options_frame,
        textvariable=format_var,
        values=["webp", "jpeg", "png"],
        width=6,
        state="readonly"
    ).grid(row=0, column=1, padx=5)

    ttk.Label(options_frame, text="Max width:").grid(row=0, column=2, padx=5)
    width_entry = ttk.Entry(options_frame, textvariable=width_var, width=6, validate="key", validatecommand=vcmd_numeric)
    width_entry.grid(row=0, column=3, padx=5)

    ttk.Label(options_frame, text="Quality:").grid(row=0, column=4, padx=5)
    quality_entry = ttk.Entry(options_frame, textvariable=quality_var, width=6, validate="key", validatecommand=vcmd_numeric)
    quality_entry.grid(row=0, column=5, padx=5)

    progress_bar = ttk.Progressbar(frame, orient="horizontal", mode="determinate", maximum=100)
    progress_bar.grid(row=5, column=0, columnspan=3, sticky="we", pady=(5, 5))

    status_label = ttk.Label(frame, textvariable=status_var)
    status_label.grid(row=6, column=0, columnspan=3, sticky="w", pady=(5, 0))

    time_remaining_label = ttk.Label(frame, textvariable=time_remaining_var)
    time_remaining_label.grid(row=7, column=0, columnspan=3, sticky="w", pady=(0, 5))

    start_btn = ttk.Button(frame, text="Start Conversion", command=start_conversion)
    start_btn.grid(row=8, column=0, columnspan=3, pady=10)
    start_btn["state"] = "disabled"

    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)

    input_var.trace_add("write", check_all_fields)
    output_var.trace_add("write", check_all_fields)
    format_var.trace_add("write", check_all_fields)
    width_var.trace_add("write", check_all_fields)
    quality_var.trace_add("write", check_all_fields)

    root.mainloop()

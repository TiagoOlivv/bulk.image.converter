from tkinter import filedialog

def select_folder(var):
    folder = filedialog.askdirectory()
    if folder:
        var.set(folder)

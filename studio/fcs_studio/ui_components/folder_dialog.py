import subprocess
import sys


def select_folder(initial_dir: str = "") -> str | None:
    """
    Select Folder

    Open a new thread with a tkinter filedialog for selecting the data directory.

    Parameters
    ----------
    initial_dir: str, default=""
        Directory that opens when the filedialog is generated.

    Returns
    -------
    directory: str | None

    """
    code = (
        "import tkinter as tk\n"
        "from tkinter import filedialog\n"
        "root = tk.Tk()\n"
        "root.withdraw()\n"
        "root.attributes('-topmost', True)\n"
        f"print(filedialog.askdirectory(title='Select Directory', initialdir={initial_dir!r}) or '')\n"
        "root.destroy()\n"
    )
    result = subprocess.run([sys.executable, "-c", code], check=False, capture_output=True, text=True)
    return result.stdout.strip() or None
# main.py
import tkinter as tk
from GUI_MP import FuzzyGUI

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x500")
    app = FuzzyGUI(root)
    root.mainloop()
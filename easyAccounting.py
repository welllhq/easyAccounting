# easyAccounting.py
import tkinter as tk
from ui import AccountingApp

def main():
    root = tk.Tk()
    app = AccountingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

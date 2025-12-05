from src.app import CalibApp
import tkinter as tk

root = tk.Tk()
app = CalibApp(root)
# Get the text of the currently selected tab
selected = app.notebook.tab(app.notebook.select(), 'text')
print(selected)
root.destroy()

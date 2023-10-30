import tkinter as tk
from tkinter import font as tkFont

root = tk.Tk()

fonts = list(tkFont.families())
fonts.sort()

display = tk.Listbox(root)
display.pack(fill=tk.BOTH, expand=tk.YES, side=tk.LEFT)

scroll = tk.Scrollbar(root)
scroll.pack(side=tk.RIGHT, fill=tk.Y, expand=tk.NO)

scroll.configure(command=display.yview)
display.configure(yscrollcommand=scroll.set)

for item in fonts:
    display.insert(tk.END, item)

root.mainloop()

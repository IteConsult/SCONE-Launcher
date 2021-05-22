import tkinter as tk
from tkinter import ttk

root = tk.Tk()

# s = ttk.Style()
# s.configure('TButton', background = 'blue', foreground = 'blue', font = ('Poppins', 12)
# s.configure('CustomClass.TButton', background = 'red')

# btn1 = ttk.Button(root, text = 'test', style = 'CustomClass.TButton')
# btn1 = ttk.Button(root, text = 'test')
# btn1.pack()

# btn2 = ttk.Button(root, text = 'test2')
# btn2.pack()

s = ttk.Style()
s.configure('TButton', font=('Poppins',10))
btn = ttk.Button(root, text = 'test')
btn.pack()

root.mainloop()
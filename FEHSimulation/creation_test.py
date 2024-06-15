import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry('800x600')

# Create left and right frames
left_frame = tk.Frame(root, bg='#14121a')
right_frame = tk.Frame(root, bg='#4a4657')

left_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
right_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

label1 = tk.Label(left_frame, text="TEST 1")
label2 = tk.Label(right_frame, text="TEST 2")

label1.pack(padx=10, pady=10)
label2.pack(padx=10, pady=10)

#left_frame.grid(row=0, column=0, sticky='ns')
#right_frame.grid(row=0, column=1, sticky='nsew')

# Left frame widgets
#image_label = tk.Label(left_frame, text='Image placeholder', height=10, width=20, bg='white')
#image_label.pack(padx=10, pady=10)#grid(row=0, column=0, padx=10, pady=10)



label_text = tk.Label(left_frame, text='Lv. 40 + 10\n Flowers + 20', height=2, width = 20)
label_text.grid(row=1, column=0, padx=10, pady=10)

two_line_text = tk.Label(left_frame, text="Sol Badguy\nThe Guilty Gear", height=2, width=20)
two_line_text.grid(row=2, column=0, padx=10, pady=10)

five_line_text = tk.Label(left_frame, text="HP: 40\nAtk: 40\nSpd: 40\nDef: 40\nRes: 40", height=5, width=16, font="Helvetica 12")
five_line_text.grid(row=3, column=0, padx=10, pady=10)

# Right frame widgets
names = ["Unit", "Rarity", "Merge", "Asset", "Blessing", "S-Support", "Weapon", "Refine", "Assist", "Special", "Emblem"]
names2 = ["Resplendent?", "Level", "DFlowers", "Flaw", "Asc. Asset", "A-Support", "A Skill", "B Skill", "C Skill", "Sacred Seal", "X Skill"]

for row in range(11):
    tk.Label(right_frame, text=names[row]).grid(row=row, column=0, padx=10, pady=5)
    combo1 = ttk.Combobox(right_frame)
    combo1.grid(row=row, column=1, padx=10, pady=12)

    tk.Label(right_frame, text=names2[row]).grid(row=row, column=2, padx=10, pady=5)
    combo2 = ttk.Combobox(right_frame)
    combo2.grid(row=row, column=3, padx=10, pady=12)

tk.Label(right_frame, text="Emblem Merge").grid(row=row+1, column=0, padx=10, pady=5)
combo1 = ttk.Combobox(right_frame)
combo1.grid(row=row+1, column=1, padx=10, pady=12)

combo1['values'] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

root.mainloop()
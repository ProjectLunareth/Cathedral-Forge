# legend_overlay.py
from tkinter import LabelFrame, Label
from cosmos_layer import describe_phase

def draw_phase_legend(parent, recursion_level: int):
    frame = LabelFrame(parent, text="SSC Phase Info", font=("Helvetica", 13))
    frame.pack(side='right', fill='y', padx=10, pady=10)
    legend_text = describe_phase(recursion_level)
    label = Label(frame, text=legend_text, justify="left", font=("Helvetica", 12), wraplength=240)
    label.pack(padx=10, pady=10)
    return frame

# run_all.py

import sys

def main():
    if "--gui" in sys.argv:
        if "--cpu" in sys.argv:
            print("Launching SSC-COSMOS Visualizer (CPU/Tkinter)...")
            from polygon_gui_hlsf import PolygonGUI
            gui = PolygonGUI(center=(0, 0), radius=5, sides=6, levels=1)
            gui.mainloop()
        else:
            print("Launching SSC-COSMOS Visualizer (GPU/VisPy)...")
            from polygon_gui_vispy import PolygonApp
            app = PolygonApp()
            app.run()
    else:
        print("No valid mode selected. Use '--gui [--cpu]' to launch a visualizer.")

if __name__ == "__main__":
    main()

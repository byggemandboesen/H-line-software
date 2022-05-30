import sys
import dearpygui.dearpygui as dpg

# Import callbacks and other stuff
sys.path.append("src/")
from src.ui import parameters

# Run user intereface
def run_ui():
    dpg.create_context()
    dpg.create_viewport(title='H-Line software - By Victor Boesen', width=650, height=500)
    
    # Show window for each parameter category
    parameters.sdrWindow()
    parameters.observerWindow()
    parameters.observationWindow()
    parameters.actionsWindow()

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    print("Launching user interface!")
    run_ui()
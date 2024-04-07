# Diego Aguirre Guerra
import tkinter as tk
from tkinter import ttk
import threading
import time

class PomodoroTimer:
    # Initialize the Pomodoro Timer application
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("600x300")
        self.root.title("Pomodoro Timer")

        # Configure styles for the notebook and buttons
        self.s = ttk.Style()
        self.s.configure("TNotebook.Tab", font=("Ubuntu", 16))
        self.s.configure("TButton", font=("Ubuntu", 16))

        # Setup notebook (tabs) for different timer phases
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", pady=10, expand=True)

        # Create tabs and labels for each timer phase
        self.tab_labels = []
        tab_texts = [("Pomodoro", "25:00"), ("Short Break", "05:00"), ("Long Break", "10:00")]
        for text, time in tab_texts:
            tab = ttk.Frame(self.tabs)
            label = ttk.Label(tab, text=time, font=("Ubuntu", 48))
            label.pack(pady=20)
            self.tabs.add(tab, text=text)
            self.tab_labels.append(label)

        # Setup layout for control buttons
        self.grid_layout = ttk.Frame(self.root)
        self.grid_layout.pack(pady=10)

        # Add control buttons
        self.start_button = ttk.Button(self.grid_layout, text="Start", command=self.start_timer_thread)
        self.start_button.grid(row=0, column=0)
        self.pause_button = ttk.Button(self.grid_layout, text="Pause", command=self.toggle_pause)
        self.pause_button.grid(row=0, column=1)
        self.skip_button = ttk.Button(self.grid_layout, text="Skip", command=self.skip_clock)
        self.skip_button.grid(row=0, column=2)
        self.reset_button = ttk.Button(self.grid_layout, text="Reset", command=self.reset_clock)
        self.reset_button.grid(row=0, column=3)

        # Label to display the number of completed Pomodoros
        self.pomodoro_counter_label = ttk.Label(self.grid_layout, text="Pomodoros: 0", font=("Ubuntu", 16))
        self.pomodoro_counter_label.grid(row=1, column=0, columnspan=4, pady=10)

        # Initialize state variables
        self.pomodoros = 0
        self.paused = False
        self.timer_cancel = threading.Event()
        self.current_phase = 0

        self.root.mainloop()

    # Starts a new timer thread if not already running
    def start_timer_thread(self):
        if hasattr(self, 'timer_thread') and self.timer_thread.is_alive():
            return
        self.timer_cancel.clear()
        self.paused = False
        self.current_phase = self.tabs.index(self.tabs.select())
        self.timer_thread = threading.Thread(target=self.timer_logic)
        self.timer_thread.start()

    # Logic for the timer countdown
    def timer_logic(self):
        durations = [25*60, 5*60, 10*60]  # Duration of each phase in seconds
        duration = durations[self.current_phase]
        for remaining in range(duration, -1, -1):
            if self.timer_cancel.is_set():  # Check if the timer is cancelled
                break
            if self.paused:  # Pause the timer if paused flag is True
                time.sleep(1)
                continue
            mins, secs = divmod(remaining, 60)
            self.update_timer_label(f"{mins:02d}:{secs:02d}")  # Update the timer label
            time.sleep(1)
        else:  # If the loop completes without interruption
            self.root.after(0, self.end_of_timer)

    # Updates the label of the current timer phase
    def update_timer_label(self, text):
        label = self.tab_labels[self.current_phase]
        self.root.after(0, lambda: label.config(text=text))

    # Actions to perform at the end of a timer phase
    def end_of_timer(self):
        self.pomodoros += 1
        self.pomodoro_counter_label.config(text=f"Pomodoros: {self.pomodoros}")
        self.skip_clock()  # Optionally, automatically skip to next phase

    # Toggles the pause state and updates the button text accordingly
    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_button.config(text="Continue" if self.paused else "Pause")

    # Skips the current timer phase and optionally starts the next one
    def skip_clock(self):
        self.timer_cancel.set()
        if hasattr(self, 'timer_thread'):
            self.timer_thread.join()
        next_phase = (self.current_phase + 1) % 3
        self.tabs.select(next_phase)
        self.current_phase = next_phase
        self.start_timer_thread()  # Optionally, start the next phase automatically

    # Resets the timer to the initial state
    def reset_clock(self):
        self.timer_cancel.set()
        if hasattr(self, 'timer_thread'):
            self.timer_thread.join()
        self.pomodoros = 0
        for label in self.tab_labels:
            label.config(text="25:00" if label == self.tab_labels[0] else "05:00" if label == self.tab_labels[1] else "10:00")
        self.pomodoro_counter_label.config(text="Pomodoros: 0")
        self.tabs.select(0)  # Go back to the first tab
        self.current_phase = 0

if __name__ == "__main__":
    PomodoroTimer()

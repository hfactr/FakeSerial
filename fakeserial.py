import serial
import serial.tools.list_ports
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
import time

# Global variables
recording = False
playing = False
recorded_file = ""
record_com_port = ""
play_com_port = ""
loop_playback = False

# Function to list available COM ports
def list_com_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

# Function to read data from the selected COM port and record it to a file with timestamps
def record_data():
    global recording
    try:
        with serial.Serial(record_com_port, 115200, timeout=1) as ser, open(recorded_file, 'w') as file:
            start_time = time.time()
            while recording:
                if ser.in_waiting > 0:
                    data = ser.readline().decode('utf-8').strip()
                    timestamp = time.time() - start_time
                    file.write(f"{timestamp},{data}\n")
                    print(f"Recorded: {data} at {timestamp}")
                    record_terminal.insert(tk.END, f"Recorded: {data} at {timestamp}\n")
                    record_terminal.see(tk.END)
    except serial.SerialException as e:
        messagebox.showerror("Error", f"Failed to read from {record_com_port}: {e}")

# Function to play recorded data from a file to the selected COM port based on timestamps
def play_data():
    global playing
    try:
        with serial.Serial(play_com_port, 115200, timeout=1) as ser:
            while playing:
                with open(recorded_file, 'r') as file:
                    lines = file.readlines()
                start_time = time.time()
                for line in lines:
                    if not playing:
                        break
                    timestamp, data = line.strip().split(',', 1)
                    timestamp = float(timestamp)
                    current_time = time.time() - start_time
                    if timestamp > current_time:
                        time.sleep(timestamp - current_time)
                    ser.write((data + '\n').encode('utf-8'))
                    print(f"Played: {data} at {timestamp}")
                    play_terminal.insert(tk.END, f"Played: {data} at {timestamp}\n")
                    play_terminal.see(tk.END)
                if not loop_playback:
                    break
    except serial.SerialException as e:
        messagebox.showerror("Error", f"Failed to write to {play_com_port}: {e}")
    finally:
        playing = False
        play_button.config(state=tk.NORMAL)
        start_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)
        stop_play_button.config(state=tk.DISABLED)

# Function to start recording
def start_recording():
    global recording, record_com_port
    record_com_port = record_com_var.get()
    if not recording and record_com_port:
        recording = True
        threading.Thread(target=record_data, daemon=True).start()
        start_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.NORMAL)
        play_button.config(state=tk.DISABLED)

# Function to stop recording
def stop_recording():
    global recording
    if recording:
        recording = False
        start_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)
        play_button.config(state=tk.NORMAL)

# Function to start playing
def start_playing():
    global playing, play_com_port
    play_com_port = play_com_var.get()
    if not playing and play_com_port:
        playing = True
        threading.Thread(target=play_data, daemon=True).start()
        play_button.config(state=tk.DISABLED)
        start_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.DISABLED)
        stop_play_button.config(state=tk.NORMAL)

# Function to stop playing
def stop_playing():
    global playing
    if playing:
        playing = False

# Function to select a file
def select_file():
    global recorded_file
    recorded_file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if recorded_file:
        file_label.config(text=f"File: {recorded_file}")
        start_button.config(state=tk.NORMAL)
        play_button.config(state=tk.NORMAL)

# Function to toggle loop playback
def toggle_loop():
    global loop_playback
    loop_playback = loop_var.get()

# Create the GUI
root = tk.Tk()
root.title("Serial Port Recorder and Player")

file_label = tk.Label(root, text="No file selected")
file_label.pack(pady=5)

select_file_button = tk.Button(root, text="Select File", command=select_file)
select_file_button.pack(pady=5)

record_com_label = tk.Label(root, text="Record COM Port")
record_com_label.pack(pady=5)

record_com_var = tk.StringVar(root)
record_com_var.set("Select COM Port")
record_com_menu = tk.OptionMenu(root, record_com_var, *list_com_ports())
record_com_menu.pack(pady=5)

play_com_label = tk.Label(root, text="Play COM Port")
play_com_label.pack(pady=5)

play_com_var = tk.StringVar(root)
play_com_var.set("Select COM Port")
play_com_menu = tk.OptionMenu(root, play_com_var, *list_com_ports())
play_com_menu.pack(pady=5)

start_button = tk.Button(root, text="Start Recording", command=start_recording, state=tk.DISABLED)
start_button.pack(pady=5)

stop_button = tk.Button(root, text="Stop Recording", command=stop_recording, state=tk.DISABLED)
stop_button.pack(pady=5)

play_button = tk.Button(root, text="Play", command=start_playing, state=tk.DISABLED)
play_button.pack(pady=5)

stop_play_button = tk.Button(root, text="Stop Playing", command=stop_playing, state=tk.DISABLED)
stop_play_button.pack(pady=5)

loop_var = tk.BooleanVar()
loop_checkbox = tk.Checkbutton(root, text="Loop Playback", variable=loop_var, command=toggle_loop)
loop_checkbox.pack(pady=5)

record_terminal_label = tk.Label(root, text="Recording Terminal")
record_terminal_label.pack(pady=5)

record_terminal = tk.Text(root, height=10, width=50)
record_terminal.pack(pady=5)

play_terminal_label = tk.Label(root, text="Playback Terminal")
play_terminal_label.pack(pady=5)

play_terminal = tk.Text(root, height=10, width=50)
play_terminal.pack(pady=5)

root.mainloop()
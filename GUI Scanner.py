import json
import tkinter as tk
import ipaddress
import time
import concurrent.futures
from tkinter import ttk

input_file = "user_input.json"

def save_user_input(start_ip, end_ip, port):
    data = {"start_ip": start_ip, "end_ip": end_ip, "port": port}
    with open(input_file, "w") as file:
        json.dump(data, file)

def load_user_input():
    try:
        with open(input_file, "r") as file:
            data = json.load(file)
        return data["start_ip"], data["end_ip"], data["port"]
    except (FileNotFoundError, json.JSONDecodeError):
        return "", "", ""

def scan_ip(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result
    except Exception as e:
        return f"Error scanning IP {ip} on port {port}: {e}"

def ip_scanner(start_ip, end_ip, port):
    result_listbox.delete(0, tk.END)
    batch_size = 10

    start = ipaddress.IPv4Address(start_ip)
    end = ipaddress.IPv4Address(end_ip)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for ip in range(int(start), int(end) + 1, batch_size):
            batch = [str(ipaddress.IPv4Address(i)) for i in range(ip, min(ip + batch_size, int(end) + 1))]
            results = list(executor.map(lambda ip: scan_ip(ip, port), batch))

            for ip_str, result in zip(batch, results):
                if result == 0:
                    result_listbox.insert(tk.END, f"IP {ip_str} on port {port} is open")
                else:
                    result_listbox.insert(tk.END, f"IP {ip_str} on port {port} is closed or unreachable")

            root.update()
            time.sleep(0.1)

def start_scan():
    start_ip = start_entry.get()
    end_ip = end_entry.get()
    port = int(port_entry.get())
    save_user_input(start_ip, end_ip, port)
    ip_scanner(start_ip, end_ip, port)

root = tk.Tk()
root.title("Remembering User Input")

default_start, default_end, default_port = load_user_input()

start_label = ttk.Label(root, text="Enter Start IP:")
start_label.pack(pady=10)

start_entry = ttk.Entry(root, style="TEntry")
start_entry.insert(0, default_start)
start_entry.pack(pady=10)

end_label = ttk.Label(root, text="Enter End IP:")
end_label.pack(pady=10)

end_entry = ttk.Entry(root, style="TEntry")
end_entry.insert(0, default_end)
end_entry.pack(pady=10)

port_label = ttk.Label(root, text="Enter Port:")
port_label.pack(pady=10)

port_entry = ttk.Entry(root, style="TEntry")
port_entry.insert(0, str(default_port))
port_entry.pack(pady=10)

style = ttk.Style()
style.configure("TButton", foreground="white", background="#ff66b2", font=("Arial", 12, "bold"))

scan_button = ttk.Button(root, text="Scan", command=start_scan, style="TButton")
scan_button.pack(pady=10)

result_listbox = tk.Listbox(root, height=10, width=70)
result_listbox.pack(pady=10)
result_listbox.configure(bg="#ffd9eb", fg="black", font=("Arial", 10))

root.mainloop()

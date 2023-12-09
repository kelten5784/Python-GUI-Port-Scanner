import json
import tkinter as tk
import ipaddress
import time
import socket
import concurrent.futures
from tkinter import ttk, simpledialog

input_file = "user_input.json"

COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 3389]

def save_user_input(start_ip, end_ip, first_port, last_port):
    data = {"start_ip": start_ip, "end_ip": end_ip, "first_port": first_port, "last_port": last_port}
    with open(input_file, "w") as file:
        json.dump(data, file)

def load_user_input():
    try:
        with open(input_file, "r") as file:
            data = json.load(file)
        return data.get("start_ip", ""), data.get("end_ip", ""), data.get("first_port", ""), data.get("last_port", "")
    except (FileNotFoundError, json.JSONDecodeError):
        return "", "", "", ""

def scan_ip(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result
    except Exception as e:
        return f"Error scanning IP {ip} on port {port}: {e}"

def ip_scanner(start_ip, end_ip, port_list=None, thorough=False, first_port=None, last_port=None):
    result_listbox.delete(0, tk.END)
    batch_size = 10

    start = ipaddress.IPv4Address(start_ip)
    end = ipaddress.IPv4Address(end_ip)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for ip in range(int(start), int(end) + 1, batch_size):
            batch = [str(ipaddress.IPv4Address(i)) for i in range(ip, min(ip + batch_size, int(end) + 1))]
            results = list(executor.map(lambda ip: (ip, scan_ports(ip, port_list, first_port, last_port)), batch))

            for ip_str, port_results in results:
                for port, result in port_results.items():
                    if result == 0:
                        result_listbox.insert(tk.END, f"IP {ip_str} on port {port} is open")
                    else:
                        result_listbox.insert(tk.END, f"IP {ip_str} on port {port} is closed or unreachable")

            root.update()
            time.sleep(0.2)  

def scan_ports(ip, port_list=None, first_port=None, last_port=None):
    port_results = {}
    if first_port and last_port:
        port_range = range(int(first_port), int(last_port) + 1)
    else:
        port_range = port_list or []

    for port in port_range:
        result = scan_ip(ip, port)
        port_results[port] = result
    return port_results

def start_scan():
    start_ip = start_entry.get()
    end_ip = end_entry.get()
    scan_type = scan_type_var.get()

    if scan_type == "Quick Scan":
        ip_scanner(start_ip, end_ip, port_list=COMMON_PORTS)
    elif scan_type == "Thorough Scan":
        first_port = simpledialog.askstring("Port Range", "Enter the first port:")
        last_port = simpledialog.askstring("Port Range", "Enter the last port:")
        save_user_input(start_ip, end_ip, first_port, last_port)
        ip_scanner(start_ip, end_ip, first_port=first_port, last_port=last_port)

root = tk.Tk()
root.title("Pretty Pink IP Scanner")
root.configure(bg="#ffd9eb") 

default_start, default_end, default_first_port, default_last_port = load_user_input()

start_label = ttk.Label(root, text="Enter Start IP:")
start_label.pack(pady=10)

start_entry = ttk.Entry(root, style="TEntry", font=("Arial", 12))  
start_entry.insert(0, default_start)
start_entry.pack(pady=10)

end_label = ttk.Label(root, text="Enter End IP:")
end_label.pack(pady=10)

end_entry = ttk.Entry(root, style="TEntry", font=("Arial", 12)) 
end_entry.insert(0, default_end)
end_entry.pack(pady=10)

scan_type_var = tk.StringVar(root)
scan_type_var.set("Quick Scan")

scan_type_menu = ttk.Combobox(root, textvariable=scan_type_var, values=["Quick Scan", "Thorough Scan"])
scan_type_menu.pack(pady=10)

style = ttk.Style()
style.configure("TButton", foreground="white", background="#ff66b2", font=("Arial", 14, "bold")) 

result_listbox = tk.Listbox(root, height=10, width=70, font=("Arial", 12), selectbackground="#ffd9eb")
result_listbox.pack(pady=10, expand=True, fill=tk.BOTH)


scrollbar = tk.Scrollbar(root, command=result_listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


scrollbar.config(command=result_listbox.yview)

start_scan_button = ttk.Button(root, text="Start Scan", command=start_scan, style="TButton")
start_scan_button.pack(pady=10)

root.mainloop()

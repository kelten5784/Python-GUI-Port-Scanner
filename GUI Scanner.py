import socket
import ipaddress
import concurrent.futures
import tkinter as tk
from tkinter import ttk
import time

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
    result_listbox.delete(0, tk.END)  # Clear previous results

    batch_size = 10  # Adjust the batch size based on your preference

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

            # Add a short delay between batches
            time.sleep(0.1)
def start_scan():
    start_ip = start_entry.get()
    end_ip = end_entry.get()
    port = int(port_entry.get())
    
    ip_scanner(start_ip, end_ip, port)

# Create the main window
root = tk.Tk()
root.title("Pretty Pink IP Scanner")

# Configure a style for the pink theme
style = ttk.Style()
style.configure("TButton", foreground="white", background="#ff66b2")  # Pink button style
style.configure("TLabel", foreground="#ff66b2", background="white")   # Pink label style
style.configure("TEntry", foreground="black", background="#ffd9eb")  # Light pink entry style
style.configure("TListbox", foreground="black", background="#ffd9eb")  # Light pink listbox style

# Create and pack widgets with pink theme
start_label = ttk.Label(root, text="Enter Start IP:")
start_label.pack(pady=10)

start_entry = ttk.Entry(root, style="TEntry")
start_entry.pack(pady=10)

end_label = ttk.Label(root, text="Enter End IP:")
end_label.pack(pady=10)

end_entry = ttk.Entry(root, style="TEntry")
end_entry.pack(pady=10)

port_label = ttk.Label(root, text="Enter Port:")
port_label.pack(pady=10)

port_entry = ttk.Entry(root, style="TEntry")
port_entry.pack(pady=10)

scan_button = ttk.Button(root, text="Scan", command=start_scan, style="TButton")
scan_button.pack(pady=10)

# Change the text color of the "Scan" button to black
style.configure("TButton", foreground="black", background="#ff66b2")

result_listbox = tk.Listbox(root, height=10, width=70)
result_listbox.pack(pady=10)

# Configure the Listbox style
result_listbox.configure(bg="#ffd9eb", fg="black")  # Set background and foreground colors

# Start the GUI main loop
root.mainloop()

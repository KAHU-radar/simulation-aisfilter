import socket
import threading
import select
import sys

UDP_IP = "127.0.0.1"
UDP_PORT = 10110  # Typical NMEA UDP port
TCP_PORT = 10111  # Port for OpenCPN to connect to

# Filtering controls
filter_ais = False
blocked_mmsi = set()  # Add MMSIs here like {'123456789'}
seen_mmsi = set()  # Add MMSIs here like {'123456789'}

def is_ais_message(nmea_line):
    return nmea_line.startswith('!AIVDM') or nmea_line.startswith('!AIVDO')

def extract_mmsi(nmea_line):
    try:
        # Extract payload, decode AIS type, and get MMSI (simplified)
        parts = nmea_line.split(',')
        if len(parts) < 6:
            return None
        payload = parts[5]
        if not payload:
            return None
        # Decode MMSI (basic way, real implementation should use AIS decoder)
        sixbit = ''.join(f'{ord(c) - 48:06b}' for c in payload)
        mmsi_bin = sixbit[8:38]
        return str(int(mmsi_bin, 2))
    except Exception:
        return None

def udp_listener(tcp_clients):
    global filter_ais
    global blocked_mmsi
    global seen_mmsi

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind((UDP_IP, UDP_PORT))
    print(f"Listening for UDP on {UDP_IP}:{UDP_PORT}")

    while True:
        data, _ = udp_sock.recvfrom(4096)
        line = data.decode(errors='ignore').strip()

        send = True
        if is_ais_message(line):
            mmsi = extract_mmsi(line)
            seen_mmsi.add(mmsi)
            if filter_ais:
                send = False
            if mmsi in blocked_mmsi:
                send = False

        if send:
            for client in tcp_clients.copy():
                try:
                    client.sendall((line + "\r\n").encode())
                except Exception:
                    tcp_clients.remove(client)

def tcp_server(tcp_clients):
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_sock.bind(('', TCP_PORT))
    tcp_sock.listen(5)
    print(f"TCP server started on port {TCP_PORT}")

    while True:
        conn, addr = tcp_sock.accept()
        print(f"Client connected: {addr}")
        tcp_clients.append(conn)

def key_listener():
    global filter_ais
    global blocked_mmsi
    global seen_mmsi
    print("Press 't' to toggle AIS filtering. Press 'q' to quit.")
    while True:
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            cmd = input("> ").lower().strip()
            if cmd == 't':
                filter_ais = not filter_ais
                print(f"AIS filtering {'ENABLED' if filter_ais else 'DISABLED'}")
            elif cmd == 'q':
                print("Exiting.")
                sys.exit(0)
            elif cmd == "l":
                print("Blocked mmsi:s")
                for mmsi in blocked_mmsi:
                    print(mmsi)
                print("Seen mmsi:s")
                for mmsi in seen_mmsi - blocked_mmsi:
                    print(mmsi)
            else:
                if cmd in blocked_mmsi:
                    blocked_mmsi.remove(cmd)
                else:
                    blocked_mmsi.add(cmd)

def main():
    tcp_clients = []

    threading.Thread(target=udp_listener, args=(tcp_clients,), daemon=True).start()
    threading.Thread(target=tcp_server, args=(tcp_clients,), daemon=True).start()
    key_listener()

if __name__ == '__main__':
    main()

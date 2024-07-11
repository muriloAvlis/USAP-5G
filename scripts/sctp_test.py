# How to use: python3 sctp_test.py {IP} {PORT}

import socket
import sys


def check_sctp_port(ip, port):
    try:
        sock = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_SCTP)
        sock.settimeout(1)  # Timeout after 1 second
        sock.connect((ip, port))
        print(f"SCTP port {port} on {ip} is open.")
        sock.close()
    except socket.error as e:
        print(f"Cannot connect to SCTP port {port} on {ip}: {e}")


IP = sys.argv[1]
SCTP_PORT = int(sys.argv[2])

# Replace by args
check_sctp_port(IP, SCTP_PORT)

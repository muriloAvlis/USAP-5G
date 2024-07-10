import socket

def check_sctp_port(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_SEQPACKET, socket.IPPROTO_SCTP)
        sock.settimeout(5)  # Timeout após 5 segundos
        sock.connect((ip, port))
        print(f"SCTP port {port} on {ip} is open.")
        sock.close()
    except socket.error as e:
        print(f"Cannot connect to SCTP port {port} on {ip}: {e}")

# Substitua pelo IP e porta desejados
check_sctp_port('10.43.195.113', 36421)
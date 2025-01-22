import socket


def get_ip_by_hostname(hostname) -> str:
    ip_addr = socket.gethostbyname(hostname)
    return ip_addr

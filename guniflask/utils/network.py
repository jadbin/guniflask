import socket


def get_local_ip_address():
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('224.0.0.0', 80))
        local_ip = s.getsockname()[0]
        return local_ip
    finally:
        if s:
            s.close()

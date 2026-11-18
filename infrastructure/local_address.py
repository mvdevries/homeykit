import socket

from ..domain.defaults import ADDRESS_PROBE_HOST, ADDRESS_PROBE_PORT


def find_local_ip_address() -> str | None:
    probe_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe_socket.connect((ADDRESS_PROBE_HOST, ADDRESS_PROBE_PORT))
        return str(probe_socket.getsockname()[0])
    except OSError:
        return None
    finally:
        probe_socket.close()

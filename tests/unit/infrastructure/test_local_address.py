import socket

from homeykit.infrastructure import local_address


class FakeSocket:
    def __init__(self, address=None, fail=False):
        self.address = address
        self.fail = fail
        self.closed = False

    def connect(self, target):
        if self.fail:
            raise OSError("unreachable")

    def getsockname(self):
        return (self.address, 12345)

    def close(self):
        self.closed = True


class TestFindLocalIpAddress:
    def test_given_a_route_when_finding_the_address_then_the_outgoing_one_is_returned(
        self, monkeypatch
    ):
        fake = FakeSocket("192.0.2.10")
        monkeypatch.setattr(socket, "socket", lambda *args: fake)

        address = local_address.find_local_ip_address()

        assert address == "192.0.2.10"
        assert fake.closed

    def test_given_no_network_when_finding_the_address_then_none_is_returned(
        self, monkeypatch
    ):
        fake = FakeSocket(fail=True)
        monkeypatch.setattr(socket, "socket", lambda *args: fake)

        address = local_address.find_local_ip_address()

        assert address is None
        assert fake.closed

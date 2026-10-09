"""Shared pytest configuration for survey-opus.

- Puts ``src/`` on ``sys.path`` so tests import the package directly.
- Hard guarantee of the NGS etiquette rule: an autouse fixture blocks every
  non-localhost socket connection, so no test can ever POST to noaa.gov.
  The local ``http.server`` mock tests only use 127.0.0.1.
"""

import pathlib
import socket
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))


@pytest.fixture(autouse=True)
def _block_non_localhost_connections(monkeypatch):
    real_connect = socket.socket.connect

    def guarded_connect(self, address):
        host = address[0] if isinstance(address, tuple) else address
        if host not in ("127.0.0.1", "::1", "localhost"):
            raise AssertionError(
                f"blocked non-localhost connection to {host!r}: "
                "tests must never contact live NGS/OPUS endpoints"
            )
        return real_connect(self, address)

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)

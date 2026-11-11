"""Shared fixtures for Acme Shield tests.

`clock` is a fake clock: tests move time with `clock.advance(seconds)` instead of sleeping.
It starts exactly at a window boundary (1_000_020 is a multiple of 60).
"""

from __future__ import annotations

import json
import logging
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from acme_shield.app import create_app

LIVE_KEY = "acme_live_00000000000000000000000000000f01"  # fernhollow, live
TEST_KEY = "acme_test_00000000000000000000000000000f02"  # fernhollow, test
OTHER_LIVE_KEY = "acme_live_00000000000000000000000000000c01"  # cedarline, live
SUSPENDED_KEY = "acme_live_00000000000000000000000000000a01"  # relaypoint, suspended


class FakeClock:
    def __init__(self, start: float = 1_000_020.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def bearer(key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {key}"}


def access_records(caplog: pytest.LogCaptureFixture) -> list[dict[str, Any]]:
    """Parsed JSON access-log lines captured during the test."""
    return [
        json.loads(r.getMessage())
        for r in caplog.records
        if r.name == "acme_shield.access"
    ]


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def app(clock: FakeClock) -> FastAPI:
    return create_app(clock=clock)


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def _capture_access_log(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger="acme_shield.access")

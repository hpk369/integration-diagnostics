"""Tenant registry, loaded from tenants.yaml.

All tenants are fictional. Keys are deliberately low-entropy placeholders, so secret
scanners don't flag them and nobody mistakes them for real credentials.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel

DEFAULT_TENANTS_PATH = Path(__file__).with_name("tenants.yaml")

KeyEnv = Literal["live", "test"]
BillingStatus = Literal["active", "suspended"]


class ApiKey(BaseModel):
    key: str
    env: KeyEnv


class Tenant(BaseModel):
    tenant_id: str
    name: str
    billing_status: BillingStatus = "active"
    api_keys: list[ApiKey]


class TenantStore:
    """Read-only lookups over the tenants file."""

    def __init__(self, tenants: list[Tenant]) -> None:
        self._by_id = {t.tenant_id: t for t in tenants}
        self._by_key = {k.key: (t, k) for t in tenants for k in t.api_keys}

    @classmethod
    def from_yaml(cls, path: Path = DEFAULT_TENANTS_PATH) -> TenantStore:
        raw = yaml.safe_load(path.read_text())
        return cls([Tenant.model_validate(t) for t in raw["tenants"]])

    def lookup_key(self, key: str) -> tuple[Tenant, ApiKey] | None:
        """Return (tenant, key record) for a known key, or None."""
        return self._by_key.get(key)

    def get(self, tenant_id: str) -> Tenant | None:
        return self._by_id.get(tenant_id)

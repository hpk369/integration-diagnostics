"""GET /v1/scans: the endpoint most API evidence is recorded against."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from acme_shield.deps import Authenticated

router = APIRouter(prefix="/v1")


@router.get("/scans")
def list_scans(auth: Authenticated) -> dict[str, Any]:
    tenant = auth.tenant.tenant_id
    return {
        "data": [
            {
                "id": f"scan_{tenant}_001",
                "domain": f"{tenant}.example",
                "status": "complete",
            },
            {
                "id": f"scan_{tenant}_002",
                "domain": f"pay-{tenant}.example",
                "status": "running",
            },
        ]
    }

"""Root-level services package — shared result types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ServiceResult:
    """Unified, non-throwing result type for all service operations."""
    ok: bool
    data: Any = None
    message: str = ""

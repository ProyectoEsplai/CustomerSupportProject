"""Tipos compartidos del proyecto."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TurnoChat:
    rol: str
    contenido: str
    nivel: str = ""

"""
Simple in-memory tools for the Skyline Motors concierge agent.

For this V1 we only expose a single meaningful tool: inventory search.
The LLM can call this tool to look up available vehicles by body type
and price range.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Vehicle:
    model: str
    trim: str
    body_type: str
    price: int  # in USD
    color: str
    in_stock: bool


# A tiny mocked inventory that is easy for the LLM to reason about.
INVENTORY: List[Vehicle] = [
    Vehicle(
        model="Skyline Aurora",
        trim="LX",
        body_type="sedan",
        price=18500,
        color="silver",
        in_stock=True,
    ),
    Vehicle(
        model="Skyline Aurora",
        trim="EX",
        body_type="sedan",
        price=22500,
        color="blue",
        in_stock=True,
    ),
    Vehicle(
        model="Skyline Horizon",
        trim="Sport",
        body_type="sedan",
        price=29500,
        color="red",
        in_stock=True,
    ),
    Vehicle(
        model="Skyline Trailrunner",
        trim="AWD",
        body_type="suv",
        price=34500,
        color="white",
        in_stock=True,
    ),
    Vehicle(
        model="Skyline CityLite",
        trim="Base",
        body_type="hatchback",
        price=15500,
        color="gray",
        in_stock=False,
    ),
]


def search_inventory(
    body_type: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """
    Filter the mocked inventory by body type and price range.

    The result is returned as a list of plain dicts so it can be passed
    directly into a tool-call response for the LLM.
    """
    results: List[Vehicle] = []
    normalized_body_type = body_type.lower() if body_type else None

    for vehicle in INVENTORY:
        if normalized_body_type and vehicle.body_type.lower() != normalized_body_type:
            continue

        if min_price is not None and vehicle.price < min_price:
            continue

        if max_price is not None and vehicle.price > max_price:
            continue

        if not vehicle.in_stock:
            continue

        results.append(vehicle)

        if len(results) >= limit:
            break

    return [asdict(v) for v in results]


def format_inventory_for_llm(vehicles: List[Dict[str, Any]]) -> str:
    """
    Convert vehicle dicts into a short, human-readable summary string.

    The LLM will typically receive the raw JSON tool result, but this helper
    can be handy for debugging or for non-tool usage.
    """
    if not vehicles:
        return "No matching vehicles found in the current inventory."

    lines: List[str] = []
    for v in vehicles:
        line = (
            f"{v['model']} {v['trim']} ({v['body_type']}), "
            f"{v['color']}, approx ${v['price']:,}."
        )
        lines.append(line)

    return "\n".join(lines)


__all__ = ["Vehicle", "INVENTORY", "search_inventory", "format_inventory_for_llm"]



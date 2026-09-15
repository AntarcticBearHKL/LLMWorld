"""Per-block (per-postcode) day summaries for the world overview.

The watch view's top layer shows every block of a world for one day of a
spacetime; this module aggregates the per-house day replays into that shape.
"""

from __future__ import annotations

import os
from typing import List

from . import derive, world_admin
from .models import BlockSummary, WorldDayBlocks

from analyze import dataset  # noqa: E402  (paths.py put src/ on sys.path)


def build_day_blocks(
    world: str,
    run: str,
    date: str,
    policy: str = "baseline",
) -> WorldDayBlocks:
    """Aggregate one (run, date) day into the blocks of *world*."""
    world_dir = world_admin.resolve_world_dir(world)
    run_houses = set(dataset.list_houses(run, run, date))
    blocks: List[BlockSummary] = []

    for postcode in world_admin.districts(world):
        base = os.path.join(world_dir, postcode)
        try:
            houses = sorted(
                child for child in os.listdir(base)
                if child.startswith("house_") and child in run_houses
            )
        except OSError:
            houses = []

        total = 0.0
        peak = 0.0
        for house in houses:
            try:
                replay = derive.build_day_replay(run, date, house, policy)
            except ValueError:
                continue
            total += replay.metrics.total_kwh
            peak = max(peak, replay.metrics.peak_watts or 0.0)

        blocks.append(BlockSummary(
            postcode=postcode,
            houses=houses,
            house_count=len(houses),
            total_kwh=round(total, 3),
            peak_watts=round(peak, 1),
        ))

    return WorldDayBlocks(world=world, run=run, date=date, blocks=blocks)

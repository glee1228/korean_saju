"""Mass verification of DayPillar.for_date() against two independent references.

Verification 1 — KASI 1867 anchor integrity:
  For each KASI month-start record (1867 records), our algorithm must predict
  the same 일진(60갑자) as KASI's recorded value. KASI anchors are the
  authoritative ground truth for 일진.

Verification 2 — 35,000 daily cross-check vs lunar-python:
  Generate 35,000 dates across 1900-01-31 to 2050-12-14, compute 일진 via our
  DayPillar.for_date() and compare against `lunar-python` package's
  getDayInGanZhi(). lunar-python is a port of 6tail/lunar (widely-used).

Usage:
  python tools/verify_daypillar.py
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta

from korean_saju import DayPillar, GanJi, load_bundled_data


def main() -> None:
    print("=" * 70)
    print("Verification 1: KASI 1867 anchor integrity")
    print("=" * 70)

    lunar, _ = load_bundled_data()
    months = lunar.months
    assert len(months) == 1867, f"expected 1867 month records, got {len(months)}"

    anchor_mismatches: list[tuple[int, int, str, str]] = []
    for m in months:
        # Convert KASI iljin string ("갑진(甲辰)" or "甲辰") to hanja-only
        iljin = m.iljin
        kasi_hanja = iljin.split("(")[-1].rstrip(")") if "(" in iljin else iljin

        our_pillar = DayPillar.for_date(m.start_solar)
        our_hanja = our_pillar.hanja

        if our_hanja != kasi_hanja:
            anchor_mismatches.append((m.year, m.month, kasi_hanja, our_hanja))

    print(f"Total anchors: {len(months)}")
    print(f"Match: {len(months) - len(anchor_mismatches)}/{len(months)} "
          f"({100 * (1 - len(anchor_mismatches) / len(months)):.4f}%)")
    if anchor_mismatches:
        print(f"Mismatches ({len(anchor_mismatches)}):")
        for y, m_, kasi, ours in anchor_mismatches[:10]:
            print(f"  음력 {y}-{m_:02d}: KASI={kasi} vs ours={ours}")
    else:
        print("✓ ALL 1867 KASI anchors verified (100% match)")

    print()
    print("=" * 70)
    print("Verification 2: 35,000 daily cross-check vs lunar-python")
    print("=" * 70)

    try:
        from lunar_python import Solar  # type: ignore
    except ImportError:
        print("lunar-python not installed — skipping. Run: pip install lunar-python")
        return

    # Date range: KASI lunar data coverage
    range_start = datetime(1900, 1, 31)
    range_end = datetime(2050, 12, 14)
    total_days = (range_end - range_start).days
    print(f"Source range: {range_start.date()} to {range_end.date()} "
          f"({total_days} days)")

    SAMPLE_SIZE = 35_000
    random.seed(42)  # reproducible
    sampled_offsets = sorted(random.sample(range(total_days), SAMPLE_SIZE))
    print(f"Random sample size: {SAMPLE_SIZE} (seed=42)")

    mismatches: list[tuple[datetime, str, str]] = []
    for i, offset in enumerate(sampled_offsets):
        d = range_start + timedelta(days=offset)
        ours = DayPillar.for_date(d).hanja

        solar = Solar.fromYmd(d.year, d.month, d.day)
        theirs = solar.getLunar().getDayInGanZhi()

        if ours != theirs:
            mismatches.append((d, ours, theirs))

        if (i + 1) % 10_000 == 0:
            print(f"  Progress: {i + 1}/{SAMPLE_SIZE} "
                  f"({len(mismatches)} mismatches so far)")

    match_count = SAMPLE_SIZE - len(mismatches)
    print()
    print(f"Total: {SAMPLE_SIZE} dates checked")
    print(f"Match: {match_count}/{SAMPLE_SIZE} "
          f"({100 * match_count / SAMPLE_SIZE:.4f}%)")

    if mismatches:
        print(f"Mismatches ({len(mismatches)}):")
        for d, ours, theirs in mismatches[:20]:
            print(f"  {d.date()}: ours={ours} vs lunar-python={theirs}")
        if len(mismatches) > 20:
            print(f"  ... and {len(mismatches) - 20} more")
    else:
        print("✓ ALL 35,000 dates match lunar-python (100%)")


if __name__ == "__main__":
    main()

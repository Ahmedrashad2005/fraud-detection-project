#!/usr/bin/env python3
"""
Fix nested artifact paths: move files from nested subdirectories to expected locations.

Problem:
  - Models are in artifacts/models/models/heavy/ instead of artifacts/models/heavy/
  - Preprocessing is in artifacts/preprocessing/preprocessing/ instead of artifacts/preprocessing/

This script copies files to the correct locations.
"""

import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent

FIXES = [
    # (source_dir, dest_dir)
    (BASE / "artifacts" / "models" / "models" / "heavy", BASE / "artifacts" / "models" / "heavy"),
    (BASE / "artifacts" / "models" / "models" / "light", BASE / "artifacts" / "models" / "light"),
    (BASE / "artifacts" / "preprocessing" / "preprocessing", BASE / "artifacts" / "preprocessing"),
]


def main():
    for src_dir, dst_dir in FIXES:
        if not src_dir.exists():
            print(f"⏩ Source not found (skip): {src_dir}")
            continue

        dst_dir.mkdir(parents=True, exist_ok=True)

        for f in src_dir.iterdir():
            if f.is_file():
                dest = dst_dir / f.name
                if dest.exists() and dest.stat().st_size == f.stat().st_size:
                    print(f"  ⏩ Already exists: {dest.name}")
                    continue
                shutil.copy2(f, dest)
                print(f"  ✅ Copied: {f.name} → {dst_dir.relative_to(BASE)}/")

    # Verify
    print("\n" + "=" * 50)
    print("VERIFICATION")
    print("=" * 50)
    expected = [
        "artifacts/models/heavy/xgb_heavy.pkl",
        "artifacts/models/heavy/lgbm_heavy.pkl",
        "artifacts/models/heavy/iso_forest.pkl",
        "artifacts/models/light/xgb_light.pkl",
        "artifacts/models/light/lgbm_light.pkl",
        "artifacts/preprocessing/all_features.pkl",
        "artifacts/preprocessing/manual_features.pkl",
        "artifacts/preprocessing/threshold.pkl",
        "artifacts/preprocessing/light_threshold.pkl",
        "artifacts/preprocessing/encoders.pkl",
        "artifacts/preprocessing/medians.pkl",
        "artifacts/preprocessing/feature_columns.pkl",
        "artifacts/preprocessing/feature_medians.pkl",
        "artifacts/preprocessing/reference_stats.pkl",
        "artifacts/preprocessing/aggregation_maps.pkl",
    ]

    all_ok = True
    for rel in expected:
        p = BASE / rel
        status = "✅" if p.exists() else "❌ MISSING"
        if not p.exists():
            all_ok = False
        print(f"  {status}: {rel}")

    if all_ok:
        print("\n🎉 All artifacts in place! Project is ready to run.")
    else:
        print("\n⚠️  Some artifacts are still missing.")


if __name__ == "__main__":
    main()

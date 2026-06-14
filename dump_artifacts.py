#!/usr/bin/env python3
"""Quick artifact dump - saves results to a text file."""
import os, sys, json
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import joblib
from pathlib import Path

BASE = Path(__file__).resolve().parent
PREP = BASE / "artifacts" / "preprocessing"

# Check both possible paths
for subdir in ["", "preprocessing"]:
    d = PREP / subdir if subdir else PREP
    for name in ["manual_features.pkl", "feature_medians.pkl", "threshold.pkl", "light_threshold.pkl"]:
        p = d / name
        if p.exists():
            data = joblib.load(p)
            out_path = BASE / f"_dump_{name}.json"
            if isinstance(data, (list, dict, float, int)):
                with open(out_path, "w") as f:
                    json.dump(data, f, indent=2, default=str)
                print(f"Dumped {p} -> {out_path}")
            else:
                print(f"Skipped {p} (type={type(data)})")

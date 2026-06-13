#!/usr/bin/env bash
# Setup virtual environment for fraud-detection (Ubuntu / PEP 668 safe)
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Creating venv..."
python3 -m venv .venv

echo "==> Installing packages (use venv python, NOT system pip)..."
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-dashboard.txt

echo ""
echo "==> Done. Activate and run:"
echo "  source .venv/bin/activate"
echo "  python -m streamlit run dashboard/app.py"

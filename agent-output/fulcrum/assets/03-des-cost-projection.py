"""Six identical planning months; no invented growth or actual-spend forecast."""
from pathlib import Path
from decimal import Decimal
import json
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".github/skills/apex-python-diagrams/scripts"))
from diagram_io import save_figure

data = json.loads((PROJECT / "contracts/02-cost-estimate.conservative-planning-v2.json").read_text(),
                  parse_float=Decimal)
assert data["status"] == "COMPLETE" and not data["unresolved_items"]
total = data["monthly_total"]
fig, ax = plt.subplots(figsize=(12, 6))
months = [f"M{i}" for i in range(1, 7)]
bars = ax.bar(months, [float(total)] * 6, color="#0078D4", width=0.65)
for bar in bars:
    ax.text(bar.get_x() + bar.get_width() / 2, float(total) + 4,
            str(total), ha="center", fontsize=10, weight="bold")
ax.set_ylim(0, float(total) * 1.3)
ax.set_ylabel("USD per planning month")
ax.set_title("Fulcrum — unchanged six-month scenario", fontsize=16, weight="bold")
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", alpha=0.2)
ax.set_axisbelow(True)
fig.text(0.5, 0.035,
         "Same approved usage, lifetimes and rates each month · Not a measured trend or billing forecast",
         ha="center", fontsize=10)
fig.tight_layout(rect=(0, 0.07, 1, 1))
save_figure(fig, Path(__file__).with_suffix(""), dpi=200)
plt.close(fig)

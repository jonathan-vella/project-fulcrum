"""Render only the actual COMPLETE pricing-owner scenario, never new rates."""
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

evidence = PROJECT / "contracts/02-cost-estimate.conservative-planning-v2.json"
data = json.loads(evidence.read_text(), parse_float=Decimal)
assert data["status"] == "COMPLETE" and len(data["resources"]) == 17
assert sum(Decimal(str(x["monthly_cost"])) for x in data["resources"]) == data["monthly_total"]
ranked = sorted(data["resources"], key=lambda x: x["monthly_cost"], reverse=True)
names = ["ACR Premium", "4 steady private endpoints", "Bastion gateway", "B1 host", "Cosmos source"]
values = [x["monthly_cost"] for x in ranked[:5]]
values.append(sum(x["monthly_cost"] for x in ranked[5:]))
names.append("Other 12 lines")
fig, ax = plt.subplots(figsize=(12, 7))
wedges, _ = ax.pie([float(x) for x in values], startangle=90,
                  colors=["#0078D4", "#008272", "#7B3FA0", "#D18B00", "#107C10", "#8A98A8"],
                  wedgeprops={"width": 0.35, "edgecolor": "white"})
ax.text(0, 0.04, f"USD {data['monthly_total']}", ha="center", va="center",
        weight="bold", fontsize=16)
ax.text(0, -0.15, "per planning month", ha="center", fontsize=11)
ax.legend(wedges, [f"{n}: USD {v}" for n, v in zip(names, values)],
          loc="center left", bbox_to_anchor=(0.98, 0.5), frameon=False)
ax.set_title("Fulcrum — approved conservative cost scenario", fontsize=16, weight="bold")
fig.text(0.5, 0.04, "17 modeled lines · Conditional volumes/lifetimes · Not an invoice prediction",
         ha="center", fontsize=10)
fig.tight_layout(rect=(0, 0.07, 1, 1))
save_figure(fig, Path(__file__).with_suffix(""), dpi=200)
plt.close(fig)

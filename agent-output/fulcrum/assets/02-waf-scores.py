"""DEV design scores, not deployed-control or compliance measurements."""
from pathlib import Path
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / ".github/skills/apex-python-diagrams/scripts"))
from diagram_io import save_figure

labels = ["Security · Medium", "Reliability · Medium", "Performance · Low",
          "Cost Optimization · Medium", "Operational Excellence · Medium"]
scores = [7, 5, 6, 8, 6]
colors = ["#C00000", "#107C10", "#FF8C00", "#D18B00", "#8764B8"]
fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(labels, scores, color=colors, height=0.6)
ax.invert_yaxis()
for bar, value in zip(bars, scores):
    ax.text(value - 0.18, bar.get_y() + bar.get_height() / 2, f"{value}/10",
            ha="right", va="center", color="white", weight="bold", fontsize=12)
ax.set_xlim(0, 10)
ax.set_xticks(range(11))
ax.set_xlabel("Evidence-backed design score / 10 · confidence shown beside pillar")
ax.set_title("Fulcrum — DEV WAF design assessment", fontsize=16, weight="bold")
ax.grid(axis="x", alpha=0.2)
ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False)
fig.text(0.5, 0.025, "Assumed Corp; not tenant-verified · All runtime paths Unverified",
         ha="center", fontsize=10)
fig.tight_layout(rect=(0, 0.06, 1, 1))
save_figure(fig, Path(__file__).with_suffix(""), dpi=200)
plt.close(fig)

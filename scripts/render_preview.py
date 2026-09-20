"""Plot actual public-demo CSV output; this is not an algorithm benchmark."""
import argparse
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--input", type=Path, required=True, help="trajectory.csv from the demo")
parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "docs/assets/demo-preview.png")
args = parser.parse_args()
with args.input.open() as stream:
    rows = list(csv.DictReader(stream))
positions = [(float(row["tx"]), float(row["ty"])) for row in rows]
times = [float(row["timestamp"]) for row in rows]
if len(rows) < 2:
    parser.error("preview needs at least two poses")
plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": "#e6efff", "axes.labelcolor": "#a3b5d3",
                     "xtick.color": "#91a5c7", "ytick.color": "#91a5c7", "axes.edgecolor": "#34415b"})
fig = plt.figure(figsize=(14, 6), facecolor="#0b1222")
ax = fig.add_axes([0.075, 0.20, 0.57, 0.61], facecolor="#0b1222")
segments = list(zip(positions, positions[1:]))
collection = LineCollection(segments, cmap="cool", linewidths=3)
collection.set_array(times[1:])
ax.add_collection(collection)
ax.autoscale()
ax.set_aspect("equal", adjustable="datalim")
ax.margins(0.1)
ax.grid(color="#1c2a43", linewidth=0.7)
ax.set_xlabel("World east / m")
ax.set_ylabel("World north / m")
ax.scatter(*positions[0], s=90, facecolors="#0b1222", edgecolors="#70f0d4", linewidths=2, zorder=3)
fig.text(0.055, 0.90, "RayCon-SLAM  /  Replay inspection", fontsize=21, weight="bold")
fig.text(0.055, 0.835, "Deterministic synthetic input. Rendered from the C++ CSV export.", fontsize=11, color="#91a5c7")
fig.text(0.73, 0.65, str(len(rows)), fontsize=46, color="#74dfff", weight="bold")
fig.text(0.73, 0.59, "EXPORTED POSES", fontsize=10, color="#91a5c7")
fig.text(0.73, 0.43, f"{times[-1] - times[0]:.1f} s", fontsize=30, color="#bb9cff")
fig.text(0.73, 0.37, "INPUT TIME SPAN", fontsize=10, color="#91a5c7")
fig.text(0.055, 0.055, "PUBLIC PREVIEW v0.1.0     /     GIVEN ODOMETRY REPLAY     /     NO VISUAL ESTIMATION", fontsize=10, color="#70f0d4")
args.output.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(args.output, dpi=140, facecolor=fig.get_facecolor())
plt.close(fig)
print(args.output)

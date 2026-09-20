"""Generate a deterministic, entirely synthetic planar replay fixture."""
import csv
import math
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "data/showcase_odometry.csv"
rows = [(0, 0, 0, 0)]
previous_x = previous_y = previous_yaw = 0.0
for frame in range(1, 121):
    angle = frame * 2 * math.pi / 120
    x = 9 * math.sin(angle)
    y = 5 * math.sin(angle) * math.cos(angle)
    dx, dy = x - previous_x, y - previous_y
    yaw = math.atan2(dy, dx)
    c, s = math.cos(previous_yaw), math.sin(previous_yaw)
    rows.append((frame * 0.1, c * dx + s * dy, -s * dx + c * dy,
                 math.remainder(yaw - previous_yaw, 2 * math.pi)))
    previous_x, previous_y, previous_yaw = x, y, yaw
with path.open("w", newline="", encoding="utf-8") as stream:
    writer = csv.writer(stream)
    writer.writerow(["timestamp", "dx_body_m", "dy_body_m", "dyaw_rad"])
    writer.writerows(rows)
print(path.name, "written; synthetic fixture only")

"""Public planar odometry replay and trajectory export; not a SLAM backend."""

import argparse
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path


def integrate(rows):
    """Compose given increments in the previous body frame, then update yaw."""
    poses = []
    x = y = yaw = distance = 0.0
    previous_time = None
    for row in rows:
        timestamp, dx, dy, dyaw = [float(row[key]) for key in
                                  ("timestamp", "dx_body_m", "dy_body_m", "dyaw_rad")]
        if not all(math.isfinite(v) for v in (timestamp, dx, dy, dyaw)):
            raise ValueError("all odometry values must be finite")
        if previous_time is not None and timestamp <= previous_time:
            raise ValueError("timestamps must strictly increase")
        if previous_time is None and (dx != 0 or dy != 0 or dyaw != 0):
            raise ValueError("first row declares the initial pose and must have zero increments")
        c, s = math.cos(yaw), math.sin(yaw)
        x, y = x + c * dx - s * dy, y + s * dx + c * dy
        yaw = math.remainder(yaw + dyaw, 2 * math.pi)
        distance += math.hypot(dx, dy)
        if not all(math.isfinite(v) for v in (x, y, yaw, distance)):
            raise ValueError("trajectory integration overflow")
        poses.append({"timestamp": timestamp, "tx": x, "ty": y, "tz": 0.0,
                      "qx": 0.0, "qy": 0.0, "qz": math.sin(yaw / 2),
                      "qw": math.cos(yaw / 2)})
        previous_time = timestamp
    if not poses:
        raise ValueError("input contains no odometry samples")
    return poses, distance


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    parser.add_argument("--version", action="version", version=f"RayCon-SLAM public preview {version}")
    parser.add_argument("--input", type=Path, default=root / "data/odometry.csv")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        with args.input.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        poses, distance = integrate(rows)
        summary = {"version": version, "mode": "public-demo", "backend": "given_planar_odometry_replay",
                   "input_count": len(rows), "pose_count": len(poses),
                   "path_length_m": distance,
                   "duration_s": poses[-1]["timestamp"] - poses[0]["timestamp"],
                   "end_distance_from_origin_m": math.hypot(poses[-1]["tx"], poses[-1]["ty"]),
                   "visual_tracking": False, "loop_closure": False}
        if not all(math.isfinite(summary[k]) for k in
                   ("duration_s", "path_length_m", "end_distance_from_origin_m")):
            raise ValueError("summary overflow")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
        output = args.output or root / "result" / stamp
        output.mkdir(parents=True, exist_ok=False)
        fields = ["timestamp", "tx", "ty", "tz", "qx", "qy", "qz", "qw"]
        with (output / "trajectory.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(poses)
        with (output / "trajectory.tum").open("w", encoding="utf-8") as stream:
            stream.write("# Synthetic input odometry replay; timestamp tx ty tz qx qy qz qw\n")
            for pose in poses:
                stream.write(" ".join(format(pose[key], ".17g") for key in fields) + "\n")
        (output / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False))
        print(f"Output: {output}")
    except (OSError, ValueError, KeyError, TypeError, csv.Error) as exc:
        parser.exit(2, f"Input/output error: {exc}\n")


if __name__ == "__main__":
    main()

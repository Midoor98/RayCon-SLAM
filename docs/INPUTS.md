# RayCon-SLAM · v0.1 companion tools: inputs and outputs

The companion tools included in v0.1 replay supplied planar odometry increments and export trajectories. This release does not accept image or IMU input and does not perform visual tracking, visual-inertial initialization, map optimization or loop closure. The full RayCon-SLAM system is outside the scope of these tools; system trial-run code is planned for the next version.

## Run

Requires Python 3.10 or later, with no third-party dependencies. Run from the repository root:

```bash
bash run.sh
python3 -B -m unittest discover -s tests -v
```

To specify an input file:

```bash
python3 -B src/trajectory.py --input data/odometry.csv --output result/custom-run
```

The directory specified by `--output` must not already exist. If omitted, a new timestamped directory is created under `result/`.

## Data and coordinate conventions

`data/odometry.csv` is a hand-authored ideal square path, not a sensor log or a trajectory from research experiments. Its columns are `timestamp,dx_body_m,dy_body_m,dyaw_rad`.

- Timestamps are in seconds and must be strictly increasing. The example starts at zero seconds and does not represent a calendar date.
- The first row represents the initial time, and all three increments must be zero. The initial position and heading are also zero.
- Each subsequent translation is the displacement between consecutive poses, expressed in the previous body frame in meters. It is not a velocity and is not multiplied by the sampling interval.
- Translation is transformed into the world frame using the previous heading before the current heading is updated. Heading increments are in radians, with counterclockwise rotation about the vertical axis taken as positive.
- The tools use a right-handed planar convention: the horizontal body axes point forward and left, and the vertical axis points upward. This is not an optical camera frame. Output height is zero.
- Output translation gives the position of the body origin in the world frame. The output quaternion represents body-to-world rotation in `qx qy qz qw` order.

## Workflow and files

1. Validate the initial row, finite numeric values and timestamp order.
2. Compose the supplied translation and heading increments.
3. Export CSV, TUM text and path statistics.

| File | Purpose |
| --- | --- |
| `src/trajectory.py` | Planar trajectory composition and command-line entry point |
| `run.sh` | Shortcut for the synthetic example; forwards command-line arguments |
| `tests/test_trajectory.py` | Checks for body-frame translation, path closure and input validation |
| `result/<run-directory>/trajectory.csv` | Per-timestamp poses with column headers |
| `result/<run-directory>/trajectory.tum` | Text in `timestamp tx ty tz qx qy qz qw` format |
| `result/<run-directory>/summary.json` | Pose count, time span, path length and final-position statistics |

The default example produces 9 poses and a path length of 8 meters, ending near the starting point. Floating-point rounding may leave very small nonzero values. This closure follows from the supplied synthetic increments; it is not a loop-closure detection result. No real reference trajectory is provided, and the tools do not compute ATE or research accuracy metrics.

The C++ entry point uses the same data format and requires the header order shown in the example, with unquoted fields. Run the default C++ example with `bash run_cpp.sh`.

"""Cross-check the standalone C++ public preview against its Python utility."""
import csv
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BINARY = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT / "src"))

def call(source, output, *extra):
    return subprocess.run([str(BINARY), "--input", str(source), "--output", str(output), *extra],
                          text=True, capture_output=True)

with tempfile.TemporaryDirectory(prefix="raycon-cpp-check-") as directory:
    temporary = Path(directory)
    version = subprocess.run([str(BINARY), "--version"], text=True, capture_output=True, check=True)
    assert "0.1.0" in version.stdout
    from trajectory import integrate
    source = ROOT / "data/odometry.csv"
    output = temporary / "default"
    result = call(source, output)
    assert result.returncode == 0, result.stderr
    with source.open() as stream:
        expected, distance = integrate(csv.DictReader(stream))
    with (output / "trajectory.csv").open() as stream:
        actual = list(csv.DictReader(stream))
    assert len(actual) == len(expected)
    for a, e in zip(actual, expected):
        for key in e:
            assert math.isclose(float(a[key]), e[key], rel_tol=1e-12, abs_tol=1e-12), (key, a, e)
    summary = json.loads((output / "summary.json").read_text())
    assert math.isclose(summary["path_length_m"], distance)
    custom = temporary / "custom.csv"
    custom.write_text("timestamp,dx_body_m,dy_body_m,dyaw_rad\n0,0,0,0\n1,1,0,1.5707963267948966\n2,2,1,0\n")
    custom_output = temporary / "custom"
    assert call(custom, custom_output).returncode == 0
    with (custom_output / "trajectory.csv").open() as stream:
        final = list(csv.DictReader(stream))[-1]
    assert math.isclose(float(final["tx"]), 0, abs_tol=1e-12)
    assert math.isclose(float(final["ty"]), 2, abs_tol=1e-12)
    invalid_samples = [
        "timestamp,dx_body_m,dy_body_m,dyaw_rad\n",
        "timestamp,dx_body_m,dy_body_m,dyaw_rad\n0,1,0,0\n",
        "timestamp,dx_body_m,dy_body_m,dyaw_rad\n0,0,0,0\n0,1,0,0\n",
        "timestamp,dx_body_m,dy_body_m,dyaw_rad\n0,0,0,0\n1,nan,0,0\n",
        "timestamp,dx_body_m,dy_body_m,dyaw_rad\n0,0,0,0\n1,1e308,0,0\n2,1e308,0,0\n",
    ]
    before = {p.name: p.read_bytes() for p in output.iterdir()}
    assert call(source, output).returncode != 0
    assert before == {p.name: p.read_bytes() for p in output.iterdir()}
    for i, content in enumerate(invalid_samples + ["wrong,header\n1,2\n"]):
        bad = temporary / f"bad-{i}.csv"
        bad.write_text(content)
        destination = temporary / f"bad-output-{i}"
        assert call(bad, destination).returncode != 0
        assert not destination.exists()
print("PASS: C++/Python agreement, custom input, invalid input, output preservation, version")

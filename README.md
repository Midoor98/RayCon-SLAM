<p align="center">
  <img src="docs/assets/hero-v0.1.png" alt="RayCon-SLAM v0.1.0 public preview — concept artwork" width="100%" />
</p>

<p align="center">
  <a href="https://github.com/Midoor98/RayCon-SLAM/releases/tag/v0.1.0"><img alt="Version v0.1.0" src="https://img.shields.io/badge/preview-v0.1.0-8b7cff?style=flat-square" /></a>
  <img alt="C++17" src="https://img.shields.io/badge/C%2B%2B-17-4cc9f0?style=flat-square" />
  <img alt="Python 3.10 or later" src="https://img.shields.io/badge/Python-3.10%2B-80e8cf?style=flat-square" />
  <img alt="Synthetic examples included" src="https://img.shields.io/badge/data-synthetic-25334d?style=flat-square" />
</p>

<h1 align="center">RayCon-SLAM</h1>
<p align="center"><strong>Visual-Inertial SLAM</strong><br />Visual-Inertial Simultaneous Localization and Mapping</p>
<p align="center"><a href="#quick-start">Quick start</a> · <a href="#preview">Preview</a> · <a href="#roadmap">Roadmap</a> · <a href="docs/INPUTS.md">Input formats</a> · <a href="CHANGELOG.md">Changelog</a></p>

RayCon-SLAM is a visual-inertial simultaneous localization and mapping (VI-SLAM) project with staged public code releases. The first public version opens the companion tools; the next version is planned to provide VI-SLAM system trial-run code, example configurations and launch scripts. `v0.1.0` includes standalone C++17 and Python implementations, reproducible synthetic examples, preview images and local check scripts.

> **Public preview:** `v0.1.0` makes the companion tools and synthetic examples available. The VI-SLAM system trial-run entry point is planned for the next version. The cover is concept artwork; the preview below shows actual output from the synthetic data included in this repository.

## Available in v0.1

| Module | Available in v0.1.0 |
| --- | --- |
| Replay | Compose supplied planar odometry increments and validate timestamp order and numeric values |
| Inspect | Summarize pose count, path length and time span; generate synthetic-example previews |
| Export | Export CSV, TUM text and a JSON summary |
| C++ + Python | Standard-library implementations with no private dependencies; includes output cross-checks between both implementations |

## Quick start

### C++ preview

Requires a C++17 compiler and CMake 3.16 or later. The default build includes checks, which also require Python 3.10 or later.

```bash
git clone https://github.com/Midoor98/RayCon-SLAM.git
cd RayCon-SLAM
bash run_cpp.sh
```

Outputs are written to a new `result/cpp-*` directory. To view the version and command-line options:

```bash
./build/raycon_slam_preview --version
./build/raycon_slam_preview --help
```

### Python preview

Uses only the Python standard library; no additional packages are required:

```bash
bash run.sh
bash run.sh --version
```

Both entry points accept `--input` and `--output`. The specified output directory must not already exist. See [Input formats](docs/INPUTS.md) for field definitions and data conventions. For a C++-only build without Python, configure CMake with `-DBUILD_TESTING=OFF`.

## Preview

![RayCon-SLAM synthetic data preview](docs/assets/demo-preview.png)

The 121 poses are produced from generated planar motion increments. The time shown is the input sequence duration, not execution time. This preview does not measure localization or reconstruction accuracy.

Generate the example data, run the C++ tool and render the preview:

```bash
python3 scripts/make_example.py
bash run_cpp.sh --input data/showcase_odometry.csv --output result/my-preview
python3 -m pip install -r requirements-preview.txt
python3 scripts/render_preview.py --input result/my-preview/trajectory.csv
```

`matplotlib` is required only to render previews; normal execution and tests do not depend on it. Choose a new `--output` directory for each run. See [Artwork](docs/ARTWORK.md) for the cover provenance and generation prompt.

## Roadmap

| Target | Planned public content | Status |
| --- | --- | --- |
| September 2026 · v0.1.0 | C++ / Python tools, synthetic data, export examples and preview images | Available |
| October 2026 | Refine data interfaces, example configurations and companion-tool documentation | Planned |
| November 2026 | Prepare the VI-SLAM system trial-run entry point and test examples | Planned |
| **December 2026 · v0.2 preview** | **Planned release of VI-SLAM trial-run code, example configurations and launch scripts** | **Tentative** |

The next version targets VI-SLAM system trial runs, with a tentative public release in December 2026. Final functionality, supported data and setup requirements will be specified in the corresponding GitHub Release.

## Build & checks

```bash
bash scripts/check.sh
```

Checks cover Python unit tests, a C++ Release build, output consistency between the two implementations, invalid inputs, protection of existing results and version reporting. The tools have been checked on Ubuntu with GCC. Platform-specific build artifacts are not included in the repository.

```text
cpp/                 C++17 source and small CSV utilities
src/                 Python implementation
data/                Synthetic fixtures only
scripts/             Checks, fixture generation and preview rendering
tests/               Unit tests and C++/Python cross-checks
docs/                Input reference and visual assets
CMakeLists.txt       Standalone C++ build
VERSION              Public preview version
```

## Feedback

Use [Issues](https://github.com/Midoor98/RayCon-SLAM/issues) to report problems with reproduction steps, ask about input formats or suggest improvements to the public tools. Please use synthetic or publicly shareable data when describing an issue.

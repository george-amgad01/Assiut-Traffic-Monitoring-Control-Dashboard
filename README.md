# 🚦 Assiut Smart Traffic Dashboard

A real-time dashboard for **cooperative multi-agent traffic signal control** across the nine
signalised intersections of Assiut City, Egypt. It runs the SUMO simulation on a background thread
and streams live per-junction metrics — queue length, waiting time, delay, throughput, CO₂ and
current signal phase — into an interactive map, so you can *watch* a reinforcement-learning policy
drive signals instead of reading a table of averages at the end.

| Mode | Flag | What it shows |
|---|---|---|
| **MAPPO** (default) | `--mode mappo` | Multi-Agent PPO with Graph Transformer + GRU + Lagrangian constraints |
| **Fixed-Time** | `--mode fixed` | The classical fixed-plan baseline, for comparison |

🏆 Developed as part of the **IEEE 1st Place Winning** Assiut Traffic Management System.

---

## Demo video

]
Watch the dashboard running against the live SUMO simulation: signal phases changing across the
nine intersections, congestion spreading through the road network, and the per-junction metrics
updating in real time.

**Link:** https://youtu.be/ED-FFY5QcNU

---

## Architecture

<img width="2314" height="2184" alt="diagram-export-6-13-2026-12_24_06-AM" src="https://github.com/user-attachments/assets/f050bfff-1d42-4098-84a1-1895696348f0" />

A full design document — the threading model, the Python↔JavaScript bridge, why a WebView was
chosen over native Qt, and the reasoning behind every tool — is in
**[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**.

---

## Contents

- [Why this exists](#why-this-exists)
- [Key features](#key-features)
- [Screenshots](#screenshots)
- [Repository structure](#repository-structure)
- [Setup](#setup)
- [Usage](#usage)
- [Keyboard shortcuts](#keyboard-shortcuts)
- [Runtime artefacts](#runtime-artefacts)
- [Tech stack](#tech-stack)
- [Standalone guarantee](#standalone-guarantee)

---

## Why this exists

The underlying research compares a learned multi-agent policy against a classical fixed-time
controller. Numbers alone — a mean delay, a mean queue — hide *where* the interesting behaviour is.
Which junction is starved? Which is over-served? Where does a green phase cascade into a downstream
queue? Averages cannot answer that.

This dashboard closes the loop between training and interpretation. The MAPPO trainer decides signal
phases; this application makes those decisions observable in real time, per intersection, on a real
map.

> **Relationship to the research codebase.** The full research project — trainer, baselines, SUMO
> network and the offline decision analyzer — lives in a separate repository. This one is a
> **standalone, self-contained application**: it carries its own copy of the simulation layer so it
> runs without that project present, and it does not import from or reference it. The trade-off is
> that the two copies must be re-synchronised when the research code changes materially. See
> [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full design rationale.

---

## Key features

Everything below is implemented in the current code.

**Live map instrumentation**
- **9 intersection markers** with congestion colouring and click-to-inspect popups
  (queue, wait, delay, throughput, CO₂, speed, NES score)
- **Road-segment colouring** — all 1,268 real network edges tinted by the congestion of the
  junctions they connect, so downstream spillback is visible
- **Animated vehicle layer** — up to 300 live vehicles, rotated by heading, coloured by type
- **Congestion heat system** — pulsing halos whose animation period scales inversely with local
  load, so overloaded junctions visibly beat faster
- **Mini-map** for a zoomed-out overview carrying the same live data
- **Click-to-spotlight** a single road segment for close inspection

**Analysis panels**
- **Per-junction ranking** scored by `throughput / (1 + delay)`, best and worst called out
- **Live KPI bar** — step count, NES, mean queue, mean delay, cumulative reward, mean wait, trip
  time, CO₂
- **Rolling charts** for queue, delay, reward and NES across the run
- **MAPPO vs Fixed-Time comparison panel** that records both modes and reports the delta
- **Episode tracker** that announces each new episode and summarises the previous NES

**Session tooling**
- **CSV and JSON export** of the full per-step session
- **PNG screenshot** of the current dashboard state

**Simulation control**
- `--mode`, `--seed`, `--steps`, `--no-gui` command-line flags
- Pause, vehicle, heat, compare, snapshot and mini-map toggles
- Keyboard shortcuts, a simulation clock and a working progress bar

---

## Screenshots

### Network overview

<img width="1916" height="960" alt="Screenshot 2026-06-07 203803" src="https://github.com/user-attachments/assets/4f0e1974-4387-47e8-aca5-74c4a3a5193c" />


### Intersection Spotlight

<img width="1554" height="905" alt="Screenshot 2026-06-07 204621" src="https://github.com/user-attachments/assets/31f0cfc6-a783-4cfc-8f66-e29216255ce2" />


### Intersection Ranking

<img width="426" height="449" alt="Screenshot 2026-06-07 213552" src="https://github.com/user-attachments/assets/87410643-79fe-4680-bc69-8d7096f09f3f" />

### Episode summary

<img width="353" height="178" alt="Screenshot 2026-06-07 194453" src="https://github.com/user-attachments/assets/a9068461-64b1-4718-981e-43a0614860b6" />

### Detail panels

<img width="352" height="281" alt="Screenshot 2026-06-07 210808" src="https://github.com/user-attachments/assets/13116a2f-9840-4a2a-af7b-f16153859a16" />

### CSV Summary (for machine learning identify gaps and problem solutions) 

<img width="1139" height="948" alt="Screenshot 2026-06-07 212810" src="https://github.com/user-attachments/assets/d0fe06fb-f4e2-4280-9b05-2c4f4ad75c87" />

---

## Repository structure

```
.
├── app/                          Presentation layer — knows nothing about reinforcement learning
│   ├── main.py                   Entry point — QApplication, CLI parsing, wiring
│   ├── window.py                 QMainWindow — hosts the WebEngineView, owns the JS bridge
│   └── worker.py                 SimWorker(QThread) — runs the simulation, emits signals
│
├── simulation/                   Research layer — knows nothing about Qt
│   ├── mappo_optimized_4.py      MAPPO trainer + environment (Graph Transformer, GRU, PPO)
│   ├── fixed_time_for_mappo_4.py Fixed-Time baseline controller
│   └── sumo_topology.py          Parses the .net.xml into a TLS adjacency graph
│
├── web/
│   └── assiut_map.html           The entire UI — map, markers, charts, panels, demo mode
│
├── sumo/                         All simulation inputs, in one flat folder
│   ├── project (2).sumocfg       Simulation configuration
│   ├── Version 3 George.net.xml  Road network — 1296 junctions, 4153 edges, 9 signals
│   ├── project (1).rou.xml       Traffic demand — 42 flows across 5 vehicle types
│   └── project (2).add.xml       98 lane-area detectors feeding the e2_*.xml outputs
│
├── docs/
│   └── ARCHITECTURE.md           Design rationale, tool choices, future work
│
├── results/                      Fixed-Time plots and logs — kept via .gitkeep
├── saved_models/                 MAPPO checkpoints and plots — created at runtime, git-ignored
├── requirements.txt
└── .gitignore / .gitattributes
```

### Which file does what

| File | Role |
|---|---|
| `app/main.py` | **Start here.** Parses flags, creates the Qt app, starts the worker, shows the window |
| `app/worker.py` | Owns the simulation thread. Emits live metrics as Qt signals |
| `app/window.py` | Owns the WebEngineView and translates signals into `runJavaScript` calls |
| `simulation/mappo_optimized_4.py` | The MAPPO agent, environment, PPO trainer and evaluator |
| `simulation/fixed_time_for_mappo_4.py` | The Fixed-Time baseline environment and evaluator |
| `simulation/sumo_topology.py` | Derives the TLS neighbour graph from the network file |
| `web/assiut_map.html` | Every pixel of the UI. No build step — edit and reload |

---

## Setup

### 1. Prerequisites

- **Python 3.10+**
- **SUMO 1.26+** — the network was generated with Eclipse SUMO netedit 1.26.0
- **Internet access at runtime** — the map loads Leaflet, Chart.js and html2canvas from a CDN and
  fetches OpenStreetMap tiles (see [Known issues](#known-issues))
- A CUDA GPU is optional; the code auto-detects and falls back to CPU

### 2. Install SUMO and set `SUMO_HOME`

`traci` ships inside the SUMO distribution and is **not** pip-installable.

```bash
# Linux / macOS
export SUMO_HOME=/path/to/sumo
export PYTHONPATH="$SUMO_HOME/tools:$PYTHONPATH"
```

```powershell
# Windows (PowerShell)
$env:SUMO_HOME = "C:\Program Files (x86)\Eclipse\Sumo"
$env:PYTHONPATH = "$env:SUMO_HOME\tools;$env:PYTHONPATH"
```

Setting `PYTHONPATH` is not strictly required — both modules in `simulation/` check `SUMO_HOME` at
import time, append `$SUMO_HOME/tools` to `sys.path` themselves, and raise a clear error if it is
unset. Setting it explicitly is still recommended, since it also makes `traci` importable from an
interactive shell.

### 3. Install Python dependencies

```bash
git clone https://github.com/<your-username>/assiut-traffic-dashboard.git
cd assiut-traffic-dashboard
pip install -r requirements.txt
```

> **PyQtWebEngine is a separate package from PyQt5.** Installing only `PyQt5` is the single most
> common setup failure — `app/window.py` imports `QtWebEngineWidgets`, which lives in
> `PyQtWebEngine`. On Linux you may also need the system WebEngine runtime packages.

---

## Usage

Run from the repository root.

```bash
# MAPPO mode (default) with the SUMO GUI
python app/main.py

# Fixed-Time baseline instead
python app/main.py --mode fixed

# Headless SUMO (no sumo-gui window)
python app/main.py --no-gui

# Reproducible run with an explicit seed and step budget
python app/main.py --seed 42 --steps 20000
```

| Flag | Default | Description |
|---|---|---|
| `--mode` | `mappo` | `mappo` or `fixed` |
| `--seed` | `42` | Random seed — keep it identical across modes to compare them fairly |
| `--steps` | from config | Override the simulation step budget |
| `--no-gui` | off | Run SUMO headless |

To compare the two modes properly, run each once with the **same** `--seed` and `--steps`.

### In the UI

| Control | Action |
|---|---|
| `Pause` | Freeze the dashboard clock (the simulation keeps running) |
| `Heat ON` | Toggle the congestion heat halos |
| `Cars ON` | Toggle the live vehicle layer |
| `Compare` | Show the MAPPO vs Fixed-Time delta panel |
| `Mini` | Toggle the overview mini-map |
| `Snap` | Save a PNG of the current view |
| `CSV` / `JSON` | Export the full session |

Click any intersection marker for a detail popup, or a road segment to spotlight it.

### Read this before you trust what you see

> ⚠️ **A fully animated dashboard is not evidence that the simulation is working.**

`web/assiut_map.html` contains a **built-in demo mode**. Until Python delivers the first real
metrics batch, it generates plausible-looking values with `Math.random()` and animates the entire
dashboard. The moment the backend connects, the demo stops and real data takes over.

This is genuinely useful — the UI can be demonstrated on a machine with no SUMO installed — but it
also means **a fully animated dashboard is not evidence that the simulation is working.** To confirm
a real run, look for the log line `Python backend connected — live SUMO data active` in the log
strip.

---

## Keyboard shortcuts

Active whenever focus is not in a text field.

| Key | Action |
|---|---|
| `Space` | Pause / resume |
| `H` | Toggle heat halos |
| `V` | Toggle vehicles |
| `C` | Toggle the comparison panel |
| `M` | Toggle the mini-map |
| `E` | Export CSV |
| `J` | Export JSON |
| `S` | Screenshot |
| `R` | Reset the map to the default view |
| `Esc` | Close the spotlight |

---

## Runtime artefacts

Nothing here is committed; all of it is produced when you run.

| Path | Written by | Contents |
|---|---|---|
| `saved_models/` | MAPPO mode | `mappo_<tag>.pt` checkpoints, `mappo_training.png`, `mappo_comparison.png`, `sumo_errors.log` |
| `results/` | Fixed-Time mode | `fixedtime_simulation_results.png`, `fixedtime_intersection_comparison.png`, `sumo_errors.log` |
| working directory | SUMO | `e2_*.xml` detector outputs (git-ignored) |



CSV and JSON session exports are written wherever you save them in the export dialog.

---

## Tech stack

Derived from the actual imports in this repository.

| Layer | Library | Why this one |
|---|---|---|
| Desktop shell | `PyQt5` | Mature, ubiquitous, first-class `QThread` support for the simulation thread |
| Map rendering | `PyQtWebEngine` (Chromium) | Rationale in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| Map library | Leaflet 1.9.4 (CDN) | Lightweight, no build step, excellent raster-tile support |
| Charts | Chart.js 4.4.1 (CDN) | Canvas charts with no framework dependency |
| Screenshot | html2canvas 1.4.1 (CDN) | Renders the live DOM to PNG without a server round-trip |
| Tiles | OpenStreetMap | Free, no API key, adequate for a city-scale view |
| Simulation | **SUMO 1.26** / `traci` | The de-facto standard for urban traffic microsimulation |
| Learning | `torch>=2.4` | Hard floor: the trainer uses the `torch.amp` device-type-first API |
| Numerics | `numpy>=1.24` | Array maths throughout the metric pipeline |
| Plotting | `matplotlib>=3.7` | End-of-run plots |

The standard library covers config (`dataclasses`), XML parsing (`xml.etree.ElementTree`) and the
JSON payloads crossing the bridge. The UI has **no build step** — there is no bundler, no npm and no
compile; `web/assiut_map.html` is edited directly.

---

## Standalone guarantee

This repository runs with **no external project dependency**. Everything it imports or opens is
committed here:

- All six Python modules, split across `app/` and `simulation/`
- The full SUMO network, demand file and detector configuration
- The complete UI

The only outside requirements are the ones a Python application cannot ship: the `traci` module
from your SUMO installation, the pip packages in `requirements.txt`, and internet access for the CDN
assets. No path, import or config in this repository points outside its own directory.


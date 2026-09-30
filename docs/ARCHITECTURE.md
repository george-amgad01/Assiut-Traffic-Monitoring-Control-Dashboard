# Architecture & System Design

> A design document for the Assiut Smart Traffic Dashboard: what problem it solves, how it is put
> together, why each technology was chosen, and where it should go next.

This document assumes you have read the [README](../README.md). It is about *why*, not *what*.

---

## Table of contents

1. [The problem this solves](#1-the-problem-this-solves)
2. [Design goals](#2-design-goals)
3. [System architecture](#3-system-architecture)
4. [The threading model](#4-the-threading-model)
5. [The Python ↔ JavaScript bridge](#5-the-python--javascript-bridge)
6. [Why a WebView for the UI](#6-why-a-webview-for-the-ui)
7. [Tool choices and their rationale](#7-tool-choices-and-their-rationale)
8. [Data flow: one step, end to end](#8-data-flow-one-step-end-to-end)
9. [The network as a graph](#9-the-network-as-a-graph)
10. [Design decisions worth questioning](#10-design-decisions-worth-questioning)
11. [Improvements, prioritised](#11-improvements-prioritised)
12. [What this project is not](#12-what-this-project-is-not)

---

## 1. The problem this solves

A reinforcement-learning traffic study produces numbers. Mean delay across the network. Mean queue
length. Improvement percentages against a baseline. Those numbers are necessary and they are also
deeply unsatisfying, for three reasons.

**Averages erase the interesting cases.** A policy can look excellent on average while starving one
junction for hours. The mean will not tell you which one, or when.

**Traffic is a spatial phenomenon.** Congestion is not a property of a junction in isolation — a
queue that spills back from a downstream junction is *caused* by that downstream junction. Any view
that flattens the network into a list of rows destroys the very structure the agent is reasoning
about.

**Decisions are continuous, results are not.** The interesting question is rarely "what was the final
score?" It is "what was the policy *doing* at the moment the third lane backed up?" That requires
watching it happen, in real time, at a speed where a human can form and test a hypothesis.

So the goal of this dashboard is narrow and concrete:

> **Make a multi-agent reinforcement-learning policy legible to a human, while it is running.**

Everything below follows from that one sentence.

---

## 2. Design goals

| # | Goal | Consequence in the design |
|---|---|---|
| G1 | Show the *network*, not a table | A geographic map with per-junction and per-segment state |
| G2 | Show it *live*, not post-hoc | Simulation on a background thread, metrics streamed per step |
| G3 | Make causality visible | Road segments coloured by the junctions they connect, so spillback is visible |
| G4 | Compare strategies fairly | A single seed and step budget across both modes, plus a delta panel |
| G5 | Zero build step for the UI | One HTML file, no bundler, no npm, no compile |
| G6 | Standalone and reproducible | No dependency on any other repository; all inputs committed |
| G7 | Degrade gracefully | A canvas fallback if the map tiles cannot be fetched |

Non-goals are listed explicitly in [§12](#12-what-this-project-is-not).

---

## 3. System architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          PROCESS BOUNDARY                              │
│                                                                        │
│  ┌──────────────────────────┐        ┌───────────────────────────────┐  │
│  │   Qt MAIN THREAD         │        │   SimWorker  (QThread)       │  │
│  │        app/              │        │         app/ + simulation/   │  │
│  │                          │        │                               │  │
│  │  main.py                 │        │  worker.py                   │  │
│  │   ├ parse_args()         │        │   ├ _run_mappo()  ──┐         │  │
│  │   ├ QApplication        │        │   └ _run_fixed()  ──┤         │  │
│  │   └ SimWorker(...)  ──────────────► │                   │         │  │
│  │                          │        │                   ▼         │  │
│  │  window.py              │        │   mappo_optimized_4.py       │  │
│  │   └ MainWindow          │        │    ├ MAPPOConfig             │  │
│  │      └ QWebEngineView   │        │    ├ SUMOMultiAgentEnv ──────┼──┐│  │
│  │         └─ loads web/   │        │    ├ MAPPOTrainer           ││  │
│  │                          │        │    └ IntersectionEvaluator ││  │
│  │   @pyqtSlot handlers    │        │                             ││  │
│  │    _on_metrics()        │        │                             ││  │
│  │    _on_vehicles()       │        │   fixed_time_for_mappo_4.py ││  │
│  │    _on_step()           │        │    └ BaselineConfig         ││  │
│  │    _on_log()            │        │      FixedTimeEnv           ││  │
│  │    _on_episode()        │        │      BaselineEvaluator      ││  │
│  │    _on_done()           │        │                             ││  │
│  │    _on_error()          │        │   sumo_topology.py          ││  │
│  └───────────┬──────────────┘        └──────────────┬──────────────┘  │
│              │ runJavaScript(...)                   │ SUMO server    │
│              │ (no return value used)               │ (subprocess)   │
│  ┌───────────▼──────────────────────────────────────▼──────────────┐  │
│  │                    CRITICAL: TraCI socket                        │  │
│  │        one connection, one owner, strict single-thread rule      │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
                    ┌────────────────────────────────┐
                    │   Chromium (QtWebEngine)      │
                    │   assiut_map.html             │
                    │   ├ Leaflet map + OSM tiles    │
                    │   ├ 9 TLS markers              │
                    │   ├ 1268 road segments         │
                    │   ├ vehicle layer              │
                    │   ├ heat halos                 │
                    │   ├ Chart.js panels            │
                    │   └ ranking / compare / export │
                    └────────────────────────────────┘
```

Two processes, really: this Python application, and SUMO itself. SUMO is launched as a subprocess
with a `remote-port` so that TraCI can attach to it. All traffic state lives in SUMO; Python reads
it and writes signal phases back over the same socket.

---

## 4. The threading model

This is the single most important structural decision in the project, and it is forced by TraCI.

**TraCI is not thread-safe.** It is a socket connection with a request/response protocol and no
locking. If two threads call into it, frames interleave and the simulation state corrupts in ways
that are extremely hard to diagnose. The rule is therefore absolute:

> **Only the simulation thread may touch TraCI.**

The dashboard respects this strictly:

- `SimWorker` subclasses `QThread`. Its `run()` executes the entire simulation — `trainer.train()`,
  `env.step()`, every `traci.*` call — on that one thread.
- The Qt main thread **never** calls TraCI. It only receives already-collected values.
- The GUI is never blocked. A 20,000-step PPO run with GPU updates would freeze the interface for
  minutes if it ran on the main thread; on a worker thread the map stays at 60 fps.

Communication is Qt's signal/slot mechanism. `SimWorker` declares six signals:

| Signal | Payload | Emitted when |
|---|---|---|
| `metrics_updated` | `str` (JSON) | Per-agent metric dict, every decision step |
| `vehicles_updated` | `str` (JSON) | Up to 300 vehicle positions, every decision step |
| `step_done` | `int` + 7 × `float` | `(step, nes, avg_q, avg_d, cum_rew, avg_w, avg_co2, trip_t)` |
| `event_log` | `str`, `str` | Human-readable message + severity |
| `episode_reset` | `int` | A new episode begins |
| `training_done` | — | Simulation finished or failed |
| `error_occurred` | `str` | Unhandled exception, with traceback |

### How the worker observes the trainer

The worker does not own the training loop, so it cannot simply be handed a callback. Instead it
**monkey-patches the trainer at runtime** — the only genuinely invasive technique in the codebase,
and worth calling out because it is both clever and fragile.

```python
original_log = trainer._log.__func__

def patched_log(self_trainer, step, cum_rew, dec_step):
    original_log(self_trainer, step, cum_rew, dec_step)   # keep console output
    ...                                                   # harvest metrics, emit signals

trainer._log = types.MethodType(patched_log, trainer)
```

`MAPPOTrainer._log` is called once per training iteration — a natural heartbeat. The patch calls
through to the original so console behaviour is unchanged, then harvests state and emits. The same
trick wraps `env.reset` to count episodes.

**Why this was chosen:** it requires no modification to the 1,700-line trainer, which is shared with
the research codebase. The alternative — adding a callback parameter to `_log` — would be cleaner
but would fork a file that is meant to stay identical to the research version.

**Why it is fragile:** it depends on the exact private signature of `_log`. If the trainer's logging
hook is renamed or its signature changes, the dashboard breaks with an `AttributeError` at startup
and fails *silently enough* that the cause is not obvious. See
[§11.1](#111-high-replace-the-monkey-patching).

---

## 5. The Python ↔ JavaScript bridge

There are two possible ways to get data from Python into a web view: a channel, or injected script.
This project uses the second, exclusively.

```python
js = (
    "if(typeof updateAllIntersections!=='undefined'){"
    f"  updateAllIntersections({metrics_json});"
    "}"
)
self._web.page().runJavaScript(js)
```

The pattern has three deliberate properties:

1. **JSON is embedded as a literal, not passed as a string.** `metrics_json` is spliced directly into
   the JavaScript source. This is safe because the payload is produced by `json.dumps` from numeric
   values, so it can never contain a backtick or a quote sequence that would break out of the
   literal. The code comments state this invariant explicitly.

2. **Every call is guarded by a `typeof` check.** If the HTML has not finished loading, or a function
   does not exist, the call is a no-op instead of a thrown exception. This is what lets the simulation
   start before the map is ready.

3. **No return values are used.** The bridge is strictly one-directional, Python → JavaScript. That
   removes the need for callback plumbing entirely.

The consequence is that **`window.py`'s `QWebChannel` is dead code.** A channel is constructed and
registered on the page (lines 56–57), but the HTML never calls `qt.webChannelTransport` and no slots
are exposed. It is harmless — just dead. It is listed in the README's known issues and should be
removed.

---

## 6. Why a WebView for the UI

The most consequential technology choice in the project is rendering the interface in a **Chromium
web view** rather than drawing it with Qt widgets.

**The alternative was a real Qt UI** — `QGraphicsView` with a custom scene for the map, QtCharts for
the graphs. It was rejected for five reasons:

**1. Mapping is a solved problem, and we would have been re-solving it.** Leaflet gives us pan, zoom,
tile loading, layer management, marker anchoring, popups and mobile touch handling — all free and all
battle-tested. A Qt equivalent is weeks of work to reach a fraction of that quality.

**2. Leaflet can draw arbitrary polylines, which is the whole point.** The congestion view colours
each of the 1,268 network road segments individually by the load of the junctions it connects. That
is a straightforward `L.polyline` per segment with a computed stroke colour. In Qt it means managing
thousands of `QGraphicsPathItem` objects and writing the geometry pipeline by hand.

**3. Animation is free in CSS.** The congestion halos pulse at a rate inversely proportional to
local load — a per-segment animation period of `(2.8 - load*2.3) * 1000` ms. Expressing that as a CSS
`setTimeout` per marker is a one-liner. The Qt equivalent is a `QTimer` and per-item opacity maths.

**4. Chart.js replaces a charting dependency.** Three rolling charts with a dark theme cost three
lines of CDN include. The Qt equivalent is either PyQtGraph (a new heavy dependency) or hand-rolled
`QPainter` work.

**5. It keeps the deliverable a single file.** `assiut_map.html` is 188 KB of self-contained UI
(apart from CDN assets). It can be opened in any browser, screenshotted, or handed to someone else
with no build step. This is goal G5, and it is genuinely valuable for a student project that others
may need to run.

**The honest cost:** a Chromium process is heavy. Launching the app starts a browser engine, and
memory usage is meaningfully higher than a pure Qt UI. On a machine with limited RAM this is a real
consideration. The `initCanvasFallback` path in the HTML is a partial hedge — if Leaflet cannot load,
a hand-rolled canvas renderer draws the network instead, so the map degrades rather than failing.

---

## 7. Tool choices and their rationale

### SUMO + TraCI

The de-facto standard for urban traffic microsimulation, and the only realistic option for a
nine-intersection network with realistic signal programs, turning movements and CO₂ emission models.
TraCI gives step-by-step control: read detector state, set the signal phase, advance the clock.

**The cost, which shaped the entire architecture:** TraCI is a socket with no thread safety. See
[§4](#4-the-threading-model).

### PyQt5 + PyQtWebEngine

`QThread` and the signal/slot model are the reason for choosing Qt over any other desktop toolkit —
the simulation/UI split needs a first-class thread abstraction with queued cross-thread delivery, and
Qt has had that for two decades. `PyQtWebEngine` then supplies the Chromium view for §6.

`PyQtWebEngine` is packaged **separately** from `PyQt5`, which is the most common installation
failure for this project. It is called out in the README and the requirements file.

### PyTorch

Not a free choice — the MAPPO implementation requires it, and specifically requires **2.4 or newer**,
because the trainer calls `torch.amp.autocast('cuda', ...)` and `GradScaler('cuda', ...)` with a
device-type-first signature introduced in that release. The floor is real and is documented.

The trainer also uses `torch.compile` (Triton), but detects Windows and disables it, because Triton
does not support that platform.

### Leaflet, Chart.js, html2canvas, OpenStreetMap

All four are CDN-loaded rather than vendored, which is a deliberate trade: it keeps the repository
small and the build trivial, at the cost of a hard internet dependency at runtime. The
[§11.5](#115-high-vendor-the-cdn-assets-or-accept-the-dependency) section weighs whether to change
that.

OpenStreetMap was chosen over any keyed tile provider because it needs no account, no API key and no
billing — important for a project that will be run by many people.

### NumPy / Matplotlib

NumPy for the per-step metric aggregation (`np.mean` across junctions, emitted every decision step).
Matplotlib only for the end-of-run plots written to `results/` — the live charts are Chart.js, so
Matplotlib is a training-time dependency, not a UI one.

---

## 8. Data flow: one step, end to end

Following a single decision step through the whole system:

```
1.  MAPPOTrainer.train()                    [worker thread]
        └─ env.step(actions)
              ├─ writes signal phases ──────────────┐
              └─ traci.simulationStep()            │
                                                     ▼
2.  SUMO advances; TraCI returns new state
        └─ traci.vehicle.*, traci.lanearea.*, traci.trafficlight.*

3.  trainer._log(step, cum_rew, dec_step)         ← the monkey-patch heartbeat
        ├─ original_log(...)                      console output preserved
        ├─ env.get_per_agent_metrics()             {tls_id: {queue, wait, delay, ...}}
        ├─ _build_agents_payload(env)              + phase, num_phases from traci.trafficlight
        └─ _build_vehicle_positions()              up to 300 × {x, y, angle, speed, type}

4.  JSON-encode and emit                         [Qt queued connection]
        metrics_updated.emit(json.dumps(agents))
        vehicles_updated.emit(json.dumps(vehicles))
        step_done.emit(step, nes, avg_q, ...)

5.  MainWindow @pyqtSlot handlers                 [main thread]
        └─ self._web.page().runJavaScript(js)

6.  Chromium executes JS
        ├─ updateAllIntersections(m)  → marker icons, road colours, KPIs, ranking
        ├─ updateVehicles(v)          → vehicle markers, rotated by heading
        └─ updateStatsBar(...)        → top bar, charts
```

Step 6 is where SUMO's metre-based coordinates become map positions. The HTML converts them with a
fixed SUMO origin (`NET_OX=-317785.18`, `NET_OY=-3006446.53` — UTM Zone 36N) into WGS84
latitude/longitude, which is why the markers land on the correct real-world streets.

---

## 9. The network as a graph

`sumo_topology.py` is what stops this dashboard from being a pretty picture of a meaningless
simulation. The MAPPO agent does not treat junctions as independent — it communicates over a graph.
That graph has to be derived from the *real* network, and deriving it robustly is harder than it
sounds.

The parser reads the `.net.xml` and reconstructs which traffic lights are neighbours, using five
escalating strategies so that no agent is ever left isolated:

| | Strategy | Purpose |
|---|---|---|
| **A** | Direct edge connection | Junctions sharing a road are neighbours |
| **B** | BFS through non-signalised junctions | Reach signals up to 6 hops away |
| **C** | Geographic proximity | Connect signals within 800 m |
| **D** | Minimum-degree backfill | Give leaf nodes at least 2 neighbours |
| **E** | Component stitching | Join disconnected components if within 2 km |

The result is a distance-weighted adjacency matrix, `1/(1 + d/500)` per edge, which becomes the
attention mask for the Graph Transformer.

The dashboard consumes this indirectly but importantly: the nine `TLS_META` entries in the HTML are
keyed by **exact SUMO traffic-light program IDs**, and those IDs only exist because the network was
parsed. All nine were verified to resolve against the network's nine programs. If they had not
matched, every marker would silently fail to update — the map would render, and simply show nothing
happening.

---

## 10. Design decisions worth questioning

Honest self-criticism, because these are the parts most likely to be wrong.

**The monkey-patching is too clever.** It avoids touching a shared 1,700-line file, at the cost of
binding to a private method signature. A callback parameter would be more honest. See
[§11.1](#111-high-replace-the-monkey-patching).

**The QWebChannel is dead code** that has never been removed. Small, but it misleads the next
reader into thinking there is a bidirectional channel.

**Per-step JSON over a string signal is wasteful.** Every decision step serialises two JSON payloads
and hands them to a browser that parses them. At `decision_interval=5` over 20,000 steps that is
4,000 round trips of string allocation. It works, and it is simple, but it is not efficient — and the
vehicle payload alone can be 300 objects.

**The CDN dependency is a real fragility.** A student demo on university Wi-Fi, or a reviewer
offline, gets a degraded experience. It is the most likely thing to make this project look broken
when it is fine.

**`"emergency": False` is hardcoded** in both metric paths, so the emergency-vehicle visual
behaviour in the HTML can never actually trigger from live data. The infrastructure is there and
unfed.

**The demo mode is a double-edged sword.** It makes the UI demonstrable with no backend at all — but
it also means a broken integration looks identical to a working one. It should be disabled by
default, or gated behind an explicit flag.

---

## 11. Improvements, prioritised

Ordered by value against effort. H = high priority, M = medium, L = low.

### 11.1 (H) Replace the monkey-patching

Add an optional observer callback to `MAPPOTrainer._log`, and an episode hook to `SUMOMultiAgentEnv`,
instead of rebinding methods at runtime. Removes the coupling to a private signature, makes the
integration explicit and greppable, and fails loudly at import time rather than mysteriously at
startup.

*Effort: small. Value: removes the single most fragile thing in the codebase.*

### 11.2 (H) Gate the demo mode behind a flag

Add `?demo=1` (or a `--demo` CLI flag) so the synthetic feed only runs when explicitly requested.
Log a persistent, visible banner while it is active. This eliminates the most likely cause of a
misleading demonstration.

*Effort: very small. Value: eliminates a whole class of confusion.*

### 11.3 (H) Vendor the CDN assets

Copy Leaflet, Chart.js and html2canvas into `vendor/` and reference them relatively. Roughly 1 MB,
and it makes the dashboard genuinely offline-capable — no internet, no degraded charts, no CDN
outage. Given that this is a university project likely to be demoed in venues with unreliable
networking, this is worth more than its size suggests.

*Effort: small (download and commit four files). Value: removes the top runtime fragility.*

### 11.4 (M) Move to a real bidirectional channel

Register a `QWebChannel` slot and have the JavaScript call it, rather than injecting script strings
in one direction. This is what the dead channel in `window.py` was presumably for. It would allow
the UI to request state, and would let the map acknowledge a pause rather than the Python side
assuming it.

*Effort: medium. Value: cleaner architecture, enables genuinely interactive controls.*

### 11.5 (M) Feed the emergency-vehicle field

The trainer already classifies emergency, heavy and police vehicle types. `worker.py` hardcodes
`"emergency": False`. Surfacing the real classification would activate the emergency-vehicle
rendering already present in the HTML and make a genuine research contribution visible in the UI.

*Effort: small. Value: makes existing code do what it was written to do.*

### 11.6 (M) Persist runs and compare across sessions

Write per-run metrics to disk as JSON, and let the comparison panel span separate invocations rather
than only the two modes within one run. This is what turns a toy comparison into a usable experiment
log.

*Effort: medium. Value: supports the research workflow directly.*

### 11.7 (M) Support checkpoint loading

MAPPO mode currently trains from scratch every launch, so the first run of the day is spent waiting.
Adding `--checkpoint` to load a saved policy would make the dashboard immediately useful for
inspection without a full training run.

*Effort: small. Value: large — turns a multi-minute wait into an instant view.*

### 11.8 (L) Batch the metric payloads

Emit on a fixed 30–60 ms timer rather than every decision step, and send deltas rather than full
state. Removes most of the JSON churn described in §10.

*Effort: medium. Value: performance only; not needed at the current scale.*

### 11.9 (DONE) Split the flat namespace into app/ and simulation/

The project previously kept all six Python modules in a single flat directory. They are now split by
layer:

- `app/` — `main.py`, `window.py`, `worker.py`. The presentation layer; knows nothing about
  reinforcement learning.
- `simulation/` — `mappo_optimized_4.py`, `fixed_time_for_mappo_4.py`, `sumo_topology.py`. The
  research layer; knows nothing about Qt.
- `web/` — `assiut_map.html`, the UI asset that `window.py` loads.

This is the layer split described in [§3](#3-system-architecture), made physical in the filesystem.
The one behavioural consequence is that both `main.py` and `worker.py` now put `app/` *and*
`simulation/` on `sys.path` at startup, since neither is importable as a package.

> A latent bug was fixed in the same pass: `worker.py` previously inserted its **parent** directory
> onto `sys.path`, which for the old flat layout meant `D:\` — searched *ahead* of the project
> directory. It worked only because nothing shadowed the module names there.

### 11.10 (L) Add a regression test for the TLS ID mapping

A ten-line test asserting that every `TLS_META` key in the HTML exists in the network would prevent
the silent-failure mode described in §9 — where the map renders perfectly and shows nothing.

*Effort: very small. Value: prevents a genuinely confusing class of bug.*

---

## 12. What this project is not

Stating boundaries is part of design.

**Not the research codebase.** The MAPPO trainer, the offline decision analyzer and the training
history live in the primary project repository. This repository is the visualisation layer and
carries its own copy of the trainer purely so that it runs standalone. The two will drift; when the
research code changes materially, this copy must be re-synchronised deliberately.

**Not a traffic engineering tool.** The signals are simulated. Nothing here touches real hardware,
and the results say nothing about a real intersection without a real-world study on top.

**Not a validated result.** This is a monitoring and interpretation aid. The performance claims come
from the research project; this dashboard makes them inspectable but does not establish them.

**Not offline-first.** Despite improvements §11.3, the current version needs internet for its CDN
assets and map tiles.

---

*Assiut Smart Traffic Dashboard — Sphinx University, Faculty of Computers and Artificial
Intelligence, 2026. Released under the MIT License.*

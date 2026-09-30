"""
===========================================================================
 window.py — Main Dashboard Window (HTML-only layout)  FIXED v3
===========================================================================
 Fixes:
   [FIX-1] _on_step signal signature matches worker: 8 args not 5
   [FIX-2] vehicles_updated signal connected
   [FIX-3] MAP_HTML points to assiut_map.html (same folder)
   [FIX-4] QWebEngineSettings applied before setUrl (critical for tiles)
   [FIX-5] _on_metrics uses raw JSON safely (no double-escape)
===========================================================================
"""

import os
import json

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtCore    import Qt, QUrl, QTimer, pyqtSlot
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtWebChannel import QWebChannel

# ── Map HTML — lives in web/, one level up from app/ ───────────
MAP_HTML = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "web", "assiut_map.html"
)


class MainWindow(QMainWindow):

    def __init__(self, worker, parent=None):
        super().__init__(parent)
        self.worker    = worker
        self._sim_sec  = 0
        self._paused   = False

        self.setStyleSheet("QMainWindow,QWidget{background:#0a0e1a;}")
        central = QWidget()
        self.setCentralWidget(central)
        lay = QVBoxLayout(central)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # ── WebEngineView ─────────────────────────────────────────
        self._web = QWebEngineView()

        # [FIX-4] Settings MUST be set before loading URL
        s = self._web.settings()
        s.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        s.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls,   True)
        s.setAttribute(QWebEngineSettings.JavascriptEnabled,               True)
        s.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows,        True)
        s.setAttribute(QWebEngineSettings.AllowRunningInsecureContent,     True)
        s.setAttribute(QWebEngineSettings.ScrollAnimatorEnabled,           False)

        # [FIX-3] QWebChannel registered BEFORE setUrl
        self._channel = QWebChannel()
        self._web.page().setWebChannel(self._channel)

        # [FIX-3] Verify file exists
        if not os.path.isfile(MAP_HTML):
            from PyQt5.QtWidgets import QLabel
            lbl = QLabel(
                f"⚠  Map file not found:\n{MAP_HTML}\n\n"
                "Place assiut_map.html in the web/ folder"
            )
            lbl.setStyleSheet(
                "color:#ffab40;font-size:14px;background:#0a0e1a;"
                "padding:30px;")
            lbl.setWordWrap(True)
            lay.addWidget(lbl)
        else:
            self._web.setUrl(QUrl.fromLocalFile(MAP_HTML))

        self._web.loadFinished.connect(self._on_map_loaded)
        lay.addWidget(self._web)

        # ── Connect worker signals ─────────────────────────────────
        self.worker.metrics_updated.connect(self._on_metrics)
        # [FIX-2] vehicle positions
        if hasattr(self.worker, 'vehicles_updated'):
            self.worker.vehicles_updated.connect(self._on_vehicles)
        # [FIX-1] 8-arg step signal
        self.worker.step_done.connect(self._on_step)
        self.worker.event_log.connect(self._on_log)
        self.worker.episode_reset.connect(self._on_episode)
        self.worker.training_done.connect(self._on_done)
        self.worker.error_occurred.connect(self._on_error)

        self._clock = QTimer(self)
        self._clock.timeout.connect(self._tick)
        self._clock.start(1000)

    # ── Safe JS runner ────────────────────────────────────────────
    def _js(self, code: str):
        self._web.page().runJavaScript(code)

    # ── Map loaded ────────────────────────────────────────────────
    @pyqtSlot(bool)
    def _on_map_loaded(self, ok: bool):
        if ok:
            self._js("typeof addLog!=='undefined' && "
                     "addLog('PyQt5 connected — MAPPO live feed active','info')")
        else:
            print(f"[WARN] Map failed to load: {MAP_HTML}")

    # ── Per-agent metrics → update map markers ────────────────────
    @pyqtSlot(str)
    def _on_metrics(self, metrics_json: str):
        # [FIX-5] Pass JSON directly inside JS template literal — safe
        # because JSON never contains backticks
        js = (
            "if(typeof updateAllIntersections!=='undefined'){"
            f"  updateAllIntersections({metrics_json});"
            "}"
        )
        self._js(js)

    # ── Vehicle positions → animate on map ───────────────────────
    @pyqtSlot(str)
    def _on_vehicles(self, vehicles_json: str):
        js = (
            "if(typeof updateVehicles!=='undefined'){"
            f"  updateVehicles({vehicles_json});"
            "}"
        )
        self._js(js)

    # ── Step stats → update stats bar ────────────────────────────
    # [FIX-1] Must match worker signal: (int, float×7)
    @pyqtSlot(int, float, float, float, float, float, float, float)
    def _on_step(self, step: int, nes: float,
                 avg_q: float, avg_d: float, cum_reward: float,
                 avg_w: float, avg_co2: float, trip_t: float):
        mode = self.worker.mode.upper()
        js = (
            # Tell the dashboard which mode is running (routes cmpStore data correctly)
            f"if(typeof window.setSimMode!=='undefined')window.setSimMode('{mode}');"
            f"if(typeof updateStatsBar!=='undefined'){{"
            f"  updateStatsBar({step},{nes:.4f},{avg_q:.2f},{avg_d:.2f},'{mode}');"
            f"}}"
            # update reward pill if it exists
            f"var r=document.getElementById('tRew');"
            f"if(r)r.textContent='{cum_reward:.1f}';"
            # update extra pills if they exist
            f"var w=document.getElementById('tWait');"
            f"if(w)w.textContent='{avg_w:.1f}s';"
            f"var t=document.getElementById('tTrip');"
            f"if(t)t.textContent='{trip_t:.1f}s';"
        )
        self._js(js)

    # ── Log events ────────────────────────────────────────────────
    @pyqtSlot(str, str)
    def _on_log(self, message: str, level: str):
        safe = message.replace("'", "\\'").replace('\n', ' ')[:200]
        self._js(f"typeof addLog!=='undefined' && addLog('{safe}','{level}')")

    # ── Episode reset ─────────────────────────────────────────────
    @pyqtSlot(int)
    def _on_episode(self, ep: int):
        self._js(f"typeof updateEpisode!=='undefined' && updateEpisode({ep})")

    # ── Training done ─────────────────────────────────────────────
    @pyqtSlot()
    def _on_done(self):
        self._js("typeof addLog!=='undefined' && "
                 "addLog('✅ Simulation complete','info')")

    # ── Error ─────────────────────────────────────────────────────
    @pyqtSlot(str)
    def _on_error(self, error_msg: str):
        safe = error_msg[:120].replace("'", "\\'").replace('\n', ' ')
        self._js(f"typeof addLog!=='undefined' && addLog('❌ {safe}','emg')")
        print(f"[ERROR] {error_msg}")

    # ── Clock ─────────────────────────────────────────────────────
    def _tick(self):
        if not self._paused:
            self._sim_sec += 1

    # ── Shutdown ──────────────────────────────────────────────────
    def closeEvent(self, event):
        self._clock.stop()
        self.worker.stop()
        self.worker.wait(3000)
        event.accept()

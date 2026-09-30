"""
===========================================================================
 worker.py — Simulation Worker Thread  (FIXED v3)
===========================================================================
 Fixes:
   [F1] Removed _apply_emergency hook — mappo_optimized_4 doesn't have it
   [F2] MAP_HTML name corrected to assiut_map_FINAL.html
   [F3] patched_log matches mappo_optimized_4._log(self, step, cum_rew, dec_step)
   [F4] step_info keys match mappo_optimized_4: 'mean_co2','mean_delay'
        (no 'emergency_mask' key in this version)
   [F5] vehicle positions collected correctly every decision step
   [F6] _total_steps set from cfg so progress bar works
===========================================================================
"""

import os
import sys
import json
import math
import time
import traceback
import numpy as np

from PyQt5.QtCore import QThread, pyqtSignal

_APP_DIR   = os.path.dirname(os.path.abspath(__file__))      # app/
_REPO_ROOT = os.path.dirname(_APP_DIR)                       # repository root/
for _p in (_APP_DIR, os.path.join(_REPO_ROOT, "simulation")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


class SimWorker(QThread):

    # ── Signals ──────────────────────────────────────────────────────
    metrics_updated  = pyqtSignal(str)   # JSON per-agent metrics dict
    vehicles_updated = pyqtSignal(str)   # JSON vehicle positions list
    # step, nes, avg_q, avg_d, cum_rew, avg_w, avg_co2, trip_t
    step_done        = pyqtSignal(int, float, float, float, float, float, float, float)
    event_log        = pyqtSignal(str, str)   # message, level
    episode_reset    = pyqtSignal(int)
    training_done    = pyqtSignal()
    error_occurred   = pyqtSignal(str)

    def __init__(self, mode="mappo", seed=42, steps=None, use_gui=False, parent=None):
        super().__init__(parent)
        self.mode         = mode
        self.seed         = seed
        self.steps        = steps
        self.use_gui      = use_gui
        self._stop        = False
        self._total_steps = steps or 20_000

    # ── Entry ─────────────────────────────────────────────────────────
    def run(self):
        try:
            if self.mode == "mappo":
                self._run_mappo()
            else:
                self._run_fixed()
        except Exception as e:
            self.error_occurred.emit(f"{e}\n\n{traceback.format_exc()}")
        finally:
            self.training_done.emit()

    def stop(self):
        self._stop = True

    # ─────────────────────────────────────────────────────────────────
    #  SHARED HELPERS
    # ─────────────────────────────────────────────────────────────────

    @staticmethod
    def _build_agents_payload(env):
        """Build per-intersection JSON dict from TraCI + env metrics."""
        import traci
        m = env.get_per_agent_metrics()
        payload = {}
        for tls_id, vals in m.items():
            try:
                phase = traci.trafficlight.getPhase(tls_id)
                np_   = len(traci.trafficlight.getAllProgramLogics(tls_id)[0].phases)
            except Exception:
                phase, np_ = 0, 4

            payload[tls_id] = {
                "queue":      round(vals['queue_length'], 2),
                "wait":       round(vals['waiting_time'], 2),
                "delay":      round(vals['delay'],        2),
                "throughput": round(vals['throughput'],   2),
                "co2":        round(vals['co2'],          1),
                "speed":      round(vals['speed'],        2),
                "phase":      phase,
                "num_phases": np_,
                "emergency":  False,
            }
        return payload, m

    @staticmethod
    def _build_vehicle_positions():
        """Collect live vehicle positions from TraCI (SUMO x,y metres)."""
        import traci
        vehicles = []
        try:
            for v in traci.vehicle.getIDList()[:300]:
                try:
                    x, y  = traci.vehicle.getPosition(v)
                    vehicles.append({
                        "id":    v,
                        "x":     round(x, 1),
                        "y":     round(y, 1),
                        "angle": round(traci.vehicle.getAngle(v), 1),
                        "speed": round(traci.vehicle.getSpeed(v), 2),
                        "type":  traci.vehicle.getTypeID(v),
                    })
                except Exception:
                    pass
        except Exception:
            pass
        return vehicles

    # ─────────────────────────────────────────────────────────────────
    #  MAPPO MODE
    # ─────────────────────────────────────────────────────────────────

    def _run_mappo(self):
        from mappo_optimized_4 import (
            MAPPOConfig, SUMOMultiAgentEnv, MAPPOTrainer, IntersectionEvaluator
        )

        cfg          = MAPPOConfig()
        cfg.seed     = self.seed
        cfg.use_gui  = self.use_gui
        if self.steps:
            cfg.total_steps = self.steps
        self._total_steps = cfg.total_steps   # [F6]

        self.event_log.emit(
            f"MAPPO starting — seed={cfg.seed}  "
            f"steps={cfg.total_steps:,}  "
            f"decision_interval={cfg.decision_interval}", "info"
        )

        env     = SUMOMultiAgentEnv(cfg)
        trainer = MAPPOTrainer(cfg, env)

        # ── Monkey-patch trainer._log ─────────────────────────────────
        # mappo_optimized_4._log signature: (self, step, cum_rew, dec_step)
        original_log = trainer._log.__func__
        worker_ref   = self

        def patched_log(self_trainer, step, cum_rew, dec_step):
            # 1. Call original for console output
            original_log(self_trainer, step, cum_rew, dec_step)

            if worker_ref._stop:
                return

            try:
                agents_payload, m = SimWorker._build_agents_payload(
                    self_trainer.env)

                avg_q   = float(np.mean([v['queue_length'] for v in m.values()]))
                avg_wt  = float(np.mean([v['waiting_time'] for v in m.values()]))
                avg_d   = float(np.mean([v['delay']        for v in m.values()]))
                avg_co2 = float(np.mean([v['co2']          for v in m.values()]))
                avg_thr = float(np.mean([v['throughput']   for v in m.values()]))
                tt      = self_trainer.env.get_mean_trip_time()
                nes     = avg_thr / (1.0 + avg_d) if (1.0 + avg_d) > 0 else 0.0

                vehicles = SimWorker._build_vehicle_positions()

                worker_ref.metrics_updated.emit(json.dumps(agents_payload))
                worker_ref.vehicles_updated.emit(json.dumps(vehicles))
                worker_ref.step_done.emit(
                    step, nes, avg_q, avg_d,
                    float(cum_rew), avg_wt, avg_co2, tt
                )
            except Exception as ex:
                worker_ref.event_log.emit(
                    f"Metrics emit error: {ex}", "warn")

        import types
        trainer._log = types.MethodType(patched_log, trainer)

        # ── Episode reset hook ────────────────────────────────────────
        original_reset = env.reset
        ep_count = [0]

        def patched_reset():
            obs, info = original_reset()
            ep_count[0] += 1
            worker_ref.episode_reset.emit(ep_count[0])
            worker_ref.event_log.emit(
                f"Episode {ep_count[0]} started — seed={cfg.seed}", "warn")
            return obs, info

        env.reset = patched_reset

        # ── Run ───────────────────────────────────────────────────────
        self.event_log.emit("SUMO connecting...", "info")
        trainer.train()

        # ── Post-training eval ────────────────────────────────────────
        self.event_log.emit("Training complete — running evaluation...", "info")
        try:
            evaluator = IntersectionEvaluator(cfg)
            results   = evaluator.evaluate(
                env, trainer.network, env.feature_extractor,
                label="Post-Training Evaluation"
            )
            self.event_log.emit(
                f"✅ NES={results['nes']:.4f} | "
                f"Best: {results['ranking'][0]['tls_id']}", "info"
            )
        except Exception as e:
            self.event_log.emit(f"Eval error (non-fatal): {e}", "warn")

        env.close()

    # ─────────────────────────────────────────────────────────────────
    #  FIXED-TIME MODE
    # ─────────────────────────────────────────────────────────────────

    def _run_fixed(self):
        try:
            from fixed_time_for_mappo_4 import (
                BaselineConfig, FixedTimeEnv, BaselineEvaluator
            )
        except ImportError:
            try:
                from fixed_time_baseline import (
                    BaselineConfig, FixedTimeEnv, BaselineEvaluator
                )
            except ImportError:
                self.error_occurred.emit(
                    "Cannot import fixed-time module.\n"
                    "Expected: fixed_time_for_mappo_4.py or fixed_time_baseline.py")
                return

        cfg          = BaselineConfig()
        cfg.seed     = self.seed
        cfg.use_gui  = self.use_gui
        if self.steps:
            cfg.total_steps = self.steps
        self._total_steps = cfg.total_steps

        self.event_log.emit(
            f"Fixed-Time starting — seed={cfg.seed}  "
            f"steps={cfg.total_steps:,}", "info"
        )

        env = FixedTimeEnv(cfg)
        env.start()
        self.event_log.emit("SUMO connected — fixed-time signals active", "info")

        import traci
        cum_reward = 0.0
        start_time = time.time()

        for sim_step in range(cfg.total_steps):
            if self._stop:
                self.event_log.emit("Stopped by user", "warn")
                break

            traci.simulationStep()
            env.sim_step = sim_step + 1
            env._update_trip_log()

            if (sim_step + 1) % cfg.decision_interval == 0:
                metrics = env._get_per_agent_metrics()

                avg_q   = float(np.mean([metrics[t]['queue_length'] for t in env.tls_ids]))
                avg_wt  = float(np.mean([metrics[t]['waiting_time'] for t in env.tls_ids]))
                avg_d   = float(np.mean([metrics[t]['delay']        for t in env.tls_ids]))
                avg_co2 = float(np.mean([metrics[t]['co2']          for t in env.tls_ids]))
                avg_thr = float(np.mean([metrics[t]['throughput']   for t in env.tls_ids]))
                trip_t  = env._get_mean_trip_time()
                nes     = avg_thr / (1.0 + avg_d) if (1.0 + avg_d) > 0 else 0.0
                cum_reward += -(avg_d / max(cfg.max_wait, 1.0)) \
                              - 0.05 * avg_q / max(cfg.max_cars, 1.0)

                # Per-agent payload
                agents_payload = {}
                for tls_id, vals in metrics.items():
                    try:
                        phase = traci.trafficlight.getPhase(tls_id)
                        np_   = len(traci.trafficlight.getAllProgramLogics(tls_id)[0].phases)
                    except Exception:
                        phase, np_ = 0, 4
                    agents_payload[tls_id] = {
                        "queue":      round(vals['queue_length'], 2),
                        "wait":       round(vals['waiting_time'], 2),
                        "delay":      round(vals['delay'],        2),
                        "throughput": round(vals['throughput'],   2),
                        "co2":        round(vals['co2'],          1),
                        "speed":      round(vals['speed'],        2),
                        "phase":      phase,
                        "num_phases": np_,
                        "emergency":  False,
                    }

                vehicles = SimWorker._build_vehicle_positions()

                self.metrics_updated.emit(json.dumps(agents_payload))
                self.vehicles_updated.emit(json.dumps(vehicles))
                self.step_done.emit(
                    sim_step + 1, nes, avg_q, avg_d,
                    cum_reward, avg_wt, avg_co2, trip_t
                )

                if (sim_step + 1) % (cfg.log_interval or 100) == 0:
                    pct = 100.0 * (sim_step + 1) / cfg.total_steps
                    self.event_log.emit(
                        f"[{pct:4.1f}%] Step {sim_step+1:,} | "
                        f"Q={avg_q:.1f} D={avg_d:.1f}s NES={nes:.3f}", "info"
                    )

            if traci.simulation.getMinExpectedNumber() <= 0:
                self.event_log.emit(
                    f"All vehicles finished at step {sim_step+1:,}", "info")
                break

        elapsed = time.time() - start_time
        self.event_log.emit(
            f"Fixed-Time done — {elapsed:.0f}s | "
            f"Completed trips: {len(env._completed_trips)}", "info"
        )
        env.close()

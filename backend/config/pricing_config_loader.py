# pricing_config_loader.py
# This module is responsible only for loading, validating, and providing the active configuration.

import os
import time
import threading
import yaml
import datetime
import random
from decimal import Decimal

class PricingConfig:
    def __init__(self, path: str, reload_interval: int = 60):
        self.path = path
        self.config = {}
        self.lock = threading.Lock()
        self.reload_interval = reload_interval
        self.last_modified = 0
        self.load_config()
        self._start_watcher()

    def load_config(self):
        """Load YAML config and validate; fallback to previous if invalid."""
        try:
            modified_time = os.path.getmtime(self.path)
            if modified_time == self.last_modified:
                return  # no changes

            with open(self.path, "r") as f:
                cfg = yaml.safe_load(f)

            self._validate(cfg)

            with self.lock:
                self.config = cfg
                self.last_modified = modified_time
            print(f"✅ Pricing config loaded: {self.path}")

        except Exception as e:
            print(f"⚠️ Pricing config load failed: {e}")
            # Keep previous config in memory

    def _validate(self, cfg):
        """Validate economic constraints, rounding, time multipliers."""
        default = cfg.get("default", {})
        min_rate = cfg.get("economic_constraints", {}).get("min_driver_rate_tjs_per_km", 1.5)
        max_rate = cfg.get("economic_constraints", {}).get("max_driver_rate_tjs_per_km", 3.0)
        per_km_rate = Decimal(default.get("per_km_rate_tjs", 0))
        if not (min_rate <= per_km_rate <= max_rate):
            raise ValueError(f"per_km_rate {per_km_rate} violates constraints ({min_rate}-{max_rate})")

        rounding = default.get("rounding_tjs", [0.5, 1, 3, 5])
        if not all(d in [0.5, 1, 3, 5] for d in rounding):
            raise ValueError(f"Invalid rounding denominations: {rounding}")

        for tb in cfg.get("time_based_multipliers", {}).values():
            start, end = tb.get("start_hour"), tb.get("end_hour")
            if not (0 <= start <= 23 and 0 <= end <= 23):
                raise ValueError(f"Invalid time range: {start}-{end}")

    def _start_watcher(self):
        """Background thread to hot-reload config periodically."""
        def watch():
            while True:
                try:
                    self.load_config()
                    time.sleep(self.reload_interval)
                except Exception as e:
                    print(f"Error in config watcher: {e}")

        t = threading.Thread(target=watch, daemon=True)
        t.start()

    def get_active_config(self, zone=None, current_hour=None):
        """Return config active for given zone and hour."""
        with self.lock:
            cfg = self.config.get("default", {}).copy()

            # Zone override
            if zone and zone in self.config.get("zone_overrides", {}):
                cfg.update(self.config["zone_overrides"][zone])

            # Time-based multiplier
            if current_hour is None:
                current_hour = datetime.datetime.utcnow().hour
            for tb in self.config.get("time_based_multipliers", {}).values():
                if tb["start_hour"] <= current_hour < tb["end_hour"]:
                    cfg["surge_multiplier"] = tb["surge_multiplier"]
                    break
            else:
                cfg["surge_multiplier"] = 1.0

            # Random A/B test variant
            ab_tests = self.config.get("ab_tests", [])
            if ab_tests:
                test = random.choice(ab_tests)
                cfg.update({k: v for k, v in test.items() if k not in ["experiment_name", "variant", "start_date", "end_date"]})
                cfg["ab_test_variant"] = test.get("variant")

            return cfg

"""Raspberry Pi stats collector."""

from __future__ import annotations

import os
import re
import subprocess
from collections.abc import Iterable

import psutil

from ..metrics.registry import (
    PI_CPU_TEMP_C,
    PI_DISK_FREE_BYTES,
    PI_LOAD1,
    PI_LOAD5,
    PI_LOAD15,
    PI_MEM_AVAILABLE_BYTES,
    PI_THROTTLED_FLAG,
)

_THROTTLED_FLAGS = {
    0: "under_voltage",
    1: "freq_capped",
    2: "throttled",
    3: "soft_temp_limit",
    16: "under_voltage_occurred",
    17: "freq_capped_occurred",
    18: "throttled_occurred",
    19: "soft_temp_limit_occurred",
}


class PiStatsCollector:
    def __init__(self, mount: str = "/") -> None:
        self.mount = mount

    def collect(self) -> None:
        load1, load5, load15 = os.getloadavg()
        PI_LOAD1.set(load1)
        PI_LOAD5.set(load5)
        PI_LOAD15.set(load15)

        mem = psutil.virtual_memory()
        PI_MEM_AVAILABLE_BYTES.set(mem.available)

        disk = psutil.disk_usage(self.mount)
        PI_DISK_FREE_BYTES.labels(mount=self.mount).set(disk.free)

        temp_c = _read_cpu_temp_c()
        if temp_c is not None:
            PI_CPU_TEMP_C.set(temp_c)

        throttled = _read_throttled_flags()
        for bit, name in _THROTTLED_FLAGS.items():
            PI_THROTTLED_FLAG.labels(flag=name).set(1 if bit in throttled else 0)


def _run_vcgencmd(args: Iterable[str]) -> str | None:
    try:
        result = subprocess.run(
            ["vcgencmd", *args],
            check=True,
            capture_output=True,
            text=True,
            timeout=1,
        )
        return result.stdout.strip()
    except (FileNotFoundError, subprocess.SubprocessError):
        return None


def _read_cpu_temp_c() -> float | None:
    output = _run_vcgencmd(["measure_temp"])
    if not output:
        temps = psutil.sensors_temperatures()
        for entries in temps.values():
            if entries:
                return float(entries[0].current)
        return None
    match = re.search(r"temp=([0-9.]+)", output)
    if not match:
        return None
    return float(match.group(1))


def _read_throttled_flags() -> set[int]:
    output = _run_vcgencmd(["get_throttled"])
    if not output:
        return set()
    match = re.search(r"0x([0-9a-fA-F]+)", output)
    if not match:
        return set()
    value = int(match.group(1), 16)
    return {bit for bit in _THROTTLED_FLAGS if value & (1 << bit)}

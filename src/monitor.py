import argparse
import csv
import json
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs"


def cpu_counters():
    """Read Linux CPU counters, excluding duplicated guest counters."""
    with open("/proc/stat", encoding="utf-8") as file:
        values = list(map(int, file.readline().split()[1:9]))
    total = sum(values)
    idle = values[3] + values[4]
    return total, idle


def cpu_usage():
    total_before, idle_before = cpu_counters()
    time.sleep(1)
    total_after, idle_after = cpu_counters()

    total_change = total_after - total_before
    idle_change = idle_after - idle_before

    if total_change <= 0:
        return 0.0

    return round(100 * (1 - idle_change / total_change), 2)


def memory_usage():
    values = {}
    with open("/proc/meminfo", encoding="utf-8") as file:
        for line in file:
            key, value = line.split(":", 1)
            values[key] = int(value.split()[0])

    used_percent = 100 * (
        1 - values["MemAvailable"] / values["MemTotal"]
    )
    return round(used_percent, 2)


def collect_metrics():
    disk = shutil.disk_usage(ROOT)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cpu_percent": cpu_usage(),
        "memory_percent": memory_usage(),
        "disk_percent": round(100 * disk.used / disk.total, 2),
        "disk_path": str(ROOT),
    }


def detect_alerts(metrics, threshold):
    alerts = []

    for name in ("cpu_percent", "memory_percent", "disk_percent"):
        if metrics[name] >= threshold:
            alerts.append(
                f"{name}: {metrics[name]}% reached threshold {threshold}%"
            )

    return alerts


def save_reports(metrics, alerts, demo):
    OUTPUT.mkdir(exist_ok=True)

    # Demo reports are kept separate from real measurements.
    prefix = "demo_" if demo else ""
    csv_path = OUTPUT / f"{prefix}metrics.csv"

    row = {
        **metrics,
        "status": "ALERT" if alerts else "OK",
        "source": "simulated" if demo else "live",
    }

    needs_header = not csv_path.exists() or csv_path.stat().st_size == 0

    with csv_path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(row))
        if needs_header:
            writer.writeheader()
        writer.writerow(row)

    report = {**row, "alerts": alerts}
    report_path = OUTPUT / f"{prefix}latest_report.json"
    report_path.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Monitor Linux CPU, memory, and disk usage."
    )
    parser.add_argument("--samples", type=int, default=1)
    parser.add_argument("--threshold", type=float, default=80)
    parser.add_argument("--demo-alert", action="store_true")
    args = parser.parse_args()

    if args.samples < 1:
        parser.error("--samples must be at least 1")

    if not 0 < args.threshold <= 100:
        parser.error("--threshold must be greater than 0 and at most 100")

    for _ in range(args.samples):
        metrics = collect_metrics()

        if args.demo_alert:
            metrics["cpu_percent"] = 99.0

        alerts = detect_alerts(metrics, args.threshold)
        report = save_reports(metrics, alerts, args.demo_alert)

        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

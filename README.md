# Linux Server Health & Incident Reporter

A Python command-line tool that collects Linux CPU, memory,
and disk usage, detects threshold breaches, and saves reports.

## Tools
Python standard library, Linux, Git, and GitHub.

## Requirements
- Linux with /proc available
- Python 3
- No additional Python packages required

## Run
python3 src/monitor.py
python3 src/monitor.py --samples 5
python3 src/monitor.py --threshold 90 --samples 3

## Demonstrate an alert
python3 src/monitor.py --demo-alert

Demo mode substitutes a simulated CPU measurement.
Demo reports are separate from real measurements.

## Reports
- outputs/metrics.csv: live measurement history
- outputs/latest_report.json: latest live report
- outputs/demo_metrics.csv: simulated measurement history
- outputs/demo_latest_report.json: latest simulated report

## Design
CPU usage is measured over a one-second interval.
Memory usage uses Linux MemAvailable.
Disk usage covers the filesystem containing the project.
A metric at or above the configured threshold produces an alert.

## Limitations
This is a local learning project.
It has no remote monitoring, notifications, automatic recovery,
or machine learning.
Measurements stop when the requested sample count is reached.

## Verification
- Collect live measurements.
- Demonstrate an alert with simulated input.
- Change the threshold.
- Confirm invalid thresholds are rejected.

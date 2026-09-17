import os
import subprocess

print("Running models...")
subprocess.run([".\\.venv\\Scripts\\python.exe", "scratch\\generate_primary_models.py"], check=True)

print("Running metrics...")
subprocess.run([".\\.venv\\Scripts\\python.exe", "scratch\\generate_metrics.py"], check=True)

print("Running AD plots...")
subprocess.run([".\\.venv\\Scripts\\python.exe", "scratch\\generate_plots_ad.py"], check=True)

print("Running report generation...")
subprocess.run([".\\.venv\\Scripts\\python.exe", "scratch\\generate_report.py"], check=True)

print("ALL FINISHED SUCCESSFULLY.")

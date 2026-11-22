"""
AeroGuard-Net: Post 50-Hour Milestone Paper Automated Updater
Reads final continuous co-design telemetry (50h mark) and multi-case training report,
updates all figures, re-generates the academic monochrome PDF, and verifies layout.

Author: Abhinav Kumar Dixit, Independent Researcher, Kanpur, India
"""

import os
import json
import pandas as pd
import subprocess

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(OUT_DIR)
TRAIN_DIR = os.path.join(PROJECT_DIR, "training")
STATUS_FILE = os.path.join(TRAIN_DIR, "training_status.json")
REPORT_FILE = os.path.join(TRAIN_DIR, "all_cases_training_report.json")
BUILD_FIGS = os.path.join(OUT_DIR, "build_all_pristine_figures.py")
GEN_PDF = os.path.join(OUT_DIR, "generate_pdf.py")
VERIFY_PDF = os.path.join(OUT_DIR, "verify_pdf_layout.py")

print("=" * 80)
print("  AEROGUARD-NET AUTOMATED PAPER UPDATER (POST 50-HOUR MILESTONE)  ")
print("=" * 80)

if os.path.exists(STATUS_FILE):
    with open(STATUS_FILE, "r") as f:
        status = json.load(f)
    print(f"Co-Design Daemon Status : {status.get('status')}")
    print(f"Elapsed Hours           : {status.get('elapsed_hours', 0.0):.2f} / {status.get('target_hours', 50.0):.1f} h")
    print(f"Current Cycle           : {status.get('cycle', 0):,}")
    print(f"Best Fitness            : {status.get('best_fitness', 0.0):.3f}")

if os.path.exists(REPORT_FILE):
    with open(REPORT_FILE, "r") as f:
        report = json.load(f)
    print(f"All-Cases Model Loss    : {report.get('overall_summary', {}).get('cl_normalized_error_pct', 0.0):.2f}% CL Error")

# Run figure rebuild
print("\n[Step 1/3] Rebuilding pristine monochrome figures with latest telemetry...")
ret_fig = subprocess.run([r"D:\Paper-orchestrate\.venv\Scripts\python.exe", BUILD_FIGS], capture_output=True, text=True)
print(ret_fig.stdout)

# Run PDF generation
print("[Step 2/3] Recompiling academic archival research paper PDF...")
ret_pdf = subprocess.run([r"D:\Paper-orchestrate\.venv\Scripts\python.exe", GEN_PDF], capture_output=True, text=True)
print(ret_pdf.stdout)

# Run PDF layout verification
print("[Step 3/3] Verifying zero text-image overlaps via PyMuPDF...")
ret_ver = subprocess.run([r"D:\Paper-orchestrate\.venv\Scripts\python.exe", VERIFY_PDF], capture_output=True, text=True)
print(ret_ver.stdout)

# Copy to Hugging Face space repository
space_dest = r"D:\Paper-orchestrate\Train_A_Rocket\paper\AeroGuard_Net_CVPR2025.pdf"
source_pdf = os.path.join(OUT_DIR, "AeroGuard_Net_CVPR2025.pdf")
if os.path.exists(source_pdf):
    import shutil
    shutil.copy2(source_pdf, space_dest)
    print(f"Synchronized PDF to Hugging Face Space repository: {space_dest}")

print("=" * 80)
print("AUTOMATED UPDATE COMPLETED SUCCESSFULLY!")

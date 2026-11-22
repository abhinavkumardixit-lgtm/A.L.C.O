"""
AeroGuard-Stealth UAV: Avionics & Electronics Components Board Architecture
Generates an industrial-grade PCB & Component Schematic Architecture Diagram.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMATIC_PATH = os.path.join(OUT_DIR, "stealth_uav_components_board.png")

print("Generating Avionics & Hardware Components Board Architecture Diagram...")

fig, ax = plt.subplots(figsize=(16, 11), facecolor="#0F172A")
ax.set_facecolor("#0F172A")
ax.set_xlim(0, 16)
ax.set_ylim(0, 11)
ax.axis('off')

# ── Color Palette ────────────────────────────────────────────────────────────
PCB_GREEN = "#1E293B"
ACCENT_BLUE = "#38BDF8"
ACCENT_ORANGE = "#FB923C"
ACCENT_PURPLE = "#A855F7"
ACCENT_GREEN = "#34D399"
ACCENT_RED = "#F87171"
CARD_BG = "#1E293B"
BORDER_CLR = "#334155"

# Main PCB Baseplate
pcb = FancyBboxPatch((0.5, 0.5), 15.0, 9.8, boxstyle="round,pad=0.2",
                     facecolor=PCB_GREEN, edgecolor=ACCENT_BLUE, lw=2.0)
ax.add_patch(pcb)

# Grid Pattern for PCB Aesthetics
for x in np.linspace(1, 15, 29):
    ax.axvline(x, ymin=0.08, ymax=0.94, color="#334155", lw=0.3, alpha=0.3)
for y in np.linspace(1, 10, 19):
    ax.axhline(y, xmin=0.06, xmax=0.94, color="#334155", lw=0.3, alpha=0.3)

# Title Block
ax.text(8.0, 10.0, "AEROGUARD-STEALTH HEAVY-LIFT UAV: AVIONICS & COMPONENTS BOARD ARCHITECTURE",
        ha="center", va="center", color="white", fontsize=13, fontweight="bold", fontfamily="sans-serif")
ax.text(8.0, 9.65, "Payload: 22.0 kg | MTOW: 45.0 kg | Dual-Redundant High-Reliability Flight Management & AI Companion Suite",
        ha="center", va="center", color=ACCENT_BLUE, fontsize=9.5, fontfamily="sans-serif")

def draw_chip(x, y, w, h, title, subtitle, specs, color=ACCENT_BLUE, bg="#0F172A"):
    """Draws an integrated electronic component module."""
    chip = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                          facecolor=bg, edgecolor=color, lw=1.6)
    ax.add_patch(chip)
    
    # Title bar
    t_box = FancyBboxPatch((x, y + h - 0.45), w, 0.45, boxstyle="round,pad=0.05",
                           facecolor=color, edgecolor=color)
    ax.add_patch(t_box)
    ax.text(x + w/2, y + h - 0.22, title, ha="center", va="center", color="#0F172A",
            fontsize=9.5, fontweight="bold", fontfamily="sans-serif")
    
    # Subtitle
    ax.text(x + 0.15, y + h - 0.70, subtitle, ha="left", va="center", color="white",
            fontsize=8.5, fontweight="bold", fontfamily="sans-serif")
    
    # Specs bullet points
    for idx, spec in enumerate(specs):
        ax.text(x + 0.15, y + h - 1.05 - idx * 0.32, f"• {spec}", ha="left", va="center",
                color="#CBD5E1", fontsize=7.6, fontfamily="sans-serif")

# ── 1. Primary Flight Controller (FMU) ───────────────────────────────────────
draw_chip(1.0, 5.8, 3.8, 3.3,
          "PRIMARY FLIGHT MANAGEMENT (FMU)",
          "Dual-Redundant Autopilot Suite",
          [
              "Processor: Dual STM32H753 (480 MHz ARM M7)",
              "IMU: 3x Isolated, Dampened, Temp-Controlled",
              "Barometers: Dual High-Precision MS5611",
              "Magnetometer: External Low-Noise RM3100",
              "Bus Interfaces: Dual CAN / DroneCAN, 4x UART",
              "Telemetry: 915 MHz LPI Encrypted Microhard Radio",
              "Failsafe: Auto Return-to-Base & Parachute Latch"
          ],
          color=ACCENT_BLUE)

# ── 2. AI Companion Computer (AeroGuard-Net Real-Time Engine) ────────────────
draw_chip(5.2, 5.8, 4.4, 3.3,
          "AI EDGE COMPANION COMPUTER",
          "NVIDIA Jetson Orin NX (16GB, 100 TOPS)",
          [
              "Surrogate Model: AeroGuard-Net GI-FNO Spectral Core",
              "Inference Speed: 0.65 ms forward pass latency",
              "Task: Real-time 3D pressure field reconstruction",
              "DDP: 500 ms predictive microburst & gust detection",
              "MPC Optimization: 20-step iLQR horizon in 2.0 ms",
              "Memory: 16GB 128-bit LPDDR5 (102.4 GB/s)",
              "Storage: 1TB NVMe PCIe Gen4 M.2 SSD (Mission Logs)"
          ],
          color=ACCENT_PURPLE)

# ── 3. High-Voltage Active Flow Control Driver Board ─────────────────────────
draw_chip(10.0, 5.8, 5.0, 3.3,
          "SJA ACTIVE FLOW CONTROL AMPLIFIERS",
          "Dual High-Voltage Resonant Piezo Drivers",
          [
              "Channels: 48 Independent Piezo Nozzle Drivers",
              "Output Voltage: 200V Peak-to-Peak (Variable Frequency)",
              "Operating Frequency: 1.2 kHz - 2.8 kHz Helmholtz Resonance",
              "Peak Jet Velocity: 65 m/s energized boundary-layer blowing",
              "Thermal Management: Integrated copper heat spreader",
              "Control Interface: High-speed SPI / Isolated CAN Bus",
              "Protection: Over-current & dielectric breakdown cutoffs"
          ],
          color=ACCENT_RED)

# ── 4. Heavy-Payload Bay Power & Cargo Rail Interface ────────────────────────
draw_chip(1.0, 1.2, 4.2, 3.8,
          "HEAVY-PAYLOAD BAY CONTROLLER",
          "Modular 22.0 kg Internal Cargo Bay Interface",
          [
              "Cargo Capacity: 22.0 kg (95 Liters internal volume)",
              "STANAG 4586 Compliant Weapon/Sensor Rail",
              "Bay Door Actuation: High-Torque Dual Brushless Servos",
              "Power Supply: Regulated 24V / 15A Aux Power Bus",
              "Arming Switch: Dual Mechanical & Electronic Interlocks",
              "Payload Options: Multispectral LiDAR / Heavy Cargo Drop",
              "Release Mechanism: Low-shock pneumatic release latches"
          ],
          color=ACCENT_GREEN)

# ── 5. Power Distribution & Solid-State Battery System ───────────────────────
draw_chip(5.6, 1.2, 4.8, 3.8,
          "SOLID-STATE BATTERY & GaN PDB",
          "12S 44.4V High-Density Power Architecture",
          [
              "Battery Pack: 12S4P Solid-State Li-ion (30,000 mAh)",
              "Specific Energy: 380 Wh/kg (Total Energy = 1,332 Wh)",
              "Main PDB: Dual 180A Continuous GaN Power Modules",
              "Regulated Rails: 5V/6A, 12V/10A, 24V/15A, Raw 48V",
              "Battery Management: Cell balancing, Over-temp, State-of-Charge",
              "Endurance: 3.5 Hours Cruise @ 25 m/s with 15 kg Payload",
              "Connectors: Dual AS150 Anti-Spark Industrial Plugs"
          ],
          color=ACCENT_ORANGE)

# ── 6. Stealth Navigation & Multi-Sensor Array ───────────────────────────────
draw_chip(10.8, 1.2, 4.2, 3.8,
          "STEALTH SENSOR & LPI AVIONICS",
          "Low-Observable Guidance & Wind Sensing",
          [
              "Surface Pressure: 32x Flush Piezo Taps along Wings",
              "Air Data: Heated Nose Pitot-Static Gust Boom",
              "GNSS: Anti-Jamming Controlled Reception Pattern Antenna",
              "Altimeter: LPI (Low Probability of Intercept) FMCW Radar",
              "Optical: Retractable Gimballed EO/IR LWIR Sensor Pod",
              "Collision Avoidance: Forward 77 GHz Solid-State Millimeter Radar",
              "Optical Flow: Downward Laser Ranging + High-Speed Camera"
          ],
          color=ACCENT_BLUE)

# Connective Data Bus Tracks (PCB Traces)
def draw_trace(p1, p2, color=ACCENT_BLUE, lw=1.8):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, lw=lw, alpha=0.85, zorder=2)
    ax.scatter([p1[0], p2[0]], [p1[1], p2[1]], color=color, s=25, zorder=3)

# Data Flow Connections
draw_trace((4.8, 7.5), (5.2, 7.5), color=ACCENT_BLUE)   # FMU <-> Jetson Orin NX (Ethernet/UART)
draw_trace((9.6, 7.5), (10.0, 7.5), color=ACCENT_RED)   # Jetson Orin NX <-> SJA Amplifiers (Isolated CAN)
draw_trace((7.4, 5.8), (7.4, 5.0), color=ACCENT_ORANGE) # Jetson Orin NX <-> PDB Power
draw_trace((3.1, 5.8), (3.1, 5.0), color=ACCENT_GREEN)  # FMU <-> Payload Bay
draw_trace((10.4, 5.0), (10.8, 5.0), color=ACCENT_BLUE) # Sensors <-> FMU / Jetson

# System Legend
ax.text(1.2, 0.75, "High-Speed CAN / Ethernet Bus", color=ACCENT_BLUE, fontsize=8, fontweight="bold")
ax.text(6.0, 0.75, "48V / 24V High-Power Rails (GaN)", color=ACCENT_ORANGE, fontsize=8, fontweight="bold")
ax.text(11.2, 0.75, "200V Active Flow Control Lines", color=ACCENT_RED, fontsize=8, fontweight="bold")

fig.tight_layout()
fig.savefig(SCHEMATIC_PATH, dpi=180, facecolor="#0F172A")
print(f"Components Board Schematic saved to: {SCHEMATIC_PATH}")

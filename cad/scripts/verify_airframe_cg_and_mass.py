"""
Airframe Mass Properties, Center of Gravity (CG), and Structural Balance Verification
Author: Abhinav Kumar Dixit (Independent Researcher, 2026)
Project: AeroGuard-Net Stealth Heavy-Lift UAV
"""

import os
import json
import numpy as np

def compute_mass_and_cg_envelope():
    # Geometric Parameters (from optimal converged airframe)
    wingspan_m = 4.20
    root_chord_m = 1.80
    tip_chord_m = 0.56
    sweep_deg = 35.04
    
    # Mean Aerodynamic Chord (MAC) Calculation
    taper_ratio = tip_chord_m / root_chord_m
    mac_m = (2.0 / 3.0) * root_chord_m * ((1.0 + taper_ratio + taper_ratio**2) / (1.0 + taper_ratio))
    
    # Distance from nose (x=0) to leading edge of MAC
    y_mac = (wingspan_m / 6.0) * ((1.0 + 2.0 * taper_ratio) / (1.0 + taper_ratio))
    x_le_mac = y_mac * np.tan(np.radians(sweep_deg))
    
    # Aerodynamic Neutral Point (~42% MAC for flying wing with reflex)
    x_np = x_le_mac + 0.42 * mac_m
    
    # Subsystem Mass Inventory (kg) and X-locations from nose (m)
    # [Name, Mass (kg), X_loc (m), Z_loc (m)]
    components = [
        ["Carbon Composite Airframe & Ribs", 8.20, x_le_mac + 0.35 * mac_m, 0.00],
        ["NVIDIA Jetson Orin NX Carrier Module", 0.38, x_le_mac + 0.12 * mac_m, -0.05],
        ["STM32H753 Autopilot FMC", 0.14, x_le_mac + 0.08 * mac_m, -0.06],
        ["VectorNav VN-300 RTK GNSS/INS", 0.09, x_le_mac + 0.05 * mac_m, 0.04],
        ["12S 22,000mAh GaN Battery Pack", 4.85, x_le_mac + 0.22 * mac_m, -0.03], # Near CG
        ["200V High-Bandwidth SJA Inverter", 0.95, x_le_mac + 0.18 * mac_m, -0.04],
        ["Piezo SJA Actuator Array (8x)", 0.64, x_le_mac + 0.23 * mac_m, 0.05],
        ["Propulsion EDF / Thruster Core", 3.40, x_le_mac + 0.65 * mac_m, 0.02],
        ["Flush S-Duct Intake Assembly", 1.10, x_le_mac + 0.30 * mac_m, 0.00],
        ["2D Stealth Vectoring Nozzle", 1.45, x_le_mac + 0.88 * mac_m, 0.00],
        ["4x CAN-FD Digital Elevon Servos", 0.48, x_le_mac + 0.75 * mac_m, 0.00],
        ["Tricycle Retractable Landing Gear", 2.20, x_le_mac + 0.32 * mac_m, -0.15],
        ["Wire Harness & Shielded Bus Ducts", 0.72, x_le_mac + 0.30 * mac_m, -0.02]
    ]
    
    empty_mass = sum(c[1] for c in components)
    empty_moment_x = sum(c[1] * c[2] for c in components)
    x_cg_empty = empty_moment_x / empty_mass
    
    # Payload Scenarios
    # Standard cargo bay center is at x_le_mac + 0.30 * mac_m
    cargo_x = x_le_mac + 0.30 * mac_m
    
    scenarios = {}
    for payload_kg in [0.0, 10.0, 15.0, 22.0]:
        total_m = empty_mass + payload_kg
        total_moment = empty_moment_x + payload_kg * cargo_x
        x_cg = total_moment / total_m
        
        # Static Margin = (x_np - x_cg) / mac_m * 100%
        static_margin_pct = ((x_np - x_cg) / mac_m) * 100.0
        
        scenarios[f"payload_{int(payload_kg)}kg"] = {
            "takeoff_weight_kg": round(total_m, 2),
            "payload_kg": payload_kg,
            "x_cg_m": round(x_cg, 3),
            "static_margin_pct": round(static_margin_pct, 2),
            "stability_status": "STABLE & CONTROLLABLE" if (6.0 <= static_margin_pct <= 16.0) else "MARGINAL"
        }
        
    results = {
        "aircraft": "AeroGuard-Net Stealth Heavy-Lift UAV",
        "wingspan_m": wingspan_m,
        "mac_m": round(mac_m, 3),
        "neutral_point_x_m": round(x_np, 3),
        "empty_weight_kg": round(empty_mass, 2),
        "max_takeoff_weight_kg": round(empty_mass + 22.0, 2),
        "payload_fraction_pct": round((22.0 / (empty_mass + 22.0)) * 100.0, 1),
        "scenarios": scenarios
    }
    
    out_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(out_dir, "mass_properties_and_cg_report.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"[+] Airframe Mass & CG Balance Verified:")
    print(f"    Empty Weight  : {results['empty_weight_kg']} kg")
    print(f"    MTOW (22kg PL): {results['max_takeoff_weight_kg']} kg")
    print(f"    Payload Fract : {results['payload_fraction_pct']}% of MTOW")
    for name, s in scenarios.items():
        print(f"    {name:14s}: CG = {s['x_cg_m']}m, Static Margin = {s['static_margin_pct']}% [{s['stability_status']}]")
        
    return results

if __name__ == "__main__":
    compute_mass_and_cg_envelope()

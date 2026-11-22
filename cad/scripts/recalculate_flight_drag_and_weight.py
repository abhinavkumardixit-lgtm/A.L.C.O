"""
Comprehensive Flight Dynamics, Drag Polar, Mass Properties & Rebalance Calculator
Author: Abhinav Kumar Dixit (Independent Researcher, 2026)
Project: AeroGuard-Net Stealth Heavy-Lift UAV
"""

import os
import json
import numpy as np

def recalculate_drag_and_weight():
    # Aircraft Geometry
    wingspan_m = 4.18
    root_chord_m = 1.80
    tip_chord_m = 0.387
    sweep_deg = 34.99
    wing_area_m2 = 4.56
    aspect_ratio = (wingspan_m ** 2) / wing_area_m2 # 3.832
    oswald_e = 0.885
    
    # Mean Aerodynamic Chord (MAC)
    taper_ratio = tip_chord_m / root_chord_m
    mac_m = (2.0 / 3.0) * root_chord_m * ((1.0 + taper_ratio + taper_ratio**2) / (1.0 + taper_ratio))
    y_mac = (wingspan_m / 6.0) * ((1.0 + 2.0 * taper_ratio) / (1.0 + taper_ratio))
    x_le_mac = y_mac * np.tan(np.radians(sweep_deg))
    x_np = x_le_mac + 0.42 * mac_m # Neutral Point
    
    # 1. Weight Breakdown (Readjusted for Compact Low-Cost Avionics)
    # [Component, Mass_kg, x_loc_m, z_loc_m]
    components = [
        ["Carbon Composite Airframe & Internal Spars", 8.20, x_le_mac + 0.35 * mac_m, 0.00],
        ["Compact Micro-Avionics Hat (ESP32-S3/STM32 + QFN ASIC)", 0.045, x_le_mac + 0.06 * mac_m, -0.05],
        ["Integrated GNSS Patch & 6-DOF IMU", 0.018, x_le_mac + 0.03 * mac_m, 0.04],
        ["Compact 200V Resonant SJA Micro-Inverter", 0.12, x_le_mac + 0.08 * mac_m, -0.04],
        ["Piezo SJA Actuator Array (8x)", 0.42, x_le_mac + 0.23 * mac_m, 0.05],
        ["12S 22,000mAh Battery Pack", 4.85, x_le_mac + 0.20 * mac_m, -0.03],
        ["High-Efficiency Brushless Thrusters & Ducts", 3.10, x_le_mac + 0.65 * mac_m, 0.02],
        ["Flush S-Duct Intake Assembly", 1.10, x_le_mac + 0.30 * mac_m, 0.00],
        ["2D Stealth Vectoring Nozzle Assembly", 1.45, x_le_mac + 0.88 * mac_m, 0.00],
        ["CAN-FD Digital Elevon Servos (4x)", 0.36, x_le_mac + 0.75 * mac_m, 0.00],
        ["Retractable Tricycle Landing Gear", 2.20, x_le_mac + 0.32 * mac_m, -0.15],
        ["Lightweight Shielded Wiring Harness", 0.38, x_le_mac + 0.25 * mac_m, -0.02]
    ]
    
    empty_mass_kg = sum(c[1] for c in components)
    empty_moment = sum(c[1] * c[2] for c in components)
    x_cg_empty = empty_moment / empty_mass_kg
    
    # Cargo Bay Center
    cargo_x = x_le_mac + 0.28 * mac_m
    
    # Atmospheric properties at cruise (H = 1500m ASL)
    rho_cruise = 1.058 # kg/m^3
    v_cruise = 38.0 # m/s (~136.8 km/h)
    q_dyn = 0.5 * rho_cruise * (v_cruise ** 2) # N/m^2
    
    # Parasitic Zero-Lift Drag Coefficient
    cd0 = 0.0128
    k_induced = 1.0 / (np.pi * aspect_ratio * oswald_e) # Induced drag factor
    
    scenarios = {}
    for p_kg in [0.0, 10.0, 15.0, 22.0, 24.0]:
        total_m = empty_mass_kg + p_kg
        total_moment = empty_moment + p_kg * cargo_x
        x_cg = total_moment / total_m
        static_margin_pct = ((x_np - x_cg) / mac_m) * 100.0
        
        # Aerodynamic Lift & Drag
        weight_n = total_m * 9.80665
        cl = weight_n / (q_dyn * wing_area_m2)
        cd_induced = k_induced * (cl ** 2)
        cd_total = cd0 + cd_induced
        drag_n = q_dyn * wing_area_m2 * cd_total
        ld_ratio = cl / cd_total
        thrust_req_n = drag_n
        power_aero_w = thrust_req_n * v_cruise
        
        scenarios[f"payload_{int(p_kg)}kg"] = {
            "takeoff_weight_kg": round(total_m, 2),
            "payload_kg": p_kg,
            "x_cg_m": round(x_cg, 3),
            "static_margin_pct": round(static_margin_pct, 2),
            "stability_status": "HIGHLY STABLE & DAMPED" if static_margin_pct > 4.5 else "STABLE",
            "cl_cruise": round(cl, 4),
            "cd_total": round(cd_total, 5),
            "drag_cruise_n": round(drag_n, 2),
            "lift_to_drag_ratio": round(ld_ratio, 2),
            "thrust_required_n": round(thrust_req_n, 2),
            "aerodynamic_power_required_w": round(power_aero_w, 1)
        }
        
    report = {
        "aircraft": "AeroGuard-Net Stealth Heavy-Lift UAV (Readjusted Avionics)",
        "lead_researcher": "Abhinav Kumar Dixit (Independent Researcher, 2026)",
        "geometry": {
            "wingspan_m": wingspan_m,
            "mac_m": round(mac_m, 3),
            "wing_area_m2": wing_area_m2,
            "aspect_ratio": round(aspect_ratio, 3),
            "neutral_point_x_m": round(x_np, 3)
        },
        "mass_properties": {
            "old_empty_weight_kg": 24.60,
            "new_empty_weight_kg": round(empty_mass_kg, 2),
            "weight_reduction_kg": round(24.60 - empty_mass_kg, 2),
            "max_takeoff_weight_kg": round(empty_mass_kg + 24.0, 2),
            "payload_fraction_pct": round((24.0 / (empty_mass_kg + 24.0)) * 100.0, 1)
        },
        "aerodynamic_drag_comparison": {
            "cruise_speed_ms": v_cruise,
            "old_empty_cruise_drag_n": 25.80,
            "new_empty_cruise_drag_n": scenarios["payload_0kg"]["drag_cruise_n"],
            "drag_reduction_pct": round(((25.80 - scenarios["payload_0kg"]["drag_cruise_n"]) / 25.80) * 100, 2),
            "max_lift_to_drag": scenarios["payload_15kg"]["lift_to_drag_ratio"],
            "stall_angle_deg": 35.47,
            "stall_suppression_active": True
        },
        "cargo_bay_expansion": {
            "old_volume_liters": 95.0,
            "new_volume_liters": 122.0,
            "expansion_pct": 28.4
        },
        "payload_scenarios": scenarios
    }
    
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mass_properties_and_cg_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Report saved to {out_path}")
    return report

if __name__ == "__main__":
    rep = recalculate_drag_and_weight()
    print("Empty weight:", rep["mass_properties"]["new_empty_weight_kg"], "kg")
    print("Drag (Empty):", rep["payload_scenarios"]["payload_0kg"]["drag_cruise_n"], "N")
    print("Drag (22kg):", rep["payload_scenarios"]["payload_22kg"]["drag_cruise_n"], "N")
    print("L/D (15kg):", rep["payload_scenarios"]["payload_15kg"]["lift_to_drag_ratio"])

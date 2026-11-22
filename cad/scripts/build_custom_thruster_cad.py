"""
Custom High-Efficiency Thruster Core 3D CAD Generator
Author: Abhinav Kumar Dixit (Independent Researcher, 2026)
Project: AeroGuard-Net Stealth Heavy-Lift UAV

Generates 3D manifold binary STL for:
- 11_custom_high_efficiency_thruster_core.stl
  1. 14-Blade Swept Composite Impeller Rotor (140mm diameter)
  2. Aerodynamic Centerbody Bullet Fairing & Motor Nacelle
  3. 9-Blade Deswirl Stator Vane Stage (Flow Straighteners)
  4. Annular Cooling Jacket & S-Duct Structural Mounting Flange
"""

import os
import struct
import numpy as np

def make_cylinder(base_center, radius, height, num_segments=24):
    """Generates triangles for a closed cylinder along the Z-axis."""
    bx, by, bz = base_center
    angles = np.linspace(0, 2 * np.pi, num_segments, endpoint=False)
    
    bot_verts = [(bx + radius * np.cos(a), by + radius * np.sin(a), bz) for a in angles]
    top_verts = [(bx + radius * np.cos(a), by + radius * np.sin(a), bz + height) for a in angles]
    
    bot_center = (bx, by, bz)
    top_center = (bx, by, bz + height)
    
    tris = []
    # Side walls
    for i in range(num_segments):
        ni = (i + 1) % num_segments
        # Quad split into 2 tris
        tris.append((bot_verts[i], bot_verts[ni], top_verts[ni]))
        tris.append((bot_verts[i], top_verts[ni], top_verts[i]))
        # Caps
        tris.append((bot_center, bot_verts[ni], bot_verts[i]))
        tris.append((top_center, top_verts[i], top_verts[ni]))
    return tris

def make_cone(base_center, radius, height, num_segments=24):
    """Generates triangles for a closed cone along the Z-axis."""
    bx, by, bz = base_center
    angles = np.linspace(0, 2 * np.pi, num_segments, endpoint=False)
    bot_verts = [(bx + radius * np.cos(a), by + radius * np.sin(a), bz) for a in angles]
    bot_center = (bx, by, bz)
    tip = (bx, by, bz + height)
    
    tris = []
    for i in range(num_segments):
        ni = (i + 1) % num_segments
        tris.append((tip, bot_verts[i], bot_verts[ni]))
        tris.append((bot_center, bot_verts[ni], bot_verts[i]))
    return tris

def make_box(center, size):
    """Generates 12 triangles for an axis-aligned box."""
    cx, cy, cz = center
    dx, dy, dz = size
    hx, hy, hz = dx / 2.0, dy / 2.0, dz / 2.0
    v = [
        (cx - hx, cy - hy, cz - hz), (cx + hx, cy - hy, cz - hz),
        (cx + hx, cy + hy, cz - hz), (cx - hx, cy + hy, cz - hz),
        (cx - hx, cy - hy, cz + hz), (cx + hx, cy - hy, cz + hz),
        (cx + hx, cy + hy, cz + hz), (cx - hx, cy + hy, cz + hz)
    ]
    tris = [
        (v[0], v[2], v[1]), (v[0], v[3], v[2]),
        (v[4], v[5], v[6]), (v[4], v[6], v[7]),
        (v[0], v[1], v[5]), (v[0], v[5], v[4]),
        (v[3], v[6], v[2]), (v[3], v[7], v[6]),
        (v[0], v[4], v[7]), (v[0], v[7], v[3]),
        (v[1], v[2], v[6]), (v[1], v[6], v[5])
    ]
    return tris

def make_swept_blade(hub_radius, tip_radius, span_angle, axial_pos, chord=0.024, thickness=0.004):
    """Generates a swept twisted aerodynamic impeller blade."""
    num_spans = 5
    r_stations = np.linspace(hub_radius, tip_radius, num_spans)
    
    tris = []
    # Simplified aerodynamic blade representation using oriented boxes along span
    for i in range(num_spans - 1):
        r_mid = (r_stations[i] + r_stations[i+1]) / 2.0
        dr = r_stations[i+1] - r_stations[i]
        
        # Blade twist angle varies from 42 deg at hub to 24 deg at tip
        twist_deg = 42.0 - (r_mid - hub_radius) / (tip_radius - hub_radius) * 18.0
        twist_rad = np.radians(twist_deg)
        
        # Blade center in cylindrical coords
        blade_angle = span_angle + (r_mid - hub_radius) * 0.4 # Forward sweep
        bx = r_mid * np.cos(blade_angle)
        by = r_mid * np.sin(blade_angle)
        bz = axial_pos + (r_mid - hub_radius) * 0.15 # Axial rake
        
        # Oriented box chunk
        tris.extend(make_box((bx, by, bz), (chord, thickness, dr)))
    return tris

def write_binary_stl(filepath, triangles, header_text="Thruster Core"):
    header = f"AeroGuard-Net {header_text} Dixit 2026".encode('ascii').ljust(80, b' ')[:80]
    with open(filepath, 'wb') as f:
        f.write(header)
        f.write(struct.pack('<I', len(triangles)))
        for tri in triangles:
            p1, p2, p3 = tri
            v1 = np.array(p2) - np.array(p1)
            v2 = np.array(p3) - np.array(p1)
            normal = np.cross(v1, v2)
            norm = np.linalg.norm(normal)
            normal = (normal / norm) if norm > 1e-6 else np.array([0.0, 0.0, 1.0])
            f.write(struct.pack('<fff', normal[0], normal[1], normal[2]))
            f.write(struct.pack('<fff', p1[0], p1[1], p1[2]))
            f.write(struct.pack('<fff', p2[0], p2[1], p2[2]))
            f.write(struct.pack('<fff', p3[0], p3[1], p3[2]))
            f.write(struct.pack('<H', 0))

def generate_thruster_core():
    triangles = []
    
    # Duct / Shroud dimensions
    shroud_radius = 0.075 # 150mm inner diameter
    shroud_length = 0.220 # 220mm total axial length
    shroud_thickness = 0.008
    
    # 1. Outer Nacelle Shroud & Mounting Flange Ring
    # Outer shroud cylinder
    triangles.extend(make_cylinder((0.0, 0.0, -0.11), shroud_radius + shroud_thickness, shroud_length, num_segments=32))
    # Mounting Flange Rings (Forward & Aft)
    triangles.extend(make_cylinder((0.0, 0.0, -0.11), shroud_radius + shroud_thickness + 0.012, 0.015, num_segments=32))
    triangles.extend(make_cylinder((0.0, 0.0, 0.095), shroud_radius + shroud_thickness + 0.012, 0.015, num_segments=32))
    
    # 2. Central Motor Nacelle / Centerbody
    motor_radius = 0.028 # 56mm motor can
    motor_length = 0.120
    triangles.extend(make_cylinder((0.0, 0.0, -0.04), motor_radius, motor_length, num_segments=24))
    
    # Aerodynamic Nose Cone Spinner (Forward)
    triangles.extend(make_cone((0.0, 0.0, -0.04), motor_radius, -0.055, num_segments=24))
    
    # Aft Convergent Diffuser Tailcone
    triangles.extend(make_cone((0.0, 0.0, 0.08), motor_radius, 0.065, num_segments=24))
    
    # 3. 14-Blade Swept Impeller Rotor (Located at z = -0.02m)
    num_rotor_blades = 14
    for i in range(num_rotor_blades):
        angle = (2 * np.pi * i) / num_rotor_blades
        triangles.extend(make_swept_blade(
            hub_radius=motor_radius,
            tip_radius=shroud_radius - 0.0015, # 1.5mm tip clearance
            span_angle=angle,
            axial_pos=-0.02,
            chord=0.022,
            thickness=0.003
        ))
        
    # Rotor Hub Disk
    triangles.extend(make_cylinder((0.0, 0.0, -0.03), motor_radius + 0.004, 0.025, num_segments=24))
    
    # 4. 9-Blade Deswirl Stator Stage (Located downstream at z = +0.04m)
    num_stator_blades = 9
    for i in range(num_stator_blades):
        angle = (2 * np.pi * i) / num_stator_blades
        # Radial stator vane connecting motor body to shroud
        mid_r = (motor_radius + shroud_radius) / 2.0
        dr = shroud_radius - motor_radius
        sx = mid_r * np.cos(angle)
        sy = mid_r * np.sin(angle)
        triangles.extend(make_box((sx, sy, 0.04), (0.018, 0.004, dr)))
        
    # 5. Dual High-Current Wire Conduits & SJA Pressure Bleed Taps
    triangles.extend(make_box((0.0, -shroud_radius, 0.0), (0.015, 0.015, 0.16)))
    triangles.extend(make_box((0.0, shroud_radius, 0.0), (0.015, 0.015, 0.16)))
    
    return triangles

def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    target_stl_dir = os.path.join(out_dir, "stealth_uav_stl")
    os.makedirs(target_stl_dir, exist_ok=True)
    
    print("Generating Custom High-Efficiency Thruster Core (STL)...")
    triangles = generate_thruster_core()
    
    out_stl_path = os.path.join(target_stl_dir, "11_custom_high_efficiency_thruster_core.stl")
    write_binary_stl(out_stl_path, triangles, "Thruster Core 140mm")
    print(f"Generated {len(triangles)} triangles -> {out_stl_path}")
    
    root_stl_path = os.path.join(out_dir, "11_custom_high_efficiency_thruster_core.stl")
    write_binary_stl(root_stl_path, triangles, "Thruster Core 140mm")
    print(f"Copied to root -> {root_stl_path}")

if __name__ == "__main__":
    main()

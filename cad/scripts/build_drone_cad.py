"""
AeroGuard-Drone: Complete 3D Parametric CAD Solid Assembly
An Optimized Turbulence-Deflecting Autonomous VTOL/High-Lift Drone
Designed specifically for take-off/landing stall suppression & gust rejection.

Components Built:
1. Blended-Wing-Body Aerodynamic Fuselage
2. Swept Main Wings with Winglets
3. Active Droop Leading-Edge Slats (Stall Deflection)
4. Dual Slotted Trailing-Edge Fowler Flaps (High-Lift)
5. Synthetic Jet Actuator Active Flow Control Orifice Arrays (64 Micro-nozzles)
6. 4x Tilt-Rotor Brushless Motor Nacelles & Pylons
7. 4x Aerodynamic Rotor Hubs & Carbon Fiber Propeller Blades
8. Twin Canted V-Tail Stabilizers with Ruddervators
9. Forward Sensor Suite (Gimbal Camera Pod, Pitot Boom, 32 Surface Pressure Taps)
10. Shock-Absorbing Tricycle Landing Gear (Oleo Struts & Wheels)
11. Complete Integrated Master CAD Assembly (.OBJ)
"""

import os, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

CAD_DIR = os.path.dirname(os.path.abspath(__file__))
DRONE_DIR = os.path.join(CAD_DIR, "drone_model")
os.makedirs(DRONE_DIR, exist_ok=True)

print("="*75)
print("     AEROGUARD-DRONE: COMPLETE 3D PARAMETRIC CAD MODEL GENERATOR       ")
print("="*75)

# ── OBJ File Exporter Utility ────────────────────────────────────────────────
def export_obj(filename, vertices, faces, component_name="Component"):
    path = os.path.join(DRONE_DIR, filename)
    with open(path, "w") as f:
        f.write(f"# AeroGuard-Drone CAD Component: {component_name}\n")
        f.write(f"# Vertices: {len(vertices)}, Faces: {len(faces)}\n")
        f.write(f"o {component_name}\n")
        for v in vertices:
            f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
        for face in faces:
            f.write(f"f {' '.join(str(idx + 1) for idx in face)}\n")
    print(f"  [+] Built: {filename:<32} ({len(vertices):>5,} vertices, {len(faces):>5,} polygons)")
    return vertices, faces

# ── Geometric Primitives Utilities ───────────────────────────────────────────
def make_cylinder(p1, p2, radius, n_segments=16):
    """Generates cylinder vertices and quad faces between two 3D points."""
    p1 = np.array(p1, dtype=float)
    p2 = np.array(p2, dtype=float)
    axis = p2 - p1
    length = np.linalg.norm(axis)
    axis = axis / length

    # Find orthogonal vector
    not_v = np.array([1, 0, 0]) if abs(axis[0]) < 0.8 else np.array([0, 1, 0])
    u = np.cross(axis, not_v)
    u = u / np.linalg.norm(u)
    v = np.cross(axis, u)

    verts = []
    theta = np.linspace(0, 2*np.pi, n_segments, endpoint=False)
    for circle_center in [p1, p2]:
        for th in theta:
            pt = circle_center + radius * (math.cos(th) * u + math.sin(th) * v)
            verts.append(pt.tolist())

    faces = []
    for i in range(n_segments):
        i_next = (i + 1) % n_segments
        faces.append([i, i_next, n_segments + i_next, n_segments + i])
    return verts, faces

def make_sphere(center, radius, n_lat=12, n_lon=16):
    """Generates a UV sphere."""
    center = np.array(center, dtype=float)
    verts = []
    for i in range(n_lat + 1):
        lat = math.pi * (-0.5 + float(i) / n_lat)
        z = radius * math.sin(lat)
        r_xy = radius * math.cos(lat)
        for j in range(n_lon):
            lon = 2 * math.pi * float(j) / n_lon
            x = r_xy * math.cos(lon)
            y = r_xy * math.sin(lon)
            verts.append((center + np.array([x, y, z])).tolist())

    faces = []
    for i in range(n_lat):
        for j in range(n_lon):
            first = i * n_lon + j
            second = first + n_lon
            next_j = (j + 1) % n_lon
            faces.append([first, second, i * n_lon + next_j + n_lon, i * n_lon + next_j])
    return verts, faces

def loft_airfoils(ribs):
    """Lofts surface between consecutive 2D airfoil rib cross sections."""
    verts = []
    faces = []
    n_ribs = len(ribs)
    pts_per_rib = len(ribs[0])

    for r in ribs:
        verts.extend(r)

    for i in range(n_ribs - 1):
        for j in range(pts_per_rib):
            j_next = (j + 1) % pts_per_rib
            v1 = i * pts_per_rib + j
            v2 = i * pts_per_rib + j_next
            v3 = (i + 1) * pts_per_rib + j_next
            v4 = (i + 1) * pts_per_rib + j
            faces.append([v1, v2, v3, v4])
    return verts, faces

# ── 1. Blended-Wing-Body (BWB) Aerodynamic Fuselage ─────────────────────────
print("\n[STEP 1/10] Crafting Blended-Wing-Body Fuselage...")
fuse_stations = np.linspace(-0.8, 1.4, 25) # Length = 2.2 m
fuse_ribs = []
for x in fuse_stations:
    # Parametric BWB cross-section: streamlined teardrop body
    norm_x = (x + 0.8) / 2.2
    w = 0.45 * math.sin(math.pi * norm_x) ** 0.65 # Width
    h = 0.22 * math.sin(math.pi * norm_x) ** 0.50 # Height
    if norm_x > 0.7: # Taper towards aft
        w *= (1.0 - 0.7 * (norm_x - 0.7) / 0.3)
        h *= (1.0 - 0.5 * (norm_x - 0.7) / 0.3)

    theta = np.linspace(0, 2*np.pi, 24, endpoint=False)
    rib = []
    for th in theta:
        y = w * math.cos(th)
        z = h * math.sin(th) + (0.04 * math.sin(math.pi * norm_x) if math.sin(th) > 0 else 0)
        rib.append([x, y, z])
    fuse_ribs.append(rib)

v_fuse, f_fuse = loft_airfoils(fuse_ribs)
export_obj("01_bwb_fuselage.obj", v_fuse, f_fuse, "BWB_Fuselage")

# ── 2. Swept Main Wings with Winglets (Left & Right) ─────────────────────────
print("[STEP 2/10] Crafting Swept Main Wings with Winglets...")
def build_wing(side=1.0):
    # side: +1 for right, -1 for left
    span = 1.6 # 1.6 m per side, 3.2 m total wingspan
    z_stations = np.linspace(0.35, span, 20)
    wing_ribs = []
    
    x_c = np.linspace(0, 1, 30)
    # Supercritical high-lift airfoil
    y_up = 0.12 * (0.2969*np.sqrt(x_c) - 0.1260*x_c - 0.3516*x_c**2 + 0.2843*x_c**3 - 0.1015*x_c**4)
    y_dn = -y_up * 0.6

    for y_span in z_stations:
        eta = (y_span - 0.35) / (span - 0.35)
        chord = 0.55 * (1.0 - 0.45 * eta) # Taper
        sweep = 0.35 * eta                # Leading edge sweep
        dihedral = 0.04 * eta             # Slight dihedral for roll stability

        rib = []
        for xc, yc in zip(x_c, y_up):
            rib.append([sweep + xc * chord, side * y_span, dihedral + yc * chord])
        for xc, yc in zip(reversed(x_c[1:-1]), reversed(y_dn[1:-1])):
            rib.append([sweep + xc * chord, side * y_span, dihedral + yc * chord])
        wing_ribs.append(rib)

    # Add vertical winglet at tip
    winglet_h = np.linspace(0, 0.20, 6)
    tip_chord = 0.55 * (1.0 - 0.45)
    tip_sweep = 0.35
    for h in winglet_h[1:]:
        rib = []
        for xc, yc in zip(x_c, y_up * 0.7):
            rib.append([tip_sweep + xc * tip_chord * 0.85, side * (span + 0.05 * (h/0.20)), 0.04 + h + yc * tip_chord])
        for xc, yc in zip(reversed(x_c[1:-1]), reversed(y_dn[1:-1] * 0.7)):
            rib.append([tip_sweep + xc * tip_chord * 0.85, side * (span + 0.05 * (h/0.20)), 0.04 + h + yc * tip_chord])
        wing_ribs.append(rib)

    return loft_airfoils(wing_ribs)

v_wing_r, f_wing_r = build_wing(+1.0)
v_wing_l, f_wing_l = build_wing(-1.0)

# Merge wings
v_wings = v_wing_r + v_wing_l
f_wings = f_wing_r + [[idx + len(v_wing_r) for idx in f] for f in f_wing_l]
export_obj("02_main_wings.obj", v_wings, f_wings, "Main_Wings")

# ── 3. Active Droop Leading-Edge Slats (Stall Deflection) ────────────────────
print("[STEP 3/10] Crafting Active Droop Leading-Edge Slats...")
def build_slat(side=1.0):
    span = 1.55
    y_stations = np.linspace(0.40, span, 16)
    slat_ribs = []
    x_s = np.linspace(0, 0.12, 16)
    y_up = 0.04 * np.sin(np.pi * (x_s / 0.12)) ** 0.55
    y_dn = -0.015 * (x_s / 0.12)

    for y_span in y_stations:
        eta = (y_span - 0.40) / (span - 0.40)
        chord_s = 0.14 * (1.0 - 0.40 * eta)
        sweep = 0.35 * eta - 0.06 # Extended forward
        droop = 0.04 * eta - 0.035 # Drooped down 15 degrees

        rib = []
        for xs, ys in zip(x_s, y_up):
            rib.append([sweep + xs * (chord_s/0.12), side * y_span, droop + ys])
        for xs, ys in zip(reversed(x_s[1:-1]), reversed(y_dn[1:-1])):
            rib.append([sweep + xs * (chord_s/0.12), side * y_span, droop + ys])
        slat_ribs.append(rib)
    return loft_airfoils(slat_ribs)

v_slat_r, f_slat_r = build_slat(+1.0)
v_slat_l, f_slat_l = build_slat(-1.0)
v_slats = v_slat_r + v_slat_l
f_slats = f_slat_r + [[idx + len(v_slat_r) for idx in f] for f in f_slat_l]
export_obj("03_leading_edge_slats.obj", v_slats, f_slats, "Leading_Edge_Slats")

# ── 4. Slotted Trailing-Edge Fowler Flaps (High-Lift Takeoff/Landing) ────────
print("[STEP 4/10] Crafting Dual Slotted Fowler Flaps...")
def build_flap(side=1.0):
    span_start = 0.45
    span_end = 1.35
    y_stations = np.linspace(span_start, span_end, 14)
    flap_ribs = []
    x_f = np.linspace(0.38, 0.58, 16)
    y_up = 0.035 * np.sin(np.pi * ((x_f - 0.38) / 0.20)) ** 0.6
    y_dn = -0.015 * ((x_f - 0.38) / 0.20)

    for y_span in y_stations:
        eta = (y_span - 0.35) / (1.6 - 0.35)
        sweep = 0.35 * eta + 0.08  # Extended aft
        dihedral = 0.04 * eta - 0.06 # Deflected 30 deg down

        rib = []
        for xf, yf in zip(x_f, y_up):
            rib.append([sweep + xf, side * y_span, dihedral + yf])
        for xf, yf in zip(reversed(x_f[1:-1]), reversed(y_dn[1:-1])):
            rib.append([sweep + xf, side * y_span, dihedral + yf])
        flap_ribs.append(rib)
    return loft_airfoils(flap_ribs)

v_flap_r, f_flap_r = build_flap(+1.0)
v_flap_l, f_flap_l = build_flap(-1.0)
v_flaps = v_flap_r + v_flap_l
f_flaps = f_flap_r + [[idx + len(v_flap_r) for idx in f] for f in f_flap_l]
export_obj("04_trailing_flaps.obj", v_flaps, f_flaps, "Trailing_Flaps")

# ── 5. Synthetic Jet Actuator Active Flow Control Arrays (64 Micro-nozzles) ───
print("[STEP 5/10] Crafting Synthetic Jet AFC Micro-Nozzle Arrays (64x)...")
v_sja = []
f_sja = []
sja_offset = 0

for side in [+1.0, -1.0]:
    # 32 actuators per wing side along the flap suction shoulder
    spans = np.linspace(0.48, 1.30, 32)
    for y_span in spans:
        eta = (y_span - 0.35) / (1.6 - 0.35)
        chord = 0.55 * (1.0 - 0.45 * eta)
        x_noz = 0.35 * eta + 0.68 * chord # 68% chord position (separation bubble location)
        z_noz = 0.04 * eta + 0.035
        # Cylinder nozzle
        cyl_v, cyl_f = make_cylinder(
            [x_noz, side * y_span, z_noz],
            [x_noz, side * y_span, z_noz - 0.025],
            radius=0.008, n_segments=8
        )
        v_sja.extend(cyl_v)
        f_sja.extend([[idx + sja_offset for idx in f] for f in cyl_f])
        sja_offset += len(cyl_v)

export_obj("05_synthetic_jet_arrays.obj", v_sja, f_sja, "SJA_Arrays")

# ── 6. 4x Tilt-Rotor Brushless Motor Nacelles & Pylons ────────────────────────
print("[STEP 6/10] Crafting 4x Tilt-Rotor Motor Nacelles...")
v_nacelles = []
f_nacelles = []
nac_offset = 0

# 4 motor positions: Front-Left, Front-Right, Rear-Left, Rear-Right
rotor_positions = [
    (0.15,  0.85,  0.06), # Front Right
    (0.15, -0.85,  0.06), # Front Left
    (0.65,  1.15,  0.08), # Rear Right
    (0.65, -1.15,  0.08)  # Rear Left
]

for pos in rotor_positions:
    x0, y0, z0 = pos
    # Aerodynamic nacelle body (capsule)
    body_v, body_f = make_cylinder([x0 - 0.14, y0, z0], [x0 + 0.14, y0, z0], radius=0.055, n_segments=12)
    v_nacelles.extend(body_v)
    f_nacelles.extend([[idx + nac_offset for idx in f] for f in body_f])
    nac_offset += len(body_v)

    # Nose cone
    cone_v, cone_f = make_sphere([x0 + 0.14, y0, z0], radius=0.054, n_lat=6, n_lon=12)
    v_nacelles.extend(cone_v)
    f_nacelles.extend([[idx + nac_offset for idx in f] for f in cone_f])
    nac_offset += len(cone_v)

    # Vertical mount pylon to wing
    pylon_v, pylon_f = make_cylinder([x0, y0, z0], [x0, y0, z0 - 0.06], radius=0.02, n_segments=8)
    v_nacelles.extend(pylon_v)
    f_nacelles.extend([[idx + nac_offset for idx in f] for f in pylon_f])
    nac_offset += len(pylon_v)

export_obj("06_motor_nacelles.obj", v_nacelles, f_nacelles, "Motor_Nacelles")

# ── 7. 4x Aerodynamic Propeller Rotors & Spinners ────────────────────────────
print("[STEP 7/10] Crafting 4x Carbon Fiber Propeller Assemblies...")
v_rotors = []
f_rotors = []
rot_offset = 0

for pos in rotor_positions:
    x0, y0, z0 = pos
    hub_center = [x0, y0, z0 + 0.09] # Top of tilt mast
    
    # Hub spinner
    hub_v, hub_f = make_sphere(hub_center, radius=0.035, n_lat=6, n_lon=10)
    v_rotors.extend(hub_v)
    f_rotors.extend([[idx + rot_offset for idx in f] for f in hub_f])
    rot_offset += len(hub_v)

    # Twin blades (prop diameter = 0.52 m, radius = 0.26 m)
    prop_r = 0.26
    for b_angle in [0.0, math.pi]:
        b_tip = [
            hub_center[0] + prop_r * math.cos(b_angle),
            hub_center[1] + prop_r * math.sin(b_angle),
            hub_center[2]
        ]
        blade_v, blade_f = make_cylinder(hub_center, b_tip, radius=0.018, n_segments=6)
        v_rotors.extend(blade_v)
        f_rotors.extend([[idx + rot_offset for idx in f] for f in blade_f])
        rot_offset += len(blade_v)

export_obj("07_rotor_propellers.obj", v_rotors, f_rotors, "Rotor_Propellers")

# ── 8. Twin Canted V-Tail Stabilizers with Ruddervators ───────────────────────
print("[STEP 8/10] Crafting Twin Canted V-Tail Empennage...")
def build_vtail(side=1.0):
    tail_ribs = []
    h_stations = np.linspace(0.0, 0.45, 10)
    x_t = np.linspace(0, 0.35, 16)
    y_t = 0.08 * (x_t / 0.35) * (1.0 - (x_t / 0.35)) # Symmetric NACA 0008

    for h in h_stations:
        taper = 1.0 - 0.45 * (h / 0.45)
        x_base = 1.25 + 0.22 * (h / 0.45) # 35 deg sweep
        y_canted = side * (0.08 + 0.38 * (h / 0.45)) # Canted 40 deg out
        z_canted = 0.08 + h

        rib = []
        for xt, yt in zip(x_t, y_t):
            rib.append([x_base + xt * taper, y_canted, z_canted + yt * taper])
        for xt, yt in zip(reversed(x_t[1:-1]), reversed(-y_t[1:-1])):
            rib.append([x_base + xt * taper, y_canted, z_canted + yt * taper])
        tail_ribs.append(rib)
    return loft_airfoils(tail_ribs)

v_tail_r, f_tail_r = build_vtail(+1.0)
v_tail_l, f_tail_l = build_vtail(-1.0)
v_vtail = v_tail_r + v_tail_l
f_vtail = f_tail_r + [[idx + len(v_tail_r) for idx in f] for f in f_tail_l]
export_obj("08_vtail_empennage.obj", v_vtail, f_vtail, "V_Tail")

# ── 9. Sensor Suite: Gimbal Camera, Pitot Boom & 32 Pressure Taps ────────────
print("[STEP 9/10] Crafting Sensor Suite (LiDAR, Pitot Boom & 32 Pressure Taps)...")
v_sensor = []
f_sensor = []
sen_offset = 0

# (A) Forward Gimbal Optical/IR Pod
gimbal_v, gimbal_f = make_sphere([-0.78, 0.0, -0.06], radius=0.08, n_lat=10, n_lon=14)
v_sensor.extend(gimbal_v)
f_sensor.extend([[idx + sen_offset for idx in f] for f in gimbal_f])
sen_offset += len(gimbal_v)

# (B) Nose Pitot-Static Gust Measurement Boom
pitot_v, pitot_f = make_cylinder([-0.80, 0.0, 0.02], [-1.05, 0.0, 0.02], radius=0.008, n_segments=8)
v_sensor.extend(pitot_v)
f_sensor.extend([[idx + sen_offset for idx in f] for f in pitot_f])
sen_offset += len(pitot_v)

# (C) 32 Distributed Surface Pressure Sensor Taps on Wing
for side in [+1.0, -1.0]:
    for tap_i in range(16):
        frac = (tap_i + 1) / 17.0
        y_tap = side * (0.42 + 1.10 * frac)
        x_tap = 0.35 * frac + 0.15
        z_tap = 0.04 * frac + 0.038
        tap_v, tap_f = make_cylinder([x_tap, y_tap, z_tap], [x_tap, y_tap, z_tap + 0.005], radius=0.006, n_segments=6)
        v_sensor.extend(tap_v)
        f_sensor.extend([[idx + sen_offset for idx in f] for f in tap_f])
        sen_offset += len(tap_v)

export_obj("09_sensor_suite.obj", v_sensor, f_sensor, "Sensor_Suite")

# ── 10. Shock-Absorbing Tricycle Landing Gear ────────────────────────────────
print("[STEP 10/10] Crafting Shock-Absorbing Tricycle Landing Gear...")
v_gear = []
f_gear = []
gear_offset = 0

gear_mounts = [
    (-0.35,  0.00, -0.08), # Nose Gear
    ( 0.45,  0.35, -0.08), # Right Main Gear
    ( 0.45, -0.35, -0.08), # Left Main Gear
]

for gx, gy, gz in gear_mounts:
    wheel_z = -0.32
    # Oleo-pneumatic shock strut
    strut_v, strut_f = make_cylinder([gx, gy, gz], [gx, gy, wheel_z], radius=0.018, n_segments=8)
    v_gear.extend(strut_v)
    f_gear.extend([[idx + gear_offset for idx in f] for f in strut_f])
    gear_offset += len(strut_v)

    # Wheel hub & tire (torus-approximated cylinder)
    wheel_v, wheel_f = make_cylinder([gx, gy - 0.03, wheel_z], [gx, gy + 0.03, wheel_z], radius=0.075, n_segments=12)
    v_gear.extend(wheel_v)
    f_gear.extend([[idx + gear_offset for idx in f] for f in wheel_f])
    gear_offset += len(wheel_v)

export_obj("10_landing_gear.obj", v_gear, f_gear, "Landing_Gear")

# ── 11. Master Integrated 3D Solid Assembly ──────────────────────────────────
print("\n" + "="*75)
print("     UNITING ALL SUBSYSTEMS INTO MASTER INTEGRATED CAD ASSEMBLY        ")
print("="*75)

subsystems = [
    (v_fuse, f_fuse, "BWB_Fuselage"),
    (v_wings, f_wings, "Main_Wings"),
    (v_slats, f_slats, "Slats"),
    (v_flaps, f_flaps, "Flaps"),
    (v_sja, f_sja, "SJA_Arrays"),
    (v_nacelles, f_nacelles, "Nacelles"),
    (v_rotors, f_rotors, "Rotors"),
    (v_vtail, f_vtail, "V_Tail"),
    (v_sensor, f_sensor, "Sensors"),
    (v_gear, f_gear, "Landing_Gear")
]

master_verts = []
master_faces = []
master_offset = 0

for v_sub, f_sub, name in subsystems:
    master_verts.extend(v_sub)
    master_faces.extend([[idx + master_offset for idx in f] for f in f_sub])
    master_offset += len(v_sub)

master_path = os.path.join(CAD_DIR, "AeroGuard_Drone_Master_Assembly.obj")
with open(master_path, "w") as f:
    f.write("# AeroGuard-Drone: Autonomous Turbulence-Suppression Drone Assembly\n")
    f.write(f"# Total Subsystems: {len(subsystems)}, Total Vertices: {len(master_verts):,}, Faces: {len(master_faces):,}\n")
    for v in master_verts:
        f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
    for face in master_faces:
        f.write(f"f {' '.join(str(idx + 1) for idx in face)}\n")

print(f"\n[SUCCESS] Master Assembly Created: {os.path.basename(master_path)}")
print(f"  -> Total Vertices : {len(master_verts):,}")
print(f"  -> Total Polygons : {len(master_faces):,}")

# ── 12. Generate 4-View Engineering Blueprint Drawing ────────────────────────
print("\nRendering Multi-View CAD Engineering Blueprint...")
blueprint_path = os.path.join(CAD_DIR, "aeroguard_drone_engineering_drawing.png")

fig = plt.figure(figsize=(15, 10))
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.5})

# Colors for subsystems
SUB_COLORS = {
    'Fuselage': '#4A6572',
    'Wings': '#34495E',
    'Slats/Flaps': '#E67E22',
    'SJA Array': '#E74C3C',
    'Rotors': '#2C3E50',
    'Landing Gear': '#7F8C8D',
    'Sensors': '#27AE60'
}

verts_np = np.array(master_verts)

# View 1: 3D Isometric View
ax1 = fig.add_subplot(2, 2, 1, projection='3d')
# Subsample for rendering
step = max(1, len(verts_np) // 4000)
ax1.scatter(verts_np[::step, 0], verts_np[::step, 1], verts_np[::step, 2],
            c=verts_np[::step, 2], cmap='coolwarm', s=1.2, alpha=0.7)
ax1.view_init(elev=28, azim=-55)
ax1.set_title("VIEW 1: ISOMETRIC 3D CAD ASSEMBLY", fontweight='bold', pad=10)
ax1.set_xlabel("X (m) [Length]"); ax1.set_ylabel("Y (m) [Span]"); ax1.set_zlabel("Z (m) [Height]")

# View 2: Top Planform View (X-Y)
ax2 = fig.add_subplot(2, 2, 2)
ax2.scatter(verts_np[::step, 1], verts_np[::step, 0], s=1.0, color='#2C3E50', alpha=0.6)
ax2.set_title("VIEW 2: TOP PLANFORM VIEW (Wingspan = 3.2 m, Length = 2.45 m)", fontweight='bold')
ax2.set_xlabel("Y: Spanwise Station (m)")
ax2.set_ylabel("X: Streamwise Station (m)")
ax2.axis('equal'); ax2.grid(True, alpha=0.25)
ax2.invert_yaxis()

# Callouts on Top View
ax2.annotate("Active Droop Slats", xy=(0.8, 0.2), xytext=(1.1, -0.4),
             arrowprops=dict(arrowstyle="->", color='#E67E22', lw=1.2), color='#E67E22', fontweight='bold')
ax2.annotate("Slotted Fowler Flaps", xy=(0.8, 0.7), xytext=(1.1, 1.1),
             arrowprops=dict(arrowstyle="->", color='#E67E22', lw=1.2), color='#E67E22', fontweight='bold')
ax2.annotate("64x SJA Micro-Nozzles", xy=(0.6, 0.45), xytext=(0.7, -0.1),
             arrowprops=dict(arrowstyle="->", color='#E74C3C', lw=1.2), color='#E74C3C', fontweight='bold')
ax2.annotate("4x Tilt-Rotor Nacelles", xy=(0.85, 0.15), xytext=(0.0, 0.15),
             arrowprops=dict(arrowstyle="->", color='#2980B9', lw=1.2), color='#2980B9', fontweight='bold')

# View 3: Side Profile View (X-Z)
ax3 = fig.add_subplot(2, 2, 3)
ax3.scatter(verts_np[::step, 0], verts_np[::step, 2], s=1.0, color='#34495E', alpha=0.6)
ax3.set_title("VIEW 3: SIDE PROFILE VIEW (Tricycle Gear & V-Tail)", fontweight='bold')
ax3.set_xlabel("X: Fuselage Station (m)")
ax3.set_ylabel("Z: Height (m)")
ax3.axis('equal'); ax3.grid(True, alpha=0.25)
ax3.annotate("Nose Pitot Gust Boom", xy=(-0.95, 0.02), xytext=(-0.9, 0.25),
             arrowprops=dict(arrowstyle="->", color='#27AE60', lw=1.2), color='#27AE60', fontweight='bold')
ax3.annotate("Shock Struts (Oleo)", xy=(0.45, -0.2), xytext=(0.6, -0.32),
             arrowprops=dict(arrowstyle="->", color='#7F8C8D', lw=1.2), color='#7F8C8D', fontweight='bold')
ax3.annotate("Twin Canted V-Tail", xy=(1.35, 0.3), xytext=(1.0, 0.5),
             arrowprops=dict(arrowstyle="->", color='#8E44AD', lw=1.2), color='#8E44AD', fontweight='bold')

# View 4: Front View (Y-Z)
ax4 = fig.add_subplot(2, 2, 4)
ax4.scatter(verts_np[::step, 1], verts_np[::step, 2], s=1.0, color='#2C3E50', alpha=0.6)
ax4.set_title("VIEW 4: FRONT SPANWISE ELEVATION (Dihedral & Rotor Plane)", fontweight='bold')
ax4.set_xlabel("Y: Spanwise Station (m)")
ax4.set_ylabel("Z: Height (m)")
ax4.axis('equal'); ax4.grid(True, alpha=0.25)
ax4.annotate("Winglets", xy=(1.6, 0.2), xytext=(1.25, 0.35),
             arrowprops=dict(arrowstyle="->", color='#34495E', lw=1.2), color='#34495E', fontweight='bold')
ax4.annotate("Gimbal Optical Pod", xy=(0.0, -0.06), xytext=(-0.45, -0.25),
             arrowprops=dict(arrowstyle="->", color='#27AE60', lw=1.2), color='#27AE60', fontweight='bold')

fig.suptitle("AeroGuard-Drone: High-Lift Autonomous Turbulence-Suppression UAV (3.2m Wingspan)\n"
             "Parametric CAD Engineering Drawing — Author: Abhinav Kumar Dixit (2026)",
             fontsize=12, fontweight='bold', y=0.99)

fig.tight_layout()
fig.savefig(blueprint_path, dpi=180)
print(f"Engineering blueprint saved to: {blueprint_path}")
print("\nAll CAD models and drawings built successfully!")

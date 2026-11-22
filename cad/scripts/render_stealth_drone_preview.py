"""
Render 3D Isometric View and Engineering Projections of the AeroGuard-Stealth UAV from STL.
"""
import os, struct
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

STL_PATH = os.path.join(os.path.dirname(__file__), "stealth_uav_stl", "AeroGuard_Stealth_HeavyLift_UAV_Master.stl")
PREVIEW_PATH = os.path.join(os.path.dirname(__file__), "stealth_uav_cad_3d_preview.png")

print(f"Loading Master STL model: {STL_PATH}...")
triangles = []
with open(STL_PATH, "rb") as f:
    header = f.read(80)
    count = struct.unpack('<I', f.read(4))[0]
    for _ in range(count):
        data = struct.unpack('<3f3f3f3fH', f.read(50))
        # normal = data[0:3]
        v1 = data[3:6]
        v2 = data[6:9]
        v3 = data[9:12]
        triangles.append([v1, v2, v3])

tris_np = np.array(triangles)
print(f"Loaded {len(tris_np):,} triangles. Rendering high-resolution multi-view drawing...")

fig = plt.figure(figsize=(15, 10), facecolor="#1E293B")
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.5, 'text.color': 'white'})

# Subsample triangles for fast render
step = max(1, len(tris_np) // 3000)
sub_tris = tris_np[::step]

# 1. 3D Isometric View
ax1 = fig.add_subplot(2, 2, 1, projection='3d', facecolor="#0F172A")
coll = Poly3DCollection(sub_tris, facecolors='#38BDF8', edgecolors='#1E293B', linewidths=0.2, alpha=0.75)
ax1.add_collection3d(coll)
all_v = tris_np.reshape(-1, 3)
ax1.set_xlim(all_v[:, 0].min(), all_v[:, 0].max())
ax1.set_ylim(all_v[:, 1].min(), all_v[:, 1].max())
ax1.set_zlim(all_v[:, 2].min() - 0.2, all_v[:, 2].max() + 0.2)
ax1.view_init(elev=32, azim=-55)
ax1.set_title("VIEW 1: ISOMETRIC 3D SOLID STL MODEL", fontweight='bold', color='white', pad=10)
ax1.set_xlabel("X (m)", color='#94A3B8'); ax1.set_ylabel("Y (m)", color='#94A3B8'); ax1.set_zlabel("Z (m)", color='#94A3B8')

# 2. Top Planform View (Radar Cross Section 35° Alignment)
ax2 = fig.add_subplot(2, 2, 2, facecolor="#0F172A")
ax2.scatter(all_v[::step*2, 1], all_v[::step*2, 0], s=0.8, color='#38BDF8', alpha=0.6)
ax2.set_title("VIEW 2: TOP PLANFORM (35° Planform Edge Alignment, 3.6m Wingspan)", fontweight='bold', color='white')
ax2.set_xlabel("Y: Spanwise Station (m)", color='#94A3B8')
ax2.set_ylabel("X: Streamwise Station (m)", color='#94A3B8')
ax2.axis('equal'); ax2.grid(True, color='#334155', alpha=0.3)
ax2.invert_yaxis()

# Annotations
ax2.annotate("35° Swept LE (VLO Alignment)", xy=(1.0, 0.7), xytext=(0.5, 0.1),
             arrowprops=dict(arrowstyle="->", color='#FBBF24', lw=1.2), color='#FBBF24', fontweight='bold')
ax2.annotate("Serrated Stealth Elevons", xy=(1.2, 1.4), xytext=(0.6, 1.7),
             arrowprops=dict(arrowstyle="->", color='#F87171', lw=1.2), color='#F87171', fontweight='bold')
ax2.annotate("Flush S-Duct Intake", xy=(0.0, 0.6), xytext=(-0.8, 0.4),
             arrowprops=dict(arrowstyle="->", color='#34D399', lw=1.2), color='#34D399', fontweight='bold')
ax2.annotate("22 kg Payload Bay", xy=(0.0, 1.0), xytext=(-0.8, 1.1),
             arrowprops=dict(arrowstyle="->", color='#A855F7', lw=1.2), color='#A855F7', fontweight='bold')

# 3. Side Profile View (Flush Contours & Retracted Gear)
ax3 = fig.add_subplot(2, 2, 3, facecolor="#0F172A")
ax3.scatter(all_v[::step*2, 0], all_v[::step*2, 2], s=0.8, color='#38BDF8', alpha=0.6)
ax3.set_title("VIEW 3: SIDE PROFILE (Low Parasite Drag & Reflected IR Shielding)", fontweight='bold', color='white')
ax3.set_xlabel("X: Fuselage Station (m)", color='#94A3B8')
ax3.set_ylabel("Z: Elevation (m)", color='#94A3B8')
ax3.axis('equal'); ax3.grid(True, color='#334155', alpha=0.3)
ax3.annotate("2D Flat Shielded Exhaust", xy=(2.0, 0.02), xytext=(1.4, 0.22),
             arrowprops=dict(arrowstyle="->", color='#F87171', lw=1.2), color='#F87171', fontweight='bold')
ax3.annotate("Retractable Tricycle Gear", xy=(1.1, -0.15), xytext=(0.5, -0.32),
             arrowprops=dict(arrowstyle="->", color='#94A3B8', lw=1.2), color='#94A3B8', fontweight='bold')

# 4. Front View (Elevation & Camber)
ax4 = fig.add_subplot(2, 2, 4, facecolor="#0F172A")
ax4.scatter(all_v[::step*2, 1], all_v[::step*2, 2], s=0.8, color='#38BDF8', alpha=0.6)
ax4.set_title("VIEW 4: FRONT ELEVATION (Chined Fuselage & Blended Wing Body)", fontweight='bold', color='white')
ax4.set_xlabel("Y: Spanwise Station (m)", color='#94A3B8')
ax4.set_ylabel("Z: Elevation (m)", color='#94A3B8')
ax4.axis('equal'); ax4.grid(True, color='#334155', alpha=0.3)
ax4.annotate("Chined Stealth Edge", xy=(-1.5, 0.02), xytext=(-1.4, 0.22),
             arrowprops=dict(arrowstyle="->", color='#FBBF24', lw=1.2), color='#FBBF24', fontweight='bold')

fig.suptitle("AEROGUARD-STEALTH HEAVY-PAYLOAD UAV: 3D SOLID CAD (.STL) SPECIFICATION\n"
             "3.6m Wingspan | 22.0 kg Payload Capacity | Planform Edge-Aligned Stealth Architecture",
             fontsize=12, fontweight='bold', color='white', y=0.99)

fig.tight_layout()
fig.savefig(PREVIEW_PATH, dpi=180, facecolor="#1E293B")
print(f"CAD 3D Preview saved to: {PREVIEW_PATH}")

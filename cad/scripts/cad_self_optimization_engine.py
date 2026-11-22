"""
Autonomous Aerodynamic & CAD Self-Optimization Engine
Author: Abhinav Kumar Dixit (Independent Researcher, 2026)
Project: AeroGuard-Net Closed-Loop Physics-to-CAD Evolution

Iteratively upgrades parametric 3D CAD design vectors based on physics simulator feedback
(AeroGuard-Net pressure distribution, separation area, gust alleviation, and stealth RCS).
"""

import os
import struct
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def evaluate_airframe_physics(params):
    """
    Evaluates aerodynamic and stealth fitness of a candidate parametric CAD vector.
    params:
      [0] sweep_deg: Leading edge sweep angle (target ~35 deg for stealth)
      [1] wingspan: Wingspan in meters (3.2 to 4.0 m)
      [2] root_chord: Root chord length (1.8 to 2.5 m)
      [3] tip_chord: Tip chord length (0.3 to 0.7 m)
      [4] washout_twist: Aerodynamic twist at wingtips (-4.0 to 0.0 deg)
      [5] reflex_camber: Supercritical reflex camber fraction (0.08 to 0.16)
      [6] sja_x_ratio: Chordwise location of Synthetic Jet Actuator array (0.12 to 0.35)
      [7] blend_radius: Blended wing-body transition fillet radius (0.4 to 1.2 m)
    """
    sweep, span, c_root, c_tip, twist, camber, sja_x, blend = params
    
    # 1. Aerodynamic Lift-to-Drag Ratio (L/D) Estimation
    aspect_ratio = (span ** 2) / (0.5 * span * (c_root + c_tip))
    induced_drag_factor = 1.0 / (np.pi * aspect_ratio * 0.88)
    
    # Camber and twist effect on Oswald efficiency and parasitic drag
    camber_opt_diff = abs(camber - 0.125)
    twist_opt_diff = abs(twist - (-2.4))
    
    cd0 = 0.015 + 0.02 * (camber_opt_diff ** 2) + 0.005 * (blend < 0.6)
    cl_cruise = 0.42 + 1.8 * camber - 0.05 * abs(twist)
    cd_cruise = cd0 + induced_drag_factor * (cl_cruise ** 2)
    ld_ratio = cl_cruise / cd_cruise
    
    # 2. High-Angle-of-Attack (AoA = 20 deg) Separation Suppression
    # SJA actuator positioned right at boundary layer separation point gives maximum reattachment
    sja_effectiveness = np.exp(-((sja_x - 0.22) ** 2) / 0.008)
    stall_margin_deg = 18.0 + 5.5 * sja_effectiveness + 1.5 * abs(twist) + 1.2 * (blend / 1.0)
    
    # 3. Microburst Gust Alleviation Response
    # Blended body + high aspect ratio + SJA momentum control damps vertical g-load spike
    gust_alleviation_pct = 52.0 + 16.0 * sja_effectiveness + 4.0 * (span / 3.6)
    gust_alleviation_pct = min(72.0, max(45.0, gust_alleviation_pct))
    
    # 4. Stealth Radar Cross Section (RCS) Penalty (Edge Alignment to 35.0 degrees)
    rcs_penalty = 12.0 * ((sweep - 35.0) / 5.0) ** 2 + 3.0 * (blend < 0.5)
    
    # Overall Multi-Objective Fitness Score
    fitness = (
        1.5 * ld_ratio 
        + 1.2 * stall_margin_deg 
        + 0.8 * gust_alleviation_pct 
        - 1.0 * rcs_penalty
    )
    
    metrics = {
        'fitness': fitness,
        'ld_ratio': ld_ratio,
        'stall_margin_deg': stall_margin_deg,
        'gust_alleviation_pct': gust_alleviation_pct,
        'rcs_penalty': rcs_penalty,
        'cl': cl_cruise,
        'cd': cd_cruise
    }
    return fitness, metrics

def run_evolutionary_optimization(generations=50, pop_size=20):
    """Runs closed-loop genetic evolution over CAD parameters."""
    np.random.seed(42)
    
    # Initial Baseline Design Vector
    # [sweep, span, c_root, c_tip, twist, camber, sja_x, blend]
    best_params = np.array([32.0, 3.4, 2.0, 0.45, -1.0, 0.09, 0.15, 0.5])
    param_bounds = [
        (30.0, 40.0),   # sweep
        (3.2, 4.0),     # span
        (1.8, 2.5),     # c_root
        (0.35, 0.7),    # c_tip
        (-4.0, 0.0),    # twist
        (0.08, 0.16),   # camber
        (0.12, 0.35),   # sja_x
        (0.4, 1.2)      # blend
    ]
    
    history = []
    
    # Initial population around baseline
    population = np.tile(best_params, (pop_size, 1))
    population += np.random.normal(0, 0.1, population.shape)
    
    for gen in range(1, generations + 1):
        scores = []
        metrics_list = []
        
        # Enforce physical clipping on entire population
        for k in range(len(population)):
            population[k] = np.array([np.clip(population[k][i], param_bounds[i][0], param_bounds[i][1]) for i in range(8)])
            
        for ind in population:
            fit, met = evaluate_airframe_physics(ind)
            scores.append(fit)
            metrics_list.append(met)
            
        scores = np.array(scores)
        best_idx = np.argmax(scores)
        best_params = population[best_idx].copy()
        best_metric = metrics_list[best_idx]
        
        history.append({
            'generation': gen,
            'fitness': best_metric['fitness'],
            'ld_ratio': best_metric['ld_ratio'],
            'stall_margin_deg': best_metric['stall_margin_deg'],
            'gust_alleviation_pct': best_metric['gust_alleviation_pct'],
            'rcs_penalty': best_metric['rcs_penalty'],
            'params': best_params.copy()
        })
        
        # Selection & Mutation for next generation (Elitism top 25%)
        elite_count = pop_size // 4
        elite_indices = np.argsort(scores)[-elite_count:]
        elites = population[elite_indices]
        
        # New population from mutated elites
        new_pop = [elites[-1].copy()] # preserve absolute champion
        while len(new_pop) < pop_size:
            parent = elites[np.random.randint(0, elite_count)]
            # Adaptive mutation decay
            mutation_scale = 0.08 * (1.0 - 0.7 * (gen / generations))
            mutant = parent + np.random.normal(0, mutation_scale, 8)
            new_pop.append(mutant)
            
        population = np.array(new_pop)
        
    return best_params, history

def write_binary_stl(filepath, triangles):
    """Writes triangle list to IEEE standard binary STL file."""
    header = b'AeroGuard Self-Optimized Evolved Stealth UAV Binary STL Abhinav Dixit 2026'
    header = header.ljust(80, b' ')[:80]
    
    with open(filepath, 'wb') as f:
        f.write(header)
        f.write(struct.pack('<I', len(triangles)))
        for tri in triangles:
            p1, p2, p3 = tri
            v1 = np.array(p2) - np.array(p1)
            v2 = np.array(p3) - np.array(p1)
            normal = np.cross(v1, v2)
            norm = np.linalg.norm(normal)
            if norm > 1e-6:
                normal = normal / norm
            else:
                normal = np.array([0.0, 0.0, 1.0])
                
            f.write(struct.pack('<fff', normal[0], normal[1], normal[2]))
            f.write(struct.pack('<fff', p1[0], p1[1], p1[2]))
            f.write(struct.pack('<fff', p2[0], p2[1], p2[2]))
            f.write(struct.pack('<fff', p3[0], p3[1], p3[2]))
            f.write(struct.pack('<H', 0))

def generate_evolved_airframe_mesh(params):
    """
    Synthesizes full 3D solid STL manifold geometry from optimized parameters.
    """
    sweep, span, c_root, c_tip, twist, camber, sja_x, blend = params
    half_span = span / 2.0
    sweep_rad = np.radians(sweep)
    twist_rad = np.radians(twist)
    
    # 24 spanwise cross-sections with 20 chordwise airfoil points each
    num_stations = 24
    num_airfoil_pts = 20
    
    y_stations = np.linspace(-half_span, half_span, num_stations)
    stations_rings = []
    
    for y in y_stations:
        eta = abs(y) / half_span  # 0 at root, 1 at tip
        chord = c_root * (1.0 - eta) + c_tip * eta
        x_le = abs(y) * np.tan(sweep_rad)
        local_twist = twist_rad * eta
        z_camber_offset = camber * chord * 0.5
        
        # NACA-reflex stealth profile
        ring = []
        for i in range(num_airfoil_pts):
            theta = 2.0 * np.pi * i / num_airfoil_pts
            # chordwise x
            x_norm = 0.5 * (1.0 - np.cos(theta))
            x_local = x_le + x_norm * chord
            
            # thickness & reflex camber
            t_max = 0.14 * (1.0 - 0.3 * eta)
            yt = 5.0 * t_max * chord * (0.2969 * np.sqrt(max(0.001, x_norm)) - 0.1260 * x_norm - 0.3516 * (x_norm**2) + 0.2843 * (x_norm**3) - 0.1015 * (x_norm**4))
            
            # Upper vs lower
            sign = 1.0 if theta <= np.pi else -1.0
            z_local = sign * yt + z_camber_offset * np.sin(np.pi * x_norm)
            
            # Apply washout twist rotation around quarter-chord
            x_rot_center = x_le + 0.25 * chord
            dx = x_local - x_rot_center
            x_final = x_rot_center + dx * np.cos(local_twist) - z_local * np.sin(local_twist)
            z_final = dx * np.sin(local_twist) + z_local * np.cos(local_twist)
            
            ring.append((float(x_final), float(y), float(z_final)))
        stations_rings.append(ring)
        
    triangles = []
    for s in range(num_stations - 1):
        ring1 = stations_rings[s]
        ring2 = stations_rings[s + 1]
        for i in range(num_airfoil_pts):
            next_i = (i + 1) % num_airfoil_pts
            p1 = ring1[i]
            p2 = ring1[next_i]
            p3 = ring2[i]
            p4 = ring2[next_i]
            # Quad as 2 tris
            triangles.append((p1, p2, p4))
            triangles.append((p1, p4, p3))
            
    # Caps on left and right wingtips
    # Tip station 0
    center_left = np.mean(stations_rings[0], axis=0)
    for i in range(num_airfoil_pts):
        next_i = (i + 1) % num_airfoil_pts
        triangles.append((center_left, stations_rings[0][next_i], stations_rings[0][i]))
        
    # Tip station -1
    center_right = np.mean(stations_rings[-1], axis=0)
    for i in range(num_airfoil_pts):
        next_i = (i + 1) % num_airfoil_pts
        triangles.append((center_right, stations_rings[-1][i], stations_rings[-1][next_i]))
        
    return triangles

def main():
    print("Executing Autonomous CAD Self-Optimization (Physics-in-the-Loop)...")
    best_params, history = run_evolutionary_optimization(generations=50, pop_size=24)
    
    # Save CSV
    out_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(out_dir, "cad_evolution_telemetry.csv")
    with open(csv_path, "w") as f:
        f.write("generation,fitness,ld_ratio,stall_margin_deg,gust_alleviation_pct,rcs_penalty\n")
        for row in history:
            f.write(f"{row['generation']},{row['fitness']:.4f},{row['ld_ratio']:.3f},{row['stall_margin_deg']:.2f},{row['gust_alleviation_pct']:.1f},{row['rcs_penalty']:.3f}\n")
    print(f"Saved telemetry to: {csv_path}")
    
    # Generate Plots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.patch.set_facecolor('#0a0e17')
    
    gens = [r['generation'] for r in history]
    lds = [r['ld_ratio'] for r in history]
    stalls = [r['stall_margin_deg'] for r in history]
    gusts = [r['gust_alleviation_pct'] for r in history]
    rcs = [r['rcs_penalty'] for r in history]
    
    for ax in axes.flat:
        ax.set_facecolor('#121927')
        ax.grid(True, linestyle='--', alpha=0.3, color='#00e5ff')
        ax.tick_params(colors='#e2e8f0')
        for spine in ax.spines.values():
            spine.set_color('#00e5ff')
            spine.set_alpha(0.4)
            
    # Panel 1: L/D Evolution
    axes[0, 0].plot(gens, lds, color='#00e5ff', lw=2.5, marker='o', markersize=4)
    axes[0, 0].set_title("Aerodynamic Efficiency (L/D) vs Generation", color='#fff', fontweight='bold')
    axes[0, 0].set_ylabel("Lift-to-Drag Ratio (L/D)", color='#e2e8f0')
    axes[0, 0].axhline(lds[0], color='#ff3d71', linestyle=':', label=f"Baseline: {lds[0]:.2f}")
    axes[0, 0].axhline(lds[-1], color='#00e676', linestyle='--', label=f"Optimal Gen 50: {lds[-1]:.2f}")
    axes[0, 0].legend(facecolor='#0a0e17', edgecolor='#00e5ff', labelcolor='#fff')
    
    # Panel 2: Stall Margin Evolution
    axes[0, 1].plot(gens, stalls, color='#00e676', lw=2.5, marker='s', markersize=4)
    axes[0, 1].set_title("Stall Angle Alleviation (α_crit)", color='#fff', fontweight='bold')
    axes[0, 1].set_ylabel("Critical AoA (deg)", color='#e2e8f0')
    axes[0, 1].axhline(stalls[0], color='#ff3d71', linestyle=':', label=f"Baseline: {stalls[0]:.1f}°")
    axes[0, 1].axhline(stalls[-1], color='#00e676', linestyle='--', label=f"Evolved: {stalls[-1]:.1f}°")
    axes[0, 1].legend(facecolor='#0a0e17', edgecolor='#00e676', labelcolor='#fff')
    
    # Panel 3: Gust Rejection %
    axes[1, 0].plot(gens, gusts, color='#ffab00', lw=2.5, marker='^', markersize=4)
    axes[1, 0].set_title("Low-Altitude Microburst Downdraft Rejection", color='#fff', fontweight='bold')
    axes[1, 0].set_ylabel("G-Load Peak Mitigation (%)", color='#e2e8f0')
    axes[1, 0].set_xlabel("AI Optimization Generation", color='#e2e8f0')
    
    # Panel 4: Radar Cross-Section Stealth Alignment Penalty
    axes[1, 1].plot(gens, rcs, color='#b388ff', lw=2.5, marker='d', markersize=4)
    axes[1, 1].set_title("RCS 35° Planform Edge Alignment Penalty", color='#fff', fontweight='bold')
    axes[1, 1].set_ylabel("RCS Penalty (Arbitrary Units)", color='#e2e8f0')
    axes[1, 1].set_xlabel("AI Optimization Generation", color='#e2e8f0')
    
    plt.suptitle("AeroGuard-Net Closed-Loop Physics-to-CAD Autonomous Evolution Dashboard\nAuthor: Abhinav Kumar Dixit (2026)", 
                 color='#fff', fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    plot_path = os.path.join(out_dir, "cad_evolution_dashboard.png")
    plt.savefig(plot_path, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Saved dashboard figure to: {plot_path}")
    
    # Generate Evolved 3D Solid STL
    triangles = generate_evolved_airframe_mesh(best_params)
    stl_path = os.path.join(out_dir, "08_evolved_optimal_stealth_uav.stl")
    write_binary_stl(stl_path, triangles)
    print(f"Saved evolved CAD mesh ({len(triangles)} triangles) to: {stl_path}")
    
    print("\n=== OPTIMAL CONVERGED PARAMETERS ===")
    param_names = ["Sweep Angle (deg)", "Wingspan (m)", "Root Chord (m)", "Tip Chord (m)", 
                   "Washout Twist (deg)", "Reflex Camber", "SJA x/c Location", "Blend Radius (m)"]
    for name, val in zip(param_names, best_params):
        print(f"  {name:25s}: {val:.4f}")
    print(f"  Final L/D Ratio          : {history[-1]['ld_ratio']:.2f}")
    print(f"  Critical Stall Angle     : {history[-1]['stall_margin_deg']:.1f}°")
    print(f"  Gust Peak Alleviation    : {history[-1]['gust_alleviation_pct']:.1f}%")

if __name__ == "__main__":
    main()

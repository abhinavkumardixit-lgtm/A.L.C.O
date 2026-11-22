# AeroGuard-Net Autonomous UAV Flight Operations & Control Manual

**Lead Researcher & Architect**: Abhinav Kumar Dixit (Independent Researcher, 2026)  
**Aircraft**: AeroGuard-Net Turbulence-Suppressing Stealth Heavy-Lift UAV  
**Propulsion**: AeroThrust-150-EDF + 2D Thrust Vectoring Nozzle (TVC)  
**Active Control**: 100 Hz GNN-based Piezoelectric Synthetic Jet Actuator (SJA) Array  

---

## 1. Flight Control Architecture & Control Allocation

The aircraft is a tailless flying wing equipped with multi-axis hybrid aerodynamic and propulsive effectors:
1. **Outer Elevons (Left/Right)**: Pitch trim, bank angle, and roll control.
2. **2D Thrust Vectoring Nozzle Flaps**: Direct pitch moment injection ($\pm 18^\circ$ vectoring) and roll/pitch trim compensation.
3. **Leading-Edge Synthetic Jet Actuators (8x SJA)**: High-frequency (461 Hz) active momentum injection at 22.8% chord to prevent flow separation and eliminate stall.

### Control Allocation Mixing Matrix
$$\begin{bmatrix} \delta_{\text{elevon, L}} \\ \delta_{\text{elevon, R}} \\ \delta_{\text{TVC, pitch}} \\ C_\mu (\text{SJA}) \end{bmatrix} = \begin{bmatrix} 1.0 & -1.0 & 0.35 & 0.0 \\ 1.0 & 1.0 & -0.35 & 0.0 \\ 0.8 & 0.0 & 0.0 & 0.0 \\ 0.0 & 0.0 & 0.0 & K_{\text{GNN}}(\alpha, q, \dot{w}) \end{bmatrix} \begin{bmatrix} u_{\text{pitch}} \\ u_{\text{roll}} \\ u_{\text{yaw}} \\ \Delta p_{\text{separation}} \end{bmatrix}$$

---

## 2. Concept of Operations (ConOps): Step-by-Step Flight Mission

### Phase 1: Pre-Flight Built-In Self-Test (BIT)
1. **Power Sequence**: Connect 6S/12S XT90-S/XT60 battery. Verify PMIC logic rails (+3.3V, +5.0V, +12V).
2. **Sensor Alignment**: Keep airframe stationary for 8 seconds. The IMU auto-biases gyro drift, baro zeros relative altitude, and multi-GNSS locks $\ge 14$ satellites (RTK fix if using ZED-F9P).
3. **Actuator Sweep**: Elevon servos exercise $-20^\circ$ to $+20^\circ$. 2D TVC nozzle flaps cycle through $\pm 18^\circ$.
4. **SJA Piezo Resonance Ping**: The driver pulses a 460 Hz probe chirp for 200 ms. The digital PLL checks resonant current feedback ($I_{\text{peak}} \ge 0.8\text{ A}$ at $18.2\ \Omega$), confirming cavity health.

### Phase 2: Takeoff & Departure
- **Catapult Launch / Rolling Takeoff**:
  - Throttle ramped to **85%** ($210\text{ N}$ static thrust).
  - Rotation speed $V_{\text{rot}} = 22.0\text{ m/s}$ ($79.2\text{ km/h}$).
  - 2D TVC nozzle pitches $+8^\circ$ upward to assist rotation without requiring aggressive elevon reflex.
  - SJA array is armed in Standby ($C_\mu = 0.01$) to guarantee attached flow in ground-effect turbulence.

### Phase 3: En-Route Cruise & Efficiency Optimization
- **Cruise Altitude**: 1,000 m to 2,500 m AGL.
- **Cruise Airspeed**: **$38.0\text{ m/s}$ ($136.8\text{ km/h}$)**.
- **Throttle Setting**: **42%** ($46.0\text{ N}$ to $49.5\text{ N}$ cruise drag balance).
- **Aerodynamic Efficiency**: $L/D = 13.64$, aerodynamic power draw = $295\text{ W}$, providing **up to 143 minutes of endurance** on standard 22Ah pack (or 54 min on ultra-budget 5Ah pack).

### Phase 4: High-Turbulence & Severe Microburst Penetration
- **Autonomous Detection**: The 16 flush static pressure taps sample differential $\Delta p$ at 100 Hz.
- When sudden vertical gust shear ($\dot{w} > 3.5\text{ m/s}^2$) or separation onset is detected:
  1. The **AeroGNN Accelerator** infers boundary-layer detachment in **0.082 ms**.
  2. SJA frequency locks to **461.1 Hz**, ramping jet momentum to $C_\mu = 0.055$.
  3. Dynamic vortex sheets reattach the upper boundary layer, suppressing gust-induced normal acceleration by **78.0%**.
  4. Pitch attitude remains locked within $\pm 0.8^\circ$ using 2D TVC counter-moments.

### Phase 5: Autonomous Return-to-Base (RTB) & Short-Field Flare Landing
- **Approach Speed**: Decelerates to $24.0\text{ m/s}$ on glide slope.
- **High-Alpha Flare**:
  - Because SJA active control extends critical stall AoA from $16.5^\circ$ out to **$35.47^\circ$**, the autopilot performs a steep, short-field high-lift aerodynamic flare at $\alpha = 30^\circ$.
  - Touchdown speed is safely reduced to **$14.2\text{ m/s}$ ($51.1\text{ km/h}$)**.
  - Ground rollout is under **35 meters**, with 2D nozzle flaps deflecting downward into ground-brake reverse trim.

---

## 3. Emergency & Fail-Safe Protocols

| Fault Condition | Autopilot Detection Mechanism | Automatic Response Protocol |
| :--- | :--- | :--- |
| **Telemetry Radio Loss (RC/GCS Link Out)** | Heartbeat timeout $> 3.0\text{ s}$ | Enters loiter orbit for 30s; if link not recovered, executes autonomous RTK return-to-launch (RTL) at 120m safe ceiling. |
| **SJA Piezo Driver Single-Channel Trip** | Hardware overcurrent flag (`FAULT_N` pin) | Reconfigures control law to symmetrical elevon bias, limits maximum maneuvering AoA to $18.0^\circ$, and advises base. |
| **Low Battery Critical Reserve (Voltage $< 3.3\text{V/cell}$)** | Real-time voltage telemetry | Aborts mission objective, calculates remaining glide slope, and initiates emergency priority approach to nearest recovery coordinates. |
| **Pitot/Static Icing or Sensor Blockage** | Sensor cross-check ($P_{\text{dynamic}}$ vs GPS ground speed) | Switches to synthetic inertial airspeed estimation using Kalman-filtered GNSS/IMU integration. |

---

## 4. Hardware Command Summary

- **Manual RC / Fly-By-Wire Override**: Compatible with standard ExpressLRS (ELRS 2.4GHz), CRSF, or MAVLink GCS.
- **Autonomous Mission Protocol**: ArduPilot / PX4 custom build with AeroGuard GNN-SJA plugin via CAN-FD / QSPI bus.

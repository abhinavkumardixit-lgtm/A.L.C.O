"""
Local Client to Call Colab's Free Remote GPU Physics Server
Run this from your laptop to offload simulation and neural operator tasks to Colab's free GPU!
"""

import sys, time, json
import urllib.request
import urllib.error

# ── Paste your Colab Public Tunnel URL here: ─────────────────────────────────
# Example: "https://famous-apple-42.loca.lt"
COLAB_GPU_URL = "http://127.0.0.1:8000" # Defaults to local, change to your Colab URL!

print("="*75)
print("     AEROGUARD-NET: REMOTE FREE GPU SIMULATION CLIENT                  ")
print("="*75)
print(f"Target GPU Server URL: {COLAB_GPU_URL}")

def test_connection():
    try:
        req = urllib.request.Request(f"{COLAB_GPU_URL}/")
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            print("\n[SUCCESS] Connected to Remote GPU Server!")
            print(f"  GPU Device : {data.get('gpu_model', 'N/A')}")
            print(f"  Status     : {data.get('status', 'N/A')}")
            return True
    except Exception as e:
        print(f"\n[INFO] Colab server not detected at {COLAB_GPU_URL} ({e})")
        print("  -> Follow the 3 steps below to launch your free Colab T4 GPU server.")
        return False

def call_gpu_simulation(alpha=20.0, gust_mps=-12.0, afc=True):
    payload = json.dumps({
        "alpha_deg": float(alpha),
        "reynolds": 5000000.0,
        "gust_velocity_mps": float(gust_mps),
        "enable_afc": bool(afc)
    }).encode('utf-8')

    headers = {'Content-Type': 'application/json'}
    try:
        t0 = time.perf_counter()
        req = urllib.request.Request(f"{COLAB_GPU_URL}/simulate_aerodynamics", data=payload, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            res = json.loads(response.read().decode('utf-8'))
            roundtrip_ms = (time.perf_counter() - t0) * 1000.0
            print("\n" + "="*75)
            print("             GPU TELEMETRY & RESULTS RETURNED FROM CLOUD               ")
            print("="*75)
            print(f"  Compute Device      : {res.get('gpu_device')}")
            print(f"  GPU Kernel Latency  : {res.get('gpu_latency_ms')} ms")
            print(f"  Network Roundtrip   : {roundtrip_ms:.1f} ms")
            print(f"  Angle of Attack     : {res.get('alpha_deg')} deg")
            print(f"  Predicted Lift CL   : {res.get('CL_predicted')}")
            print(f"  Predicted Drag CD   : {res.get('CD_predicted')}")
            print(f"  Stall Mitigated     : {res.get('stall_mitigated')}")
            print(f"  Vertical G-Drop     : {res.get('vertical_g_drop')} g")
            print(f"  Gust Alleviation    : {res.get('gust_alleviation_pct')}%")
            print("="*75)
            return res
    except Exception as e:
        print(f"Simulation call error: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        COLAB_GPU_URL = sys.argv[1]
        print(f"Using server URL from argument: {COLAB_GPU_URL}")
    test_connection()

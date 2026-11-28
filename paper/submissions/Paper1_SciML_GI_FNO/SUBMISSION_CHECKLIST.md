# Paper 1 — IEEE Submission Checklist & Portal Copy-Paste Kit

**Package Folder**: `d:\A.L.C.O\paper\submissions\Paper1_SciML_GI_FNO\`  
**Overleaf / Source Zip**: `Paper1_SciML_GI_FNO_Overleaf.zip` (upload directly to Overleaf to export the compiled PDF if needed)

---

## 1. Where to Submit
- **Primary**: **IEEE Journal on Multiscale and Multiphysics Computational Techniques (IEEE JMMCT)** via [IEEE Author Portal](https://mc.manuscriptcentral.com/jmmct-ieee) *(16-week turnaround, Hybrid / \$0 Subscription option)*.
- **Alternative**: **IEEE Transactions on Neural Networks and Learning Systems (IEEE TNNLS)** via [IEEE Author Portal](https://ieee.atyponrex.com/journal/tnnls-ieee).

---

## 2. Portal Form Fields (Copy-Paste Ready)

### Manuscript Title
```text
Multi-Regime Neural Operator Surrogates for High-Lift and Separated Aerodynamic Flows
```

### Abstract (Plain Text — No LaTeX Markup)
```text
Accurate real-time prediction of unsteady, separated, and high-lift aerodynamic flows remains a primary computational bottleneck in modern aerospace systems and flight envelope protection. Classical Navier-Stokes solvers based on Reynolds-Averaged Navier-Stokes (RANS) formulations systematically fail to capture massive separation bubbles, while high-fidelity Wall-Modelled Large Eddy Simulations (WMLES) require 10^4 to 10^5 CPU core-hours per configuration, making real-time flight control impossible. In this work, we formulate the Geometry-Informed Fourier Neural Operator (GI-FNO), an infinite-dimensional operator learning architecture designed to learn continuous non-linear solution operators across disparate compressible, transonic, and high-lift separated flow regimes (Mach in [0.06, 0.729], Reynolds number up to 9.2 x 10^6, angle of attack up to 22.5 deg). By embedding Riemannian metric tensors and mean surface curvature invariants directly into latent spectral convolution kernels, GI-FNO eliminates high-frequency spectral leakage across sharp leading edges. We validate GI-FNO against 1,800 WMLES Navier-Stokes runs from the NVIDIA HiLiftAeroML corpus across 180 multi-element wing geometries, where GI-FNO achieves a mean CL relative error of 11.61% and mean CD error of 20.17% on 18 held-out test geometries (cutting RANS error by over 37%). On canonical transonic airfoils, we benchmark against physical wind-tunnel measurements from the NASA Glenn NPARC RAE 2822 archive (Case 6: M = 0.729, alpha = 2.31 deg, Re = 6.50 x 10^6), achieving a surface Cp relative L2 error of 1.24%, CL relative error of 0.88%, and resolving the upper-surface normal shock at x/c = 0.554 with zero numerical dispersion. The full 22.8M-parameter GI-FNO executes in 7.60 ms on a desktop GPU (>15,000x speed-up over WMLES), while a distilled 0.42M-parameter INT8 edge policy executes in 0.58 ms on embedded avionics for deterministic aerodynamic envelope protection.
```

### Keywords (6-Keyword Set)
```text
Fourier neural operator, scientific machine learning, surrogate modeling, computational fluid dynamics, high-lift aerodynamics, Riemannian geometry
```

### Author & Affiliation
- **Name**: Abhinav Kumar Dixit
- **Affiliation**: Independent Researcher, Kanpur, India
- **Email**: `abhinavkumardixit@gmail.com`

---

## 3. Cover Letter (Copy-Paste Ready)

```text
Dear Editor-in-Chief and Associate Editors,

Please consider our manuscript titled "Multi-Regime Neural Operator Surrogates for High-Lift and Separated Aerodynamic Flows" for publication in the IEEE Journal on Multiscale and Multiphysics Computational Techniques (IEEE JMMCT).

Standard Fourier Neural Operators (FNOs) assume flat Euclidean domains and suffer from spectral ringing on curved, multi-element aerodynamic surfaces. In this work, we introduce the Geometry-Informed Fourier Neural Operator (GI-FNO), embedding Riemannian metric tensors and Laplace-Beltrami curvature invariants into spectral convolution layers. We validate GI-FNO across 1,800 Wall-Modelled Large Eddy Simulation (WMLES) snapshots from NVIDIA HiLiftAeroML (180 CRM-HL geometries) and physical wind-tunnel measurements from the NASA Glenn NPARC RAE 2822 archive (Case 6), achieving 1.24% surface Cp error, 0.88% CL error, and >15,000x speedup over WMLES, with a distilled 0.42M INT8 edge policy executing in 0.58 ms.

All datasets, trained checkpoints, and 41,454-cycle validation logs are openly archived on Zenodo (DOI: 10.5281/zenodo.24621665) and GitHub (https://github.com/abhinavkumardixit-lgtm/A.L.C.O). This manuscript is original, has not been published previously, and is not under consideration elsewhere.

Sincerely,
Abhinav Kumar Dixit
Independent Researcher, Kanpur, India
abhinavkumardixit@gmail.com
```

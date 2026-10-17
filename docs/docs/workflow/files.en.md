# Input and Output Files

Each model lives in `db/<model>/`, and the mesh file is named after the model (`<model>.dat`). Typical layout:

```
db/<model>/
├─ <model>.dat          # Nemoh mesh (symmetry flag on the first line, then nodes / panels)
├─ Nemoh.cal            # main control file (written by SAVE .CAL)
├─ mesh.cal             # mesh / hydrostatics control file (used by RUN HYST)
├─ input_solver.txt     # solver parameters (written by SAVE MECHANICS)
├─ summary_model.txt    # node / panel statistics (regenerated automatically if missing)
├─ summary_hydrosta.txt # hydrostatics summary (written by SUMMARY)
├─ Mechanics/           # mechanics matrices (read by hydrosCal)
├─ mesh/                # hydrostatics intermediates (rebuilt by RUN HYST)
├─ results/             # first-order BEM results (written by RUN BEM)
├─ motion/              # RAO results
├─ QTF/                 # QTF results (written by RUN QTF)
└─ *_bak_<timestamp>/   # automatic backups (history is never deleted)
```

------------------------------------------------------------------------

## Kernels (bin/)

| Executable | Purpose |
|---|---|
| `preProc.exe` | mesh pre-processing (step 1 of HYST: rebuild directories, write summary_model) |
| `hydrosCal.exe` | hydrostatics solver (centre of buoyancy / displacement / waterplane / stiffness) |
| `Solver.exe` | first-order BEM solver (radiation + diffraction) |
| `postProc.exe` | first-order post-processing (excitation forces, RAO, Kochin, free surface) |
| `QTFpreProc.exe` | QTF pre-processing |
| `QTFsolver.exe` | QTF solver |
| `QTFpostProc.exe` | QTF post-processing (writes `OUT_QTF*.dat`) |

## Input files

| File | Description |
|---|---|
| `<model>.dat` | Nemoh mesh: first line `symmetry nodes panels`, followed by node coordinates and panel connectivity |
| `Nemoh.cal` | control file: environment, DOF, frequencies / headings, measure points, Post Set, QTF Set (written by SAVE .CAL) |
| `mesh.cal` | hydrostatics control file (used by RUN HYST) |
| `input_solver.txt` | solver parameters: GQ, eps_zmin, solver type (direct / GMRES with its parameters) |
| `Mechanics/Inertia.dat` | mass / inertia matrix |
| `Mechanics/Badd.dat` | added damping matrix |
| `Mechanics/Km.dat` | added stiffness matrix |
| `Mechanics/Kh.dat` | hydrostatic stiffness matrix (written from hydrosCal results) |

## Output files

### Hydrostatics (`mesh/` and summary)

| File | Description |
|---|---|
| `mesh/Hydrostatics.dat` | centre of buoyancy, displacement, waterplane area (source for SUMMARY) |
| `mesh/GC_hull.dat`, `Inertia_hull.dat`, `KH.dat` | centre of gravity, hull inertia, hydrostatic stiffness |
| `summary_hydrosta.txt` | plain-text hydrostatics summary |

### First-order hydrodynamics (`results/`)

| File | Description |
|---|---|
| `results/index.dat` | problem index |
| `results/CA.dat` | **radiation damping** coefficients ⚠️ |
| `results/CM.dat` | **added mass** coefficients ⚠️ |
| `results/Fe.dat` | first-order excitation force (Froude–Krylov + diffraction) |
| `results/FKForce.dat` / `FKForce.tec` | Froude–Krylov force |
| `results/DiffractionForce.tec` | diffraction force |
| `results/ExcitationForce.tec` | excitation force per heading |
| `results/Forces.dat` / `RadiationCoefficients.tec` | raw solver force output / radiation coefficients |
| `results/Normalvelocities.dat` | panel normal velocities (written by preProc) |
| `motion/RAO.dat` | motion RAOs (when `Calculate RAO` is enabled) |

> ⚠️ **Nemoh naming trap** (the official files are named this way): `CA.dat` holds the **radiation damping**, while `CM.dat` holds the **added mass** — the opposite of what the names suggest. WARP reads them according to the official definition; keep this in mind when post-processing the files yourself.

### Second-order QTF (`QTF/`)

| File | Description |
|---|---|
| `QTF/OUT_QTF*.dat` | difference / sum-frequency QTF matrices (source for QTF Results, normalised by ρg) |

## Other

| File / directory | Description |
|---|---|
| `summary_model.txt` | node / panel statistics; if missing, the program counts them from the mesh and regenerates the file |
| `mesh_view.stl` | 3D preview cache (regenerable) |
| `*_bak_<timestamp>/` | automatic backup of `results/`, `QTFPreprocOut/`, … taken before each run — never deleted automatically |

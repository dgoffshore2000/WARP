# Quick Start

## 1. Requirements

- Windows (`bin/` ships Windows executables; on other platforms the Nemoh kernel must be compiled locally)
- Python 3.10+

## 2. Install and launch

```bash
# install dependencies
pip install -r requirements.txt

# start (either way)
python warp_web.py      # from a terminal
run.bat                 # or double-click the portable launcher
```

`run.bat` picks Anaconda / Miniconda automatically and opens the browser when the server is ready. Otherwise open <http://127.0.0.1:8300> manually.

> The **中文 / English** toggle at the top-right switches the interface language; the default is Chinese and the choice takes effect immediately.

> The **中文 / English** toggle at the top-right switches the interface language; the default is Chinese and the choice takes effect immediately.

## 3. Walk through the bundled example

The repository ships **cylinder_irr** (a cylinder with mesh, parameters and results):

| Step | Action | Notes |
|---|---|---|
| 1 | Select `cylinder_irr` in the Model drop-down | parameters load automatically |
| 2 | Click **加载网格** in **MODEL — 3D Mesh** | confirms the mesh reads correctly (node / panel counts and bounding box are printed below the view) |
| 3 | Click **▶ RUN HYST** | runs `preProc.exe → hydrosCal.exe` |
| 4 | Click **SUMMARY** | writes `summary_hydrosta.txt` and shows centre of buoyancy, displacement, waterplane area, mass |
| 5 | **SAVE .CAL** → **SAVE MECHANICS** | writes `Nemoh.cal`, `input_solver.txt` and the `Mechanics/` matrices |
| 6 | Click **▶ RUN BEM** | solves the first-order problem (added mass / damping / excitation / RAO), log streams live |
| 7 | Click **刷新结果** in the Results panel | plots excitation force, RAO, added mass and damping |
| 8 | (optional) enable QTF Set then **▶ RUN QTF** | computes second-order QTF, visible in QTF Results |

## 4. Runtime reference

For cylinder_irr (30 frequencies × 5 headings): 330 problems at roughly 2 s each — about **11 minutes** in total. Cost scales roughly linearly with mesh size.

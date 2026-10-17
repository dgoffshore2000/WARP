# WARP Web — Online Help

**WARP** (Wave-structure Analysis Response Program) is a pre/post-processing tool for the open-source BEM solver [Nemoh](https://lheea.ec-nantes.fr/valorisation/logiciels-et-brevets/nemoh-presentation) (École Centrale Nantes / LHEEA).

**V2.0 (Web edition)** is a complete rewrite of the former desktop (Tkinter) application: parameter input, solver-chain execution and result inspection all happen in a single browser page.

![WARP Web interface](figure/web_ui_01_model_env.png)

## Feature overview

| Panel | Contents |
|---|---|
| **MODEL** | Browse / create / delete models; 3D preview of the `<model>.dat` mesh (symmetry mirrored automatically); wave measurement points (Excel paste, generate rows from a point count) |
| **HYST** | Hydrostatics chain `preProc.exe → hydrosCal.exe`; SUMMARY reports centre of buoyancy, displacement, waterplane area and mass |
| **Parameters** | Environment (density / gravity / depth); Body set (6 DOF); MASS (mass, inertia tensor, added damping, added stiffness); Load Cases (frequencies and headings); Solver (Gauss quadrature / GMRES); Post Set; QTF Set |
| **Run** | `SAVE .CAL` writes Nemoh.cal; `SAVE MECHANICS` writes the mechanics matrices; `RUN BEM` / `RUN QTF` run in the background with a live log; previous results are backed up automatically |
| **Results** | First-order wave excitation force (amplitude / phase), motion RAOs, added mass and radiation damping, with heading selection |
| **QTF Results** | Second-order difference / sum-frequency QTF contour panels and mean drift force along the main diagonal |

## What changed from desktop V1.0

- The Tkinter desktop client is replaced by a browser UI (NiceGUI) — nothing to install on the client side.
- The hydrostatics chain is now `preProc.exe → hydrosCal.exe` (desktop used `mesh.exe`).
- New: GMRES iterative solver option, bulk paste for wave measurement points, model deletion, live run log.
- Added mass and radiation damping are now read from the correct Nemoh files (`CA.dat` = radiation damping, `CM.dat` = added mass).

> Only **single-body** parameter input is supported; multi-body cases require hand-editing the `.cal` file.

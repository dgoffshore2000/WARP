# FAQ

## Parameters and saving

**Q: SAVE .CAL reports "summary_model.txt missed"?**
A: V2.0 falls back automatically — node / panel counts are taken directly from `<model>.dat` and the file is regenerated. The error only appears when no mesh file exists at all; import a mesh first.

**Q: RUN HYST reports "Nemoh.cal missing"?**
A: Run **SAVE .CAL** first (preProc.exe needs `Nemoh.cal`).

**Q: hydrosCal crashes and no Hydrostatics.dat is produced?**
A: Older builds required a pre-existing `Mechanics/` directory. The current version creates it before running; update the program if you still hit this.

**Q: I changed Symm / Waterplane / Tcol but SUMMARY did not change.**
A: Expected. Hydrostatics are driven by **COG and Rho / Gravity** (hydrosCal determines the equilibrium attitude); the other fields exist for compatibility with desktop parameter files.

**Q: Why is the MASS inertia zero by default?**
A: Zero means "let the program decide". Fill them in when you want explicit control (e.g. damping calibration) and press **SAVE MECHANICS**.

## Solving

**Q: When should I use GMRES, and with what settings?**
A: Leave it off by default (direct solver). Enable it when mesh size makes memory or time prohibitive; `Restart 10 / Rel Tol 1e-5 / Max iter 1000` suits most cases — raise Restart to 30–50 if convergence stalls.

**Q: The BEM log seems frozen?**
A: Fixed in V2.0 — gfortran pipe buffering used to hold progress lines until the process ended; the log now streams each problem as it completes. Reference: 330 problems ≈ 11 minutes for cylinder_irr (~2 s each).

**Q: How long should a run take?**
A: Number of problems = frequencies × (headings for diffraction + ticked DOFs for radiation). Runtime scales roughly linearly with mesh size.

**Q: Are `CA.dat` and `CM.dat` swapped?**
A: No — this is how Nemoh names them: `CA.dat` = radiation damping, `CM.dat` = added mass. WARP follows the official definition.

## Results

**Q: What are the units of the rotational excitation force?**
A: Normalised by unit amplitude: translational N/m, rotational N·m/m.

**Q: Do rotational RAOs need a 180/π conversion?**
A: No. The data files are already in deg/m.

**Q: The QTF Results plots are empty.**
A: Run the QTF computation first (QTF Set configured + RUN QTF), confirm `results/QTF/OUT_QTF*.dat` exists, then click **加载QTF选项**.

## Other

**Q: Is multi-body supported?**
A: Only single-body parameter input; multi-body cases require hand-editing the `.cal` file.

**Q: Can it run on Linux?**
A: `bin/` ships Windows executables. On Linux you must compile the Nemoh kernel yourself, and remember the program accesses the lowercase `db/` path.

**Q: Will a new run overwrite previous results?**
A: No. Before each run the old `results/`, `QTFPreprocOut/`, … are renamed to `*_bak_<timestamp>`; history is never deleted automatically.

**Q: How is the irregular frequency (IRR) handled?**
A: Tick **IRR 去除不规则频率** in the HYST panel; the removal range is written to `Nemoh.cal`. Whether it is needed depends on whether the mesh's natural frequencies fall inside the computed range.

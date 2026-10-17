# Results

Result panels use the same conventions as the desktop PLOT page. Click **刷新结果** after BEM finishes to load data; **加载方向列表** loads the available headings.

![Results](figure/web_ui_05_results.png)

## Results (first-order curves)

| Control | Description |
|---|---|
| Type | Wave excitation force / RAO / added mass / radiation damping, etc. |
| DOF i / DOF j | force direction and motion direction |
| Direction | wave heading (all headings can be overlaid: `Wave 0° / 45° / …`) |
| X axis | frequency or period (rad/s / Hz / period s) |

**Units**:

- Excitation forces are normalised by unit wave amplitude (`Fe(t) = a·|Fe|·cos(ωt − ∠Fe)`): translational **N/m**, rotational **N·m/m**.
- Added mass in **kg** (kg·m² for rotations); radiation damping in **N·s/m** (N·m·s/rad for rotations).
- Rotational RAO data files are already in **deg/m**; no radian conversion is applied in the UI.

## QTF Results (second-order contours)

![QTF Results](figure/web_ui_06_qtf.png)

- Source: `results/QTF/OUT_QTF*.dat` (normalised by ρg).
- Four panels: **amplitude / phase** on the left, **real / imaginary** on the right; colour scale is `log10(|QTF|/ρg)`.
- Controls: QTF type (difference `QTFM (ω1−ω2)` / sum `QTFP (ω1+ω2)`), heading pair β, DOF, X axis (frequency / period).
- **加载QTF选项** loads the QTF Set configuration to determine the available combinations.

## QTF Diagonal (mean drift force)

![QTF Diagonal](figure/web_ui_07_qtfdiag.png)

- Takes the `ω1 = ω2` diagonal, i.e. the **mean drift force**.
- All heading pairs are overlaid in one figure, styled like the Results panel; the Y axis can be switched (e.g. `|QTF|/ρg`) and the X axis between frequency and period.

> Second-order slow-drift studies usually start from QTF Diagonal (mean drift) for a first check; a full slow-drift response also needs the difference-frequency QTF together with mooring and damping models.

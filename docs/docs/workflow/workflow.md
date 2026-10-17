# 界面总览与工作流程

页面自上而下依次为：**模型区 → Environment / 测量点 → HYST 静水力 → 3D 网格预览 → Body set / MASS → Load Cases / Solver / Post Set / QTF Set → 计算按钮与日志 → Results → QTF Results**。

![界面顶部](../figure/web_ui_01_model_env.png)

------------------------------------------------------------------------

## 1. 模型管理（顶部）

- **Model 下拉框**：选择 `db/` 下已有的模型目录，页面参数自动载入。
- **New model name + 新建**：输入英文名称（不含特殊字符与空格）新建工作目录。需要将模型文件拷贝到工作目录才能运行或显示。
- **删除**：删除当前选中模型的整个目录（会弹出确认框；运行中禁止删除）。

> **命名规则**：网格文件必须与模型同名，即 `db/<model>/<model>.dat`，区分大小写，避免 `@ # 空格` 等符号。

## 2. Environment（全局环境参数）

`Rho kg/m³`（水密度）、`Gravity m/s²`（重力加速度）、`Water depth m`（水深）、`Bodies`（体数，当前固定为 1）。

## 3. Wave measure points（波浪测量点）

- 每行一个 `x y` 坐标，**框选后可直接粘贴 Excel 两列数据**，粘贴自动补行。
- **点数 + 生成**：输入点数一键生成对应行数（多退少补，保留已有前 N 行）；支持 `+ 行 / 删行`。
- 写入 `Nemoh.cal` 的 `wmpoints` 段；不需要时保持默认 `0  0`（程序不会额外写入）。
- 除非必要，不建议增加或者修改 `wave measure points`

## 4. HYST — Hydrostatics（静水力）

`bin/preProc.exe → bin/hydrosCal.exe`。

- **RUN HYST**：自动重建 `mesh/` 目录（旧目录改名 `*_bak_<时间戳>` 备份）、复制网格、校正计数后运行。
- **SUMMARY**：根据 `mesh/Hydrostatics.dat` 结果生成 `summary_hydrosta.txt`，汇总浮心 XB/YB/ZB、排水量、水线面面积与质量。
- `Rho / Gravity` 共用上方 Environment 值。

## 5. MODEL — 3D Mesh（网格三维预览）

![3D 预览](../figure/web_ui_08_mesh3d.png)

- **加载网格**：读取 `db/<model>/<model>.dat` 并渲染；文件首行的对称标志会自动镜像补全半模。
- **仅线框（不填充）** / **背景颜色**：显示选项可切换。
- 图下方实时显示：节点数、面片数（含镜像补全后的三角面 / 网格线数）、对称性、包围盒范围。

## 6. Body set — Degrees of freedom

勾选需要计算的 6 个自由度：Surge / Sway / Heave / Roll / Pitch / Yaw。未勾选的自由度不参与辐射问题求解。

## 7. MASS / Mechanics（质量与力学矩阵）

![MASS 矩阵](../figure/web_ui_02_mechanics.png)

- **Mass (kg)**：结构质量，单位为kg。
- **Moment of inertia tensor (kg·m²)**：3×3 转动惯量。
- **附加阻尼 D11..D66 (badd.dat)**、**附加刚度 S11..S66 (km.dat)**：6×6 矩阵，支持从 Excel 复制后 Ctrl+V 整块粘贴。
- 全部留 0 表示完全由程序按静水力结果计算（推荐做法：仅在需要额外阻尼 / 刚度时填写）。

## 8. Load Cases / Solver / Post Set / QTF Set

![参数区](../figure/web_ui_03_cases_solver.png)

四个折叠面板对应 `Nemoh.cal` 与 `input_solver.txt` 的各个段落，逐项含义见 [参数解释](../params/params.md)。

## 9. 计算按钮与运行日志

![计算区](../figure/web_ui_04_run.png)

- **SAVE .CAL** → 生成 `Nemoh.cal`（运行 BEM / QTF 的前置条件）。
- **SAVE MECHANICS** → 生成 `input_solver.txt` 与 `Mechanics/` 下四个参数矩阵对应文件。
- **RUN BEM** / **RUN QTF**：后台运行，下方日志**实时滚动**（每个 Problem 一条）。
- 运行前旧 `results/`、`QTFPreprocOut/` 等目录自动改名为 `*_bak_<时间戳>`，**不会删除任何历史结果**。

## 10. Results / QTF Results（结果查看）

见 [结果查看](../results.md)。

------------------------------------------------------------------------

## 关键注意事项

- **文件命名**：模型与项目文件必须同名（区分大小写）。
- **计算顺序**：HYST（可选）→ SAVE .CAL → SAVE MECHANICS → RUN BEM → RUN QTF。
- **RAO 曲线**：需先在 MASS 中保存参数并勾选 Post Set 的 `Calculate RAO` 后运行 BEM。
- **QTF 计算**：必须在 QTF Set 中完成参数配置，且一阶问题（BVP + RAO）已求解。
- **加盖去除不规则频率**：勾选IRR去除不规则频率后进行计算，官方不建议再QTF求解中考虑加盖。需要注意，去除不规则频率需要模型在静水面封闭。

## 推荐做法

- 无特殊需求时保持求解器默认设置。
- 正式计算前先在 3D 预览中检查网格质量与对称性。
- 定期备份 `db/` 目录（程序自动备份只保留运行时快照）。
- 高级设置请参考 [Nemoh 官方手册](https://lheea.gitlab.io/Nemoh/)。

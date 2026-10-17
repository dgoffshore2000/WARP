# 输入与输出文件说明

模型目录固定为 `db/<model>/`，网格文件与模型同名（`<model>.dat`）。目录结构：

```
db/<model>/
├─ <model>.dat          # Nemoh 格式网格（首行为对称标志 + 节点/面片数据）
├─ Nemoh.cal            # 计算主控文件（SAVE .CAL 生成）
├─ mesh.cal             # 网格 / 静水力控制文件（RUN HYST 使用）
├─ input_solver.txt     # 求解器参数（SAVE MECHANICS 生成）
├─ summary_model.txt    # 模型节点/面片统计（可由程序自动生成）
├─ summary_hydrosta.txt # 静水力汇总（SUMMARY 生成）
├─ Mechanics/           # 力学矩阵（hydrosCal 读入）
├─ mesh/                # 静水力中间结果（RUN HYST 重建）
├─ results/             # BEM 一阶结果（RUN BEM 生成）
├─ motion/              # RAO 结果
├─ QTF/                 # QTF 结果（RUN QTF 生成）
└─ *_bak_<时间戳>/      # 运行前自动备份（不删除历史）
```

------------------------------------------------------------------------

## 计算内核（bin/）

| 可执行文件 | 用途 |
|---|---|
| `preProc.exe` | 网格预处理（HYST 第一步：重建目录、生成 summary_model） |
| `hydrosCal.exe` | 静水力求解（浮心 / 排水量 / 水线面 / 刚度矩阵） |
| `Solver.exe` | 一阶 BEM 求解器（辐射 + 绕射） |
| `postProc.exe` | 一阶后处理（激励力、RAO、Kochin、自由面等） |
| `QTFpreProc.exe` | QTF 前处理 |
| `QTFsolver.exe` | QTF 求解器 |
| `QTFpostProc.exe` | QTF 后处理（输出 OUT_QTF*.dat） |

## 输入文件

| 文件 | 说明 |
|---|---|
| `<model>.dat` | Nemoh 格式网格：首行 `对称标志 节点数 单元数`，其后为节点坐标与面片连接关系 |
| `Nemoh.cal` | 主控文件：环境参数、DOF、频率 / 浪向、测量点、Post Set、QTF Set 段落（SAVE .CAL 生成） |
| `mesh.cal` | 静水力控制文件（RUN HYST 使用） |
| `input_solver.txt` | 求解器参数：GQ、eps_zmin、求解方法（直接 / GMRES 及其参数） |
| `Mechanics/Inertia.dat` | 质量矩阵 |
| `Mechanics/Badd.dat` | 附加阻尼矩阵 |
| `Mechanics/Km.dat` | 附加刚度矩阵 |
| `Mechanics/Kh.dat` | 静水刚度矩阵（由 hydrosCal 结果写入） |

## 输出文件

### 静水力（mesh/ 与 summary）

| 文件 | 说明 |
|---|---|
| `mesh/Hydrostatics.dat` | 浮心、排水量、水线面面积等静水力结果（SUMMARY 的数据源） |
| `mesh/GC_hull.dat` / `Inertia_hull.dat` / `KH.dat` | 重心、船体惯性、静水刚度 |
| `summary_hydrosta.txt` | 静水力汇总文本 |

### 一阶水动力（results/）

| 文件 | 说明 |
|---|---|
| `results/index.dat` | 各问题的参数索引 |
| `results/CA.dat` | **辐射阻尼**系数 ⚠️ |
| `results/CM.dat` | **附加质量**系数 ⚠️ |
| `results/Fe.dat` | 一阶波浪激励力（Froude–Krylov + 绕射合成） |
| `results/FKForce.dat` / `FKForce.tec` | Froude–Krylov 力 |
| `results/DiffractionForce.tec` | 绕射力 |
| `results/ExcitationForce.tec` | 激励力（按浪向） |
| `results/Forces.dat` / `RadiationCoefficients.tec` | 求解器原始力输出 / 辐射系数 |
| `results/Normalvelocities.dat` | 面元法向速度（preProc 生成） |
| `motion/RAO.dat` | 运动 RAO（Post Set 勾选 Calculate RAO 时） |

> ⚠️ **Nemoh 命名（官方文件即如此）**：`CA.dat` 是**辐射阻尼（Radiation Damping）**，`CM.dat` 才是**附加质量（Added Mass）**，与直觉相反。WARP 已按官方定义读取；自行解析结果文件时请注意。

### 二阶 QTF（QTF/）

| 文件 | 说明 |
|---|---|
| `QTF/OUT_QTF*.dat` | 差频 / 和频 QTF 矩阵（QTF Results 页的数据源，按 ρg 归一化） |

## 其他

| 文件 / 目录 | 说明 |
|---|---|
| `summary_model.txt` | 节点 / 单元统计；缺失时程序会直接从网格文件统计并自动生成 |
| `mesh_view.stl` | 3D 预览缓存（可再生成） |
| `*_bak_<时间戳>/` | 每次 RUN 前对 `results/`、`QTFPreprocOut/` 等的自动备份，**永不自动删除** |

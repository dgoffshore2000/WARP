# -*- coding: utf-8 -*-
"""WARP Web 界面多语言支持（中 / 英）。

设计：
- 代码里所有 UI 文案用 tr('中文原文') 包裹，英文查表 EN，查不到时回退中文。
- 语言开关只切换模块级 LANG，页面重建时所有 tr() 重新求值。
- 单机本地服务（127.0.0.1），因此语言是进程级全局；多客户端同时使用时可忽略
  （如需按会话隔离，可改为 app.storage）。
"""

LANG = "zh"          # 'zh' | 'en'

# 中文原文 -> 英文
EN = {
    # ---------- 顶栏 / 模型管理 ----------
    "Nemoh BEM + QTF · Web 原型": "Nemoh BEM + QTF · Web UI",
    "新建": "New",
    "删除": "Delete",
    "删除当前选中模型的文件夹（需确认）": "Delete the folder of the selected model (confirmation required)",
    "※ 网格生成（MODEL 页）仍用桌面版；本页支持 3D 网格预览 + CASE/RUN/PLOT。":
        "Note: mesh generation still uses the desktop MODEL page; this page covers 3D preview + CASE/RUN/PLOT.",
    "请输入模型名": "Please enter a model name",
    "模型名含非法字符": "Model name contains invalid characters",
    "未选择模型": "No model selected",
    "有计算正在运行，请等待结束或完成后再删除模型": "A run is in progress — wait for it to finish before deleting the model",
    "路径校验失败，拒绝删除": "Path validation failed — deletion refused",
    "确认删除模型": "Confirm model deletion",
    "取消": "Cancel",
    "删除失败：%s": "Deletion failed: %s",
    "已删除 db/": "Deleted db/",

    # ---------- Environment / 测量点 ----------
    "COG 重心位置": "COG — centre of gravity",
    "重心 %s 坐标；可拖拽框选后粘贴 Excel 数据": "COG %s coordinate; drag-select then paste from Excel",
    "测量点 %s 坐标；可拖拽框选后粘贴 Excel 数据": "Measure point %s; drag-select then paste from Excel",
    '每行一个 "x y"，可框选后直接粘贴 Excel 数据':
        'One "x y" per row; drag-select and paste directly from Excel',
    "点数": "Rows",
    "生成": "Generate",
    "+ 行": "+ Row",
    "删行": "Del row",
    "删除最后一行": "Delete the last row",
    "点击\"生成\"直接创建对应数量的测量点行": 'Click "Generate" to create that many measure-point rows',
    "请输入点数": "Please enter a row count",
    "点数需在 1-500 之间": "Row count must be between 1 and 500",
    "已生成 %d 个测量点行": "Generated %d measure-point rows",

    # ---------- HYST ----------
    "HYST — Hydrostatics（静水力，bin/preProc.exe → bin/hydrosCal.exe）":
        "HYST — Hydrostatics (bin/preProc.exe → bin/hydrosCal.exe)",
    "水线面原点 X Y": "Waterplane origin X Y",
    "水线 Z 向移动（吃水调整）": "Z shift of waterline (draft adjustment)",
    "IRR 去除不规则频率": "IRR — remove irregular frequencies",
    "IRR 后处理开关。mesh.cal 第 6 行固定写 2（去除不规则频率）。当前链路（preProc + hydrosCal）不修改 <model>.dat，此勾选仅保留参数记录。默认不勾选":
        "IRR post-processing switch. Line 6 of mesh.cal is always written as 2 (remove irregular frequencies). "
        "The current chain (preProc + hydrosCal) does not modify <model>.dat, so this flag only records the parameter. Off by default.",
    "Rho / Gravity 共用上方 Environment 值；hydrosCal 产物写入 mesh/（Hydrostatics.dat、Inertia_hull.dat、KH.dat 等），Summary 按其结果总结静水力":
        "Rho / Gravity are shared with Environment above; hydrosCal writes into mesh/ "
        "(Hydrostatics.dat, Inertia_hull.dat, KH.dat, …) and Summary reports from those results",
    "浮心/重心 (m):  XF %s | XG %s\n": "Centre of buoyancy / gravity (m):  XF %s | XG %s\n",
    "排水量 Displacement  m³: %s\n": "Displacement  m³: %s\n",
    "水线面面积 WPA       m²: %s\n": "Waterplane area WPA  m²: %s\n",
    "初稳性高:  GMX %s m   GMY %s m\n": "Metacentric height:  GMX %s m   GMY %s m\n",
    " hull 惯性矩:  IX %s  IY %s  IZ %s\n": " hull inertia:  IX %s  IY %s  IZ %s\n",
    "静水刚度:  K33 %s N\n": "Hydrostatic stiffness:  K33 %s N\n",
    "→ summary_hydrosta.txt 已更新（Save .cal 的 COG 来源）":
        "→ summary_hydrosta.txt updated (source of COG for Save .cal)",
    "静水力摘要已更新": "Hydrostatics summary updated",
    "mesh/ 产物缺失（先 Run HYST）：%s": "mesh/ outputs missing (run HYST first): %s",

    # ---------- 3D 预览 ----------
    "MODEL — 3D Mesh（Nemoh 网格三维预览）": "MODEL — 3D Mesh (Nemoh mesh preview)",
    "🔄 加载网格": "🔄 Load mesh",
    "仅线框（不填充）": "Wireframe only",
    "解析 db/<model>/<model>.dat 并渲染；首行对称标志自动镜像补全半模":
        "Parses db/<model>/<model>.dat; the symmetry flag on the first line mirrors a half model",
    "加载失败：%s": "Load failed: %s",
    "网格：未加载": "Mesh: not loaded",
    "XOZ 镜像": "XOZ mirror",
    " + YOZ 镜像": " + YOZ mirror",
    "无": "none",
    "节点 %d · 面片 %d（镜像 %d 次补全 → %d 三角面 / %d 网格线） · 对称: %s · 范围 x[%g, %g] y[%g, %g] z[%g, %g]":
        "Nodes %d · panels %d (mirrored %d× → %d triangles / %d wireframe edges) · symmetry: %s · bbox x[%g, %g] y[%g, %g] z[%g, %g]",

    # ---------- 参数区 ----------
    "MASS / Mechanics（Inertia + 阻尼 + 刚度）": "MASS / Mechanics (inertia + damping + stiffness)",
    "附加阻尼 D11..D66（badd.dat，空 = 0）": "Added damping D11..D66 (badd.dat, empty = 0)",
    "附加刚度 S11..S66（km.dat，空 = 0）": "Added stiffness S11..S66 (km.dat, empty = 0)",
    "鼠标从左上角拖拽框选矩阵区域 → 在 Excel 复制 → Ctrl+V 整块粘贴":
        "Drag-select the matrix from its top-left corner → copy in Excel → Ctrl+V to paste the block",
    "Load Cases（Nemoh.cal 波浪频率/浪向）": "Load Cases (Nemoh.cal frequencies / headings)",
    "周期 s": "Period s",
    "Solver（input_solver.txt）": "Solver (input_solver.txt)",
    "0 GAUSS ELIM.; 1 LU DECOMP.（勾选 GMRES 时忽略，自动写 2）":
        "0 GAUSS ELIM.; 1 LU DECOMP. (ignored when GMRES is ticked — 2 is written)",
    "勾选后线性方程组改用 GMRES 迭代法求解（solver 行写 2），适合大规模网格；不勾选时用上方 Solver 选项（0 高斯消元 / 1 LU 分解）":
        "Tick to solve the linear system with GMRES (solver line written as 2), suited to large meshes; "
        "otherwise the Solver option above is used (0 Gaussian elimination / 1 LU decomposition)",
    "GMRES 重启参数": "GMRES restart",
    "GMRES 相对容差": "GMRES relative tolerance",
    "GMRES 最大迭代次数": "GMRES max iterations",
    "Post Set": "Post Set",
    "QTF Set": "QTF Set",
    "启用 QTF 计算": "Enable QTF computation",
    "浪向组合": "Heading combination",
    "单向 β1=β2": "Unidirectional β1=β2",
    "双向 全组合": "Bidirectional, full combination",
    "Contrib（计算内容）": "Contrib (terms included)",
    "仅 DUOK（近场二次项）": "DUOK only (near-field)",
    "DUOK+HASBO（+势项）": "DUOK+HASBO (+ potential terms)",
    "完整 QTF（+自由面积分）": "Full QTF (+ free-surface integral)",
    "仅 Contrib=3：自由面网格文件": "Contrib=3 only: free-surface mesh file",
    "Re Nre NBessel（Bessel 默认 30）": "Re Nre NBessel (Bessel default 30)",
    "计入二阶运动水静力恢复项 −[K]ξ̃⁽²⁾（含 z_G 耦合）":
        "Include 2nd-order hydrostatic restoring −[K]ξ̃⁽²⁾ (with z_G coupling)",
    "输出频率": "Output frequency",
    "QTFpostproc 汇总开关": "QTFpostproc switches",
    "近场二次项（可直接压力积分，无需二阶势）": "Near-field term (direct pressure integration, no 2nd-order potential)",
    "势项·船体/水线（间接法）": "Potential term · hull/waterline (indirect method)",
    "自由面积分：有限域 + 半无限域渐近（间接法）": "Free-surface integral: finite domain + semi-infinite asymptotics (indirect)",
    "N freq": "N freq",
    "Min freq": "Min freq",
    "Max freq": "Max freq",
    "径向频率个数": "Number of radial frequencies",
    "最小频率 rad/s": "Minimum frequency rad/s",
    "最大频率 rad/s": "Maximum frequency rad/s",

    # ---------- 运行 ----------
    "Run 前旧 results/QTFPreprocOut 等目录自动改名为 *_bak_<时间戳>，不会删除任何历史结果。":
        "Before each run, results/ and QTFPreprocOut/ etc. are renamed to *_bak_<timestamp>; no history is deleted.",
    "SAVE .CAL": "SAVE .CAL",
    "SAVE MECHANICS": "SAVE MECHANICS",
    "Nemoh.cal 已生成": "Nemoh.cal written",
    "%s 运行已启动": "%s run started",
    "%s 运行完成 (%.0fs)": "%s finished (%.0fs)",
    "%s 运行失败，请检查日志": "%s failed — check the log",

    # ---------- Results ----------
    "Results（与桌面版 PLOT 页同口径）": "Results (same conventions as the desktop PLOT page)",
    "类型": "Type",
    "幅值": "Amplitude",
    "相位": "Phase",
    "方向": "Direction",
    "所有方向": "All directions",
    "横坐标": "X axis",
    "刷新结果": "Refresh results",
    "加载方向列表": "Load headings",
    "已加载 %d 个浪向（可选单个方向或所有方向）": "Loaded %d headings (pick one or all)",
    "QTF Results（等高线，数据源 results/QTF/OUT_QTF*.dat，值已按 ρg 归一化）":
        "QTF Results (contours from results/QTF/OUT_QTF*.dat, normalised by ρg)",
    "四联显示：左组 幅值 / 相位，右组 实部 / 虚部（|QTF|/ρg 取 log10 色标）":
        "Four panels: amplitude / phase (left), real / imaginary (right); log10 colour scale of |QTF|/ρg",
    "QTF 类型": "QTF type",
    "差频 QTFM（ω1−ω2，慢漂）": "Difference QTFM (ω1−ω2, slow drift)",
    "和频 QTFP（ω1+ω2）": "Sum QTFP (ω1+ω2)",
    "波浪方向对": "Heading pair",
    "自由度 DOF": "DOF",
    "坐标单位": "X unit",
    "加载QTF选项": "Load QTF options",
    "QTF Diagonal — 主对角线二阶载荷（ω1=ω2 等同平均漂移力；全部浪向对同图对比，样式同 Results）":
        "QTF Diagonal — 2nd-order load on the main diagonal (ω1=ω2, mean drift; all heading pairs in one plot)",
    "量": "Quantity",
    "相位 deg": "Phase deg",
    "该结果不存在（%s）：%s": "Result not available (%s): %s",
    "该模型无 %s 结果文件": "No %s result file for this model",
    "该模型无 %s 结果": "No %s result for this model",
    "无该 (方向, DOF) 组合的数据": "No data for that (heading, DOF) combination",
    "无对角线数据": "No diagonal data",
    "无结果": "No results",
    "无 QTF 结果": "No QTF results",
    "差频 QTFM": "Difference QTFM",
    "和频 QTFP": "Sum QTFP",
    "差频 QTFM (ω1-ω2)": "Difference QTFM (ω1-ω2)",
    "和频 QTFP (ω1+ω2)": "Sum QTFP (ω1+ω2)",

    # ---------- 其他 ----------
    "已从剪贴板粘贴 %d 个单元格（起点 r%d c%d）": "Pasted %d cells from the clipboard (from r%d c%d)",
    "粘贴失败：%s": "Paste failed: %s",
    "已粘贴 COG %d 个值（起点第 %d 格）": "Pasted %d COG values (from cell %d)",
    "已粘贴测量点 %d 个值（起点 P%d 第 %d 列）": "Pasted %d measure-point values (from P%d, column %d)",
    "已创建 db/": "Created db/",
    "（网格请用桌面版 MODEL 页生成后放入 mesh/）": " (generate the mesh with the desktop MODEL page and put it in mesh/)",

    # ---------- 补遗（对比扫描得出） ----------
    "%s 主对角线 ω1=ω2 · %s · %s (%s)": "%s diagonal ω1=ω2 · %s · %s (%s)",
    "DOF j（幅值/阻尼用）": "DOF j (for amplitude / damping)",
    "|QTF|/ρg（模）": "|QTF|/ρg (modulus)",
    'β（点"加载QTF选项"填充）': 'β (click "Load QTF options")',
    "将永久删除文件夹 db/%s（含网格、计算结果等全部文件），此操作不可恢复！":
        "All files under db/%s (mesh, results, …) will be permanently deleted. This cannot be undone!",
    "浅灰": "Light grey",
    "深蓝灰": "Dark blue-grey",
    "白（参考图）": "White (reference)",
    "背景颜色": "Background",
    "黑": "Black",
    "（QTF 仅接受 rad/s）": " (QTF accepts rad/s only)",
    "浮心/重心 (m):  XF %s | XG %s\n"
    "               YF %s | YG %s\n"
    "               ZF %s | ZG %s\n"
    "排水量 Displacement  m³: %s\n"
    "水线面面积 WPA       m²: %s\n"
    "初稳性高:  GMX %s m   GMY %s m\n"
    " hull 惯性矩:  IX %s  IY %s  IZ %s\n"
    "静水刚度:  K33 %s N\n"
    "           K44 %s N/rad\n"
    "           K55 %s N/rad\n"
    "→ summary_hydrosta.txt 已更新（Save .cal 的 COG 来源）":
        "Centre of buoyancy / gravity (m):  XF %s | XG %s\n"
        "                                  YF %s | YG %s\n"
        "                                  ZF %s | ZG %s\n"
        "Displacement  m³: %s\n"
        "Waterplane area WPA  m²: %s\n"
        "Metacentric height:  GMX %s m   GMY %s m\n"
        "Hull inertia:  IX %s  IY %s  IZ %s\n"
        "Hydrostatic stiffness:  K33 %s N\n"
        "                        K44 %s N/rad\n"
        "                        K55 %s N/rad\n"
        "→ summary_hydrosta.txt updated (source of COG for Save .cal)",
}


def tr(text):
    """返回当前语言下的文案；英文缺失时回退中文原文。"""
    if LANG == "en":
        return EN.get(text, text)
    return text


def set_lang(lang):
    global LANG
    LANG = "en" if str(lang).lower().startswith("en") else "zh"


def is_en():
    return LANG == "en"

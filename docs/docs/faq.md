# 常见问题 FAQ

## 参数与保存

**Q：点 SAVE .CAL 提示 "summary_model.txt missed"？**
A：V2.0 已自动回退——程序直接从 `<model>.dat` 网格统计节点 / 面片数并生成该文件。仅当目录里连网格文件都没有时才会报错，此时请先导入网格。

**Q：点 RUN HYST 提示 "Nemoh.cal missing"？**
A：RUN HYST 前需要先点 **SAVE .CAL** 生成 `Nemoh.cal`（preProc.exe 依赖它）。

**Q：hydrosCal 崩溃、没有 Hydrostatics.dat？**
A：老版本需手工准备 `Mechanics/` 目录；当前版本在 RUN 前自动创建，若仍遇到请更新程序。

**Q：修改了 Symm / Waterplane / Tcol，SUMMARY 数值没变？**
A：正常。当前静水力由 **COG 与 Rho / Gravity** 驱动（hydrosCal 自动求平衡浮态），这些字段仅用于兼容桌面版参数文件。

**Q：MASS 惯性默认是 0？**
A：是。留 0 表示由程序处理；需要显式控制质量 / 惯性（如做阻尼标定）时再填写，并通过 **SAVE MECHANICS** 写盘。

## 计算与求解

**Q：GMRES 什么时候用？参数怎么设？**
A：默认不勾选（直接法）。网格规模大、直接法内存 / 耗时难以接受时勾选；参数 `Restart 10 / Rel Tol 1e-5 / Max iter 1000` 适用于多数场景，迭代收敛停滞时把 Restart 提高到 30–50。

**Q：RUN BEM 日志不动了？**
A：V2.0 已修复 gfortran 管道缓冲导致的进度积压问题，日志按 Problem 实时滚动。以 cylinder_irr 为参考：330 个问题约 11 分钟（约 2 秒/个）。

**Q：计算多久算正常？**
A：问题数 = 频率数 ×（浪向数（绕射）+ 已勾选 DOF 数（辐射））。耗时与网格规模近似线性。

**Q：结果文件 CA.dat / CM.dat 是不是反了？**
A：不是反了——**Nemoh 官方命名即如此**：`CA.dat` = 辐射阻尼，`CM.dat` = 附加质量。WARP 已按官方定义正确读取。

## 结果查看

**Q：转动方向的激励力单位是什么？**
A：按单位波幅归一化：平动力 N/m，转动力矩 N·m/m。

**Q：转动 RAO 需要乘 180/π 转成度吗？**
A：不需要。数据文件本身就是 deg/m，界面直接显示。

**Q：QTF Results 图是空的？**
A：需要先完成 QTF 计算（QTF Set 配置 + RUN QTF），并确认 `results/QTF/OUT_QTF*.dat` 存在，然后点 **加载QTF选项**。

## 其他

**Q：支持多体吗？**
A：当前仅支持单体参数输入；多体工况需手工编辑 `.cal` 文件。

**Q：能在 Linux 上运行吗？**
A：`bin/` 提供的是 Windows 可执行文件。Linux 需自行编译 Nemoh 内核，并注意模型目录大小写（程序按小写 `db/` 访问）。

**Q：运行前会覆盖旧结果吗？**
A：不会。每次 RUN 前旧 `results/`、`QTFPreprocOut/` 自动改名为 `*_bak_<时间戳>`，历史结果永不自动删除。

**Q：IRR（不规则频率）如何处理？**
A：HYST 区勾选 **IRR 去除不规则频率**，在 `Nemoh.cal` 中写入去除区间；是否启用取决于网格的固有频率是否落入计算频段。

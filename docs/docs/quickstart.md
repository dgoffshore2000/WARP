# 快速开始

## 1. 环境要求

- Windows（`bin/` 内核为 Windows 可执行文件；其他平台需自行编译 Nemoh 内核）
- Python 3.10+

## 2. 安装与启动

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务（两种方式任选）
python warp_web.py      # 命令行启动
run.bat                 # 或双击便携启动脚本（自动选用 Anaconda，启动后自动打开浏览器）

> 界面右上角 **中文 / English** 可随时切换语言；默认中文，选择会立即生效并刷新页面。

> 界面右上角 **中文 / English** 可随时切换语言；默认中文，选择会立即生效并刷新页面。
```

浏览器打开 <http://127.0.0.1:8300> 即可使用。

## 3. 用示例模型跑通全流程

仓库自带示例模型 **cylinder_irr**（圆柱，网格 + 参数 + 结果齐全）：

| 步骤 | 操作 | 说明 |
|---|---|---|
| 1 | 顶部 Model 下拉框选择 `cylinder_irr` | 参数自动载入 |
| 2 | 右侧 **MODEL — 3D Mesh** 点 **加载网格** | 确认网格读取正常（节点 / 单元数显示在图下方） |
| 3 | HYST 区点 **▶ RUN HYST** | 运行 `preProc.exe → hydrosCal.exe` |
| 4 | 点 **SUMMARY** | 生成 `summary_hydrosta.txt`，页面显示浮心 / 排水量 / 水线面面积 / 质量 |
| 5 | 参数区依次 **SAVE .CAL** → **SAVE MECHANICS** | 生成 `Nemoh.cal` 与 `input_solver.txt`、`Mechanics/` 矩阵 |
| 6 | 点 **▶ RUN BEM** | 求解一阶问题（附加质量 / 阻尼 / 激励力 / RAO），日志实时滚动 |
| 7 | 结果区点 **刷新结果** | 查看波浪激励力、RAO、附加质量与阻尼曲线 |
| 8 | （可选）勾选 QTF Set 后 **▶ RUN QTF** | 计算二阶差频 / 和频 QTF，在 QTF Results 查看 |

## 4. 计算耗时参考

以 cylinder_irr（30 个频率 × 5 个浪向）为例：BEM 共 330 个问题，约 2 秒/个，全程约 **5 分钟**。网格规模增大后耗时近似线性增长。

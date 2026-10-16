#coding:utf-8
"""
warp_core.py — WARP Web 原型核心引擎

从 WARP_clean.py 逐行移植的文件生成逻辑（去 Tkinter 依赖，参数改为纯字典）：
  - write_nemoh_cal()    <- savecal()        写 db/<model>/Nemoh.cal
  - write_mechanics()    <- save_data_rao()  写 db/<model>/Mechanics/{Inertia,badd,km}.dat
  - write_input_solver() <- intfile_run()    写 db/<model>/input_solver.txt
  - prepare_bem_run()    <- intfile_run()    准备 results/sources 目录（不再生成 run.bat，直接调用 exe）
  - prepare_qtf_run()    <- qtf_run()        准备 QTFPreprocOut/results/QTF（不再生成 runq.bat，直接调用 exe）
  - RunManager           <- run_nemoh.py     subprocess 运行 + 日志采集（供 Web 轮询）
  - get_results()        <- read_in/read_r/read_f/read_rao + read_*.py 解析为 JSON

移植原则：与桌面版行为保真（格式串、目录重建策略、空值默认行均一致）；
仅两处刻意偏差（均有注释）：
  1. Summary_hydrosta.txt 缺失时不再崩溃，降级为 COG=0 并记录提示；
  2. 弹窗（mbox）改为返回 notes 列表 / 抛 ValueError。
"""

import os
import sys
import shutil
import time
import math
import threading
import collections
import subprocess
import re

if getattr(sys, 'frozen', False):
    # PyInstaller 打包后：以 exe 所在目录为基准（bin/ db/ 与其同级外置）
    BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# 复用桌面版 PLOT 页同一套结果解析纯函数（口径完全一致）
import read_index as ri
import read_radia as rrd
import read_force_rao as rfr
import read_motion_rao as rmr

DOF_NAMES = ["Surge", "Sway", "Heave", "Roll", "Pitch", "Yaw"]

# --------------------------------------------------------------------------
# 参数默认值（与桌面版各 Entry 的默认一致处尽量对齐）
# --------------------------------------------------------------------------
DEFAULT_PARAMS = {
    "model_name": "",
    # Environment（CASE 页 Env set）
    "rho": "1025.0",
    "gravity": "9.81",
    "waterdepth": "80.0",
    "wave_points": "0  0",        # 每行一个 "x y" 波浪测量点（默认一个 0 0 点）
    # Body set
    "num_bodies": "1",
    # Degrees of freedom
    "dof_surge": True, "dof_sway": True, "dof_heave": True,
    "dof_roll": True, "dof_pitch": True, "dof_yaw": True,
    # Load Cases
    "freq_type": "1",           # 1,2,3=[rad/s,Hz,s]
    "min_wf": "0.3", "max_wf": "2.0", "num_wf": "30",
    "min_wd": "0", "max_wd": "180", "num_wd": "5",
    # Post Set
    "irf": "", "show_pressure": False, "kochin": "", "free_surface": "",
    "calc_rao": True, "out_freq_type": "1",
    # QTF Set
    "qtf": False, "qtff": "", "qtfd": "", "qtfc": "", "fsmf": "",
    "fsmf_qtf": "", "hys_term": "", "freq_qtft": "", "duko": "",
    "hasbo": "", "hasfs_symp": "",
    # Mechanics（MASS 页；默认 0，程序不自动设置）
    "mass": "0", "ixx": "0", "ixy": "0", "ixz": "0",
    "iyy": "0", "iyz": "0", "izz": "0",
    # HYST（静水力；rho/gravity 与 Environment 共用）
    "hyst_xoz": "1",        # Symm about XOZ, 0 no / 1 yes
    "hyst_xoy": "0 0",      # Waterplane location X Y
    "hyst_cog": "0 0 0",    # COG location X Y Z
    "hyst_tcol": "0",       # Tcol water line move (draft shift)
    "hyst_irr": "0",        # IRR 后处理开关：勾选('1')时 HYST 后保留 mesh 替换网格（打 .meshed 标记），
                            # Run BEM 时还原原始模型、重读节点/面片数写入 Nemoh.cal。
                            # 注意：mesh.cal 第6行固定写 2，与本勾选无关（用户明确要求）
    # Solver（RUN 页 Calculation Setting）
    "gq": "2", "eps": "0.001", "solver": "0",
    "use_gmres": "0", "gmres_restart": "10", "gmres_tol": "1e-5", "gmres_maxit": "1000",
}
# 阻尼矩阵 D11..D66 与附加刚度矩阵 S11..S66
for _i in range(1, 7):
    for _j in range(1, 7):
        DEFAULT_PARAMS["d%d%d" % (_i, _j)] = ""
        DEFAULT_PARAMS["s%d%d" % (_i, _j)] = ""


def merge_params(overrides):
    p = dict(DEFAULT_PARAMS)
    if overrides:
        for k, v in overrides.items():
            if k in p:
                p[k] = v
    return p


# --------------------------------------------------------------------------
# 路径与模型列表
# --------------------------------------------------------------------------
def model_dir(model):
    return BASE_DIR + "/db/" + str(model)


def list_models():
    db = BASE_DIR + "/db"
    models = []
    if os.path.isdir(db):
        for name in sorted(os.listdir(db)):
            d = db + "/" + name
            if os.path.isdir(d) and (os.path.exists(d + "/summary_model.txt")
                                     or os.path.isdir(d + "/mesh")):
                models.append(name)
    return models


# --------------------------------------------------------------------------
# 小工具
# --------------------------------------------------------------------------
def _req(val, msg):
    if val is None or str(val).strip() == "":
        raise ValueError(msg)
    return val


def _num(val):
    """空值 -> 0.0（与桌面版 if xx=="": xx=0 行为一致）"""
    if val is None or str(val).strip() == "":
        return 0.0
    return float(str(val).strip())


def _req_num(val, msg):
    if val is None or str(val).strip() == "":
        raise ValueError(msg)
    return float(str(val).strip())


def _write_matrix(path, m):
    """6x6 矩阵，'{:<16s}'.format(format(val,'.7E')) 逐元素——与桌面版格式完全一致"""
    lines = []
    for i in range(6):
        row = ""
        for j in range(6):
            row += '{:<16s}'.format(format(m[i][j], '.7E'))
        lines.append(row + "\n")
    f = open(path, "w")
    f.writelines(lines)
    f.close()


# --------------------------------------------------------------------------
# Nemoh.cal（移植 savecal）
# --------------------------------------------------------------------------
def write_nemoh_cal(params):
    """生成 db/<model>/Nemoh.cal，返回 notes 提示列表（对应桌面版的 mbox.showinfo）。"""
    p = params
    model = _req(p["model_name"], "Modelname missed")
    dbpath = model_dir(model)
    if not os.path.isdir(dbpath):
        raise ValueError("Model folder not found: " + dbpath)
    rho_ = _req(p["rho"], "RHO of water missed")
    g_ = _req(p["gravity"], "Grivity missed")
    wdn_ = _req(p["waterdepth"], "Waterdepth missed")
    numb = p["num_bodies"]
    freqts = _req(p["freq_type"], "Freq type. missed")
    minwf = _req(p["min_wf"], "Min wave freq. missed")
    maxwf = _req(p["max_wf"], "Max wave freq. missed")
    numwf = _req(p["num_wf"], "Numbers of wave freq. missed")
    minwds = _req(p["min_wd"], "Min wave direction missed")
    maxwds = _req(p["max_wd"], "Max wave direction missed")
    numwds = _req(p["num_wd"], "Numbers of wave direction missed")
    irfs = p["irf"]
    shpre1 = 1 if p["show_pressure"] else 0
    kochins = p["kochin"]
    freess = p["free_surface"]
    raoss = 1 if p["calc_rao"] else 0
    freq_ts = p["out_freq_type"]
    qtfs = 1 if p["qtf"] else 0
    qtffs = p["qtff"]; qtfds = p["qtfd"]; qtfcs = p["qtfc"]; fsmfs = p["fsmf"]
    fsmf_qtfs = p["fsmf_qtf"]; hys_terms = p["hys_term"]
    freq_qtfts = p["freq_qtft"]; dukos = p["duko"]
    HASBOs = p["hasbo"]; HASFS_ASYMPs = p["hasfs_symp"]

    notes = []

    # ---- 重力中心：Summary_hydrosta.txt 第 7/8/9 行，列 28:36 ----
    # （桌面版缺该文件会直接异常；此处降级为 COG=0 并提示）
    xg = yg = zg = "0.000"
    hs = dbpath + "/Summary_hydrosta.txt"
    if os.path.exists(hs):
        f = open(hs, "r")
        for _ in range(6):
            f.readline()
        xg = f.readline()[28:36]
        yg = f.readline()[28:36]
        zg = f.readline()[28:36]
        f.close()
        if xg.strip() == "":
            xg = yg = zg = "0.000"
    else:
        notes.append("Summary_hydrosta.txt not found -> COG set to 0.000")

    cdgxyz = '{:>10s}'.format(xg) + '{:>10s}'.format(yg) + '{:>10s}'.format("0.000")
    cdgrxyz = '{:>10s}'.format(xg) + '{:>10s}'.format(yg) + '{:>10s}'.format(zg)

    # RAO 计算开启时重建 motion 目录（旧目录备份，见 _recreate_dir）
    if raoss == 1:
        _recreate_dir(dbpath + "/motion", notes, "motion")

    # ---- panels/nodes：summary_model.txt（缺失时回退：直接数网格 .dat 文件）----
    sm = dbpath + "/summary_model.txt"
    panels = None
    nodes = None
    if os.path.exists(sm):
        f = open(sm, "r")
        line = f.readline()
        while line:
            line = f.readline()
            if line[0:30] == "  Total model panel number is:":
                panels = int(line[31:35])
            elif line[0:30] == "  Total model node number is :":
                nodes = int(line[31:35])
        f.close()
    if panels is None or nodes is None:
        meshfile = dbpath + "/" + model + ".dat"
        if not os.path.exists(meshfile):
            raise ValueError("summary_model.txt missed and mesh file not found: " + meshfile)
        nodes, panels = _count_grid_file(meshfile)
        notes.append("summary_model.txt not found -> nodes/panels counted from "
                     + model + ".dat (nodes=%d panels=%d)" % (nodes, panels))

    # ---- 波浪测量点（默认 "0  0"，程序不再兜底注入；清空则不写该行）----
    wmpoints = [ln.strip() for ln in str(p["wave_points"]).splitlines() if ln.strip()]

    out = []
    A = out.append
    A("--- Environment----")
    A('{:<20s}'.format(rho_) + "! Fluid density kg/m**3 ")
    A('{:<20s}'.format(g_) + "! Gravity       m/s**2 ")
    A('{:<20s}'.format(wdn_) + "! Water depth   m     ")
    for wmp in wmpoints:
        A('{:<20s}'.format(wmp) + "! XEFF YEFF, Wave measurement point m")
    A("--- Description of floating bodies ------")
    A('{:<20s}'.format(numb) + "! Number of bodies")
    A("--- Body 1 ---------------")
    A('{:<20s}'.format(model + '.dat') + "! Name of mesh file")
    A('{:<20s}'.format(str(nodes) + " " + str(panels)) + "! Number of points and number of panels")

    # ---- DOF ----
    flags = [p["dof_surge"], p["dof_sway"], p["dof_heave"],
             p["dof_roll"], p["dof_pitch"], p["dof_yaw"]]
    vectors = ["1  0  0  ", "0  1  0  ", "0  0  1  ",
               "1  0  0  ", "0  1  0  ", "0  0  1  "]
    temp = [" "] * 6
    deg = 0
    for i in range(6):
        if flags[i]:
            temp[i] = vectors[i]
            deg += 1

    A(str(deg) + "                 ! Number of degrees of freedom")
    for i in range(6):
        if temp[i] == " ":
            continue
        if i < 3:
            A("1" + "  " + temp[i] + "  " + cdgxyz + "   ! degree " + str(i + 1))
        else:
            A("2" + "  " + temp[i] + "  " + cdgrxyz + "   ! degree " + str(i + 1))

    A(str(deg) + "                 ! Number of degrees of freedom")
    for i in range(6):
        if temp[i] == " ":
            continue
        if i <= 2:
            A("1" + "  " + temp[i] + "  " + cdgxyz + "   ! force " + str(i + 1))
        else:
            A("2" + "  " + temp[i] + "  " + cdgrxyz + "   ! force " + str(i + 1))

    A('{:<20s}'.format(str("0")) + "! Number of lines of additional information")
    A("--- Load cases to be solved ---------")
    # 注意：值与行内注释 "!" 之间必须有空格——gfortran list-directed 读实数时
    # 字段 "2.0!" 会被整体解析为 bad real（preProc 曾因此报
    # "Bad real number in item 4 of list input"）
    A(str(freqts) + " " + str(numwf) + " " + str(minwf) + " " + str(maxwf) + " "
      + "! Freq type 1,2,3=[rad/s,Hz,s], Number of wave frequencies/periods, Min, and Max")
    A(str(numwds) + " " + str(minwds) + " " + str(maxwds) + " "
      + "! Number of wave directions, Min and Max (degrees)")
    A("--- Post processing -------")

    if irfs == "":
        notes.append("No IDRS.")
        A('{:<20s}'.format('0  0   0  ')
          + "! IRF calculation (0 for no calculation), time step and duration")
    else:
        A('{:<20s}'.format(str(irfs))
          + "! IRF calculation (0 for no calculation), time step and duration")

    if shpre1 == 0:
        A('{:<20s}'.format('0 ') + "! Show pressure")
        notes.append("No Pressure.")
    else:
        A('{:<20s}'.format('1 ') + "! Show pressure")

    if kochins == "":
        notes.append("No KOCHINS.")
        A('{:<20s}'.format('0 0 0 ')
          + "! Kochin function ! Number of directions of calculation (0 for no calculations), Min and Max (degrees)")
    else:
        A('{:<20s}'.format(str(kochins))
          + "! Kochin function ! Number of directions of calculation (0 for no calculations), Min and Max (degrees)")

    if freess == "":
        notes.append("No Free surface elevation.")
        A('{:<20s}'.format('0 0 0 0')
          + "! Free surface elevation! Number of points in x direction (0 for no calcutions)and y direction and dimensions of domain in x and y direction")
    else:
        A('{:<20s}'.format(str(freess))
          + "! Free surface elevation! Number of points in x direction (0 for no calcutions)and y direction and dimensions of domain in x and y direction")

    if raoss == 0:
        notes.append("RAO not considered.")
        A('{:<20s}'.format('0')
          + "! Response Amplitude Operator (RAO), 0 no calculation, 1 calculated")
    else:
        A('{:<20s}'.format(str(raoss))
          + "! Response Amplitude Operator (RAO), 0 no calculation, 1 calculated")

    if freq_ts == "":
        notes.append("rad/s is used.")
        A('{:<20s}'.format('1') + "! output freq type, 1,2,3=[rad/s,Hz,s]")
    else:
        A('{:<20s}'.format(str(freq_ts)) + "! output freq type, 1,2,3=[rad/s,Hz,s]")

    A("----- QTF--------------------")
    A('{:<20s}'.format(str(qtfs)) + "! QTF flag, 1 is calculated")
    if qtfs == 0:
        notes.append("QTF not considered.")

    # QTF 块共 11 行，任何情况下固定写全——漏行会导致 Nemoh 读 cal 时格式错位
    # （qtfd 空时跳行会缺 "0 Unidirection, Bidirection 1" 等三行，用户确认为错误）。
    # 空值写与参考文件一致的默认值：qtff='0 0 0'、qtfd='0'、qtfcs='0'、fsmf='NA'、
    # fsmf_qtf='0 0 0'（Re Nre NBessel 三个值）、其余为 '0'
    if qtffs != "":
        A('{:<20s}'.format(str(qtffs))
          + "! Number of radial frequencies, Min, and Max values for the QTF computation")
    else:
        A('{:<20s}'.format('0 0 0')
          + "! Number of radial frequencies, Min, and Max values for the QTF computation")

    if qtfds != "":
        A('{:<20s}'.format(str(qtfds)) + "! 0 Unidirection, Bidirection 1 ")
    else:
        A('{:<20s}'.format('0') + "! 0 Unidirection, Bidirection 1 ")

    if qtfcs != "":
        A('{:<20s}'.format(str(qtfcs))
          + "! Contrib, 1 DUOK, 2 DUOK+HASBO, 3 Full QTF (DUOK+HASBO+HASFS+ASYMP)")
    else:
        A('{:<20s}'.format('0')
          + "! Contrib, 1 DUOK, 2 DUOK+HASBO, 3 Full QTF (DUOK+HASBO+HASFS+ASYMP)")

    # fsmf 空默认写 'NA'（手册规定 not applicable 时填 NA；'0' 会被当文件名）
    if fsmfs != "":
        A('{:<20s}'.format(str(fsmfs))
          + "! Name of free surface meshfile (Only for Contrib 3), type 'NA' if not applicable")
    else:
        A('{:<20s}'.format('NA')
          + "! Name of free surface meshfile (Only for Contrib 3), type 'NA' if not applicable")

    # fsmf_qtf 为三个参数 Re Nre NBessel，空默认写 '0 0 0'
    if fsmf_qtfs != "":
        A('{:<20s}'.format(str(fsmf_qtfs))
          + "! Free surface QTF parameters: Re Nre NBessel (for Contrib 3)")
    else:
        A('{:<20s}'.format('0 0 0')
          + "! Free surface QTF parameters: Re Nre NBessel (for Contrib 3)")

    if hys_terms != "":
        A('{:<20s}'.format(str(hys_terms))
          + "! 1 Includes Hydrostatic terms of the quadratic first order motion, -[K]xi2_tilde")
    else:
        A('{:<20s}'.format('0')
          + "! 1 Includes Hydrostatic terms of the quadratic first order motion, -[K]xi2_tilde")

    if freq_qtfts != "":
        A('{:<20s}'.format(str(freq_qtfts))
          + "! For QTFposProc, output freq type, 1,2,3=[rad/s,Hz,s]")
    else:
        A('{:<20s}'.format('0')
          + "! For QTFposProc, output freq type, 1,2,3=[rad/s,Hz,s]")

    if dukos != "":
        A('{:<20s}'.format(str(dukos))
          + "! For QTFposProc, 1 includes DUOK in total QTFs, 0 otherwise")
    else:
        A('{:<20s}'.format('0')
          + "! For QTFposProc, 1 includes DUOK in total QTFs, 0 otherwise")

    if HASBOs != "":
        A('{:<20s}'.format(str(HASBOs))
          + "! For QTFposProc, 1 includes HASBO in total QTFs, 0 otherwise")
    else:
        A('{:<20s}'.format('0')
          + "! For QTFposProc, 1 includes HASBO in total QTFs, 0 otherwise")

    if HASFS_ASYMPs != "":
        A('{:<20s}'.format(str(HASFS_ASYMPs))
          + "! For QTFposProc, 1 includes HASFS+ASYMP in total QTFs, 0 otherwise")
    else:
        A('{:<20s}'.format('0')
          + "! For QTFposProc, 1 includes HASFS+ASYMP in total QTFs, 0 otherwise")

    calpath = dbpath + "/Nemoh.cal"
    f = open(calpath, "w")
    f.writelines("\n".join(out) + "\n")
    f.close()
    notes.append("Nemoh.cal written -> " + calpath)
    return notes


# --------------------------------------------------------------------------
# Mechanics 三矩阵（移植 save_data_rao）
# --------------------------------------------------------------------------
def load_inertia(model):
    """读 db/<model>/Mechanics/Inertia.dat（6x6 质量矩阵）回填 mass/惯性矩；无文件返回 None。"""
    path = model_dir(model) + "/Mechanics/Inertia.dat"
    if not os.path.exists(path):
        return None
    vals = []
    with open(path) as f:
        for ln in f:
            parts = ln.split()
            if len(parts) == 6:
                vals.append([float(x) for x in parts])
    if len(vals) < 6:
        return None
    return {"mass": vals[0][0], "ixx": vals[3][3], "ixy": vals[3][4],
            "ixz": vals[3][5], "iyy": vals[4][4], "iyz": vals[4][5],
            "izz": vals[5][5]}


def write_mechanics(params):
    """写 db/<model>/Mechanics/{Inertia,badd,km}.dat 并复制 mesh/kh.dat。"""
    p = params
    model = _req(p["model_name"], "Modelname missed")
    dbpath = model_dir(model)
    if not os.path.isdir(dbpath):
        raise ValueError("Model folder not found: " + dbpath)

    mech = dbpath + "/Mechanics"
    _recreate_dir(mech, None, "Mechanics")

    mass1 = _req_num(p["mass"], "Mass not specified!")
    Ixx1 = _req_num(p["ixx"], "Ixx not specified!")
    Iyy1 = _req_num(p["iyy"], "Iyy not specified!")
    Izz1 = _req_num(p["izz"], "Izz not specified!")
    Ixy1 = _num(p["ixy"])
    Ixz1 = _num(p["ixz"])
    Iyz1 = _num(p["iyz"])

    mass_matrix = [[0.0] * 6 for _ in range(6)]
    mass_matrix[0][0] = mass1
    mass_matrix[1][1] = mass1
    mass_matrix[2][2] = mass1
    mass_matrix[3][3] = Ixx1
    mass_matrix[3][4] = Ixy1
    mass_matrix[3][5] = Ixz1
    mass_matrix[4][4] = Iyy1
    mass_matrix[4][5] = Iyz1
    mass_matrix[5][5] = Izz1
    _write_matrix(mech + "/Inertia.dat", mass_matrix)

    dadd_matrix = [[_num(p["d%d%d" % (i + 1, j + 1)]) for j in range(6)] for i in range(6)]
    _write_matrix(mech + "/badd.dat", dadd_matrix)

    km_matrix = [[_num(p["s%d%d" % (i + 1, j + 1)]) for j in range(6)] for i in range(6)]
    _write_matrix(mech + "/km.dat", km_matrix)

    kh_src = dbpath + "/mesh/kh.dat"
    if os.path.exists(kh_src):
        shutil.copy2(kh_src, mech)
    else:
        raise ValueError("Hydrostatic(mesh) not run! (mesh/kh.dat missing)")
    return "Mass, damping and stiffness data saved."


# --------------------------------------------------------------------------
# input_solver.txt / 求解器 exe 列表（移植 intfile_run / qtf_run 的准备部分；直接调用 exe，不再生成 .bat）
# --------------------------------------------------------------------------
def write_input_solver(params):
    p = params
    model = _req(p["model_name"], "Modelname missed!")
    dbpath = model_dir(model)
    inputpath = dbpath + "/input_solver.txt"
    f = open(inputpath, "w")
    f.writelines('{:<20s}'.format(str(p["gq"]))
                 + " ! Gauss quadrature (GQ) surface integration, N^2 GQ Nodes, specify N(1,4) \n")
    f.writelines('{:<20s}'.format(str(p["eps"]))
                 + " ! eps_zmin for determine minimum z of flow and source points of panel, zmin=eps_zmin*body_diameter \n")
    # 求解器选项：勾选 GMRES -> 写 2；否则用界面 Solver 值（0 GAUSS ELIM / 1 LU DECOMP）
    use_gmres = str(p.get("use_gmres", "0")) == "1"
    solver_val = "2" if use_gmres else str(p["solver"])
    f.writelines('{:<20s}'.format(solver_val)
                 + " ! 0 GAUSS ELIM.; 1 LU DECOMP.: 2 GMRES\t!Linear system solver \n")
    # GMRES 参数行（手册 Table 4：restart / Rel Tol / max iter；Solver 忽略该行当非 GMRES）
    f.writelines('{:<20s}'.format("%s %s %s" % (p["gmres_restart"], p["gmres_tol"], p["gmres_maxit"]))
                 + " ! Restart parameter, Relative Tolerance, max iter -> additional input for GMRES \n")
    f.close()
    if not os.path.exists(inputpath):
        raise ValueError("Input file missed!")
    if not os.path.exists(dbpath + "/nemoh.cal"):
        raise ValueError("Nemoh.cal file missed!")
    return inputpath


def _recreate_dir(path, notes=None, label=""):
    """重建目录：旧目录改名备份（results_bak_<时间戳>），绝不删除。

    原因：1) 桌面版语义是 rmtree 清空重算，但用户的历史计算结果不应被静默清掉；
          2) 本环境的删除保护 hook 会拦截大目录 rmtree 并杀掉进程（SystemExit）。
    os.rename 仅同盘改名，不触发删除保护，速度快且可随时找回。
    """
    if os.path.exists(path):
        bak = path + "_bak_" + time.strftime("%Y%m%d_%H%M%S")
        n = 1
        while os.path.exists(bak):  # 同一秒内多次重建时避免时间戳碰撞
            bak = path + "_bak_" + time.strftime("%Y%m%d_%H%M%S") + "_%d" % n
            n += 1
        os.rename(path, bak)
        if notes is not None:
            notes.append("%s old dir kept as: %s" % (label or os.path.basename(path), bak))
    os.mkdir(path)


def _exe_paths(exes):
    """bin 目录下求解器 exe 的全路径列表（不再生成 .bat，由 RunManager 直接逐个调用）"""
    return [BASE_DIR + "/bin/" + e for e in exes]


def _count_grid_file(path):
    """统计网格文件节点/面片数，兼容两种格式：
      - Nemoh 格式：首行=节点数、次行=面片数（如 db/<model>/<model>）
      - WARP  格式：首行=对称标志，节点段以 '0 ...' 结束，随后面片段同样以 '0 ...' 结束
    返回 (nodes, panels)。
    """
    f = open(path, "r", errors="replace")
    try:
        head = f.readline().split()
        if len(head) == 1 and head[0].isdigit() and int(head[0]) > 0:
            n = int(head[0])
            second = f.readline().split()
            m = int(second[0]) if second else 0
            return n, m
        n = 0
        line = f.readline()
        t = line.split()
        while t and t[0] != '0':
            n += 1
            line = f.readline()
            t = line.split()
        line = f.readline()          # 节点结束行之后的第一个面片行
        t = line.split()
        m = 0
        while t and t[0] != '0':
            m += 1
            line = f.readline()
            t = line.split()
        return n, m
    finally:
        f.close()


def _update_nemoh_counts(dbpath, nodes, panels):
    """把网格实际节点/面片数写入 Nemoh.cal 的计数行（格式与 write_nemoh_cal 一致）。"""
    nc = dbpath + "/Nemoh.cal"
    if not os.path.exists(nc):
        return False
    out = []
    hit = False
    for line in open(nc, "r", errors="replace").read().splitlines():
        if "! Number of points and number of panels" in line:
            out.append('{:<20s}'.format(str(nodes) + " " + str(panels))
                       + "! Number of points and number of panels")
            hit = True
        else:
            out.append(line)
    if hit:
        open(nc, "w").write("\n".join(out) + "\n")
    return hit


def _mesh_file_from_nemoh_cal(dbpath):
    """读取 Nemoh.cal 中 "! Name of mesh file" 指定的网格文件名；未找到返回 None。"""
    nc = dbpath + "/Nemoh.cal"
    if not os.path.exists(nc):
        return None
    for line in open(nc, "r", errors="replace").read().splitlines():
        if "! Name of mesh file" in line:
            return line.split("!")[0].strip()
    return None


def _flag_mark(path, note):
    """打标记：写入说明内容"""
    with open(path, "w") as fh:
        fh.write(note)


def _flag_clear(path):
    """清标记：截断为 0 字节（不删文件）。

    不调用 os.remove——当该文件恰好被环境的安全删除层拦截时，会直接
    SystemExit 打断整个服务进程（实测 Run BEM 曾因此把服务打挂）。语义等价。
    """
    try:
        with open(path, "w"):
            pass
    except OSError:
        pass


def _flag_set(path):
    """标记是否有效：文件存在且非空（被清空过的标记视为无效）"""
    return os.path.exists(path) and os.path.getsize(path) > 0


def prepare_bem_run(params):
    """移植 intfile_run()：写 input_solver.txt、重建 results/sources，返回待执行 exe 列表。

    另按需求处理 IRR：mesh 运行会把 <model>.dat 替换成带 lid 网格，因此 Run BEM
    一律使用【原始模型】——检测到 mesh 替换标记时先从 .srcbak 还原原始网格；随后
    单独读取模型文件确定节点/单元数并写入 Nemoh.cal，再运行 Solver。
    """
    p = params
    model = _req(p["model_name"], "Modelname missed!")
    dbpath = model_dir(model)
    if not os.path.isdir(dbpath):
        raise ValueError("Model folder not found: " + dbpath)
    notes = []

    # 1) IRR 后 Run BEM 用原始模型：还原被 mesh.exe 替换的 <model>.dat
    dat_path = dbpath + "/" + model + ".dat"
    bak_path = dat_path + ".srcbak"
    meshed_flag = dat_path + ".meshed"
    if _flag_set(meshed_flag) and os.path.exists(bak_path):
        shutil.copy(bak_path, dat_path)
        _flag_clear(meshed_flag)
        notes.append("IRR: restored original %s.dat from backup "
                     "(mesh-replaced grid discarded)" % model)

    # 2) 单独读取模型文件确定节点/单元数并写入 Nemoh.cal
    grid = _mesh_file_from_nemoh_cal(dbpath) or (model + ".dat")
    grid_path = dbpath + "/" + grid
    # IRR 用原始模型求解：即使 Nemoh.cal 指向别的网格文件，也强制对 <model>.dat 计数
    if _flag_set(meshed_flag) or not os.path.exists(grid_path):
        grid_path = dat_path
    if os.path.exists(grid_path):
        nodes, panels = _count_grid_file(grid_path)
        if _update_nemoh_counts(dbpath, nodes, panels):
            notes.append("model grid %s re-read: nodes=%d panels=%d -> Nemoh.cal updated"
                         % (os.path.basename(grid_path), nodes, panels))
        else:
            notes.append("model grid %s re-read: nodes=%d panels=%d (Nemoh.cal missing)"
                         % (os.path.basename(grid_path), nodes, panels))

    write_input_solver(p)
    if not os.path.isdir(dbpath + "/mesh"):
        os.mkdir(dbpath + "/mesh")
    _recreate_dir(dbpath + "/results", notes, "results")
    os.mkdir(dbpath + "/results/sources")
    exes = _exe_paths(["preProc.exe", "Solver.exe", "postProc.exe"])
    return exes, notes


def prepare_qtf_run(params):
    """移植 qtf_run()：校验 nemoh.cal、重建 QTFPreprocOut 与 results/QTF，返回待执行 exe 列表。"""
    p = params
    model = _req(p["model_name"], "Model name missed!")
    dbpath = model_dir(model)
    if not os.path.exists(dbpath + "/nemoh.cal"):
        raise ValueError("Nemoh.cal file missed!")
    qdir = dbpath + "/QTFPreprocOut"
    notes = []
    _recreate_dir(qdir, notes, "QTFPreprocOut")
    rdir = dbpath + "/results/QTF"
    os.makedirs(rdir, exist_ok=True)
    exes = _exe_paths(["QTFpreProc.exe", "QTFsolver.exe", "QTFpostProc.exe"])
    return exes, notes


# --------------------------------------------------------------------------
# 运行管理器（对应 run_nemoh.py 的 run_n/bars，改为可轮询的线程安全实现）
# --------------------------------------------------------------------------
class RunManager:
    def __init__(self):
        self._lock = threading.Lock()
        self._init_state()

    def _init_state(self):
        self.proc = None
        self.lines = collections.deque(maxlen=5000)
        self.n_total = 0
        self.status = "idle"      # idle / running / done / failed
        self.returncode = None
        self.kind = ""
        self.model = ""
        self.t_start = None
        self.t_end = None

    @property
    def running(self):
        with self._lock:
            return self.status == "running"

    def start(self, kind, params):
        with self._lock:
            if self.status == "running":
                raise RuntimeError("A calculation is already running")
            self._init_state()
            notes = []
            if kind == "bem":
                exes, notes = prepare_bem_run(params)
            elif kind == "qtf":
                exes, notes = prepare_qtf_run(params)
            elif kind == "hyst":
                exes, notes = hydros_prepare(params)
            else:
                raise ValueError("unknown run kind: %r" % kind)
            dbpath = model_dir(params["model_name"])
            self.kind = kind
            self.model = params["model_name"]
            self.status = "running"
            self.t_start = time.time()
            self.n_total += 1
            self.lines.append("[cmd] " + " -> ".join(
                os.path.basename(e) for e in exes))
            for n in notes:
                self.lines.append("[prep] " + n)
            threading.Thread(target=self._run_chain,
                             args=(exes, dbpath), daemon=True).start()

    def _run_chain(self, exes, dbpath):
        """直接逐个调用 exe（不经 cmd.exe/.bat）：每个跑完检查返回码，
        非 0 立即中止链条并标 failed；日志按 [step] 分段标记。"""
        rc = 0
        failed = False
        for exe in exes:
            name = os.path.basename(exe)
            with self._lock:
                self.lines.append("[step] run " + name)
                self.n_total += 1
            try:
                # gfortran 运行时对管道输出全缓冲（进度行积压到进程结束才刷出），
                # 设置无缓冲环境变量使 Solver 等的进度实时逐行进入日志
                env = os.environ.copy()
                env["GFORTRAN_UNBUFFERED_ALL"] = "Y"
                env["GFORTRAN_UNBUFFERED_PRECONNECTED"] = "Y"
                # bufsize=0：stdout 为无缓冲原始流，read() 有数据即返回，
                # 配合下方 \r/\n 切分实现进度实时上屏
                proc = subprocess.Popen(
                    [exe], cwd=dbpath, env=env, bufsize=0,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            except OSError as e:
                with self._lock:
                    self.lines.append("[error] cannot start %s: %s" % (name, e))
                    self.n_total += 1
                failed = True
                rc = -1
                break
            with self._lock:
                self.proc = proc          # 供后续停止功能使用

            def _push(line):
                line = line.strip()
                if line:
                    self.lines.append(line)
                    self.n_total += 1

            buf = ""
            while True:
                chunk = proc.stdout.read(4096)
                if not chunk:
                    break
                text = buf + chunk.decode("gbk", "replace")
                # Nemoh 进度行用 \r（ADVANCE='NO'）分隔而非换行，需双分隔符切分
                parts = re.split(r"[\r\n]", text)
                buf = parts.pop()
                with self._lock:
                    for p in parts:
                        _push(p)
            with self._lock:
                _push(buf)
                self.proc = None
            rc = proc.wait()
            with self._lock:
                self.proc = None
                self.lines.append("[exit] %s returncode=%s" % (name, rc))
                self.n_total += 1
            if rc != 0:
                failed = True
                break
        with self._lock:
            self.returncode = rc
            self.t_end = time.time()
            self.status = "failed" if failed else "done"
            self.lines.append("[exit] %s (returncode=%s)"
                              % (self.status, self.returncode))
            self.n_total += 1

    def snapshot(self):
        with self._lock:
            elapsed = 0
            if self.t_start is not None:
                elapsed = (self.t_end or time.time()) - self.t_start
            return {
                "status": self.status,
                "kind": self.kind,
                "model": self.model,
                "returncode": self.returncode,
                "elapsed": elapsed,
                "n": self.n_total,
                "lines": list(self.lines)[-2000:],
            }


RUN = RunManager()


# --------------------------------------------------------------------------
# 结果解析为 JSON（口径与 PLOT 页一致）
# --------------------------------------------------------------------------
def get_results(model):
    """读取 db/<model>/results 与 motion/RAO.dat，返回可 JSON 化的字典。

    口径说明（与桌面 PLOT 页一致，CA/CM 按 Nemoh 官方语义）：
      - addedmass: read_radia 第 1 参 <- results/CM.dat；damping: 第 2 参 <- results/CA.dat
        （Nemoh 命名陷阱：CA.dat 是阻尼、CM.dat 是附加质量）-> [freqn][6][6]
      - waveforce: read_force_rao(ExcitationForce.tec) -> [direcn][freqn][6]
      - wavephase_deg: 桌面版显示时 *180/2/pi，此处直接转为 deg
      - rao_amp: 原始值（RAO.dat 表头：平动 m/m；转动已是 deg/m，直接绘制不换算）
      - rao_phase_deg: RAO.dat 相位列本身为 deg（桌面版直接绘制）
    """
    dbpath = model_dir(model)
    res = {"model": model, "ok": False, "errors": [], "sections": {}}
    indexpath = dbpath + "/results/index.dat"
    if not os.path.exists(indexpath):
        res["errors"].append("results/index.dat not found —— 请先运行 BEM")
        return res
    try:
        direcn, freqn, direc, freq = ri.read_index(indexpath)
    except Exception as e:
        res["errors"].append("index.dat parse failed: %s" % e)
        return res
    res["axes"] = {
        "period_s": [2 * math.pi / fr for fr in freq],
        "freq_rads": freq,
        "direc_deg": direc,
    }
    res["dof_names"] = DOF_NAMES
    res["ok"] = True

    try:
        # Nemoh 命名陷阱（官方手册明确）：CA.dat = damping，CM.dat = added mass。
        # read_radia(addedmass 文件, damping 文件) -> 传 CM, CA。
        admass, damp = rrd.read_radia(dbpath + "/results/CM.dat",
                                      dbpath + "/results/CA.dat", freqn)
        res["sections"]["addedmass"] = admass.tolist()
        res["sections"]["damping"] = damp.tolist()
    except Exception as e:
        res["errors"].append("radiation: %s" % e)

    try:
        wf, wp = rfr.read_force_rao(dbpath + "/results/ExcitationForce.tec",
                                    direcn, freqn)
        res["sections"]["waveforce"] = wf.tolist()
        res["sections"]["wavephase_deg"] = (wp * 180.0 / (2 * math.pi)).tolist()
    except Exception as e:
        res["errors"].append("excitation: %s" % e)

    try:
        ra, rp = rmr.read_motion_rao(dbpath + "/motion/RAO.dat", direcn, freqn)
        res["sections"]["rao_amp"] = ra.tolist()
        res["sections"]["rao_phase_deg"] = rp.tolist()
    except Exception as e:
        res["errors"].append("rao: %s" % e)

    return res


def get_qtf_results(model):
    """读取 db/<model>/results/QTF/OUT_QTFM_N.dat（差频）与 OUT_QTFP_N.dat（和频）。

    手册 v3.0.1 p.25 口径：
      - 列: w1 w2 beta1(deg) beta2(deg) DOF |QTF|/rho*g PHASE(deg) Re/rho*g Im/rho*g
      - 文件只存下三角（w1 >= w2）；差频上三角 = 下三角的共轭（相位取负、虚部变号），
        和频上三角 = 下三角的对称复制。两种情况均镜像补全为完整矩阵
    返回 {"ok", "errors", "dofs", "sets": {qtfm/qtfp: {"w":[...], "betas":[[b1,b2],..],
          "data": {"b1,b2,dof": [[ [mod,ph,re,im] | None ]*n ]*n}}}}
    """
    res = {"model": model, "ok": False, "errors": [], "dofs": DOF_NAMES, "sets": {}}
    qdir = model_dir(model) + "/results/QTF"
    if not os.path.isdir(qdir):
        res["errors"].append("results/QTF not found —— 请先运行 QTF 计算")
        return res
    for key, fn in (("qtfm", "OUT_QTFM_N.dat"), ("qtfp", "OUT_QTFP_N.dat")):
        p = os.path.join(qdir, fn)
        if not os.path.exists(p):
            continue
        groups = {}
        for ln in open(p, errors="replace").read().splitlines()[1:]:
            t = ln.split()
            if len(t) < 9:
                continue
            k = (float(t[2]), float(t[3]), int(float(t[4])))
            groups.setdefault(k, []).append(
                (float(t[0]), float(t[1]), float(t[5]), float(t[6]), float(t[7]), float(t[8])))
        if not groups:
            continue
        ws = sorted({round(r[0], 4) for v in groups.values() for r in v}
                    | {round(r[1], 4) for v in groups.values() for r in v})
        idx = {w: i for i, w in enumerate(ws)}
        n = len(ws)
        data = {}
        for (b1, b2, dof), recs in groups.items():
            g = [[None] * n for _ in range(n)]
            for w1, w2, mod, ph, re, im in recs:
                i, j = idx[round(w1, 4)], idx[round(w2, 4)]
                g[i][j] = [mod, ph, re, im]
                if key == "qtfm":
                    # 差频：上三角与下三角共轭对称（手册 p.25），保证慢漂力为实力
                    g[j][i] = [mod, -ph, re, -im]
                else:
                    # 和频：上三角与下三角对称（手册 p.25）
                    g[j][i] = [mod, ph, re, im]
            data["%g,%g,%d" % (b1, b2, dof)] = g
        res["sets"][key] = {"w": ws,
                            "betas": sorted({(b1, b2) for b1, b2, _ in groups}),
                            "data": data}
    res["ok"] = bool(res["sets"])
    if not res["ok"]:
        res["errors"].append("results/QTF 下无 OUT_QTFM_N.dat / OUT_QTFP_N.dat")
    return res


# --------------------------------------------------------------------------
# HYST 静水力（移植 runmesh / update_hydrosum，修复桌面版 dbpath 污染 bug）
# --------------------------------------------------------------------------
def _convert_mesh_dat(dbpath, model):
    """model.dat（Mesh 格式）-> summary_model.txt + model（Nemoh 格式）。

    保真移植 runmesh L982-1051 的转换分支；对三角面（少于 4 列）补 0 防崩。
    返回 (nodes, panels, symm_line)。
    """
    modelpath = dbpath + "/" + model + ".dat"
    modelfile = open(modelpath, "r")
    symm = modelfile.readline()
    n = 0
    m = 0
    line = modelfile.readline()
    temp = line.split()
    while temp[0] != '0':
        n = n + 1
        line = modelfile.readline()
        temp = line.split()
    line = modelfile.readline()
    temp = line.split()
    while temp[0] != '0':
        m = m + 1
        line = modelfile.readline()
        temp = line.split()

    sufile = open(dbpath + "/summary_model.txt", "w")
    sufile.writelines("*-----------------------------------------" + '\n')
    sufile.writelines("*   WARP Demo -- Based on Nemoh            " + '\n')
    sufile.writelines("*   Programmed by Wei Gao                 " + '\n')
    sufile.writelines("*-----------------------------------------" + '\n')
    sufile.writelines("1.Model Summary" + '\n')
    sufile.writelines("  DB name  is                : " + str(model) + '\n')
    sufile.writelines("  Model name is              : " + str(model) + '\n')
    sufile.writelines("  Symm of model is           : " + str(symm) + '\n')
    sufile.writelines("  Total model node number is : " + str(n) + '\n')
    sufile.writelines("  Total model panel number is: " + str(m) + '\n')
    sufile.close()

    model_no_dat = open(dbpath + "/" + model, "w")
    model_no_dat.writelines(str(n) + '\n')
    model_no_dat.writelines(str(m) + '\n')

    modelfile = open(modelpath, "r")
    modelfile.readline()
    line = modelfile.readline()
    temp = line.split()
    while temp[0] != '0':
        a = '{:>15s}'.format(temp[1])
        b = '{:>15s}'.format(temp[2])
        c = '{:>15s}'.format(temp[3])
        model_no_dat.writelines(a + b + c + '\n')
        line = modelfile.readline()
        temp = line.split()
    line = modelfile.readline()
    temp = line.split()
    while temp[0] != '0':
        t4 = (temp + ['0'] * 4)[:4]
        a = '{:>5s}'.format(t4[0])
        b = '{:>5s}'.format(t4[1])
        c = '{:>5s}'.format(t4[2])
        d = '{:>5s}'.format(t4[3])
        model_no_dat.writelines(a + b + c + d + '\n')
        line = modelfile.readline()
        temp = line.split()
    model_no_dat.close()
    modelfile.close()
    return n, m, symm


def hydros_prepare(params):
    """HYST 文件准备（新链路：preProc.exe -> hydrosCal.exe，不再调用 mesh.exe）。

    1. 校验 Nemoh.cal（preProc.exe 的输入）
    2. 无 summary_model.txt 时从 model.dat 统计并转换出 Nemoh 格式 model 文件
    3. 写 mesh.cal（10 行，与桌面版格式一致；hydrosCal.exe 读取）
    4. 重建 mesh/ 目录（旧目录备份，绝不删除）+ 复制模型网格进 mesh/
    5. 返回待执行 exe 列表（preProc.exe -> hydrosCal.exe）
    注意：该链路不修改 <model>.dat，无需备份/还原（原 mesh.exe 特有行为）。
    返回 (exes, notes)
    """
    p = params
    model = _req(p["model_name"], "DB name not specified!")
    dbpath = model_dir(model)
    if not os.path.isdir(dbpath):
        raise ValueError("Model folder not found: " + dbpath)
    if not os.path.exists(dbpath + "/" + model + ".dat"):
        raise ValueError(model + ".dat not found (先用 MODEL 页导入网格)")
    if not os.path.exists(dbpath + "/nemoh.cal"):
        raise ValueError("Nemoh.cal missing (preProc.exe 需要，先 Save .cal)")
    notes = []

    if not os.path.exists(dbpath + "/summary_model.txt"):
        n, m, _symm = _convert_mesh_dat(dbpath, model)
        notes.append("summary_model.txt + model generated from %s.dat (%d nodes / %d panels)"
                     % (model, n, m))

    # panels 从 summary_model.txt 读取（与桌面版一致）
    panels = ""
    f = open(dbpath + "/summary_model.txt", "r")
    line = f.readline()
    while line:
        line = f.readline()
        if line[0:30] == "  Total model panel number is:":
            panels = line[31:35].strip()
    f.close()
    if panels == "":
        raise ValueError("Panels is not specified!")
    panels = str(int(panels))

    rh = _req(p["rho"], "RHO of Water is not specified!")
    g_ = _req(p["gravity"], "Gravity is not specified!")
    tc = p["hyst_tcol"]
    if tc is None or str(tc).strip() == "":
        raise ValueError("Tcol is not specified!")

    # mesh.cal（10 行，格式与桌面版/现有可运行文件一致）
    meshcal = open(dbpath + "/mesh.cal", "w")
    meshcal.writelines('{:<20s}'.format(model) + "! modelname   " + '\n')
    meshcal.writelines('{:<20s}'.format(str(p["hyst_xoz"])) + "! SYMM of XOZ   " + '\n')
    meshcal.writelines('{:<20s}'.format(str(p["hyst_xoy"])) + "! location at XOY   " + '\n')
    meshcal.writelines('{:<20s}'.format(str(p["hyst_cog"])) + "! COG   " + '\n')
    meshcal.writelines('{:<20s}'.format(panels) + "! panels   " + '\n')
    meshcal.writelines("2" + "\n")   # 第6行固定写 2（去除不规则频率），与 IRR 勾选无关
    meshcal.writelines('{:<20s}'.format(str(tc)) + "! TCOL water line move   " + '\n')
    meshcal.writelines('{:<20s}'.format(str(1)) + "! for scale" + '\n')
    meshcal.writelines('{:<20s}'.format(rh) + "! rho of water  " + '\n')
    meshcal.writelines('{:<20s}'.format(g_) + "! gravity   " + '\n')
    meshcal.close()
    notes.append("mesh.cal established (line6 = 2)")

    # mesh/ 目录重建（备份模式）+ 网格复制
    _recreate_dir(dbpath + "/mesh", notes, "mesh")
    shutil.copy(dbpath + "/" + model, dbpath + "/mesh/" + model)
    # preProc.exe 需要根目录的网格文件（Nemoh.cal 指向）与 results/ 目录
    os.makedirs(dbpath + "/results", exist_ok=True)
    # hydrosCal.exe 需要根目录 Mechanics/ 目录（写 Inertia.dat/Kh.dat 等，
    # 缺失时 Fortran 报 "Cannot open file './Mechanics/Inertia.dat'"）
    os.makedirs(dbpath + "/Mechanics", exist_ok=True)
    notes.append("model %s.dat 不被本链路修改（preProc/hydrosCal 无 mesh.exe 的重写行为）"
                 % model)

    # preProc 按 Nemoh.cal 声明的点/面片数读取网格：计数陈旧会导致
    # "Bad integer ... in list input" 崩溃，运行前强制重读校正
    nodes, panels_n = _count_grid_file(dbpath + "/" + model + ".dat")
    if _update_nemoh_counts(dbpath, nodes, panels_n):
        notes.append("Nemoh.cal counts re-read: nodes=%d panels=%d -> updated"
                     % (nodes, panels_n))
    else:
        notes.append("Nemoh.cal counts re-read: nodes=%d panels=%d (cal missing, skip)"
                     % (nodes, panels_n))

    exes = _exe_paths(["preProc.exe", "hydrosCal.exe"])
    return exes, notes


def hydros_summary(params):
    """移植 update_hydrosum：读 mesh/ 产物 -> 写 summary_hydrosta.txt -> 返回结构化 dict。"""
    p = params
    model = _req(p["model_name"], "Modelname missed")
    dbpath = model_dir(model)
    rho_ = float(_req(p["rho"], "RHO of water missed"))
    g_ = float(_req(p["gravity"], "Grivity missed"))

    f = open(dbpath + "/mesh/Hydrostatics.dat", "r")
    line = f.readline()
    xf = line[5:13]
    xg = line[20:28]
    line = f.readline()
    yf = line[5:13]
    yg = line[20:28]
    line = f.readline()
    zf = line[5:13]
    zg = line[20:28]
    line = f.readline()
    disp = line[15:]
    line = f.readline()
    wpa = line[18:]
    f.close()

    f = open(dbpath + "/mesh/Inertia_hull.dat", "r")
    ix = f.readline()
    iy = f.readline()
    iz = f.readline()
    f.close()

    f = open(dbpath + "/mesh/KH.dat", "r")
    f.readline()
    f.readline()
    line = f.readline()
    kz = line[30:75]
    line = f.readline()
    krx = line[30:75]
    line = f.readline()
    kry = line[30:75]
    f.close()

    gmx = round(float(krx[15:30]) / g_ / float(disp) / rho_, 2)
    gmy = round(float(kry[30:45]) / g_ / float(disp) / rho_, 2)

    sumfile = open(dbpath + "/summary_hydrosta.txt", "w")
    sumfile.writelines("*-----------------------------------------" + '\n')
    sumfile.writelines("*   WARP Demo -- Based on Nemoh        " + '\n')
    sumfile.writelines("*   Programmed by Wei Gao                 " + '\n')
    sumfile.writelines("*-----------------------------------------" + '\n')
    sumfile.writelines("2.Hydrostatic Summary" + '\n')
    sumfile.writelines("2.1 Basic Floating" + '\n')
    sumfile.writelines("   XB m = " + xf + ";  XG m = " + xg + '\n')
    sumfile.writelines("   YB m = " + yf + ";  YG m = " + yg + '\n')
    sumfile.writelines("   ZB m = " + zf + ";  ZG m = " + zg + '\n')
    sumfile.writelines("   GMX m  :" + str(gmx) + '\n')
    sumfile.writelines("   GMY m  :" + str(gmy) + '\n')
    sumfile.writelines("2.2 Hull inertia based on input model" + '\n')
    sumfile.writelines("   Displacement     m3:  " + disp)
    sumfile.writelines("   Water plane area m2:  " + wpa)
    sumfile.writelines("   IX kgm2: " + ix)
    sumfile.writelines("   IY kgm2: " + iy)
    sumfile.writelines("   IZ kgm2: " + iz)
    sumfile.writelines("2.3 Still water stiffness" + '\n')
    sumfile.writelines("    Z     N : " + kz + '\n')
    sumfile.writelines("   RX  N/rad: " + krx + '\n')
    sumfile.writelines("   RY  N/rad: " + kry + '\n')
    sumfile.close()

    def _vals(s):
        return [t for t in s.split()]

    return {
        "model": model,
        "xb": xf.strip(), "xg": xg.strip(),
        "yb": yf.strip(), "yg": yg.strip(),
        "zb": zf.strip(), "zg": zg.strip(),
        "displacement_m3": disp.strip(),
        "waterplane_m2": wpa.strip(),
        "gmx_m": gmx, "gmy_m": gmy,
        "ix": _vals(ix), "iy": _vals(iy), "iz": _vals(iz),
        "kz": _vals(kz), "krx": _vals(krx), "kry": _vals(kry),
        "summary_file": dbpath + "/summary_hydrosta.txt",
    }


# ================================================================ 3D 网格查看器（model.dat -> STL 供 ui.scene 加载）
#
# Nemoh 网格文件格式（与桌面版 MODEL 页 tooltip 一致）：
#   第 1 行:  "a b" —— 桌面版约定 "2 0 for no XOZ symm; 2 1 for XOZ symm"，
#             即第二个数 =1 表示沿 XOZ 平面对称（显示时 y -> -y 镜像补全半模）；
#             第一个数 =1 表示沿 YOZ 平面对称（x -> -x 镜像）
#   节点段:  每行 "id x y z"，以首列为 0 的行结束（如 "0 0.00 0.00 0.00"）
#   面片段:  每行 "n1 n2 n3 n4"（1-based 节点号；逆时针排序，右手法线指向外界水体），
#            以首列为 0 的行结束（如 "0 0 0 0"）；n3==n4 视为三角面

def _find_mesh_dat(model):
    dbpath = model_dir(model)
    cands = [os.path.join(dbpath, str(model) + ".dat"),
             os.path.join(dbpath, "mesh", str(model) + ".dat")]
    for c in cands:
        if os.path.exists(c):
            return c
    raise WarpError("Mesh file not found: tried " + "; ".join(cands))


def read_mesh_dat(model):
    """解析 Nemoh 网格文件。返回 dict:
       nodes=[(x,y,z)...], panels=[(i,j,k,l)...](0-based), sym_x/sym_y=bool, path=str
    """
    path = _find_mesh_dat(model)
    nodes, panels = [], []
    sym_x = sym_y = False
    section = 0  # 0=节点段, 1=面片段
    with open(path) as f:
        first = f.readline().split()
        sym_x = (len(first) > 0 and first[0] == "1")
        sym_y = (len(first) > 1 and first[1] == "1")
        for line in f:
            t = line.split()
            if not t:
                continue
            if t[0] == "0":          # 段结束标记行
                section += 1
                if section >= 2:
                    break
                continue
            if section == 0:
                nodes.append((float(t[1]), float(t[2]), float(t[3])))
            else:
                idx = [int(v) - 1 for v in t[:4]]
                if len(idx) < 4 or idx[3] == idx[2]:   # 三角面（n4 缺省或与 n3 重合）
                    idx = [idx[0], idx[1], idx[2], idx[2]]
                panels.append(tuple(idx))
    if not nodes or not panels:
        raise WarpError("Mesh file parse failed (nodes=%d panels=%d): %s"
                        % (len(nodes), len(panels), path))
    return {"path": path, "nodes": nodes, "panels": panels,
            "sym_x": sym_x, "sym_y": sym_y}


def _stl_tri(out, a, b, c):
    """写一个 ASCII STL 三角面（法线按右手法则计算），零面积面自动跳过"""
    ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
    nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
    ln = math.sqrt(nx * nx + ny * ny + nz * nz)
    if ln < 1e-12:
        return 0
    nx, ny, nz = nx / ln, ny / ln, nz / ln
    out.write(" facet normal %.6e %.6e %.6e\n" % (nx, ny, nz))
    out.write("  outer loop\n")
    for p in (a, b, c):
        out.write("   vertex %.6e %.6e %.6e\n" % p)
    out.write("  endloop\n endfacet\n")
    return 1


def build_mesh_stl(model):
    """读取网格 -> 按对称性镜像补全 -> 写 db/<model>/mesh_view.stl。
    四边形面拆两个三角（保持原绕序：法线指向外界水体）；镜像面片反绕序以保持法线朝外。
    返回统计 dict（含 Web 可用的 url）。"""
    m = read_mesh_dat(model)
    nodes = list(m["nodes"])
    tris = []
    for (i, j, k, l) in m["panels"]:
        tris.append((i, j, k))
        if l != k:
            tris.append((i, k, l))
    n_mirror = 0
    if m["sym_y"]:                       # XOZ 对称：y -> -y
        n0 = len(nodes)
        nodes += [(x, -y, z) for (x, y, z) in m["nodes"]]
        tris += [(a + n0, c + n0, b + n0) for (a, b, c) in tris]   # 反绕序保法线朝外
        n_mirror += 1
    if m["sym_x"]:                       # YOZ 对称：x -> -x
        n1 = len(nodes)
        nodes += [(-x, y, z) for (x, y, z) in m["nodes"]]
        tris += [(a + n1, c + n1, b + n1) for (a, b, c) in tris]
        n_mirror += 1
    path = os.path.join(model_dir(model), "mesh_view.stl")
    n_written = 0
    with open(path, "w") as out:
        out.write("solid WARP_mesh\n")
        for (a, b, c) in tris:
            n_written += _stl_tri(out, nodes[a], nodes[b], nodes[c])
        out.write("endsolid WARP_mesh\n")
    xs = [p[0] for p in nodes]
    ys = [p[1] for p in nodes]
    zs = [p[2] for p in nodes]
    return {"path": path,
            "url": "/mesh_files/%s/mesh_view.stl" % model,
            "n_nodes": len(m["nodes"]), "n_panels": len(m["panels"]),
            "n_tris": n_written, "n_mirror": n_mirror,
            "sym_x": m["sym_x"], "sym_y": m["sym_y"],
            "bounds": [min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)]}


def build_mesh_edges(model):
    """面片边界线段（含镜像），用于三维视图中绘制真实四边形网格线
    （STL wireframe 会多出三角化对角线，故单独按面片边生成）。
    返回 (segments, stats)：segments=[(x1,y1,z1,x2,y2,z2)...]"""
    m = read_mesh_dat(model)
    nodes = list(m["nodes"])
    edges = []
    base = 0
    for (i, j, k, l) in m["panels"]:
        for a, b in ((i, j), (j, k), (k, l), (l, i)):
            if a == b:
                continue          # 三角面补零边不画
            pa, pb = nodes[a], nodes[b]
            edges.append((pa[0], pa[1], pa[2], pb[0], pb[1], pb[2]))
    n_mirror = 0
    if m["sym_y"]:                # XOZ 对称：y -> -y
        n0 = len(nodes)
        nodes += [(x, -y, z) for (x, y, z) in m["nodes"]]
        base = len(edges)         # 镜像前已有的全部边
        edges += [(x1, -y1, z1, x2, -y2, z2)
                  for (x1, y1, z1, x2, y2, z2) in edges[:base]]
        n_mirror += 1
    if m["sym_x"]:                # YOZ 对称：x -> -x
        n1 = len(nodes)
        nodes += [(-x, y, z) for (x, y, z) in m["nodes"]]
        edges += [(-x1, y1, z1, -x2, y2, z2)
                  for (x1, y1, z1, x2, y2, z2) in edges[:len(edges)]]
        n_mirror += 1
    # 去重（对称面上的边镜像后与自身重合；端点 4 位小数做键）
    seen = set()
    uniq = []
    for s in edges:
        a = (round(s[0], 4), round(s[1], 4), round(s[2], 4))
        b = (round(s[3], 4), round(s[4], 4), round(s[5], 4))
        k = (a, b) if a <= b else (b, a)
        if k not in seen:
            seen.add(k)
            uniq.append(s)
    return uniq, {"n_mirror": n_mirror}

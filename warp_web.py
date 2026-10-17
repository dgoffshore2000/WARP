#coding:utf-8
"""
warp_web.py — WARP 的 NiceGUI Web 原型

浏览器(http://127.0.0.1:8300) -> NiceGUI/Python 后端 -> bin/*.exe 与 db/ 原样复用。
与桌面版 Tkinter 并行不干扰：只读写 db/<model>/ 下的同名文件，不改桌面版任何代码。

原型范围（今天交付的骨架）：
  参数表单 -> Save .cal -> Save Mechanics -> Run BEM -> Run QTF -> 实时日志 -> 结果曲线
  网格生成（MODEL 页）仍走桌面版；本原型只消费其产物（summary_model.txt / mesh/）。

启动：C:/ProgramData/anaconda3/python.exe warp_web.py
"""

from nicegui import ui, app

import os
import json
import time
import shutil

import warp_core as wc
from warp_i18n import tr, is_en
import warp_i18n as i18n

# 供 3D 网格查看器加载 STL：/mesh_files/<model>/mesh_view.stl
app.add_static_files('/mesh_files', os.path.join(wc.BASE_DIR, 'db'))

# 单用户原型的会话参数（进程级共享；多开浏览器标签共用一份，够用）
P = wc.merge_params(None)
MODELS = wc.list_models()
if MODELS and not P["model_name"]:
    P["model_name"] = MODELS[0]


DOF_KEYS = [("dof_surge", "Surge"), ("dof_sway", "Sway"), ("dof_heave", "Heave"),
            ("dof_roll", "Roll"), ("dof_pitch", "Pitch"), ("dof_yaw", "Yaw")]

RESULT_TYPES = [
    ("addedmass", "Added mass"),
    ("damping", "Radiation damping"),
    ("waveforce", "Wave excitation force"),
    ("wavephase_deg", "Wave force phase"),
    ("rao_amp", "Motion RAO"),
    ("rao_phase_deg", "RAO phase"),
]


# 矩阵表格的框选 + 粘贴（纯客户端处理选区，粘贴时把文本和选区左上角一起发给后端）
_GRID_JS = """
<script>
window.__warpSel = null;
window.__warpGridCtx = (target, cols) => {
  const cont = target.closest ? target.closest('.warp-grid') : null;
  if (!cont) return null;
  const ins = [...cont.querySelectorAll('input')];
  const idx = ins.indexOf(target);
  if (idx < 0) return null;
  return {cont: cont, ins: ins, idx: idx, r: Math.floor(idx / cols), c: idx % cols, cols: cols};
};
window.warpGridPaint = () => {
  const s = window.__warpSel;
  if (!s) return;
  const r0 = Math.min(s.r0, s.r1), r1 = Math.max(s.r0, s.r1);
  const c0 = Math.min(s.c0, s.c1), c1 = Math.max(s.c0, s.c1);
  s.ins.forEach((el, i) => {
    const r = Math.floor(i / s.cols), c = i % s.cols;
    const cell = el.closest('.warp-cell');
    if (cell) cell.classList.toggle('warp-sel', r >= r0 && r <= r1 && c >= c0 && c <= c1);
  });
};
window.warpGridClear = () => {
  document.querySelectorAll('.warp-cell.warp-sel').forEach(el => el.classList.remove('warp-sel'));
  if (window.__warpSel) window.__warpSel.cont.classList.remove('warp-selecting');
  window.__warpSel = null;
};
window.warpGridDown = (e, cols) => {
  const g = window.__warpGridCtx(e.target, cols);
  if (!g) return;
  window.warpGridClear();
  window.__warpSel = {cont: g.cont, ins: g.ins, cols: cols, r0: g.r, c0: g.c, r1: g.r, c1: g.c};
  g.cont.classList.add('warp-selecting');
  window.warpGridPaint();
};
window.warpGridOver = (e, cols) => {
  const s = window.__warpSel;
  if (!s) return;
  const g = window.__warpGridCtx(e.target, cols);
  if (!g || g.cont !== s.cont) return;
  s.r1 = g.r;
  s.c1 = g.c;
  window.warpGridPaint();
};
window.warpGridPasteText = (e, cols) => {
  e.preventDefault();  // 阻止原生粘贴插入聚焦输入框，避免与后端回写竞争产生拼接脏值
  const text = e.clipboardData ? e.clipboardData.getData('text') : '';
  const s = window.__warpSel;
  const g = window.__warpGridCtx(e.target, cols);
  let r = 0, c = 0;
  if (s && (!g || g.cont === s.cont)) {
    r = Math.min(s.r0, s.r1);
    c = Math.min(s.c0, s.c1);
  } else if (g) {
    r = g.r;
    c = g.c;
  }
  return JSON.stringify({text: text, r: r, c: c});
};
window.addEventListener('mouseup', () => {
  if (window.__warpSel) window.__warpSel.cont.classList.remove('warp-selecting');
});
window.addEventListener('mousedown', (e) => {
  if (window.__warpSel && (!e.target.closest || !e.target.closest('.warp-grid'))) window.warpGridClear();
}, true);
</script>
<style>
.warp-selecting, .warp-selecting * { user-select: none !important; }
.warp-cell.warp-sel { outline: 2px solid #3b82f6 !important; outline-offset: -2px; border-radius: 6px; }
.warp-cell.warp-sel .q-field__control { background: rgba(59,130,246,0.22) !important; }
</style>
"""


def _wire_grid_cell(inp, cols, paste_h):
    """给矩阵单元格接上：拖拽框选（客户端）+ 剪贴板粘贴（文本与选区起点发后端）"""
    inp.on('mousedown', js_handler='(e) => window.warpGridDown(e, %d)' % cols)
    inp.on('mouseover', js_handler='(e) => window.warpGridOver(e, %d)' % cols)
    inp.on('paste', paste_h,
           js_handler='(e) => emit(window.warpGridPasteText(e, %d))' % cols)


def _make_paste_handler(keys2d, inputs2d):
    """Paste 处理器：按选区左上角（无选区则按被粘贴格）逐格填充 Tab/换行分隔的数据"""
    def handle(e):
        try:
            raw = e.args
            if isinstance(raw, (list, tuple)):
                raw = raw[0] if raw else ''
            si = sj = 0
            text = raw if isinstance(raw, str) else ''
            if isinstance(raw, str) and raw.lstrip().startswith('{'):
                data = json.loads(raw)
                text = data.get('text', '')
                si = int(data.get('r') or 0)
                sj = int(data.get('c') or 0)
            else:
                for i, row in enumerate(inputs2d):
                    for j, el in enumerate(row):
                        if el is e.sender:
                            si, sj = i, j
            if not text or not text.strip():
                return
            rows = [r.split('\t') for r in
                    text.replace('\r\n', '\n').replace('\r', '\n').strip('\n').split('\n')]
            n = 0
            for di, vals in enumerate(rows):
                for dj, v in enumerate(vals):
                    ii, jj = si + di, sj + dj
                    if ii < len(keys2d) and jj < len(keys2d[ii]):
                        val = v.strip()
                        P[keys2d[ii][jj]] = val
                        inputs2d[ii][jj].value = val
                        n += 1
            ui.notify(tr('已从剪贴板粘贴 %d 个单元格（起点 r%d c%d）') % (n, si + 1, sj + 1),
                      type='positive')
        except Exception as ex:
            ui.notify(tr('粘贴失败：%s') % ex, type='negative')
    return handle


# ---------------------------------------------------------------- 控件工厂
def bind(key):
    def handler(e):
        P[key] = e.value
    return handler


def num_input(label, key, tip="", cls="w-28"):
    inp = ui.input(label, value=str(P[key]), on_change=bind(key)) \
        .props('dense outlined hide-bottom-space').classes(cls)
    if tip:
        inp.tooltip(tip)
    return inp


def cog_fields():
    """COG 重心 X/Y/Z：1x3 网格（样式与 Inertia 矩阵一致）。
    支持三种输入方式：
    1) 单框直接输入；
    2) 任一框粘贴多值（tab/空格/逗号分隔）自动分发；
    3) 与 Inertia/D/S 相同的连续框选 + Excel 整块粘贴（warp-grid 选区机制）。"""
    parts = (P.get('hyst_cog') or '').split()
    vals = [parts[i] if len(parts) > i else '' for i in range(3)]
    refs = []

    def write_back():
        P['hyst_cog'] = ' '.join(v.strip() for v in vals)

    def on_part(idx):
        def handler(e):
            raw = str(e.value or '')
            toks = [t for t in raw.replace('\t', ' ').replace('\n', ' ')
                    .replace(',', ' ').split() if t]
            if len(toks) >= 2:
                # 多值粘贴：按序分发到 X/Y/Z
                for i in range(3):
                    vals[i] = toks[i] if i < len(toks) else ''
                for i, r in enumerate(refs):
                    if i == idx:
                        continue
                    if r.value != vals[i]:
                        r.value = vals[i]
                # 当前框自身的归一化延后执行——在其 on_change 处理中同步改
                # 自身 value 会被正在进行的输入事件回写覆盖，显示不更新
                ui.timer(0.1, lambda: setattr(refs[idx], 'value', vals[idx]),
                         once=True)
                write_back()
                return
            vals[idx] = toks[0] if toks else ''
            write_back()
        return handler

    def paste_h(e):
        """框选/单元格粘贴：按选区起点顺序填充（行优先展平，兼容多行一列）"""
        raw = e.args
        if isinstance(raw, (list, tuple)):
            raw = raw[0] if raw else ''
        text = raw if isinstance(raw, str) else ''
        sj = 0
        if isinstance(raw, str) and raw.lstrip().startswith('{'):
            data = json.loads(raw)
            text = data.get('text', '')
            sj = int(data.get('c') or 0)
        if not text or not text.strip():
            return
        toks = []
        for line in text.replace('\r\n', '\n').replace('\r', '\n') \
                .strip('\n').split('\n'):
            toks.extend(v.strip() for v in line.split('\t'))
        n = 0
        for k, v in enumerate(toks):
            jj = sj + k
            if 0 <= jj < 3 and v:
                vals[jj] = v
                if refs[jj].value != v:
                    refs[jj].value = v
                n += 1
        write_back()
        if n:
            ui.notify(tr('已粘贴 COG %d 个值（起点第 %d 格）') % (n, sj + 1),
                      type='positive')

    with ui.row().classes('items-center gap-3 flex-wrap'):
        ui.label(tr('COG 重心位置')).classes('text-sm opacity-70')
        with ui.grid(columns=4).classes('gap-0 w-fit border border-gray-600 warp-grid cog-grid'):
            ui.label('').classes('px-2 py-1 border-b border-gray-600')
            for ax in ('x', 'y', 'z'):
                ui.label(ax).classes(
                    'px-2 py-1 text-center text-sm opacity-70 border-b border-gray-600')
            ui.label('COG').classes(
                'px-2 py-1 text-sm opacity-70 border-r border-gray-600 flex items-center')
            for i in range(3):
                inp = ui.input('', value=vals[i], on_change=on_part(i)) \
                    .props('dense outlined hide-bottom-space') \
                    .classes('w-24 text-right rounded-none warp-cell') \
                    .tooltip(tr('重心 %s 坐标；可拖拽框选后粘贴 Excel 数据') % 'XYZ'[i])
                refs.append(inp)
            for inp in refs:
                _wire_grid_cell(inp, 3, paste_h)
    return refs


def wave_points_grid():
    """Wave measure points：N 行 x 2 列网格（样式与 COG 一致）。
    支持：1) 单框直接输入；2) 拖拽框选 + Excel 整块粘贴（warp-grid 选区机制），
    粘贴行数超出当前行数时自动加行；3) 手动 加行/删行。
    数据写回 P['wave_points']，每行 'x y'（口径与原 textarea 完全一致）。"""
    box = {}

    def parse_rows():
        rows = []
        for ln in str(P.get('wave_points') or '').splitlines():
            ln = ln.strip()
            if not ln:
                continue
            t = ln.replace('\t', ' ').replace(',', ' ').split()
            rows.append([t[0] if t else '', t[1] if len(t) > 1 else ''])
        return rows or [['', '']]

    def write_back():
        P['wave_points'] = '\n'.join(
            ' '.join(v.strip() for v in r) for r in box['rows']
            if any(v.strip() for v in r))

    def rebuild():
        box['rows'] = box.get('rows') or parse_rows()
        with box['holder'].clear():
            with ui.grid(columns=3).classes(
                    'gap-0 w-fit border border-gray-600 warp-grid pts-grid'):
                ui.label('').classes(
                    'px-2 py-1 border-b border-r border-gray-600')
                for ax in ('x', 'y'):
                    ui.label(ax).classes(
                        'px-2 py-1 text-center text-sm opacity-70 '
                        'border-b border-gray-600')
                for i, r in enumerate(box['rows']):
                    ui.label('P%d' % (i + 1)).classes(
                        'px-2 py-1 text-sm opacity-70 border-r border-gray-600 '
                        'flex items-center')
                    for j in range(2):
                        inp = ui.input('', value=r[j],
                                       on_change=(lambda idx=i, col=j:
                                                  lambda e: _set_cell(
                                                      idx, col, e.value))()) \
                            .props('dense outlined hide-bottom-space') \
                            .classes('w-24 text-right rounded-none warp-cell') \
                            .tooltip(tr('测量点 %s 坐标；可拖拽框选后粘贴 Excel 数据')
                                     % 'xy'[j])
                        _wire_grid_cell(inp, 2, paste_h)

    def _set_cell(i, j, v):
        box['rows'][i][j] = str(v or '').strip()
        write_back()

    def paste_h(e):
        """按选区左上角整块粘贴（行优先，tab 分列）；行数不足自动加行"""
        raw = e.args
        if isinstance(raw, (list, tuple)):
            raw = raw[0] if raw else ''
        text = raw if isinstance(raw, str) else ''
        r0 = c0 = 0
        if isinstance(raw, str) and raw.lstrip().startswith('{'):
            data = json.loads(raw)
            text = data.get('text', '')
            r0 = int(data.get('r') or 0)
            c0 = int(data.get('c') or 0)
        if not text or not text.strip():
            return
        n = 0
        for di, line in enumerate(
                text.replace('\r\n', '\n').replace('\r', '\n')
                .strip('\n').split('\n')):
            for dj, v in enumerate(line.split('\t')):
                v = v.strip()
                ii, jj = r0 + di, c0 + dj
                if jj >= 2 or not v:
                    continue
                while ii >= len(box['rows']):
                    box['rows'].append(['', ''])
                box['rows'][ii][jj] = v
                n += 1
        write_back()
        rebuild()
        if n:
            ui.notify(tr('已粘贴测量点 %d 个值（起点 P%d 第 %d 列）')
                      % (n, r0 + 1, c0 + 1), type='positive')

    with ui.expansion('Wave measure points',
                      caption=tr('每行一个 "x y"，可框选后直接粘贴 Excel 数据'),
                      value=True).classes('w-full border border-gray-600 '
                                          'rounded-lg px-3'):
        with ui.row().classes('items-center gap-2'):
            def gen_rows():
                try:
                    n = int(gen_input.value)
                except (TypeError, ValueError):
                    ui.notify(tr('请输入点数'), type='warning')
                    return
                if not 1 <= n <= 500:
                    ui.notify(tr('点数需在 1-500 之间'), type='warning')
                    return
                cur = box['rows'] or []
                # 保留前 n 行已有数据，多退少补空行
                box['rows'] = [(cur[i][:] if i < len(cur) else ['', ''])
                               for i in range(n)]
                write_back()
                rebuild()
                ui.notify(tr('已生成 %d 个测量点行') % n, type='positive')

            def add_row():
                box['rows'].append(['', ''])
                write_back()
                rebuild()

            def del_row():
                if len(box['rows']) > 1:
                    box['rows'].pop()
                    write_back()
                rebuild()

            gen_input = ui.number(tr('点数'), value=max(len(parse_rows()), 1),
                                  precision=0, min=1, max=500) \
                .props('dense outlined hide-bottom-space').classes('w-24') \
                .tooltip(tr('点击"生成"直接创建对应数量的测量点行'))
            ui.button(tr('生成'), on_click=gen_rows).props('dense outline size=sm')
            ui.button(tr('+ 行'), on_click=add_row).props('dense outline size=sm')
            ui.button(tr('删行'), on_click=del_row) \
                .props('dense outline size=sm') \
                .tooltip(tr('删除最后一行'))
        box['holder'] = ui.column().classes('gap-0')
    box['rows'] = None
    rebuild()


def bool_input(key, label):
    return ui.checkbox(label, value=bool(P[key]), on_change=bind(key))


def bind_str(key):
    """toggle/select -> P 存字符串（与 write_nemoh_cal 的字符串约定一致）"""
    def handler(e):
        P[key] = str(e.value) if e.value is not None else ''
    return handler


def bind_bool01(key):
    """checkbox -> P 存 '1'/'0' 字符串"""
    def handler(e):
        P[key] = '1' if e.value else '0'
    return handler


def qtf_freq_fields():
    """QTF freq set 拆成 N/Min/Max 三个输入（与 Load Cases 风格统一），
    任一输入变化时重组为 'N ωmin ωmax' 写回 P['qtff']。返回 [input1, input2, input3]。"""
    parts = (P.get('qtff') or '').split()
    vals = [parts[i] if len(parts) > i else '' for i in range(3)]

    def on_part(idx):
        def handler(e):
            vals[idx] = str(e.value or '').strip()
            P['qtff'] = ' '.join(v for v in vals if v)
        return handler

    outs = []
    for idx, (label, tip) in enumerate((('N freq', tr('径向频率个数')),
                                        ('Min freq', tr('最小频率 rad/s')),
                                        ('Max freq', tr('最大频率 rad/s')))):
        outs.append(ui.input(label, value=vals[idx], on_change=on_part(idx))
                    .props('dense outlined hide-bottom-space')
                    .classes('w-24').tooltip(tip + tr('（QTF 仅接受 rad/s）')))
    return outs


def set_disabled(el, off):
    """Quasar 组件禁用/启用（Element 无通用 disable 方法，用 disable prop）"""
    if off:
        el.props('disable')
    else:
        el.props(remove='disable')


def _sync_qtf(refs):
    """按 勾选状态 联动 QTF 面板：未启用/不适用/有冲突的选项置灰并强制复位。
    规则（对照 Nemoh 手册 p.19-20）：
      - QTF 未启用 -> 全部置灰、后处理开关复位 0
      - Contrib=1  -> HASBO / HASFS+ASYMP 不可选（未计算）、FS 输入禁用
      - Contrib=2  -> HASFS+ASYMP 必须为 0（手册硬约束）、FS 输入禁用
      - Contrib=3  -> 全部可选，FS meshfile / FS QTF params 启用
      - 启用且未选 Contrib 时自动取 2（DUOK+HASBO，慢漂标准配置）"""
    on = bool(P['qtf'])
    contrib = int(P['qtfc']) if str(P['qtfc']) in ('1', '2', '3') else 0
    if on and contrib == 0:
        contrib = 2
        P['qtfc'] = '2'
        refs['qtfc'].value = 2
        if P['duko'] != '1':
            P['duko'] = '1'
            refs['duko'].value = True
        if P['hasbo'] != '1':
            P['hasbo'] = '1'
            refs['hasbo'].value = True
    if on and P['freq_qtft'] not in ('1', '2', '3'):
        P['freq_qtft'] = '1'
        refs['freq_qtft'].value = 1
    for k in ('qtfd', 'qtfc', 'hys_term', 'freq_qtft', 'duko'):
        set_disabled(refs[k], not on)
    # qtff 现为三个输入框的列表（N/Min/Max），逐个禁用
    for el in (refs['qtff'] if isinstance(refs['qtff'], list) else [refs['qtff']]):
        set_disabled(el, not on)
    fs_on = on and contrib == 3
    set_disabled(refs['fsmf'], not fs_on)
    set_disabled(refs['fsmf_qtf'], not fs_on)
    set_disabled(refs['hasbo'], not (on and contrib >= 2))
    set_disabled(refs['hasfs'], not (on and contrib == 3))
    if not on or contrib < 2:
        P['hasbo'] = '0'
        refs['hasbo'].value = False
    if not on or contrib != 3:
        P['hasfs_symp'] = '0'
        refs['hasfs'].value = False
    if not on:
        P['duko'] = '0'
        refs['duko'].value = False


def _on_qtf_contrib(e, refs):
    P['qtfc'] = str(e.value) if e.value is not None else ''
    # 输出开关默认跟随 Contrib：凡是本次计算覆盖到的项自动勾上，
    # 之后仍可手动取消某个开关做分项归因（输出 ⊆ 计算内容）
    if P['qtf'] and e.value is not None:
        c = int(P['qtfc'])
        P['duko'] = '1'
        refs['duko'].value = True
        P['hasbo'] = '1' if c >= 2 else '0'
        refs['hasbo'].value = c >= 2
        P['hasfs_symp'] = '1' if c == 3 else '0'
        refs['hasfs'].value = c == 3
    _sync_qtf(refs)


def matrix_grid(prefix):
    """6x6 矩阵输入（prefix='d' -> D11..D66 阻尼；'s' -> S11..S66 附加刚度）
    支持鼠标拖拽框选整个矩阵后 Ctrl+V 从 Excel 粘贴"""
    cols = 6
    keys = [["%s%d%d" % (prefix, i, j) for j in range(1, cols + 1)] for i in range(1, cols + 1)]
    inputs = [[None] * cols for _ in range(cols)]
    paste_h = _make_paste_handler(keys, inputs)
    with ui.grid(columns=cols + 1).classes(
            'gap-x-1 gap-y-1 items-center warp-grid matrix-grid-' + prefix):
        ui.label('')
        for j in range(1, cols + 1):
            ui.label(str(j)).classes('text-xs opacity-60 text-center')
        for i in range(cols):
            ui.label(str(i + 1)).classes('text-xs opacity-60')
            for j in range(cols):
                inp = ui.input(value=str(P[keys[i][j]]), on_change=bind(keys[i][j])) \
                    .props('dense outlined hide-bottom-space') \
                    .classes('w-16 warp-cell') \
                    .tooltip(prefix.upper() + str(i + 1) + str(j + 1))
                _wire_grid_cell(inp, cols, paste_h)
                inputs[i][j] = inp


# ---------------------------------------------------------------- 动作
def act_new_model(new_input, model_sel):
    name = (new_input.value or "").strip()
    if not name:
        ui.notify(tr('请输入模型名'), type='warning')
        return
    if any(ch in name for ch in '\\/:*?"<>|'):
        ui.notify(tr('模型名含非法字符'), type='negative')
        return
    import os
    d = wc.model_dir(name)
    os.makedirs(d + "/mesh", exist_ok=True)
    P["model_name"] = name
    model_sel.options = wc.list_models()
    model_sel.update()
    model_sel.value = name
    new_input.value = ""
    ui.notify(tr('已创建 db/') + name + tr('（网格请用桌面版 MODEL 页生成后放入 mesh/）'),
              type='positive')


def act_delete_model(model_sel, mesh_holder):
    """删除当前选中模型对应的 db/<name> 文件夹。
    弹确认窗口；有计算运行时禁止删除；删除前做路径校验（必须位于 db/ 一级子目录）。"""
    name = model_sel.value
    if not name:
        ui.notify(tr('未选择模型'), type='warning')
        return
    if wc.RUN.snapshot()["status"] == "running":
        ui.notify(tr('有计算正在运行，请等待结束或完成后再删除模型'), type='negative')
        return
    # 安全校验：只允许删除 db/ 下一级且真实存在的模型目录
    d = os.path.realpath(wc.model_dir(name))
    db_root = os.path.realpath(os.path.join(wc.BASE_DIR, 'db'))
    if os.path.dirname(d) != db_root or not os.path.isdir(d):
        ui.notify(tr('路径校验失败，拒绝删除'), type='negative')
        return

    with ui.dialog() as dlg, ui.card().classes('min-w-[360px]'):
        ui.label(tr('确认删除模型')).classes('text-base font-semibold')
        ui.label(tr('将永久删除文件夹 db/%s（含网格、计算结果等全部文件），'
                    '此操作不可恢复！') % name).classes('text-sm')
        with ui.row().classes('w-full justify-end gap-2'):
            ui.button(tr('取消'), on_click=dlg.close).props('flat')

            def do_del():
                dlg.close()
                try:
                    shutil.rmtree(d)
                except Exception as ex:
                    ui.notify(tr('删除失败：%s') % ex, type='negative')
                    return
                models = wc.list_models()
                P["model_name"] = models[0] if models else ''
                model_sel.options = models or ['']
                model_sel.value = P["model_name"]
                model_sel.update()
                # 场景已加载过网格时，_on_model_change（由 value 赋值触发）会
                # 自动重载为新模型的网格；无剩余模型时清空 3D 场景
                sc = mesh_holder.get('scene')
                if sc is not None and _mesh_loaded(sc) and not models:
                    sc.clear()
                    mesh_holder['info'].set_text(tr('网格：未加载'))
                ui.notify(tr('已删除 db/') + name, type='positive')

            ui.button(tr('删除'), on_click=do_del).props('color=negative')
    dlg.open()


def act_save_cal(log):
    try:
        for n in wc.write_nemoh_cal(P):
            log.push(n)
        ui.notify(tr('Nemoh.cal 已生成'), type='positive')
    except Exception as e:
        ui.notify(str(e), type='negative')


def act_save_mech(log):
    try:
        msg = wc.write_mechanics(P)
        log.push(msg)
        ui.notify(msg, type='positive')
    except Exception as e:
        ui.notify(str(e), type='negative')


def act_run(kind, log):
    try:
        wc.RUN.start(kind, P)
        log.push('=== Run %s started (model: %s) ===' % (kind.upper(), P["model_name"]))
        ui.notify(tr('%s 运行已启动') % kind.upper())
    except Exception as e:
        ui.notify(str(e), type='negative')


def act_hyst_summary(out_label):
    try:
        r = wc.hydros_summary(P)
        text = tr(
            '浮心/重心 (m):  XF %s | XG %s\n'
            '               YF %s | YG %s\n'
            '               ZF %s | ZG %s\n'
            '排水量 Displacement  m³: %s\n'
            '水线面面积 WPA       m²: %s\n'
            '初稳性高:  GMX %s m   GMY %s m\n'
            ' hull 惯性矩:  IX %s  IY %s  IZ %s\n'
            '静水刚度:  K33 %s N\n'
            '           K44 %s N/rad\n'
            '           K55 %s N/rad\n'
            '→ summary_hydrosta.txt 已更新（Save .cal 的 COG 来源）'
        ) % (r["xb"], r["xg"], r["yb"], r["yg"], r["zb"], r["zg"],
             r["displacement_m3"], r["waterplane_m2"], r["gmx_m"], r["gmy_m"],
             r["ix"][0], r["iy"][1], r["iz"][2],
             r["kz"][0] if r["kz"] else '-',
             r["krx"][1] if len(r["krx"]) > 1 else '-',
             r["kry"][2] if len(r["kry"]) > 2 else '-')
        out_label.set_text(text)
        ui.notify(tr('静水力摘要已更新'), type='positive')
    except FileNotFoundError as e:
        ui.notify(tr('mesh/ 产物缺失（先 Run HYST）：%s') % e.filename, type='warning')
    except Exception as e:
        ui.notify(str(e), type='negative')


_poll_state = {"offset": 0, "last_elapsed": 1e18, "prev_status": "idle"}


def act_load_mesh(info_label, scene_box, wire_checkbox):
    """解析 db/<model>/<model>.dat -> 镜像 -> STL -> 三维场景渲染
    按背景亮度自适应配色：浅底=参考图风格（绿网格/蓝水线/深色标签），
    深底=暗色主题配色（青水线/亮色标签）"""
    try:
        st = wc.build_mesh_stl(P["model_name"])
        edge_segs, _ = wc.build_mesh_edges(P["model_name"])
    except Exception as e:
        ui.notify(str(e), type='negative')
        info_label.set_text(tr('加载失败：%s') % e)
        return
    _hex = (scene_box._props.get('background-color') or '#ffffff').lstrip('#')
    try:
        _r, _g, _b = int(_hex[0:2], 16), int(_hex[2:4], 16), int(_hex[4:6], 16)
        light_bg = (0.2126 * _r + 0.7152 * _g + 0.0722 * _b) > 127
    except Exception:
        light_bg = True
    wl_col = '#2255cc' if light_bg else '#22d3ee'
    scene_box.clear()
    with scene_box:
        # 面片填充（浅黄，白底参考图风格）；勾选"仅线框"时不填充
        if not wire_checkbox.value:
            scene_box.stl(st["url"] + '?t=%d' % int(time.time())) \
                .material('#f0e68c', 0.95, 'both')
        # 面片边界：按面片四边生成线段（网格线）。
        # 填充模式用深色边线衬托；纯线框模式用绿色网格线（参考 Nemoh/GMESH 出图）
        edge_col = '#1c2431' if not wire_checkbox.value else '#2eb872'
        for (x1, y1, z1, x2, y2, z2) in edge_segs:
            scene_box.line([x1, y1, z1], [x2, y2, z2]).material(edge_col, 1.0)
        # z=0 水面：4 条水线框线。
        # 框中心取模型包围盒中心（模型可能不在原点，如 MPV 原点在艉部）
        bx = st["bounds"]
        xc, yc = (bx[0] + bx[1]) / 2, (bx[2] + bx[3]) / 2
        W = max(0.62 * abs(bx[1] - bx[0]), 0.62 * abs(bx[3] - bx[2]), 2.0)
        for (p1, p2) in (((xc - W, yc - W, 0), (xc + W, yc - W, 0)),
                         ((xc + W, yc - W, 0), (xc + W, yc + W, 0)),
                         ((xc + W, yc + W, 0), (xc - W, yc + W, 0)),
                         ((xc - W, yc + W, 0), (xc - W, yc - W, 0))):
            scene_box.line(list(p1), list(p2)).material(wl_col, 0.7)
        # 模型坐标系：仅保留三色轴（无文字标签），文字由左下角迷你坐标系承担
        L = 0.18 * max(abs(bx[1] - bx[0]), abs(bx[3] - bx[2]), 1.0)
        scene_box.axes_helper(L)
    zc = (bx[4] + bx[5]) / 2
    # 正交相机无透视畸变，位置只决定方位角/俯仰角（距离不影响大小）；
    # 视线中心 = 包围盒中心，方位与参考图一致：艏部在右、自舷侧上方斜视
    d = 3.0 * max(abs(bx[1] - bx[0]), abs(bx[3] - bx[2]), 10.0)
    scene_box.move_camera(x=xc + d * 0.65, y=yc - d * 0.62, z=zc + d * 0.45,
                          look_at_x=xc, look_at_y=yc,
                          look_at_z=zc, duration=0)
    # 左下角迷你坐标系：屏幕空间小工具（不在场景里画轴），
    # 每 40ms 用相机 view 矩阵把世界 XYZ 单位向量投影到屏幕，
    # 画轴线（正轴实线/负轴虚线）+ X/Y/Z 字母，随视角实时联动。
    # getElement() 是 NiceGUI 前端全局（runJavascript 的 eval 作用域内可见）
    ui.run_javascript('''
        (function() {
          var root = document.querySelector('.mesh-scene-root');
          if (!root || root.querySelector('.mesh-axis-gizmo')) return;
          var S = 96, C = 48, R = 30;
          var g = document.createElement('div');
          g.className = 'mesh-axis-gizmo';
          g.style.cssText = 'position:absolute;left:14px;bottom:14px;width:' + S + 'px;height:' + S +
                            'px;pointer-events:none;z-index:5;';
          var NS = 'http://www.w3.org/2000/svg';
          var svg = document.createElementNS(NS, 'svg');
          svg.setAttribute('width', S); svg.setAttribute('height', S);
          svg.style.cssText = 'position:absolute;left:0;top:0;';
          g.appendChild(svg);
          var c = document.createElement('div');
          c.style.cssText = 'position:absolute;left:50%;top:50%;width:6px;height:6px;margin:-3px 0 0 -3px;border-radius:50%;background:#9ca3af;';
          g.appendChild(c);
          g._lines = []; g._labels = [];
          [['X', '#ef4444', 1, 0, 0], ['Y', '#22c55e', 0, 1, 0], ['Z', '#3b82f6', 0, 0, 1]]
          .forEach(function(a) {
            [[1, 1], [-1, 0]].forEach(function(sgn) {
              var ln = document.createElementNS(NS, 'line');
              ln.setAttribute('stroke', a[1]);
              ln.setAttribute('stroke-width', 2);
              if (sgn[0] < 0) { ln.setAttribute('stroke-dasharray', '3,3'); ln.setAttribute('opacity', 0.4); }
              svg.appendChild(ln);
              g._lines.push({el: ln, s: sgn[0], v: [a[2] * sgn[0], a[3] * sgn[0], a[4] * sgn[0]]});
            });
            var s = document.createElement('div');
            s.textContent = a[0];
            s.style.cssText = 'position:absolute;font:bold 13px Consolas,monospace;color:' + a[1] +
                              ';transform:translate(-50%,-50%);text-shadow:0 0 3px rgba(127,127,127,.55);';
            g.appendChild(s);
            g._labels.push({el: s, v: [a[2], a[3], a[4]]});
          });
          root.appendChild(g);
          if (!window.__meshGizmoLoop) {
            window.__meshGizmoLoop = setInterval(function() {
              document.querySelectorAll('.mesh-axis-gizmo').forEach(function(gz) {
                var rid = (gz.parentElement.id || '').slice(1);
                var sc;
                try { sc = getElement(rid); } catch (e) { return; }
                if (!sc || !sc.camera || !sc.camera.matrixWorldInverse) return;
                var m = sc.camera.matrixWorldInverse.elements;
                var proj = function(v) {
                  return [m[0] * v[0] + m[4] * v[1] + m[8] * v[2],
                          -(m[1] * v[0] + m[5] * v[1] + m[9] * v[2])];
                };
                gz._lines.forEach(function(o) {
                  var p = proj(o.v);
                  o.el.setAttribute('x1', C); o.el.setAttribute('y1', C);
                  o.el.setAttribute('x2', C + p[0] * R * o.s);
                  o.el.setAttribute('y2', C + p[1] * R * o.s);
                });
                gz._labels.forEach(function(o) {
                  var p = proj(o.v);
                  o.el.style.left = (C + p[0] * (R + 9)) + 'px';
                  o.el.style.top = (C + p[1] * (R + 9)) + 'px';
                });
              });
            }, 40);
          }
        })();
    ''')
    sym = (tr('XOZ 镜像') if st["sym_y"] else '') + (tr(' + YOZ 镜像') if st["sym_x"] else '')
    info_label.set_text(
        tr('节点 %d · 面片 %d（镜像 %d 次补全 → %d 三角面 / %d 网格线） · 对称: %s · 范围 x[%g, %g] y[%g, %g] z[%g, %g]')
        % (st["n_nodes"], st["n_panels"], st["n_mirror"], st["n_tris"],
           len(edge_segs), sym or tr('无'), bx[0], bx[1], bx[2], bx[3], bx[4], bx[5]))


def _mesh_loaded(scene_box):
    """场景里是否已有网格内容。
    NiceGUI 的 Scene 没有 children()（3.17 实测 AttributeError），
    只能查其内部对象列表；取不到时按"未加载"处理，避免回调抛异常打断事件处理。"""
    try:
        return bool(scene_box.objects)
    except Exception:
        return False


def _mesh_reload(info_label, scene_box, wire_checkbox):
    """线框开关切换：若已加载过网格则立即重渲染"""
    if _mesh_loaded(scene_box):
        act_load_mesh(info_label, scene_box, wire_checkbox)


def _on_model_change(e, mesh_holder):
    """切换模型：更新参数；3D 场景已加载过网格时才自动重载（默认不加载）"""
    P.update(model_name=e.value)
    sc = mesh_holder.get('scene')
    if sc is not None and _mesh_loaded(sc):
        act_load_mesh(mesh_holder.get('info'), sc, mesh_holder.get('wire'))


def poll_run(log, status_labels):
    """1s 轮询：推送日志增量 + 刷新本页所有运行状态标签（status_labels 为
    当前页面自己的标签列表，由 index 的定时器闭包传入，避免多页/刷新后串页失效）"""
    snap = wc.RUN.snapshot()
    # 新一轮运行检测：elapsed 归零回绕
    if snap["elapsed"] + 1.0 < _poll_state["last_elapsed"] and snap["status"] == "running":
        _poll_state["offset"] = 0
        log.clear()
    _poll_state["last_elapsed"] = snap["elapsed"]
    lines = snap["lines"]
    if len(lines) > _poll_state["offset"]:
        for ln in lines[_poll_state["offset"]:]:
            log.push(ln)
        _poll_state["offset"] = len(lines)
    elif len(lines) < _poll_state["offset"]:
        _poll_state["offset"] = 0

    label = '%s' % snap["status"]
    if snap["kind"]:
        label += ' | %s | %s | %.0fs' % (snap["kind"], snap["model"], snap["elapsed"])
    if snap["returncode"] is not None and snap["status"] != "running":
        label += ' | rc=%s' % snap["returncode"]
    cls = ('text-sm font-mono ' +
           {'running': 'text-orange-400', 'done': 'text-green-400',
            'failed': 'text-red-400'}.get(snap["status"], 'opacity-70'))
    for lab in status_labels:
        lab.set_text(label)
        lab.classes(cls)

    # 运行结束通知一次
    if _poll_state["prev_status"] == "running" and snap["status"] in ("done", "failed"):
        if snap["status"] == "done":
            ui.notify(tr('%s 运行完成 (%.0fs)') % (snap["kind"].upper(), snap["elapsed"]),
                      type='positive')
        else:
            ui.notify(tr('%s 运行失败，请检查日志') % snap["kind"].upper(), type='negative')
    _poll_state["prev_status"] = snap["status"]


def refresh_results(res_type, dof_i, dof_j, direc_sel, chart, x_sel=None):
    model = P["model_name"]
    data = wc.get_results(model)
    if not data.get("ok"):
        ui.notify('；'.join(data["errors"]) or tr('无结果'), type='warning')
        return
    sec_key = res_type.value
    sec = data["sections"].get(sec_key)
    if sec is None:
        ui.notify(tr('该结果不存在（%s）：%s') % (sec_key, '；'.join(data["errors"])),
                  type='warning')
        return
    i = int(dof_i.value)
    j = int(dof_j.value)
    d = int(direc_sel.value)
    periods = data["axes"]["period_s"]
    dirdegs = data["axes"]["direc_deg"]
    dofs = data["dof_names"]

    # 自动同步方向下拉选项（免去手动点"加载方向列表"）：
    # 保持当前选择；若原选项不在新列表中则回到"所有方向"
    _opts = {-1: tr('所有方向'),
             **{i2: ('Wave %.0f°' % dd) for i2, dd in enumerate(dirdegs)}}
    if direc_sel.options != _opts:
        _cur = direc_sel.value
        direc_sel.options = _opts
        direc_sel.value = _cur if _cur in _opts else -1
        direc_sel.update()
        d = int(direc_sel.value)

    # 横坐标模式：period(s) / freq(Hz) / freq(rad/s)，由 T=periods 换算
    xmode = x_sel.value if x_sel is not None else 'period'
    if xmode == 'hz':
        xs = sorted(1.0 / t for t in periods if t)
        xlabel = 'Frequency Hz'
    elif xmode == 'rad':
        xs = sorted(2.0 * 3.141592653589793 / t for t in periods if t)
        xlabel = 'Frequency rad/s'
    else:
        xs = list(periods)
        xlabel = 'Wave Period s'

    def xy(ys):
        pts = list(zip(xs, ys[:len(xs)]))
        return sorted(pts) if xmode != 'period' else pts

    series = []
    ylabel = ''
    title = RESULT_TYPES[[k for k, _ in RESULT_TYPES].index(sec_key)][1]
    if sec_key in ("addedmass", "damping"):
        y = [sec[k][i][j] for k in range(len(periods))]
        series.append({"name": '%s/%s' % (dofs[i], dofs[j]),
                       "data": xy([sec[k][i][j] for k in range(len(periods))])})
        unit = 'kg' if i <= 3 else 'kg*m^2'
        if sec_key == "damping":
            unit = 'kg/s' if i <= 3 else 'kg*m/s'
        ylabel = unit
    else:
        # 单位口径（Nemoh 官方：Fe(t) = a·|Fe(ω,β)|·cos(ωt−∠Fe)，即文件值已除以波幅）：
        #   Wave excitation force：平动 N/m；转动为力矩 N*m/m（每米波幅）
        #   RAO：RAO.dat 表头明确转动列为 deg（每米波幅），原始值直接绘制，不做 rad->deg 换算
        if sec_key == "rao_amp":
            ylabel = 'm/m' if i <= 3 else 'deg/m'
        elif sec_key == "rao_phase_deg":
            ylabel = 'deg'
        elif sec_key == "wavephase_deg":
            ylabel = 'deg'
        else:
            ylabel = 'N/m' if i <= 3 else 'N*m/m'
        if d == -1 or d >= len(dirdegs):
            plot_dirs = list(range(len(dirdegs)))
        else:
            plot_dirs = [d]
        for dd in plot_dirs:
            y = [sec[dd][k][i] for k in range(len(periods))]
            series.append({"name": 'Wave %.0f°' % dirdegs[dd],
                           "data": xy(y)})

    # NiceGUI 3.x: options 是只读 property，需原地修改后调用 update()
    chart.options.clear()
    chart.options.update({
        "backgroundColor": "transparent",
        "textStyle": {"color": "#bbb"},
        "title": {"text": '%s (%s)' % (title, P["model_name"]),
                  "top": 4, "left": "center",
                  "textStyle": {"color": "#ddd", "fontSize": 14}},
        "tooltip": {"trigger": "axis"},
        "legend": {"top": 30, "type": "scroll", "textStyle": {"color": "#bbb"}},
        "grid": {"top": 84, "left": 64, "right": 24, "bottom": 48},
        "xAxis": {"type": "value", "name": xlabel,
                  "nameTextStyle": {"color": "#bbb"},
                  "axisLabel": {"color": "#bbb"},
                  "axisLine": {"lineStyle": {"color": "#666"}}},
        "yAxis": {"type": "value", "name": ylabel,
                  "nameTextStyle": {"color": "#bbb"},
                  "axisLabel": {"color": "#bbb"},
                  "splitLine": {"lineStyle": {"color": "#333"}}},
        "series": [{"type": "line", "symbol": "circle", "symbolSize": 5,
                    **s} for s in series],
    })
    chart.update()


# ---------------------------------------------------------------- QTF 结果
def load_qtf_options(qtf_set, qtf_beta, qtf_dof):
    """读取 QTF 结果并填充 浪向对/DOF 下拉框"""
    data = wc.get_qtf_results(P["model_name"])
    if not data.get("ok"):
        ui.notify('；'.join(data["errors"]) or tr('无 QTF 结果'), type='warning')
        return None
    key = qtf_set.value
    st = data["sets"].get(key)
    if not st:
        ui.notify(tr('该模型无 %s 结果文件') % (tr('差频 QTFM') if key == 'qtfm' else tr('和频 QTFP')),
                  type='warning')
        return None
    cur_beta = qtf_beta.value
    qtf_beta.options = {i: ('β %g° / %g°' % (b1, b2)) for i, (b1, b2)
                        in enumerate(st["betas"])}
    qtf_beta.value = cur_beta if cur_beta in qtf_beta.options else 0
    qtf_beta.update()
    cur_dof = qtf_dof.value
    qtf_dof.options = {i: n for i, n in enumerate(data["dofs"])}
    qtf_dof.value = cur_dof if cur_dof in qtf_dof.options else 0
    qtf_dof.update()
    qtf_beta.enable()
    qtf_dof.enable()
    return data


def refresh_qtf_diag(qtf_set2, qtf_dof2, qtf_qty2, qtf_x2, chart2):
    """主对角线二阶载荷（ω1=ω2，等同平均漂移力）：全部浪向对画成多条曲线，
    样式与 Results 卡一致（数值横轴 + 顶部图例 + 圆点折线）"""
    data = wc.get_qtf_results(P["model_name"])
    if not data.get("ok"):
        ui.notify('；'.join(data["errors"]) or tr('无 QTF 结果'), type='warning')
        return
    key = qtf_set2.value
    st = data["sets"].get(key)
    if not st:
        ui.notify(tr('该模型无 %s 结果') % key, type='warning')
        return
    dof = int(qtf_dof2.value)          # 界面 0 基
    gkey = "%g,%g,%d" % (0.0, 0.0, dof + 1)
    # 对角线值按浪向对逐条取（data 键含 β1,β2）
    col = {"mod": 0, "phase": 1, "re": 2, "im": 3}[qtf_qty2.value]
    xmode = qtf_x2.value
    ws = st["w"]
    n = len(ws)
    if xmode == 'hz':
        xs = sorted(w / (2 * 3.141592653589793) for w in ws)
        xlabel = 'Frequency Hz'
    elif xmode == 'rad':
        xs = sorted(ws)
        xlabel = 'Frequency rad/s'
    else:
        xs = sorted(2 * 3.141592653589793 / w for w in ws if w)
        xlabel = 'Wave Period s'

    def xy(vals_sorted, src):
        """把对角线序列按横坐标排序输出（period 模式下 ω 升序 = 周期降序）"""
        order = sorted(range(n), key=lambda i: vals_sorted[i])
        return [(vals_sorted[i], src[i]) for i in order
                if src[i] is not None and src[i] == src[i]]

    series = []
    for k, (b1, b2) in enumerate(st["betas"]):
        gk = "%g,%g,%d" % (b1, b2, dof + 1)
        g = st["data"].get(gk)
        if g is None:
            continue
        diag = [g[i][i][col] if g[i][i] is not None else None for i in range(n)]
        series.append({"name": 'β %g°/%g°' % (b1, b2), "data": xy(xs, diag)})
    if not series:
        ui.notify(tr('无对角线数据'), type='warning')
        return
    title_set = tr('差频 QTFM (ω1-ω2)') if key == 'qtfm' else tr('和频 QTFP (ω1+ω2)')
    qty_name = {'mod': '|QTF|/ρg', 'phase': 'PHASE [deg]',
                're': 'Re(QTF)/ρg', 'im': 'Im(QTF)/ρg'}[qtf_qty2.value]
    title = tr('%s 主对角线 ω1=ω2 · %s · %s (%s)') % (
        title_set, data["dofs"][dof], qty_name, P["model_name"])
    chart2.options.clear()
    chart2.options.update({
        "backgroundColor": "transparent",
        "textStyle": {"color": "#bbb"},
        "title": {"text": title, "top": 4, "left": "center",
                  "textStyle": {"color": "#ddd", "fontSize": 14}},
        "tooltip": {"trigger": "axis"},
        "legend": {"top": 30, "type": "scroll", "textStyle": {"color": "#bbb"}},
        "grid": {"top": 84, "left": 64, "right": 24, "bottom": 48},
        "xAxis": {"type": "value", "name": xlabel,
                  "nameTextStyle": {"color": "#bbb"},
                  "axisLabel": {"color": "#bbb"},
                  "axisLine": {"lineStyle": {"color": "#666"}}},
        "yAxis": {"type": "value", "name": qty_name,
                  "nameTextStyle": {"color": "#bbb"},
                  "axisLabel": {"color": "#bbb"},
                  "splitLine": {"lineStyle": {"color": "#333"}}},
        "series": [{"type": "line", "symbol": "circle", "symbolSize": 5,
                    **s} for s in series],
    })
    chart2.update()


def _qtf_axis_labels(ws, xmode):
    """按横坐标模式把 ω 网格转为显示标签；返回 (labels, 数值列表, 轴名)"""
    if xmode == 'hz':
        vals = sorted(w / (2 * 3.141592653589793) for w in ws)
        return ['%.3f' % v for v in vals], vals, 'Frequency Hz'
    if xmode == 'rad':
        return ['%.3f' % w for w in sorted(ws)], sorted(ws), 'Frequency rad/s'
    tp = sorted(2 * 3.141592653589793 / w for w in ws if w)
    return ['%.2f' % t for t in tp], tp, 'Wave Period s'


_VIRIDIS = ["#440154", "#482878", "#3e4989", "#31688e", "#26828e",
            "#1f9e89", "#35b779", "#6ece58", "#b5de2b", "#fde725"]


_QTF_COL = {'mod': 0, 'phase': 1, 're': 2, 'im': 3}
_QTF_NAME = {'mod': '|QTF|/ρg', 'phase': 'PHASE [deg]',
             're': 'Re(QTF)/ρg', 'im': 'Im(QTF)/ρg'}
# 并排两大组：左组 幅值 / 相位，右组 实部 / 虚部
_QTF_GROUPS = (('mod', 'phase'), ('re', 'im'))


def _qtf_fill_chart(chart, ws, g, qty, labels, xlabel, tick_int):
    """单张 ECharts 热力图（与 matplotlib 演示一致：|QTF|/ρg 用 log10 色标，0 值留白）"""
    from math import log10
    n = len(ws)
    col = _QTF_COL[qty]

    def _shown(v):
        """色标取值：|QTF|/ρg 取 log10（≤0 留白），其余量用原值"""
        if qty != 'mod':
            return v
        return log10(v) if v > 0 else None

    flat = [_shown(g[i][j][col]) for i in range(n) for j in range(n)
            if g[i][j] is not None and g[i][j][col] == g[i][j][col]
            and (qty != 'mod' or g[i][j][col] > 0)]
    if qty == 'phase':
        vmin, vmax = -180.0, 180.0
    elif flat:
        vmin, vmax = min(flat), max(flat)
        if vmin == vmax:
            vmin, vmax = vmin - 1, vmax + 1
    else:
        vmin, vmax = 0.0, 1.0
    pts = [[j, i, _shown(g[i][j][col]), g[i][j][col]]
           for i in range(n) for j in range(n)
           if g[i][j] is not None and g[i][j][col] == g[i][j][col]
           and (qty != 'mod' or g[i][j][col] > 0)]
    vmap_name = ('log\u2081\u2080(|QTF|/\u03c1g)' if qty == 'mod' else _QTF_NAME[qty])
    chart.options.clear()
    chart.options.update({
        "backgroundColor": "transparent",
        "textStyle": {"color": "#bbb"},
        "title": {"text": vmap_name, "top": 4, "left": "center",
                  "textStyle": {"color": "#ddd", "fontSize": 13}},
        "tooltip": {"position": "top",
                    "formatter": ("function(p){var o=p.data[3];"
                                  "return '%s<br>'+p.data[2].toFixed(3)+' (log10)<br>"
                                  "|QTF|/\u03c1g = '+o.toExponential(3);}" % xlabel)
                    if qty == 'mod' else
                    "function(p){return '%s: '+p.data[3].toExponential(3);}" % xlabel},
        "grid": {"top": 56, "left": 68, "right": 96, "bottom": 48},
        "xAxis": {"type": "category", "data": labels, "name": xlabel,
                  "nameTextStyle": {"color": "#bbb"},
                  "axisLabel": {"color": "#bbb", "interval": tick_int,
                                "fontSize": 10},
                  "splitArea": {"show": False}},
        "yAxis": {"type": "category", "data": labels, "name": xlabel,
                  "nameTextStyle": {"color": "#bbb"},
                  "axisLabel": {"color": "#bbb", "interval": tick_int}},
        "visualMap": {"min": vmin, "max": vmax, "calculable": True,
                      "dimension": 2,
                      "orient": "vertical", "right": 4, "top": "center",
                      "textStyle": {"color": "#bbb"},
                      "inRange": {"color": _VIRIDIS}},
        "series": [{"type": "heatmap", "data": pts, "progressive": 2000,
                    "name": vmap_name}],
    })
    chart.update()


def refresh_qtf(qtf_set, qtf_beta, qtf_dof, qtf_x, charts, ctx_label=None):
    data = wc.get_qtf_results(P["model_name"])
    if not data.get("ok"):
        ui.notify('；'.join(data["errors"]) or tr('无 QTF 结果'), type='warning')
        return
    key = qtf_set.value
    st = data["sets"].get(key)
    if not st:
        ui.notify(tr('该模型无 %s 结果') % key, type='warning')
        return
    beta = st["betas"][int(qtf_beta.value)] if int(qtf_beta.value) < len(st["betas"]) \
        else st["betas"][0]
    dof = int(qtf_dof.value)          # 界面 0 基（0=Surge）
    gkey = "%g,%g,%d" % (beta[0], beta[1], dof + 1)   # 文件 DOF 列为 1 基
    g = st["data"].get(gkey)
    if g is None:
        ui.notify(tr('无该 (方向, DOF) 组合的数据'), type='warning')
        return
    ws = st["w"]
    n = len(ws)
    xmode = qtf_x.value
    labels, vals, xlabel = _qtf_axis_labels(ws, xmode)
    # 分类轴按 ω 升序排列（period 模式下标签是降序周期，但格子与 ω 一一对应）
    title_set = tr('差频 QTFM (ω1-ω2)') if key == 'qtfm' else tr('和频 QTFP (ω1+ω2)')
    ctx = '%s · %s · β %g°/%g° (%s)' % (
        title_set, data["dofs"][dof], beta[0], beta[1], P["model_name"])
    if ctx_label is not None:
        ctx_label.set_text(ctx)

    tick_int = max(1, n // 10)
    for qty, chart in charts.items():          # 面板标题已含量名，先置空
        chart.set_visibility(True)
        _qtf_fill_chart(chart, ws, g, qty, labels, xlabel, tick_int)


# ---------------------------------------------------------------- 页面
@ui.page('/')
def index():
    ui.dark_mode(True)
    ui.colors(primary='#3b82f6')
    ui.add_head_html(_GRID_JS)
    # 本页的运行状态标签列表（HYST 卡 Summary 旁 + Run 卡），由页面定时器闭包持有
    status_labels = []

    # 顶栏
    mesh_holder = {}   # 3D 网格控件引用（顶栏先建、卡片后建，切换模型时回调取用）
    def _switch_lang(lang):
        i18n.set_lang(lang)
        ui.navigate.reload()

    with ui.row().classes('w-full items-center gap-3 px-4 py-2'):
        ui.label('WARP Web').classes('text-2xl font-bold')
        ui.label(tr('Nemoh BEM + QTF · Web 原型')).classes('text-sm opacity-60')
        ui.space()
        ui.toggle({'zh': '中文', 'en': 'English'}, value=i18n.LANG,
                  on_change=lambda e: _switch_lang(e.value)) \
            .props('dense unelevated').classes('text-xs')

    # 模型选择行（标题下方、参数卡上方）。
    # 模型列表每次进页面实时扫描：MODELS 若只在启动时快照，新建模型后刷新页面
    # 会因 value 不在 options 中抛 ValueError -> 500
    _models = wc.list_models()
    if P["model_name"] not in _models:
        P["model_name"] = _models[0] if _models else ''
    with ui.row().classes('w-full items-center gap-3 px-4'):
        model_sel = ui.select(_models or [''], value=P["model_name"] or '', label='Model',
                              on_change=lambda e: _on_model_change(e, mesh_holder)) \
            .classes('w-48')
        new_input = ui.input('New model name').props('dense outlined').classes('w-40')
        ui.button(tr('新建'), on_click=lambda: act_new_model(new_input, model_sel)) \
            .props('dense outline')
        ui.button(tr('删除'), on_click=lambda: act_delete_model(model_sel, mesh_holder)) \
            .props('dense outline color=negative') \
            .tooltip(tr('删除当前选中模型的文件夹（需确认）'))
        ui.label(tr('※ 网格生成（MODEL 页）仍用桌面版；本页支持 3D 网格预览 + CASE/RUN/PLOT。')) \
            .classes('text-xs opacity-50')

    with ui.row().classes('w-full items-stretch gap-3 px-4 flex-wrap'):
        # ---------------- 左列：Environment / HYST ----------------
        # 两列都用 flex-1（basis=0 等分）而非 flex-grow（basis=auto 按内容分配）：
        # 加载网格后 mesh_info 标签变长文本，flex-grow 会让右列基准宽暴涨、
        # 触发 flex-wrap 把 3D 卡挤到下一行（实测"加载后 3D 窗口移动"的根因）
        with ui.column().classes('gap-2 flex-1 min-w-0'):
            with ui.card().classes('w-full'):
                ui.label('Environment').classes('font-semibold')
                with ui.row().classes('items-center gap-2 flex-wrap'):
                    num_input('Rho kg/m³', 'rho', cls='w-32')
                    num_input('Gravity m/s²', 'gravity', cls='w-32')
                    num_input('Water depth m', 'waterdepth', cls='w-36')
                    num_input('Bodies', 'num_bodies', cls='w-24')
                wave_points_grid()
            with ui.card().classes('w-full'):
                ui.label(tr('HYST — Hydrostatics（静水力，bin/preProc.exe → bin/hydrosCal.exe）')).classes('font-semibold')
                with ui.row().classes('items-center gap-2 flex-wrap'):
                    num_input('Symm XOZ 0/1', 'hyst_xoz', '0 no; 1 yes', 'w-32')
                    num_input('Waterplane X Y', 'hyst_xoy', tr('水线面原点 X Y'), 'w-36')
                    num_input('Tcol', 'hyst_tcol', tr('水线 Z 向移动（吃水调整）'), 'w-24')
                    ui.checkbox(tr('IRR 去除不规则频率'),
                                value=(str(P.get('hyst_irr', '0')) == '1'),
                                on_change=bind_bool01('hyst_irr')) \
                        .tooltip(tr('IRR 后处理开关。mesh.cal 第 6 行固定写 2（去除不规则频率）。'
                                    '当前链路（preProc + hydrosCal）不修改 <model>.dat，'
                                    '此勾选仅保留参数记录。默认不勾选'))
                # COG 重心：X/Y/Z 分开输入，支持 Excel 粘贴（多列自动分发）
                cog_fields()
                ui.label(tr('Rho / Gravity 共用上方 Environment 值；hydrosCal 产物写入 mesh/'
                            '（Hydrostatics.dat、Inertia_hull.dat、KH.dat 等），Summary 按其结果总结静水力')) \
                    .classes('text-xs opacity-50')
                with ui.row().classes('gap-2 flex-wrap items-center'):
                    ui.button('▶ Run HYST', on_click=lambda: act_run("hyst", log)) \
                        .props('dense').classes('bg-amber-600')
                    ui.button('Summary', on_click=lambda: act_hyst_summary(hyst_out)) \
                        .props('dense outline')
                    # Summary 旁的运行状态显示（与 Run 卡状态同步，1s 轮询）
                    hyst_status = ui.label('idle').classes('text-sm font-mono opacity-70')
                    status_labels.append(hyst_status)
                hyst_out = ui.label('').classes('text-xs font-mono whitespace-pre-wrap')

        # ---------------- 右列：MODEL 3D Mesh 预览 ----------------
        with ui.column().classes('gap-2 flex-1 min-w-0'):
            with ui.card().classes('w-full'):
                ui.label(tr('MODEL — 3D Mesh（Nemoh 网格三维预览）')).classes('font-semibold')
                with ui.row().classes('items-center gap-3 flex-wrap'):
                    ui.button(tr('🔄 加载网格'), on_click=lambda: act_load_mesh(
                        mesh_info, mesh_scene, mesh_wire)) \
                        .props('dense').classes('bg-sky-600')
                    mesh_wire = ui.checkbox(tr('仅线框（不填充）'), value=True,
                                            on_change=lambda e: _mesh_reload(
                                                mesh_info, mesh_scene, mesh_wire))
                    mesh_bg = ui.select({'#ffffff': tr('白（参考图）'), '#e9edf2': tr('浅灰'),
                                         '#101826': tr('深蓝灰'), '#000000': tr('黑')},
                                        value='#ffffff', label=tr('背景颜色')) \
                        .props('dense outlined').classes('w-36')
                # grid=False：NiceGUI 场景的 grid 会自带一块 z=-0.01 的不透明地面板，
                # 而船体网格在 z<=0（吃水以下），会被完全遮住
                # 正交相机（参考 Nemoh/GMESH 出图风格，无透视畸变）：
                # size = 视口高度（m），按当前模型水平尺度定，保证模型充满画面
                def _build_scene():
                    """按当前背景选择构建场景（相机参数/背景只在元素 mounted 时读取，
                    故换背景必须重建元素）"""
                    try:
                        _b = wc.build_mesh_stl(P["model_name"])["bounds"]
                        _ext = max(abs(_b[1] - _b[0]), abs(_b[3] - _b[2]), 10.0)
                    except Exception:
                        _ext = 60.0
                    _cam = ui.scene.orthographic_camera(size=_ext / 1.35)
                    with ui.scene(width=640, height=400, grid=False, camera=_cam) \
                            .props('background-color=' + mesh_bg.value) \
                            .classes('mx-auto mesh-scene-root') as sc:
                        pass
                    return sc

                scene_wrap = ui.column().classes('items-center w-full')
                with scene_wrap:
                    mesh_scene = _build_scene()
                # 背景颜色切换：重建场景元素（新元素以新背景色初始化），
                # 已加载的网格随后重绘一次（标签/水线配色随底色自适应）
                def _mesh_bg_change(e):
                    nonlocal mesh_scene
                    _had = _mesh_loaded(mesh_scene)
                    scene_wrap.clear()
                    with scene_wrap:
                        mesh_scene = _build_scene()
                    mesh_holder['scene'] = mesh_scene
                    if _had:
                        act_load_mesh(mesh_info, mesh_scene, mesh_wire)
                mesh_bg.on('update:model-value', _mesh_bg_change)
                mesh_info = ui.label(tr('解析 db/<model>/<model>.dat 并渲染；首行对称标志自动镜像补全半模')) \
                    .classes('text-xs opacity-50')
                # 默认不自动加载；点"🔄 加载网格"按钮后，顶栏切换模型才自动刷新
                mesh_holder['scene'] = mesh_scene
                mesh_holder['info'] = mesh_info
                mesh_holder['wire'] = mesh_wire

    with ui.row().classes('w-full items-stretch gap-3 px-4 flex-wrap'):
        # ---------------- 参数列：DOF / MASS / Load Cases / Solver / Post / QTF ----------------
        with ui.column().classes('gap-2 flex-grow'):
            with ui.card().classes('w-full'):
                ui.label('Body set — Degrees of freedom').classes('font-semibold')
                with ui.row().classes('gap-x-4 flex-wrap'):
                    for key, label in DOF_KEYS:
                        bool_input(key, label)

            with ui.expansion(tr('MASS / Mechanics（Inertia + 阻尼 + 刚度）')).classes('w-full'):
                ui.label('Mass (kg):').classes('text-sm font-semibold opacity-80')
                num_input('', 'mass', cls='w-40')
                ui.label('Moment of inertia tensor (kg.m^2):') \
                    .classes('text-sm font-semibold opacity-80')
                _inertia_keys = [['ixx', 'ixy', 'ixz'],
                                 ['ixy', 'iyy', 'iyz'],
                                 ['ixz', 'iyz', 'izz']]
                _inertia_inputs = [[None] * 3 for _ in range(3)]
                _inertia_paste = _make_paste_handler(_inertia_keys, _inertia_inputs)
                _axes = ('x', 'y', 'z')
                with ui.grid(columns=4).classes(
                        'gap-0 w-fit border border-gray-600 warp-grid inertia-grid'):
                    ui.label('').classes('px-2 py-1 border-b border-gray-600')
                    for h in _axes:
                        ui.label(h).classes(
                            'px-2 py-1 text-center text-sm opacity-70 border-b border-gray-600')
                    for i in range(3):
                        ui.label(_axes[i]).classes(
                            'px-2 py-1 text-sm opacity-70 border-r border-gray-600 flex items-center')
                        for j in range(3):
                            inp = num_input('', _inertia_keys[i][j],
                                            tip=_inertia_keys[i][j].upper(),
                                            cls='w-24 text-right rounded-none warp-cell')
                            _wire_grid_cell(inp, 3, _inertia_paste)
                            _inertia_inputs[i][j] = inp
                ui.separator()
                ui.label(tr('附加阻尼 D11..D66（badd.dat，空 = 0）')).classes('text-sm opacity-70')
                ui.label(tr('鼠标从左上角拖拽框选矩阵区域 → 在 Excel 复制 → Ctrl+V 整块粘贴')) \
                    .classes('text-xs opacity-50')
                matrix_grid('d')
                ui.separator()
                ui.label(tr('附加刚度 S11..S66（km.dat，空 = 0）')).classes('text-sm opacity-70')
                ui.label(tr('鼠标从左上角拖拽框选矩阵区域 → 在 Excel 复制 → Ctrl+V 整块粘贴')) \
                    .classes('text-xs opacity-50')
                matrix_grid('s')

            with ui.expansion(tr('Load Cases（Nemoh.cal 波浪频率/浪向）')).classes('w-full'):
                with ui.row().classes('items-center gap-2 flex-wrap'):
                    ui.label('Freq type').classes('text-sm opacity-70')
                    ui.toggle({1: 'rad/s', 2: 'Hz', 3: tr('周期 s')},
                              value=(int(P['freq_type'])
                                     if str(P['freq_type']) in ('1', '2', '3') else 1),
                              on_change=bind_str('freq_type'))
                    num_input('Min freq', 'min_wf', 'Min. Wave Freq. rad/s', 'w-28')
                    num_input('Max freq', 'max_wf', 'Max. Wave Freq. rad/s', 'w-28')
                    num_input('N freq', 'num_wf', 'Numbers Wave Freq.', 'w-24')
                with ui.row().classes('items-center gap-2 flex-wrap'):
                    num_input('Min dirc °', 'min_wd', cls='w-28')
                    num_input('Max dirc °', 'max_wd', cls='w-28')
                    num_input('N dirc', 'num_wd', cls='w-24')

            with ui.expansion('Solver（input_solver.txt）').classes('w-full'):
                with ui.row().classes('items-center gap-2 flex-wrap'):
                    num_input('GQ', 'gq', 'N^2 GQ Nodes, N(1,4)', 'w-24')
                    num_input('eps_zmin', 'eps', 'zmin=eps_zmin*body_diameter', 'w-32')
                    num_input('Solver', 'solver',
                              tr('0 GAUSS ELIM.; 1 LU DECOMP.（勾选 GMRES 时忽略，自动写 2）'), 'w-24')
                with ui.row().classes('items-center gap-2 flex-wrap'):
                    def _gmres_toggle(v):
                        (g_r.enable if v else g_r.disable)()
                        (g_t.enable if v else g_t.disable)()
                        (g_m.enable if v else g_m.disable)()

                    def _gmres_change(e):
                        P['use_gmres'] = '1' if e.value else '0'
                        _gmres_toggle(bool(e.value))
                    gmres_chk = ui.checkbox(
                        'GMRES', value=(str(P.get('use_gmres', '0')) == '1'),
                        on_change=_gmres_change) \
                        .tooltip(tr('勾选后线性方程组改用 GMRES 迭代法求解（solver 行写 2），'
                                    '适合大规模网格；不勾选时用上方 Solver 选项'
                                    '（0 高斯消元 / 1 LU 分解）'))
                    g_r = num_input('Restart', 'gmres_restart', tr('GMRES 重启参数'), 'w-20')
                    g_t = num_input('Rel Tol', 'gmres_tol', tr('GMRES 相对容差'), 'w-24')
                    g_m = num_input('Max iter', 'gmres_maxit', tr('GMRES 最大迭代次数'), 'w-24')
                    _gmres_toggle(gmres_chk.value)

            with ui.expansion('Post Set').classes('w-full'):
                with ui.row().classes('items-center gap-2 flex-wrap'):
                    num_input('IRF a b c', 'irf', 'IRF calculation: time step and duration', 'w-36')
                    num_input('Kochin a b c', 'kochin', 'Suggest: 361 0 360', 'w-36')
                with ui.row().classes('items-center gap-2 flex-wrap'):
                    num_input('Free surface a b c d', 'free_surface', cls='w-44')
                    ui.label('Out freq type').classes('text-sm opacity-70')
                    ui.toggle({1: 'rad/s', 2: 'Hz', 3: tr('周期 s')},
                              value=(int(P['out_freq_type'])
                                     if str(P['out_freq_type']) in ('1', '2', '3') else 1),
                              on_change=bind_str('out_freq_type'))
                with ui.row().classes('items-center gap-4'):
                    bool_input("show_pressure", "Show pressure")
                    bool_input("calc_rao", "Calculate RAO")

            with ui.expansion('QTF Set').classes('w-full'):
                qtf_refs = {}
                ui.checkbox(tr('启用 QTF 计算'), value=bool(P['qtf']),
                            on_change=lambda e: (P.__setitem__('qtf', e.value),
                                                 _sync_qtf(qtf_refs)))
                with ui.column().classes('gap-2 w-full'):
                    with ui.row().classes('items-center gap-2 flex-wrap'):
                        ui.label('QTF freq set').classes('text-sm opacity-70')
                        qtf_refs['qtff'] = qtf_freq_fields()
                        ui.label(tr('浪向组合')).classes('text-sm opacity-70')
                        qtf_refs['qtfd'] = ui.toggle(
                            {0: tr('单向 β1=β2'), 1: tr('双向 全组合')},
                            value=int(P['qtfd'] or 0), on_change=bind_str('qtfd'))
                    with ui.row().classes('items-center gap-2 flex-wrap'):
                        ui.label(tr('Contrib（计算内容）')).classes('text-sm opacity-70')
                        qtf_refs['qtfc'] = ui.toggle(
                            {1: tr('仅 DUOK（近场二次项）'), 2: tr('DUOK+HASBO（+势项）'),
                             3: tr('完整 QTF（+自由面积分）')},
                            value=(int(P['qtfc']) if str(P['qtfc']) in ('1', '2', '3') else None),
                            on_change=lambda e: _on_qtf_contrib(e, qtf_refs))
                    with ui.row().classes('items-center gap-2 flex-wrap'):
                        qtf_refs['fsmf'] = num_input('FS meshfile', 'fsmf',
                                                     tr('仅 Contrib=3：自由面网格文件'), 'w-40')
                        qtf_refs['fsmf_qtf'] = num_input('FS QTF params', 'fsmf_qtf',
                                                         tr('Re Nre NBessel（Bessel 默认 30）'), 'w-40')
                    qtf_refs['hys_term'] = ui.checkbox(
                        tr('计入二阶运动水静力恢复项 −[K]ξ̃⁽²⁾（含 z_G 耦合）'),
                        value=P['hys_term'] == '1', on_change=bind_bool01('hys_term'))
                    with ui.row().classes('items-center gap-2'):
                        ui.label(tr('输出频率')).classes('text-sm opacity-70')
                        qtf_refs['freq_qtft'] = ui.toggle(
                            {1: 'rad/s', 2: 'Hz', 3: tr('周期 s')},
                            value=(int(P['freq_qtft']) if str(P['freq_qtft']) in ('1', '2', '3') else None),
                            on_change=bind_str('freq_qtft'))
                    with ui.row().classes('items-center gap-4 flex-wrap qtfpost-row'):
                        ui.label(tr('QTFpostproc 汇总开关')).classes('text-sm opacity-70')
                        qtf_refs['duko'] = ui.checkbox(
                            'DUOK', value=P['duko'] == '1', on_change=bind_bool01('duko')) \
                            .tooltip(tr('近场二次项（可直接压力积分，无需二阶势）'))
                        qtf_refs['hasbo'] = ui.checkbox(
                            'HASBO', value=P['hasbo'] == '1', on_change=bind_bool01('hasbo')) \
                            .tooltip(tr('势项·船体/水线（间接法）'))
                        qtf_refs['hasfs'] = ui.checkbox(
                            'HASFS+ASYMP', value=P['hasfs_symp'] == '1', on_change=bind_bool01('hasfs_symp')) \
                            .tooltip(tr('自由面积分：有限域 + 半无限域渐近（间接法）'))
                _sync_qtf(qtf_refs)

    # ---------------- 全宽：Run 动作 + 实时日志 ----------------
    with ui.card().classes('w-full mx-4 my-1'):
        status_label = ui.label('idle').classes('text-sm font-mono opacity-70')
        status_labels.append(status_label)
        with ui.row().classes('gap-2 flex-wrap'):
            ui.button('Save .cal', on_click=lambda: act_save_cal(log)) \
                .props('dense outline')
            ui.button('Save Mechanics', on_click=lambda: act_save_mech(log)) \
                .props('dense outline')
            ui.button('▶ Run BEM', on_click=lambda: act_run("bem", log)) \
                .props('dense').classes('bg-green-600')
            ui.button('▶ Run QTF', on_click=lambda: act_run("qtf", log)) \
                .props('dense').classes('bg-purple-600')
        ui.label(tr('Run 前旧 results/QTFPreprocOut 等目录自动改名为 *_bak_<时间戳>，不会删除任何历史结果。')) \
            .classes('text-xs opacity-50')
        log = ui.log(max_lines=800).classes('w-full h-72')

    # ---------------- 结果曲线 ----------------
    def _sync_res_controls():
        """按结果类型启用/禁用：附加质量/辐射阻尼用 DOF j（无方向意义）；
        波浪力/RAO/相位用方向（与 DOF j 无关）"""
        is_matrix = res_type.value in ('addedmass', 'damping')
        if is_matrix:
            dof_j.enable()
            direc_sel.disable()
        else:
            dof_j.disable()
            direc_sel.enable()

    with ui.card().classes('w-full mx-4 my-2'):
        ui.label(tr('Results（与桌面版 PLOT 页同口径）')).classes('font-semibold')
        with ui.row().classes('items-center gap-2 flex-wrap'):
            res_type = ui.select({k: v for k, v in RESULT_TYPES},
                                 value='waveforce', label=tr('类型'),
                                 on_change=lambda e: _sync_res_controls()) \
                .props('dense outlined').classes('w-44')
            dof_i = ui.select({0: 'Surge', 1: 'Sway', 2: 'Heave',
                               3: 'Roll', 4: 'Pitch', 5: 'Yaw'},
                              value=0, label='DOF i') \
                .props('dense outlined').classes('w-28')
            dof_j = ui.select({0: 'Surge', 1: 'Sway', 2: 'Heave',
                               3: 'Roll', 4: 'Pitch', 5: 'Yaw'},
                              value=0, label=tr('DOF j（幅值/阻尼用）')) \
                .props('dense outlined').classes('w-44')
            direc_sel = ui.select({-1: tr('所有方向'), 0: 'dir[0]'}, value=-1,
                                  label=tr('方向')) \
                .props('dense outlined').classes('w-32')
            x_sel = ui.select({'period': 'Period (s)', 'hz': 'Frequency (Hz)',
                               'rad': 'Frequency (rad/s)'}, value='period',
                              label=tr('横坐标'),
                              on_change=lambda e: refresh_results(
                                  res_type, dof_i, dof_j, direc_sel, chart, x_sel)) \
                .props('dense outlined').classes('w-40')
            ui.button(tr('刷新结果'), on_click=lambda: refresh_results(
                res_type, dof_i, dof_j, direc_sel, chart, x_sel)).props('dense')
            ui.button(tr('加载方向列表'), on_click=lambda: load_directions(direc_sel)) \
                .props('dense outline')
        _sync_res_controls()   # 初始状态：waveforce -> DOF j 禁用、方向可用
        chart = ui.echart({"backgroundColor": "transparent",
                           "textStyle": {"color": "#bbb"},
                           "xAxis": {"type": "value"},
                           "yAxis": {"type": "value"},
                           "series": []}).classes('w-full h-96')

    # ---------------- QTF 结果（等高线） ----------------
    with ui.card().classes('w-full mx-4 my-2'):
        ui.label(tr('QTF Results（等高线，数据源 results/QTF/OUT_QTF*.dat，值已按 ρg 归一化）')) \
            .classes('font-semibold')
        ui.label(tr('四联显示：左组 幅值 / 相位，右组 实部 / 虚部（|QTF|/ρg 取 log10 色标）')) \
            .classes('text-xs opacity-70')
        with ui.row().classes('items-center gap-2 flex-wrap'):
            qtf_set = ui.select({'qtfm': tr('差频 QTFM（ω1−ω2，慢漂）'),
                                 'qtfp': tr('和频 QTFP（ω1+ω2）')},
                                value='qtfm', label=tr('QTF 类型')) \
                .props('dense outlined').classes('w-56')
            qtf_beta = ui.select({0: tr('β（点"加载QTF选项"填充）')}, value=0,
                                 label=tr('波浪方向对')) \
                .props('dense outlined').classes('w-44')
            qtf_dof = ui.select({i: n for i, n in enumerate(
                ['Surge', 'Sway', 'Heave', 'Roll', 'Pitch', 'Yaw'])},
                value=2, label=tr('自由度 DOF')) \
                .props('dense outlined').classes('w-36')
            qtf_x = ui.select({'period': 'Period (s)', 'hz': 'Frequency (Hz)',
                               'rad': 'Frequency (rad/s)'}, value='rad',
                              label=tr('坐标单位')) \
                .props('dense outlined').classes('w-40')
            ui.button(tr('加载QTF选项'), on_click=lambda: (
                load_qtf_options(qtf_set, qtf_beta, qtf_dof),
                _qtf_refresh(), _qtf_diag_refresh())).props('dense outline')
        qtf_ctx = ui.label('').classes('text-xs opacity-80')
        # 集中刷新：任一 QTF 选择变化即重绘（.on 的回调需接受 *args）
        def _qtf_refresh(*_):
            refresh_qtf(qtf_set, qtf_beta, qtf_dof, qtf_x,
                        qtf_charts, qtf_ctx)
        for _c in (qtf_set, qtf_beta, qtf_dof, qtf_x):
            _c.on('update:model-value', _qtf_refresh)
        qtf_charts = {}
        with ui.row().classes('w-full items-start justify-center gap-6 no-wrap'):
            for _grp in _QTF_GROUPS:      # 左组 幅值/相位，右组 Re/Im
                with ui.column().classes('gap-2 items-center'):
                    for _q in _grp:
                        qtf_charts[_q] = ui.echart({
                            "backgroundColor": "transparent",
                            "textStyle": {"color": "#bbb"},
                            "xAxis": {"type": "category"},
                            "yAxis": {"type": "category"},
                            "series": []}) \
                            .classes('w-[476px] max-w-full h-[26rem]')
        # 不自动加载：需手动点"加载QTF选项"或切换选择才绘图

    # ---------------- QTF 主对角线二阶载荷（Results 样式，多浪向对比） ----------------
    with ui.card().classes('w-full mx-4 my-2'):
        ui.label(tr('QTF Diagonal — 主对角线二阶载荷（ω1=ω2 等同平均漂移力；'
                    '全部浪向对同图对比，样式同 Results）')).classes('font-semibold')
        with ui.row().classes('items-center gap-2 flex-wrap'):
            qtf_set2 = ui.select({'qtfm': tr('差频 QTFM（ω1−ω2，慢漂）'),
                                  'qtfp': tr('和频 QTFP（ω1+ω2）')},
                                 value='qtfm', label=tr('QTF 类型')) \
                .props('dense outlined').classes('w-56')
            qtf_dof2 = ui.select({i: n for i, n in enumerate(
                ['Surge', 'Sway', 'Heave', 'Roll', 'Pitch', 'Yaw'])},
                value=0, label=tr('自由度 DOF')) \
                .props('dense outlined').classes('w-36')
            qtf_qty2 = ui.select({'mod': tr('|QTF|/ρg（模）'), 're': 'Re/ρg',
                                  'im': 'Im/ρg', 'phase': tr('相位 deg')},
                                 value='mod', label=tr('量')) \
                .props('dense outlined').classes('w-40')
            qtf_x2 = ui.select({'period': 'Period (s)', 'hz': 'Frequency (Hz)',
                                'rad': 'Frequency (rad/s)'}, value='period',
                               label=tr('横坐标')) \
                .props('dense outlined').classes('w-40')
        def _qtf_diag_refresh(*_):
            refresh_qtf_diag(qtf_set2, qtf_dof2, qtf_qty2, qtf_x2, qtf_diag_chart)
        for _c in (qtf_set2, qtf_dof2, qtf_qty2, qtf_x2):
            _c.on('update:model-value', _qtf_diag_refresh)
        qtf_diag_chart = ui.echart({
            "backgroundColor": "transparent",
            "textStyle": {"color": "#bbb"},
            "xAxis": {"type": "value"},
            "yAxis": {"type": "value"},
            "series": []}).classes('w-full h-96')
        # 不自动加载：需切换上方选择或点"加载QTF选项"后手动触发

    # 运行状态轮询
    ui.timer(1.0, lambda: poll_run(log, status_labels))


def load_directions(direc_sel):
    data = wc.get_results(P["model_name"])
    if not data.get("ok"):
        ui.notify('；'.join(data["errors"]) or tr('无结果'), type='warning')
        return
    dirs = data["axes"]["direc_deg"]
    cur = direc_sel.value
    direc_sel.options = {-1: tr('所有方向'),
                         **{i: ('Wave %.0f°' % d) for i, d in enumerate(dirs)}}
    direc_sel.value = cur if cur in direc_sel.options else -1
    direc_sel.update()
    ui.notify(tr('已加载 %d 个浪向（可选单个方向或所有方向）') % len(dirs))


if __name__ in {"__main__", "__mp_main__"}:
    import sys
    # 打包版（PyInstaller frozen）双击 exe、或 run.bat 设置 WARP_OPEN_BROWSER=1 时，
    # 服务就绪后自动打开浏览器；直接用 python warp_web.py 调试时不弹窗
    _open_browser = bool(getattr(sys, 'frozen', False)) \
        or os.environ.get("WARP_OPEN_BROWSER") == "1"
    ui.run(host="127.0.0.1", port=8300, title="WARP Web", reload=False,
           show=_open_browser)

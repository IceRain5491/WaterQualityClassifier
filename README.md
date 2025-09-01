# WaterQualityClassifier

面向地表水水质监测/自动站数据的一套**水质分类与上色**工具集。  
支持按站点类型（河流/湖库）差异化指标阈值、批量表格处理，以及将分类结果**导出为带颜色的 Excel**，用于快速复核与出表。

> 典型场景：原始监测数据经过筛选后，调用分类器输出“类别/判定结果 + 配色”，一键导出 `.xlsx`。

---

## ✨ Features

- **函数式站点配置**：仅通过 API 调用在运行期注入站点名单（如：`set_lake_stations` / `add_lake_station` / `remove_lake_station`）。仓库不提供、不读取任何外部 CSV/模板。  
- **站点类型识别**：可按名单识别湖库站点；未命中名单默认按河流逻辑处理。  
- **模糊匹配**：`is_lake_station(..., fuzzy=True)` 可容忍常见的前后缀/空格差异。  
- **一键导出**：与 GUI/脚本配合，导出当前可见表格为 Excel，并按分类结果为单元格着色。  
- **轻依赖、易集成**：纯 Python 实现，便于在你的数据清洗/报表脚本里直接调用。

---

## 🧱 Repo Structure（简要）

```
WaterQualityClassifier/
├─ WaterQualityClassifier/
│  ├─ __init__.py
│  ├─ classifiers.py          # 核心分类/站点类型逻辑（含湖库站点管理、模糊匹配等）
│  ├─ constants.py            # 常量/颜色映射等
│  └─ utils.py                # 工具函数
├─ pyproject.toml / project.toml（视仓库实际情况）
└─ README.md
```

---

## 🚀 Quick Start

### 1) 环境要求
- Python 3.10+（推荐 3.10 或 3.11）
- 常用依赖：`pandas`、`openpyxl`（导出 Excel 用）、（可选）`PySide6`（若使用 GUI）

### 2) 安装依赖
- 若仓库提供 `requirements.txt` / `pyproject.toml`：  
  ```bash
  pip install -r requirements.txt
  # 或
  pip install .
  ```
- 或手动安装最小依赖：
  ```bash
  pip install pandas openpyxl
  # 如需 GUI：
  pip install PySide6
  ```

### 3) 作为库使用（示例，匿名化）
```python
from WaterQualityClassifier.classifiers import WaterQualityClassifier

wqc = WaterQualityClassifier()

# 仅通过函数注入湖库站点（匿名占位示例；请替换为你的真实名单）
wqc.set_lake_stations([
    "湖库站点A", "湖库站点B", "湖库站点C"
])

# 可选：增删单个站点
wqc.add_lake_station("湖库站点D")
wqc.remove_lake_station("湖库站点D")

# 判定是否湖库站点（默认启用模糊匹配）
is_lake = wqc.is_lake_station("湖库站点A")
print(is_lake)  # True/False

# —— 与你的数据处理/导出流程集成 ——
# 典型做法：先得到筛选后的 DataFrame（df_filtered），
# 调用分类器获取判定与颜色，然后按列/单元格上色导出到 .xlsx
# （导出逻辑通常在你的 GUI/脚本里实现）
```

> 本仓库不包含任何站点名单文件，也不提供任何 CSV/模板；站名仅能通过调用函数在运行期注入。

---

## 🎨 关于颜色上色

- 分类器会根据**站点类型**与**指标阈值**给出**分类名称/级别**，并映射到固定颜色（例如“Ⅰ～Ⅴ类、劣Ⅴ类”的色卡）。  
- 你的 GUI/导出函数可用该映射把单元格背景或字体上色，便于快速查验与报表展示。  
- 若需自定义颜色或阈值，可在 `constants.py` / 配置层面扩展（保持与项目现有结构一致）。

---

## 🧪 与 GUI 的配合（示例流程）

1. 在 GUI 中完成筛选 → 得到 `df_filtered`。  
2. 遍历 `df_filtered` 的相关列/指标，使用分类器计算**判定结果**与**颜色**。  
3. 使用 `openpyxl` 写出 `.xlsx` 并对单元格着色。  
4. 文件命名可包含时间与筛选条件，便于留档。

---

## ❓FAQ

**Q1：为什么仓库里没有任何站点名单或模板？**  
- 为了隐私与可控性；本项目仅支持**运行期通过函数注入**站名，避免任何敏感名单出现在仓库。

**Q2：如何在不同运行环境复用同一份站名名单？**  
- 由你在**外部私有存储**（如自有配置文件/数据库/密钥管理）保存名单，并在程序启动时读取后调用 `set_lake_stations([...])` 注入。该外部存储不属于本仓库范畴。

**Q3：能不能只把“当下可见的筛选结果”导出成 Excel 并带颜色？**  
- 可以。项目已提供对应的 GUI/脚本逻辑；`WaterQualityClassifier` 提供判定与色彩映射。

---

## 🤝 Contributing

- 欢迎提交 PR/Issue。  
- 建议遵守以下约定：
  - 提交信息简明规范（feat/fix/docs/chore 等）。
  - 新增/修改阈值或色卡，附上说明与示例截图。
  - 与 GUI 交互的改动，尽量提供最小复现数据或步骤。

---

## 📄 License

TBD（可按需选择：MIT / Apache-2.0 / GPL-3.0 / 内部使用）。

---

---

## 🧩 最小 GUI 导出示例（PySide6）

> 载入 CSV/XLSX → 选择“站点列”（可选）→ 自动识别 pH/溶解氧/CODMn/氨氮/总磷 → 依据分类结果为单元格着色 → 导出为上色的 `.xlsx`。

依赖安装：
```bash
pip install PySide6 pandas openpyxl
```

运行：
```bash
python min_gui_export.py
```

示例代码（可直接保存为 `min_gui_export.py` 运行）：
```python
# -*- coding: utf-8 -*-
import sys, os
import pandas as pd
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox, QComboBox
from openpyxl.styles import PatternFill

# 与仓库内结构一致的导入
from WaterQualityClassifier.classifiers import WaterQualityClassifier

class MiniExportGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("最小水质表导出（上色示例）")
        self.resize(520, 160)
        self.df = None
        self.wqc = WaterQualityClassifier(water_type="河流")

        # 仅通过函数注入湖库站点（占位示例；运行时替换为你的真实名单）
        self.wqc.set_lake_stations(["湖库站点A", "湖库站点B"])

        btn_load = QPushButton("加载 CSV/XLSX")
        btn_load.clicked.connect(self.load_file)

        self.station_col = QComboBox()
        self.station_col.setEditable(False)
        self.station_col.addItem("(无站点列)")

        btn_export = QPushButton("导出上色 Excel")
        btn_export.clicked.connect(self.export_excel)

        top = QHBoxLayout()
        top.addWidget(btn_load)
        top.addStretch(1)
        top.addWidget(QLabel("站点列:"))
        top.addWidget(self.station_col)
        top.addWidget(btn_export)

        lay = QVBoxLayout(self)
        lay.addLayout(top)
        self.msg = QLabel("未加载数据")
        lay.addWidget(self.msg)

    def load_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "表格 (*.xlsx *.xls *.csv)")
        if not path:
            return
        try:
            if path.lower().endswith((".xlsx", ".xls")):
                self.df = pd.read_excel(path)
            else:
                self.df = pd.read_csv(path, encoding="utf-8")
        except Exception as e:
            QMessageBox.critical(self, "读取失败", str(e))
            return

        self.station_col.clear()
        self.station_col.addItem("(无站点列)")
        for c in self.df.columns:
            s = str(c)
            if any(k in s for k in ["站", "断面", "点", "断面名称", "站点", "站名"]):
                self.station_col.addItem(s)

        nrows, ncols = self.df.shape
        self.msg.setText(f"已加载：{os.path.basename(path)} | {nrows} 行 × {ncols} 列")

    def export_excel(self):
        if self.df is None or self.df.empty:
            QMessageBox.warning(self, "提示", "请先加载数据表。")
            return

        path, _ = QFileDialog.getSaveFileName(self, "保存为", "导出.xlsx", "Excel 文件 (*.xlsx)")
        if not path:
            return

        dff = self.df.copy()
        station_col_name = None if self.station_col.currentIndex() <= 0 else self.station_col.currentText()

        # 自动识别常见指标列
        metric_cols = []
        for c in dff.columns:
            mid = WaterQualityClassifier.recognized_metric_id(str(c))
            if mid is not None:
                metric_cols.append((c, mid))

        if not metric_cols:
            QMessageBox.warning(self, "提示", "未识别到可用指标列（pH/溶解氧/CODMn/氨氮/总磷）。")
            return

        try:
            # 直接用 openpyxl 写入颜色：先写 DataFrame，再逐格上色
            from openpyxl import Workbook
            wb = Workbook()
            ws = wb.active
            ws.title = "Sheet1"

            # 写表头
            ws.append(list(dff.columns))

            # 写数据 + 上色
            for r_idx, row in dff.iterrows():
                ws.append(list(row.values))
                station_name = str(row[station_col_name]) if station_col_name else None

                for col_name, metric_id in metric_cols:
                    val = row[col_name]
                    if metric_id == "总磷":
                        cat = self.wqc.classify_total_phosphorus_by_type(val, station_name=station_name)
                    else:
                        cat = self.wqc.classify_value(metric_id, val)
                    hexcolor = WaterQualityClassifier.CATEGORY_COLORS.get(cat, "#FFFFFF")
                    cell = ws.cell(row=r_idx+2, column=list(dff.columns).index(col_name)+1)
                    cell.fill = PatternFill(start_color=hexcolor.lstrip("#"),
                                            end_color=hexcolor.lstrip("#"),
                                            fill_type="solid")

            wb.save(path)
            QMessageBox.information(self, "完成", f"已导出：{path}")
        except Exception as e:
            QMessageBox.critical(self, "导出失败", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MiniExportGUI()
    w.show()
    sys.exit(app.exec())
```


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水质因子标准分类表GUI（修正版）
- 修正 pH 与 CODCr 显示逻辑（pH: I~V = 6.0–9.0；劣V = <6 或 >9；CODCr: I/II=≤15，III=≤20，IV=≤30，V=≤40，劣V=>40）
- 统一“劣V类=V类的补集”
- 表格自适应铺满、选中行列更易读
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QHeaderView,
    QAbstractItemView, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

from classifiers import WaterQualityClassifier


CATEGORIES = ["I类", "II类", "III类", "IV类", "V类", "劣V类"]

# 指标清单（展示名, 逻辑ID, 水体类型）
METRICS = [
    ("pH值", "pH", "河流"),
    ("溶解氧", "溶解氧", "河流"),
    ("高锰酸盐指数", "CODMn", "河流"),
    ("化学需氧量", "CODCr", "河流"),
    ("氨氮", "氨氮", "河流"),
    ("总磷（河流）", "总磷", "河流"),
    ("总磷（湖库）", "总磷", "湖库"),
    ("总氮", "总氮", "河流"),
    ("生化需氧量", "生化需氧量", "河流"),
]


class WaterQualityStandardsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.classifier = WaterQualityClassifier()
        self.init_ui()
        self.populate_table()

    def init_ui(self):
        self.setWindowTitle("水质因子标准分类表")
        self.resize(1100, 650)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("水质因子标准分类表")
        f = QFont()
        f.setPointSize(16)
        f.setBold(True)
        title.setFont(f)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectItems)  # 单元格选中，行列高亮更直观
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setWordWrap(False)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                background-color: white;
                alternate-background-color: #f8f8f8;
            }
            QTableWidget::item {
                padding: 6px; /* 适度内边距，避免挤占空间 */
                border: 1px solid #dcdcdc;
            }
            QTableWidget::item:selected {
                background-color: #2d7dff;
                color: white;
            }
            QHeaderView::section {
                background-color: #e9e9e9;
                padding: 8px;
                border: 1px solid #d0d0d0;
                font-weight: bold;
            }
        """)
        # 列头拉伸策略
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        layout.addWidget(self.table)

        # 点击自动把目标滚动到居中，避免“看不全”的体验
        self.table.cellClicked.connect(self._center_on_cell)

        btnrow = QHBoxLayout()
        btnrow.addStretch()
        close_btn = QPushButton("关闭")
        close_btn.setFixedSize(100, 36)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; color: white; border: none;
                border-radius: 6px; font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:pressed { background-color: #3d8b40; }
        """)
        close_btn.clicked.connect(self.close)
        btnrow.addWidget(close_btn)
        layout.addLayout(btnrow)

    def _center_on_cell(self, r, c):
        item = self.table.item(r, c)
        if item:
            self.table.scrollToItem(item, QAbstractItemView.PositionAtCenter)

    # —— 核心：将“类别 → 文本”映射统一在一处（特别处理 pH / CODCr），其余走通用规则 —— #
    def _cell_text_for(self, metric_id: str, water_type: str, category: str,
                       boundary_dict: dict[str, float]) -> str:
        mid = metric_id

        # pH：I~V 统一 6.0–9.0；劣V = <6.0 或 >9.0
        if mid == "pH":
            if category in ("I类", "II类", "III类", "IV类", "V类"):
                return "6.0–9.0"
            else:
                return "<6.0 或 >9.0"

        # CODCr：I、II=≤15；III=≤20；IV=≤30；V=≤40；劣V=>40
        if mid == "CODCr":
            mapping = {
                "I类": 15, "II类": 15,
                "III类": 20, "IV类": 30, "V类": 40
            }
            if category in mapping:
                return f"≤{mapping[category]}"
            else:
                return f">{mapping['V类']}"

        # 其它指标：I~V 显示“≤阈值”；劣V = “>V类阈值”
        if category == "劣V类":
            v_val = boundary_dict.get("V类")
            if v_val is not None:
                return f">{v_val}"
            # 兜底：若某指标没有V类（极少见），给个通用文案
            return ">V类标准"
        else:
            val = boundary_dict.get(category)
            return f"≤{val}" if val is not None else "-"

    def populate_table(self):
        # 建表头
        self.table.setRowCount(len(METRICS))
        self.table.setColumnCount(len(CATEGORIES) + 1)  # +1: 指标名
        headers = ["指标名称"] + CATEGORIES
        self.table.setHorizontalHeaderLabels(headers)

        # 每个指标逐行填充
        for r, (mname, mid, wtype) in enumerate(METRICS):
            # 第一列：指标名
            name_item = QTableWidgetItem(mname)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            name_item.setBackground(QColor("#f5f5f5"))
            name_item.setFont(QFont("Microsoft YaHei", 9, QFont.Bold))
            self.table.setItem(r, 0, name_item)

            # 取得“视觉边界”→ 转成 {类别: 值}，注意：对 pH / CODCr 我们只把它们当“参考”
            # 这里优先用 metric_boundaries 来拿统一阈值，再由 _cell_text_for 做展示映射
            bounds = self.classifier.metric_boundaries(mid, wtype)
            # 规范化标签名到 “*类”
            bdict = {}
            for label, v in bounds:
                lab = str(label)
                if lab in ("I/II", "IⅡ", "I II"):
                    bdict["I类"] = v
                    bdict["II类"] = v
                elif lab.endswith("类"):
                    bdict[lab] = v
                elif lab in ("I", "II", "III", "IV", "V"):
                    bdict[f"{lab}类"] = v
                # pH 下限/上限在 _cell_text_for 里直接忽略，用固定文案

            # 填各类别
            for c, cat in enumerate(CATEGORIES, start=1):
                text = self._cell_text_for(mid, wtype, cat, bdict)
                it = QTableWidgetItem(text)
                it.setFlags(it.flags() & ~Qt.ItemIsEditable)
                it.setTextAlignment(Qt.AlignCenter)

                # 着色（沿用你的配色）
                if cat == "I类":
                    it.setBackground(QColor("#CFFFFF"))
                elif cat == "II类":
                    it.setBackground(QColor("#8FFFFF"))
                elif cat == "III类":
                    it.setBackground(QColor("#7FFF7F"))
                elif cat == "IV类":
                    it.setBackground(QColor("#FFFF6F"))
                elif cat == "V类":
                    it.setBackground(QColor("#FFC000"))
                else:  # 劣V类
                    it.setBackground(QColor("#FF0000"))
                    it.setForeground(QColor("#FFFFFF"))

                self.table.setItem(r, c, it)

        # 列宽拉伸：第0列自适应，其余拉伸铺满
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for col in range(1, self.table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.Stretch)

        # 行高稍微大一点，更易读
        self.table.verticalHeader().setDefaultSectionSize(40)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("水质因子标准分类表")
    app.setApplicationVersion("1.1")
    app.setOrganizationName("Water Quality Classifier")

    w = WaterQualityStandardsWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

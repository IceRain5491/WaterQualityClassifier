# WaterQualityClassifier.py（重构示例）
from __future__ import annotations
from typing import List, Tuple


class WaterQualityClassifier:
    # 类属性：类别排序映射
    CATEGORY_ORDER = {
        "合格": 1,
        "I类": 1,
        "II类": 2,
        "III类": 3,
        "IV类": 4,
        "V类": 5,
        "劣V类": 6
    }

    ORDER_TO_CATEGORY = {
        1: "I类",
        2: "II类",
        3: "III类",
        4: "IV类",
        5: "V类",
        6: "劣V类",
    }

    # —— 可视化配色（供 UI 使用）——
    CATEGORY_COLORS = {
        "合格": "#CFFFFF",
        "I类":   "#CFFFFF",
        "II类":  "#8FFFFF",
        "III类": "#7FFF7F",
        "IV类":  "#FFFF6F",
        "V类":   "#FFC000",
        "劣V类": "#FF0000",
        "pH":    "#FF0000",
    }

    NORMALIZE_CATEGORY = {
        "合格": "I类",
        "合格类": "I类",
        "I类": "I类", "II类":"II类", "III类":"III类",
        "IV类":"IV类","V类":"V类","劣V类":"劣V类"
    }

    def __init__(self, water_type: str = "河流"):
        """
        water_type: "河流" 或 "湖库"，决定总磷的判定标准
        """
        self.water_type = water_type

    # ----------------- 分类方法（按指标） -----------------
    @staticmethod
    def classify_pH(value: float | str) -> str:
        try:
            n = float(value)
        except Exception:
            return ""
        return "I类" if 6.0 <= n <= 9.0 else "劣V类"

    @staticmethod
    def classify_dissolved_oxygen(value: float | str) -> str:
        try:
            n = float(value)
        except Exception:
            return ""
        if n >= 7.5: return "I类"
        if n >= 6.0: return "II类"
        if n >= 5.0: return "III类"
        if n >= 3.0: return "IV类"
        if n >= 2.0: return "V类"
        return "劣V类"

    @staticmethod
    def classify_permanganate_index(value: float | str) -> str:
        try:
            n = float(value)
        except Exception:
            return ""
        if n <= 2.0: return "I类"
        if n <= 4.0: return "II类"
        if n <= 6.0: return "III类"
        if n <= 10.0: return "IV类"
        if n <= 15.0: return "V类"
        return "劣V类"

    @staticmethod
    def classify_ammonia_nitrogen(value: float | str) -> str:
        try:
            n = float(value)
        except Exception:
            return ""
        if n <= 0.15: return "I类"
        if n <= 0.5:  return "II类"
        if n <= 1.0:  return "III类"
        if n <= 1.5:  return "IV类"
        if n <= 2.0:  return "V类"
        return "劣V类"

    @staticmethod
    def classify_total_phosphorus(value: float | str) -> str:
        try:
            n = float(value)
        except Exception:
            return ""
        # 默认河流标准（可由实例方法按类型切换）
        if n <= 0.02: return "I类"
        if n <= 0.1:  return "II类"
        if n <= 0.2:  return "III类"
        if n <= 0.3:  return "IV类"
        if n <= 0.4:  return "V类"
        return "劣V类"

    @staticmethod
    def classify_total_phosphorus_lake(value: float | str) -> str:
        try:
            n = float(value)
        except Exception:
            return ""
        if n <= 0.015: return "I类"
        if n <= 0.025: return "II类"
        if n <= 0.05:  return "III类"
        if n <= 0.1:   return "IV类"
        if n <= 0.2:   return "V类"
        return "劣V类"

    def classify_total_phosphorus_by_type(self, value: float | str) -> str:
        if self.water_type == "湖库":
            return self.classify_total_phosphorus_lake(value)
        else:
            return self.classify_total_phosphorus(value)

    def classify_metric(self, metric_name: str, value: float | str) -> str:
        """
        根据指标名调用对应的分类方法。
        metric_name: "pH", "溶解氧", "CODMn"（或 "CODₘₙ"）、"氨氮", "总磷"
        """
        # 规范 metric_name（一些来源可能写法不同）
        name = str(metric_name).strip().lower()
        if "ph" in name:
            return self.classify_pH(value)
        if "溶解氧" in name:
            return self.classify_dissolved_oxygen(value)
        if "高锰酸" in name or "cod" in name:
            return self.classify_permanganate_index(value)
        if "氨氮" in name:
            return self.classify_ammonia_nitrogen(value)
        if "总磷" in name or "tp" in name:
            return self.classify_total_phosphorus_by_type(value)
        return ""

    # ----------------- 辅助：阈值和可视化 -----------------
    @classmethod
    def metric_boundaries(cls, metric_id: str, water_type: str) -> List[Tuple[str, float]]:
        """返回按顺序的 (label, value) 阈值列表（由好到差或按业务约定）"""
        mid = str(metric_id)
        if "ph" in mid.lower():
            return [("pH下限", 6.0), ("pH上限", 9.0)]
        if "溶解氧" in mid:
            return [("I类", 7.5), ("II类", 6.0), ("III类", 5.0), ("IV类", 3.0), ("V类", 2.0)]
        if "cod" in mid.lower() or "高锰酸" in mid:
            return [("I类", 2.0), ("II类", 4.0), ("III类", 6.0), ("IV类", 10.0), ("V类", 15.0)]
        if "氨氮" in mid:
            return [("I类", 0.15), ("II类", 0.5), ("III类", 1.0), ("IV类", 1.5), ("V类", 2.0)]
        if "总磷" in mid:
            if water_type == "湖库":
                return [("I类", 0.015), ("II类", 0.025), ("III类", 0.05), ("IV类", 0.1), ("V类", 0.2)]
            else:
                return [("I类", 0.02), ("II类", 0.1), ("III类", 0.2), ("IV类", 0.3), ("V类", 0.4)]
        return []

    @classmethod
    def get_visual_boundaries(cls, metric_id: str, water_type: str) -> List[Tuple[str, float, str]]:
        """返回 (label, value, color) 列表，UI 可直接绘制横线与右侧标注"""
        bounds = cls.metric_boundaries(metric_id, water_type)
        out = []
        for label, v in bounds:
            color = cls.CATEGORY_COLORS.get(label, cls.CATEGORY_COLORS.get(metric_id, "#999999"))
            out.append((label, v, color))
        return out

    # ----------------- 整体判定 -----------------
    @classmethod
    def overall_category(cls, categories: list[str]) -> str:
        """
        从各指标类别列表中选最差的，返回总体水质类别
        """
        if not categories:
            return "无有效数据"
        worst_order = 0
        for c in categories:
            worst_order = max(worst_order, cls.CATEGORY_ORDER.get(c, 0))
        return cls.ORDER_TO_CATEGORY.get(worst_order, "")

    # 便捷：实例方法版 classify_value（使用实例的 water_type）
    def classify_value(self, metric_id: str, value) -> str:
        mid = str(metric_id)
        # pH 特殊处理
        if "ph" in mid.lower():
            return self.classify_pH(value)
        # 其它通过 classify_metric（内部会根据字符串匹配调用对应函数）
        return self.classify_metric(metric_id, value)
    
    @staticmethod
    def recognized_metric_id(colname: str) -> str | None:
        name = str(colname)
        low = name.lower()
        if "ph" in low: return "pH"
        if "溶解氧" in name: return "溶解氧"
        if ("高锰酸盐" in name) or ("cod" in low): return "CODMn"
        if "氨氮" in name: return "氨氮"
        if "总磷" in name: return "总磷"
        return None
    
# 示范在你的 UI 代码中调用方式：
def evaluate_and_display(self):
    # 假设你已经从界面获取了这些原始值
    ph_value        = self.ph_lineedit.text()
    do_value        = self.do_lineedit.text()
    cod_value       = self.cod_lineedit.text()
    ammonia_value   = self.ammonia_lineedit.text()
    phosphorus_value= self.phosphorus_lineedit.text()
    water_type      = self.water_type_combo.currentText()  # "河流" 或 "湖库"

    # 实例化分类器
    classifier = WaterQualityClassifier(self.water_type_combo_box.currentText())

    # 读取并分类各指标
    ph_category        = classifier.classify_pH(ph_value)
    do_category        = classifier.classify_dissolved_oxygen(do_value)
    cod_category       = classifier.classify_permanganate_index(cod_value)
    ammonia_category   = classifier.classify_ammonia_nitrogen(ammonia_value)
    phosphorus_category= classifier.classify_total_phosphorus_by_type(phosphorus_value)

    # 计算总体
    categories = [ph_category, do_category, cod_category, ammonia_category, phosphorus_category]
    overall = WaterQualityClassifier.overall_category([c for c in categories if c])
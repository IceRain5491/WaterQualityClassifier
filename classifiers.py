from __future__ import annotations
from typing import List, Tuple, Iterable, Optional
import re


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

    def __init__(self, water_type: str = "河流", lake_stations: Optional[Iterable[str]] = None):
        """
        water_type: "河流" 或 "湖库"，决定总磷的默认判定标准（可在调用 classify_total_phosphorus_by_type 时被覆盖）
        lake_stations: 可选的初始湖库站点集合（应用端可在启动时注入 LAKE_TP_STATIONS）
        """
        self.water_type = water_type
        # 内部保存归一化（小写、去首尾空白、去括号内内容等）
        self._lake_station_set: set[str] = set()
        if lake_stations:
            self.set_lake_stations(lake_stations)

    # ----------------- 站点集合管理 API -----------------
    @staticmethod
    def _norm_station(s: Optional[str]) -> str:
        """把站名归一化为小写、去括号内容、折叠空白，便于匹配"""
        if s is None:
            return ""
        s = str(s).strip()
        if not s:
            return ""
        # 去掉中英文括号内内容
        s = re.sub(r"\（.*?\）|\(.*?\)", "", s)
        # 去掉常见编号前缀 (如 "01-" 等)
        s = re.sub(r"^[\s\-_0-9]+", "", s)
        # 折叠空白并小写
        s = re.sub(r"[\s　]+", " ", s).strip().lower()
        return s

    def set_lake_stations(self, names: Iterable[str]) -> None:
        """覆盖式设置湖库站点集合（传入可迭代对象）"""
        try:
            self._lake_station_set = {self._norm_station(n) for n in names if n is not None}
        except Exception:
            # 容错：若任何异常就清空集合
            self._lake_station_set = set()

    def add_lake_station(self, name: str) -> None:
        """增量添加单个站点（设计时或运行时都可调用）"""
        if not hasattr(self, "_lake_station_set"):
            self._lake_station_set = set()
        self._lake_station_set.add(self._norm_station(name))

    def remove_lake_station(self, name: str) -> None:
        """从集合中移除站点（没有则忽略）"""
        try:
            self._lake_station_set.discard(self._norm_station(name))
        except Exception:
            pass

    def is_lake_station(self, station_name: Optional[str], fuzzy: bool = True) -> bool:
        """
        判断某站点是否为湖库站点。
        - 先做规范化精确匹配；
        - 若 fuzzy=True 且未匹配到，再尝试宽松匹配（子串/倒置子串）以容错常见写法差异。
        """
        if not station_name:
            return False
        n = self._norm_station(station_name)
        sset = getattr(self, "_lake_station_set", set())
        if not sset:
            return False
        if n in sset:
            return True
        if not fuzzy:
            return False
        # 宽松匹配：站名包含集合中某个项或集合某项包含站名
        for s in sset:
            if not s:
                continue
            if s in n or n in s:
                return True
        return False

    # ----------------- 分类方法（按指标） -----------------
    @staticmethod
    def classify_pH(value: float | str) -> str:
        """pH值"""
        try:
            n = float(value)
        except Exception:
            return ""
        return "I类" if 6.0 <= n <= 9.0 else "劣V类"

    @staticmethod
    def classify_dissolved_oxygen(value: float | str) -> str:
        """溶解氧"""
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
        """高锰酸盐指数"""
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
    def classify_codcr(value: float | str) -> str:
        """化学需氧量"""
        try:
            n = float(value)
        except Exception:
            return ""
        if n < 0:
            return ""
        if n <= 15:
            return "I类" 
        if n <= 20:
            return "III类"
        if n <= 30:
            return "IV类"
        if n <= 40:
            return "V类"
        return "劣V类"

    @staticmethod
    def classify_ammonia_nitrogen(value: float | str) -> str:
        """氨氮"""
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
        """总磷（河流）"""
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
        """总磷（湖库）"""
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

    @staticmethod
    def classify_total_nitrogen(value: float | str) -> str:
        """总氮"""
        try:
            n = float(value)
        except Exception:
            return ""
        if n <= 0.2: return "I类"
        if n <= 0.5: return "II类"
        if n <= 1.0: return "III类"
        if n <= 1.5: return "IV类"
        if n <= 2.0: return "V类"
        return "劣V类"

    @staticmethod
    def classify_biochemical_oxygen_demand(value: float | str) -> str:
        """生化需氧量"""
        try:
            n = float(value)
        except Exception:
            return ""
        if n <= 3.0: return "I类"
        if n <= 3.0: return "II类"
        if n <= 4.0: return "III类"
        if n <= 6.0: return "IV类"
        if n <= 10.0: return "V类"
        return "劣V类"

    def classify_total_phosphorus_by_type(
        self,
        value: float | str,
        station_name: Optional[str] = None,
        explicit_water_type: Optional[str] = None
    ) -> str:
        """
        更智能的总磷判定：
        - explicit_water_type 优先（调用者显式指定 "湖库" 或 "河流"）
        - 否则如果传入 station_name 且为湖库（is_lake_station）则按湖库标准
        - 否则使用实例 self.water_type（初始化时的默认）
        """
        # 优先 explicit
        if explicit_water_type:
            wt = explicit_water_type
        else:
            # 若给了站名并 classifier 里能判断
            if station_name and self.is_lake_station(station_name):
                wt = "湖库"
            else:
                wt = self.water_type or "河流"

        if wt == "湖库":
            return self.classify_total_phosphorus_lake(value)
        else:
            return self.classify_total_phosphorus(value)

    @staticmethod
    def _normalize_metric_name(name: str) -> str:
        s = str(name).strip()
        # 常见全角括号/冒号 → 半角
        s = s.replace("（", "(").replace("）", ")").replace("：", ":")
        # Unicode 下标 m/n → m/n
        s = s.replace("ₘ", "m").replace("ₙ", "n")
        # 去空白并小写
        s = re.sub(r"\s+", "", s).lower()
        return s

    @staticmethod
    def recognized_metric_id(metric_name: str) -> str | None:
        raw = str(metric_name)
        low = WaterQualityClassifier._normalize_metric_name(raw)

        # pH
        if "ph" in low:
            return "pH"

        # 溶解氧
        if ("溶解氧" in raw) or re.search(r"\bdo\b", low):
            return "溶解氧"

        # —— 先判 CODMn（避免 'cod' 被误入 CODCr）——
        if ("高锰酸" in raw) or ("codmn" in low) or re.search(r"cod(\(|-|_)?mn", low):
            return "CODMn"

        # CODCr（化学需氧量）
        if ("化学需氧量" in raw) or ("codcr" in low) or ("cod(cr)" in low):
            return "CODCr"

        # 裸 'cod'：无 'mn' 时默认按 CODCr 处理
        if re.search(r"\bcod\b", low):
            return "CODCr"

        # 氨氮
        if "氨氮" in raw or re.search(r"\bnh[-_ ]?3[-_ ]?n\b", low):
            return "氨氮"

        # 总磷 / TP
        if "总磷" in raw or re.search(r"\btp\b", low):
            return "总磷"

        # 总氮 / TN
        if "总氮" in raw or re.search(r"\btn\b", low):
            return "总氮"

        # 生化需氧量 / BOD
        if ("生化需氧量" in raw) or ("bod" in low) or re.search(r"\bbod\b", low):
            return "生化需氧量"

        return None

    def classify_metric(self, metric_name: str, value: float | str) -> str:
        mid = self.recognized_metric_id(metric_name)
        if not mid:
            return ""

        if mid == "pH":
            return self.classify_pH(value)
        if mid == "溶解氧":
            return self.classify_dissolved_oxygen(value)
        if mid == "CODMn":
            return self.classify_permanganate_index(value)
        if mid == "CODCr":
            return self.classify_codcr(value)
        if mid == "氨氮":
            return self.classify_ammonia_nitrogen(value)
        if mid == "总磷":
            try:
                return self.classify_total_phosphorus_by_type(value)
            except Exception:
                func = getattr(self, "classify_total_phosphorus", None)
                return func(value) if callable(func) else ""
        if mid == "总氮":
            return self.classify_total_nitrogen(value)
        if mid == "生化需氧量":
            return self.classify_biochemical_oxygen_demand(value)

        func = getattr(self, f"classify_{mid}", None)
        return func(value) if callable(func) else ""

    # ----------------- 辅助：阈值和可视化 -----------------
    @classmethod
    def metric_boundaries(cls, metric_id: str, water_type: str) -> List[Tuple[str, float]]:
        mid = str(metric_id)
        low = cls._normalize_metric_name(mid)

        if "ph" in low:
            return [("pH下限", 6.0), ("pH上限", 9.0)]

        if "溶解氧" in mid:
            return [("I类", 7.5), ("II类", 6.0), ("III类", 5.0), ("IV类", 3.0), ("V类", 2.0)]

        # —— 先判 CODMn（高锰酸盐指数）——
        if ("高锰酸" in mid) or ("codmn" in low) or re.search(r"cod(\(|-|_)?mn", low):
            return [("I类", 2.0), ("II类", 4.0), ("III类", 6.0), ("IV类", 10.0), ("V类", 15.0)]

        # —— 再判 CODCr（化学需氧量）; 裸 cod 也归到 CODCr —— 
        if ("化学需氧量" in mid) or ("codcr" in low) or ("cod(cr)" in low) or re.search(r"\bcod\b", low):
            return [("I/II", 15.0), ("III", 20.0), ("IV", 30.0), ("V", 40.0)]

        if "氨氮" in mid:
            return [("I类", 0.15), ("II类", 0.5), ("III类", 1.0), ("IV类", 1.5), ("V类", 2.0)]

        if "总磷" in mid or "tp" in low:
            if water_type == "湖库":
                return [("I类", 0.015), ("II类", 0.025), ("III类", 0.05), ("IV类", 0.1), ("V类", 0.2)]
            else:
                return [("I类", 0.02), ("II类", 0.1), ("III类", 0.2), ("IV类", 0.3), ("V类", 0.4)]

        if "总氮" in mid or "tn" in low:
            return [("I类", 0.2), ("II类", 0.5), ("III类", 1.0), ("IV类", 1.5), ("V类", 2.0)]

        if "生化需氧量" in mid or "bod" in low:
            return [("I类", 3.0), ("II类", 3.0), ("III类", 4.0), ("IV类", 6.0), ("V类", 10.0)]
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
        # 其它通过 classify_metric（内部会根据字符串匹配调用对应函数） but note for TP you may want station_name
        return self.classify_metric(metric_id, value)

# __init__.py -- 兼容两种布局（package 或 扁平模块）
try:
    # package 布局（优先）
    from .classifiers import WaterQualityClassifier
    from .constants import COLOR_MAP, DATE_TYPE_MAP
except Exception:
    # fallback 到仓库根同级模块（若没有作为 package 安装）
    from classifiers import WaterQualityClassifier
    from constants import COLOR_MAP, DATE_TYPE_MAP

# 便捷函数别名（若不存在则为 None）
classify_pH = getattr(WaterQualityClassifier, "classify_pH", None)
classify_dissolved_oxygen = getattr(WaterQualityClassifier, "classify_dissolved_oxygen", None)

def classify_by_header(header: str, value, water_type: str = "河流"):
    return WaterQualityClassifier(water_type).classify_metric(header, value)

__all__ = [
    "WaterQualityClassifier",
    "classify_by_header",
    "classify_pH",
    "classify_dissolved_oxygen",
    "COLOR_MAP",
    "DATE_TYPE_MAP",
]

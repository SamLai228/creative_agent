"""
驗證腳本：從 reference EDM 提取文字區域並疊加到空白 template

執行方式：
    source venv/bin/activate
    python scripts/test_template_overlay.py

輸出：
    output/test/overlay_test_YYYYMMDD_HHMMSS.png       （成品）
    output/test/overlay_test_YYYYMMDD_HHMMSS_debug.png （debug，標示各 region bbox）
"""
import sys
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import TEMPLATE_IMAGES_DIR, OUTPUT_DIR, TEMPLATE_CONFIGS_DIR
from src.generator.template_region_detector import TemplateRegionDetector
from src.generator.layout_engine import LayoutEngine
from src.generator.copywriter import Copywriter


# ── 設定 ────────────────────────────────────────────────
TEMPLATE_NAME = "edm_template_01.jpeg"
REFERENCE_NAME = "edm_full_01.png"
REFERENCES_DIR = TEMPLATE_IMAGES_DIR.parent / "references"
OUTPUT_TEST_DIR = OUTPUT_DIR / "test_gpt5.2"
OUTPUT_TEST_DIR.mkdir(parents=True, exist_ok=True)

REGION_COLORS = {
    "title":      (255, 80,  80),
    "content":    (80,  160, 255),
    "cta":        (80,  220, 120),
    "conclusion": (220, 160, 80),
}
DEFAULT_REGION_COLOR = (200, 100, 200)


def step1_get_regions() -> dict:
    """Step 1：載入或重新偵測 region config"""
    print("\n[Step 1] 從 reference 偵測文字區域...")
    template_path = str(TEMPLATE_IMAGES_DIR / TEMPLATE_NAME)
    reference_path = str(REFERENCES_DIR / REFERENCE_NAME)

    detector = TemplateRegionDetector()
    config = detector.detect_regions_from_reference(
        reference_path=reference_path,
        template_path=template_path,
    )

    template_stem = Path(TEMPLATE_NAME).stem
    config_file = TEMPLATE_CONFIGS_DIR / f"{template_stem}.json"
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    regions = config.get("regions", [])
    print(f"  識別到 {len(regions)} 個區域，配置已存至 {config_file}")
    for r in regions:
        bbox = r["bbox"]
        fs = r["font_size"]
        cpl = max(1, int(bbox[2] / (fs * 1.2)))
        lines = max(1, int(bbox[3] / (fs + 10)))
        print(f"  [{r['id']:12s}] y={bbox[1]:4d} ~{cpl*lines}字")
    return config


def step2_generate_copy(config: dict) -> dict:
    """Step 2：依 region 結構生成精確字數的文案"""
    print("\n[Step 2] 生成 template-aware 文案...")
    copywriter = Copywriter()
    requirements = {
        "product_name": "幸福人生保障計畫",
        "promotion_type": "新品推出",
        "key_message": "全方位保障，守護您與家人的每一天",
        "target_audience": "30-50 歲有家庭責任的上班族",
        "tone": "溫暖、專業、安心",
    }
    copy_map = copywriter.generate_copy_for_template(config, requirements)
    print(f"  生成 {len(copy_map)} 個 region 的文案：")
    for rid, text in copy_map.items():
        print(f"  [{rid:12s}] ({len(text)}字) {text!r}")
    return copy_map


def step3_overlay_text(config: dict, copy_map: dict, timestamp: str) -> Path:
    """Step 3：疊加文字到 template"""
    print("\n[Step 3] 疊加文字到 template...")

    layout_engine = LayoutEngine()
    canvas = layout_engine.create_canvas(template_path=TEMPLATE_NAME)

    for region in config.get("regions", []):
        rid = region["id"]
        text = copy_map.get(rid, "").strip()

        # 確保 font_size 不超過 region 高度的 80%
        bbox = region.get("bbox", [0, 0, 0, 0])
        region_h = bbox[3]
        max_fs = max(10, int(region_h * 0.80))
        if region.get("font_size", 32) > max_fs:
            region = dict(region, font_size=max_fs)

        if text:
            canvas = layout_engine.place_text_in_region(canvas, text, region)
            print(f"  [{rid:12s}] ({len(text)}字) {text[:25]!r}")
        else:
            print(f"  略過 [{rid}]")

    out_path = OUTPUT_TEST_DIR / f"overlay_test_{timestamp}.png"
    canvas.save(str(out_path))
    print(f"  成品輸出: {out_path}")
    return out_path


def step4_debug_image(config: dict, timestamp: str) -> Path:
    """Step 4：輸出 debug 圖（彩色 bbox + region id 標籤）"""
    print("\n[Step 4] 輸出 debug 圖...")
    from PIL import Image, ImageDraw, ImageFont

    template_path = TEMPLATE_IMAGES_DIR / TEMPLATE_NAME
    with Image.open(template_path) as img:
        debug_img = img.convert("RGB").copy()

    draw = ImageDraw.Draw(debug_img, "RGBA")

    try:
        from src.generator.layout_engine import LayoutEngine as _LE
        _le = _LE()
        label_font = (
            ImageFont.truetype(_le.chinese_font_path, 18)
            if _le.chinese_font_path
            else ImageFont.load_default()
        )
    except Exception:
        label_font = ImageFont.load_default()

    for region in config.get("regions", []):
        rtype = region.get("type", "other")
        bbox = region.get("bbox", [0, 0, 0, 0])
        if len(bbox) != 4:
            continue
        rx, ry, rw, rh = bbox
        color = REGION_COLORS.get(rtype, DEFAULT_REGION_COLOR)
        draw.rectangle(
            [rx, ry, rx + rw, ry + rh],
            fill=(*color, 55),
            outline=(*color, 210),
            width=2,
        )
        draw.text((rx + 4, ry + 2), region.get("id", rtype), fill=(*color, 255), font=label_font)

    debug_path = OUTPUT_TEST_DIR / f"overlay_test_{timestamp}_debug.png"
    debug_img.save(str(debug_path))
    print(f"  debug 圖輸出: {debug_path}")
    return debug_path


def validate(config: dict, out_path: Path, debug_path: Path):
    print("\n[驗證]")
    regions = config.get("regions", [])
    assert len(regions) >= 3, f"regions 數量不足：{len(regions)}"
    print(f"  ✓ regions 數量: {len(regions)}")
    assert out_path.exists() and out_path.stat().st_size > 0
    print(f"  ✓ 成品圖存在: {out_path.stat().st_size} bytes")
    assert debug_path.exists() and debug_path.stat().st_size > 0
    print(f"  ✓ debug 圖存在: {debug_path.stat().st_size} bytes")
    print("\n所有驗證通過！")


def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    config = step1_get_regions()
    copy_map = step2_generate_copy(config)
    out_path = step3_overlay_text(config, copy_map, timestamp)
    debug_path = step4_debug_image(config, timestamp)
    validate(config, out_path, debug_path)
    print(f"\n完成！\n  成品：{out_path}\n  Debug：{debug_path}")


if __name__ == "__main__":
    main()

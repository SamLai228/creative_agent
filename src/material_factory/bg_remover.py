"""背景移除工具 - 使用 rembg 移除圖片背景"""
from pathlib import Path


def remove_background(
    input_path: Path,
    force: bool = False,
    model_name: str = "birefnet-general",
) -> Path:
    """
    移除圖片背景，輸出透明 PNG。
    使用 birefnet-general 模型 + alpha matting 以保留白色/淺色前景物件。

    Args:
        input_path: 原始圖片路徑
        force: 若為 True，即使去背檔案已存在也重新處理
        model_name: rembg 模型名稱

    Returns:
        去背後的圖片路徑（同目錄，檔名加 _nobg.png）
    """
    try:
        from rembg import remove, new_session
    except ImportError:
        raise ImportError("需要安裝 rembg：pip install rembg")

    output_path = input_path.parent / f"{input_path.stem}_nobg.png"

    if output_path.exists() and not force:
        return output_path

    print(f"  - 正在去背：{input_path.name} → {output_path.name}")

    session = new_session(model_name)

    with open(input_path, "rb") as f:
        input_data = f.read()

    output_data = remove(
        input_data,
        alpha_matting=True,
        alpha_matting_foreground_threshold=200,
        alpha_matting_background_threshold=20,
        alpha_matting_erode_size=10,
        post_process_mask=True,
        session=session,
    )

    with open(output_path, "wb") as f:
        f.write(output_data)

    return output_path

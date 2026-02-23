"""命令列介面"""
import argparse
from pathlib import Path
from src.material_factory import MaterialFactory
from src.config import ASSETS_DIR


def main():
    parser = argparse.ArgumentParser(description="行銷 EDM 素材工廠 - 素材貼標工具")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 貼標命令
    tag_parser = subparsers.add_parser("tag", help="為素材貼標")
    tag_parser.add_argument(
        "--file",
        type=str,
        help="單一檔案路徑"
    )
    tag_parser.add_argument(
        "--dir",
        type=str,
        default=str(ASSETS_DIR),
        help="素材目錄（預設: assets/）"
    )
    tag_parser.add_argument(
        "--force",
        action="store_true",
        help="強制更新已存在的標籤"
    )
    
    # 搜尋命令
    search_parser = subparsers.add_parser("search", help="搜尋素材")
    search_parser.add_argument("--category", type=str, help="類型")
    search_parser.add_argument("--style", type=str, nargs="+", help="風格（可多個）")
    search_parser.add_argument("--scenario", type=str, nargs="+", help="情境（可多個）")
    search_parser.add_argument("--color", type=str, help="色系")
    search_parser.add_argument("--mood", type=str, nargs="+", help="氛圍（可多個）")
    search_parser.add_argument("--keywords", type=str, nargs="+", help="關鍵字（可多個）")
    
    # 統計命令
    stats_parser = subparsers.add_parser("stats", help="顯示素材統計資訊")
    
    args = parser.parse_args()
    
    factory = MaterialFactory()
    
    if args.command == "tag":
        if args.file:
            # 單一檔案
            image_path = Path(args.file)
            if not image_path.exists():
                print(f"錯誤: 檔案不存在: {image_path}")
                return
            
            tags = factory.tag_single_material(image_path, args.force)
            print("\n標籤資訊:")
            print(f"  類型: {tags.get('category')}")
            print(f"  風格: {', '.join(tags.get('style', []))}")
            print(f"  情境: {', '.join(tags.get('scenario', []))}")
            print(f"  色系: {tags.get('color_scheme')}")
            print(f"  氛圍: {', '.join(tags.get('mood', []))}")
            print(f"  關鍵字: {', '.join(tags.get('keywords', []))}")
        else:
            # 批次處理
            directory = Path(args.dir)
            if not directory.exists():
                print(f"錯誤: 目錄不存在: {directory}")
                return
            
            factory.tag_batch_materials(directory, force_update=args.force)
    
    elif args.command == "search":
        results = factory.search_materials(
            category=args.category,
            style=args.style,
            scenario=args.scenario,
            color_scheme=args.color,
            mood=args.mood,
            keywords=args.keywords
        )
        
        print(f"\n找到 {len(results)} 個符合條件的素材:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {Path(result['file_path']).name}")
            print(f"   類型: {result.get('category')}")
            print(f"   風格: {', '.join(result.get('style', []))}")
            print(f"   情境: {', '.join(result.get('scenario', []))}")
            print()
    
    elif args.command == "stats":
        stats = factory.get_material_stats()
        print("\n素材統計資訊:")
        print(f"總素材數: {stats['total_materials']}")
        print(f"\n按類型分類:")
        for category, count in stats['by_category'].items():
            print(f"  {category}: {count}")
        print(f"\n按風格分類:")
        for style, count in sorted(stats['by_style'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {style}: {count}")
        print(f"\n按情境分類:")
        for scenario, count in sorted(stats['by_scenario'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {scenario}: {count}")
        print(f"\n按色系分類:")
        for color, count in stats['by_color_scheme'].items():
            print(f"  {color}: {count}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
icon.ico ファイルを生成するスクリプト
PIL/Pillow を使用して、簡単なアイコンを作成します
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """シンプルなアイコンを作成"""
    
    # 256x256 のアイコンを作成
    size = 256
    img = Image.new('RGB', (size, size), color=(30, 58, 138))  # 紺色背景
    
    draw = ImageDraw.Draw(img)
    
    # 円を描画
    margin = 30
    draw.ellipse(
        [(margin, margin), (size-margin, size-margin)],
        fill=(100, 150, 255),  # 薄い青
        outline=(255, 255, 255),  # 白い枠線
        width=3
    )
    
    # VNC の文字（簡略）
    try:
        # フォントを使用
        text = "VNC"
        # フォントサイズを大きく
        draw.text(
            (size//2 - 30, size//2 - 20),
            text,
            fill=(255, 255, 255),
            font=None
        )
    except:
        pass
    
    # icon.ico として保存（複数サイズ）
    icon_sizes = [16, 32, 64, 128, 256]
    icon_images = []
    
    for icon_size in icon_sizes:
        icon_img = img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
        icon_images.append(icon_img)
    
    # ICO ファイルとして保存
    icon_images[0].save(
        'icon.ico',
        format='ICO',
        sizes=[(size, size) for size in icon_sizes]
    )
    
    print("✅ icon.ico を生成しました")

if __name__ == '__main__':
    try:
        create_icon()
    except ImportError:
        print("⚠️  PIL (Pillow) が必要です")
        print("以下を実行してください:")
        print("  pip install Pillow")

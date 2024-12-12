from PIL import Image, ImageDraw, ImageFont
import textwrap

# 背景画像のファイル名
background_image_path = "/Users/hiratasoma/Documents/NeoTama_hackukosen2024/spotApp/test_program/mikuji.png"
# 出力ファイル名
output_image_path = "mikuji_result.jpg"
# おみくじの結果（20文字前後の日本語）
omikuji_result = "大吉！今年は素晴らしい年になるでしょう。あなたの努力が報われる年です。"

# 背景画像を読み込む
background = Image.open(background_image_path).convert("RGBA")

# フォントを設定（フォントファイルとサイズを指定）
font_path = "/Users/hiratasoma/Documents/NeoTama_hackukosen2024/spotApp/YujiMai-Regular.ttf"  # フォントファイルを指定
font_size = 80  # フォントサイズを指定
font = ImageFont.truetype(font_path, font_size)

# 描画用のオブジェクトを作成
draw = ImageDraw.Draw(background)

# テキストを8文字ごとに分割
wrapped_text = "\n".join(textwrap.wrap(omikuji_result, width=8))

# テキストの描画位置を計算（中央揃え）
text_bbox = draw.textbbox((0, 0), wrapped_text, font=font)
text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
image_width, image_height = background.size
text_x = (image_width - text_width) // 2
text_y = (image_height - text_height) // 2

# テキストの色を設定（黒色）
text_color = (0, 0, 0, 255)  # RGBA形式（完全不透明の黒）

# テキストを描画
draw.multiline_text((text_x, text_y), wrapped_text, font=font, fill=text_color, align="center")

# JPG用にアルファチャンネルを除去して白背景を設定
jpg_background = Image.new("RGB", background.size, (255, 255, 255))  # 白背景を作成
jpg_background.paste(background, mask=background.split()[3])  # アルファチャンネルを使って合成

# JPG形式で保存
jpg_background.save(output_image_path, format="JPEG")

print(f"おみくじの画像を保存しました: {output_image_path}")

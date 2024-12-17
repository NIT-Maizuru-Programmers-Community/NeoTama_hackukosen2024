from PIL import Image, ImageDraw, ImageFont
import textwrap

def generate_omikuji_image(background_image_path, font_path, omikuji_result, output_image_path):
    """
    おみくじ結果を背景画像に描画して保存する関数。

    :param background_image_path: 背景画像のファイルパス
    :param font_path: フォントファイルのパス
    :param omikuji_result: おみくじの結果テキスト（日本語）
    :param output_image_path: 出力画像の保存パス
    """
    try:
        # 背景画像を読み込む
        background = Image.open(background_image_path).convert("RGBA")

        # フォントを設定
        font_size = 250
        font = ImageFont.truetype(font_path, font_size)

        # 描画用のオブジェクトを作成
        draw = ImageDraw.Draw(background)

        # テキストを8文字ごとに分割
        wrapped_text = "\n".join(textwrap.wrap(omikuji_result, width=8))

        # テキストサイズを計算（幅と高さを取得）
        text_bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
        image_width, image_height = background.size
        text_x = (image_width - text_width) // 2
        text_y = 250#(image_height - text_height) // 2

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

    except Exception as e:
        print(f"エラーが発生しました: {e}")

# 使用例
#background_image_path = "spotApp/assets/badge.jpg"
#font_path = "spotApp/DelaGothicOne-Regular.ttf"
#omikuji_result = "50%"
#output_image_path = "spotApp/assets/budge_result.jpg"
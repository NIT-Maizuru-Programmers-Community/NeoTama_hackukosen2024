import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2
import time

# 写真撮影関数
def take_photo():
    # カメラを開く
    cap = cv2.VideoCapture(0)  # ここでカメラのIDを指定

    # カメラが正常に開かれたか確認
    if not cap.isOpened():
        print("カメラのオープンに失敗しました")
        return False

    # 解像度を設定（オプション）
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1040)  # 幅を設定
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 700)  # 高さを設定

    # 画像を保存するディレクトリ（assetsフォルダ）
    assets_dir = "assets"
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)

    # 写真撮影
    time.sleep(0.1)
    ret, frame = cap.read()  # フレームを取得
    if not ret:
        print("フレームの取得に失敗しました")
        cap.release()
        return False

    # 画像を保存するパス（ファイル名に現在時刻を使ってユニークに）
    photo_path = ("spotApp/assets/photo.jpg")

    # 画像を保存
    cv2.imwrite(photo_path, frame)
    print(f"写真が保存されました: {photo_path}")

    # カメラを解放
    cap.release()
    cv2.destroyAllWindows()

    return photo_path

# 他のプログラムから呼び出す例
if __name__ == "__main__":
    photo_path = take_photo()
    if photo_path:
        print(f"写真が保存されたパス: {photo_path}")
    else:
        print("写真の撮影に失敗しました")

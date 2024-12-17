from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

# モデルの読み込み
model = load_model("/Users/hiratasoma/Documents/NeoTama_hackukosen2024/spotApp/pre_process/emotion_judge/emotion_model.h5")

# クラスラベルの対応表
class_labels = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

# 推論用の画像パス
image_path = "/Users/hiratasoma/Documents/NeoTama_hackukosen2024/spotApp/assets/photo.jpg"

# 画像の前処理
img = image.load_img(image_path, target_size=(48, 48, 3))
img_array = image.img_to_array(img)
img_array = np.expand_dims(img_array, axis=0)  # バッチ次元を追加
img_array /= 255.0  # 正規化

# 推論
predictions = model.predict(img_array)
predicted_class = np.argmax(predictions)  # 最も確率の高いクラス
happiness_score = predictions[0][class_labels.index("happy")]  # "happy" ラベルのスコア

print(f"Predicted Class: {class_labels[predicted_class]}")
print(f"Happiness Score: {happiness_score}")
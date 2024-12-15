import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# データのパス
train_dir = "/Users/hiratasoma/Documents/NeoTama_hackukosen2024/spotApp/pre_process/emotion_train_data/train"
test_dir = "/Users/hiratasoma/Documents/NeoTama_hackukosen2024/spotApp/pre_process/emotion_train_data/test"

# 画像のサイズ
img_size = (48, 48)  # FER2013に準拠
batch_size = 32

# データ拡張と正規化
train_datagen = ImageDataGenerator(
    rescale=1.0 / 255,              # 正規化
    rotation_range=30,              # 画像の回転
    width_shift_range=0.2,          # 横方向の平行移動
    height_shift_range=0.2,         # 縦方向の平行移動
    shear_range=0.2,                # シアー変換
    zoom_range=0.2,                 # ズーム
    horizontal_flip=True,           # 水平反転
    fill_mode="nearest"             # 空白の埋め方
)

test_datagen = ImageDataGenerator(rescale=1.0 / 255)  # テストデータは拡張せず正規化のみ

# トレーニングデータジェネレータ
train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode="categorical",
    color_mode="grayscale"  # グレースケールで読み込む
)

# テストデータジェネレータ
test_generator = test_datagen.flow_from_directory(
    test_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode="categorical",
    color_mode="grayscale"  # グレースケールで読み込む
)

#from keras import models, layers
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout

# モデルの構築
model = Sequential([
    Conv2D(32, (3, 3), activation="relu", input_shape=(48, 48, 1)),  # グレースケール用
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.25),

    Conv2D(64, (3, 3), activation="relu"),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.25),

    Conv2D(128, (3, 3), activation="relu"),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.25),

    Flatten(),
    Dense(128, activation="relu"),
    Dropout(0.5),
    Dense(7, activation="softmax")  # 7つのクラスに対応
])

# モデルのコンパイル
model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# モデルの概要を表示
model.summary()

# モデルのトレーニング
with tf.device('/GPU:0'):
    history = model.fit(
        train_generator,
        epochs=100,
        validation_data=test_generator
    )

# モデルの保存
model.save("/Users/hiratasoma/Documents/NeoTama_hackukosen2024/spotApp/pre_process/emotion_model.h5")
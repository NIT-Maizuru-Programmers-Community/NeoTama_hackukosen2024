import tensorflow as tf
import numpy as np
import sounddevice as sd

# 変換されたモデルのパス
MODEL_PATH = '/Users/hiratasoma/Documents/NeoTama_hackukosen2024/spotApp/pre_process/NeoTamaModel/converted_model.h5'
LABELS_PATH = '/Users/hiratasoma/Documents/NeoTama_hackukosen2024/spotApp/pre_process/NeoTamaModel/metadata.json'  # metadata.json のパス

# ラベルを読み込む
def load_labels(labels_path):
    import json
    with open(labels_path, 'r') as f:
        metadata = json.load(f)
    return metadata['wordLabels']

# モデルをロード
def load_model(model_path):
    return tf.keras.models.load_model(model_path)

# 推論を実行
def predict(model, audio_data):
    # 必要に応じて音声データを前処理
    input_data = np.expand_dims(audio_data, axis=0).astype(np.float32)
    predictions = model(input_data)
    return predictions.numpy()

# 音声をリアルタイムでキャプチャして予測
def detect_clap(model_path, labels_path):
    labels = load_labels(labels_path)
    model = load_model(model_path)

    def audio_callback(indata, frames, time, status):
        if status:
            print(f"Audio Error: {status}")
        audio_data = np.mean(indata, axis=1)  # モノラルに変換
        predictions = predict(model, audio_data)
        label_idx = np.argmax(predictions)
        print(f"Detected: {labels[label_idx]} ({predictions[0][label_idx]:.2f})")

    # 音声ストリーム
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=16000):
        print("Listening... Press Ctrl+C to stop.")
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("Stopped.")

# 実行
detect_clap(MODEL_PATH, LABELS_PATH)

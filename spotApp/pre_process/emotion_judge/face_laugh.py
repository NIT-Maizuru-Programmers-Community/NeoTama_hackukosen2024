import cv2
import mediapipe as mp
import numpy as np

# MediaPipeの設定
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh()

# カメラキャプチャ
cap = cv2.VideoCapture(2)

while cap.isOpened():
    ret, frame = cap.read()
    
    if not ret:
        break

    # RGB形式に変換
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # 顔ランドマークの取得
    result = face_mesh.process(rgb_frame)
    
    if result.multi_face_landmarks:
        landmarks = result.multi_face_landmarks[0]

        # 左口角、右口角、上唇先端、下唇先端を使用
        left_corner = landmarks.landmark[61]  # 左口角
        right_corner = landmarks.landmark[291]  # 右口角
        top_lip = landmarks.landmark[0]  # 上唇の先端
        bottom_lip = landmarks.landmark[17]  # 下唇の先端

        # 各ランドマークの座標を利用して距離を計算
        left_x, left_y = left_corner.x, left_corner.y
        right_x, right_y = right_corner.x, right_corner.y
        top_x, top_y = top_lip.x, top_lip.y
        bottom_x, bottom_y = bottom_lip.x, bottom_lip.y

        # 各距離の総和を計算
        distance = (
            np.linalg.norm(np.array([left_x, left_y]) - np.array([right_x, right_y])) +
            np.linalg.norm(np.array([top_x, top_y]) - np.array([bottom_x, bottom_y]))
        ) / 2
        
        # 距離を利用して笑顔の明るさを表示
        cv2.putText(frame, f'Smile Brightness: {distance:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        if distance < 0.08:
            print("普通")
        else:
            print("笑顔")
    
    # フレームの表示
    cv2.imshow('Smile Brightness', frame)

    # キー操作終了条件 (ESCキー)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
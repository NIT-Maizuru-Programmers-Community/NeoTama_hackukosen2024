import cv2
import mediapipe as mp
import numpy as np

#MediaPipeの初期化
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

#笑顔スコアの計算
def calculate_smile_score(face_landmarks):
    mouth_left = face_landmarks.landmark[61]
    mouth_right = face_landmarks.landmark[291]
    mouth_top = face_landmarks.landmark[13]
    mouth_bottom = face_landmarks.landmark[14]

    mouth_width = abs(mouth_right.x - mouth_left.x)
    mouth_height = abs(mouth_top.y - mouth_bottom.y)
    smile_score = mouth_height / mouth_width
    return max(0, smile_score)  #スコアを0以上に制限

#視線方向の計算
def calculate_gaze_direction(face_landmarks):
    left_eye_center = face_landmarks.landmark[468]
    right_eye_center = face_landmarks.landmark[473]
    gaze_direction = (right_eye_center.x - left_eye_center.x, right_eye_center.y - left_eye_center.y)
    return gaze_direction

#視線一致度の計算
def calculate_gaze_match(gaze1, gaze2):
    dot_product = gaze1[0] * gaze2[0] + gaze1[1] * gaze2[1]
    magnitude1 = (gaze1[0]**2 + gaze1[1]**2)**0.5
    magnitude2 = (gaze2[0]**2 + gaze2[1]**2)**0.5
    similarity = dot_product / (magnitude1 * magnitude2)
    #-1 ～ 1 を 0 ～ 1 に変換
    normalized_similarity = (similarity + 1) / 2
    return normalized_similarity

#ミラーリングスコアの計算
def calculate_mirroring_score(face_landmarks1, face_landmarks2):
    score = 0
    for i in range(len(face_landmarks1.landmark)):
        x1, y1 = face_landmarks1.landmark[i].x, face_landmarks1.landmark[i].y
        x2, y2 = face_landmarks2.landmark[i].x, face_landmarks2.landmark[i].y
        score += ((x1 - x2)**2 + (y1 - y2)**2)**0.5  #距離の和
    max_possible_distance = 0.5  #カメラのスケールに応じて調整
    normalized_score = max(0, 1 - (score / max_possible_distance))
    return normalized_score

#顔の中心点を計算
def calculate_face_center(face_landmarks):
    x_coords = [landmark.x for landmark in face_landmarks.landmark]
    y_coords = [landmark.y for landmark in face_landmarks.landmark]
    center_x = sum(x_coords) / len(x_coords)
    center_y = sum(y_coords) / len(y_coords)
    return center_x, center_y

#物理的な距離を計算
def calculate_physical_distance(center1, center2):
    distance = ((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)**0.5
    return distance

#距離スコアを計算
def calculate_distance_score(distance, max_distance=0.5):
    normalized_score = max(0, 1 - (distance / max_distance))
    return normalized_score

#合計
def calculate_affinity(smile_score1, smile_score2, gaze_match, mirroring_score, distance_score):
    smile_weight = 0.3
    gaze_weight = 0.2
    mirror_weight = 0.2
    distance_weight = 0.3
    affinity_score = (
        smile_weight * (smile_score1 + smile_score2) / 2 +
        gaze_weight * gaze_match +
        mirror_weight * mirroring_score +
        distance_weight * distance_score
    )
    return affinity_score * 100  #0～100にスケール

def friendly_main():
    #カメラの初期化
    cap = cv2.VideoCapture(0)

    with mp_face_mesh.FaceMesh(
        max_num_faces=2,  #最大2人分の顔を検出
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as face_mesh:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("カメラからのフレームを取得できませんでした。")
                break

            #画像をRGBに変換
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = face_mesh.process(image)

            #ランドマークの描画
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.multi_face_landmarks and len(results.multi_face_landmarks) == 2:
                #2人の顔ランドマークを取得
                face1 = results.multi_face_landmarks[0]
                face2 = results.multi_face_landmarks[1]

                #各特徴量を計算
                smile1 = calculate_smile_score(face1)
                print(smile1)
                smile2 = calculate_smile_score(face2)
                print(smile2)
                gaze1 = calculate_gaze_direction(face1)
                gaze2 = calculate_gaze_direction(face2)
                gaze_match = calculate_gaze_match(gaze1, gaze2)
                print(gaze_match)
                mirroring = calculate_mirroring_score(face1, face2)
                print(mirroring)
                center1 = calculate_face_center(face1)
                center2 = calculate_face_center(face2)
                physical_distance = calculate_physical_distance(center1, center2)
                distance_score = calculate_distance_score(physical_distance)
                print(distance_score)

                #親密度スコアの計算
                affinity = calculate_affinity(smile1, smile2, gaze_match, mirroring, distance_score)

                #親密度スコアを表示
                cv2.putText(image, f"friendly: {affinity:.2f}", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            #画像を表示
            cv2.imshow('Face Affinity', image)
            if cv2.waitKey(5) & 0xFF == 27:  # ESCキーで終了
                break

    cap.release()
    cv2.destroyAllWindows()

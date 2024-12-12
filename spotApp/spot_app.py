import flet as ft
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
import random as rnd
from camera import take_photo
from clap import wait_hands_clap
import time
import threading
import csv
import cv2
from time import sleep
import base64
import mediapipe as mp
import numpy as np


global_token=None
global_token2=None
global display_out
display_out = "ゲスト"
#------
#Firebase初期設定
#------
cred = credentials.Certificate("spotApp/token.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
#コレクションデータ取得の前処理
nowToken = db.collection("Hard").document("token")
# Firebaseのドキュメント作成の前処理
data={"display_name": "", "id": "", "time_stamp": "", "url": "", "name": ""}

#Hardコレクションのデータを全て削除する
def delete_all_documents_in_collection(collection_name):
    # Firestoreクライアントを再利用
    docs = db.collection(collection_name).stream()

    for doc in docs:
        print(f"Deleting document {doc.id} in collection {collection_name}...")
        db.collection(collection_name).document(doc.id).delete()
    print("過去のセッションデータを削除完了。新セッションスタート。")

# Hardコレクションのデータを全て削除する
def delete_all_documents_in_collection(collection_name):
    docs = db.collection(collection_name).stream()
    for doc in docs:
        db.collection(collection_name).document(doc.id).delete()
# Firebaseからユーザーの表示名を取得する関数
def get_user_display_name(token):
    try:
        doc_ref = db.collection("Hard").document(str(token))
        doc = doc_ref.get().to_dict().get("display_name")
        return doc
    except Exception as e:
        print(f"Error fetching data: {e}")
        return "エラー"
    
def monitor_csv(on_change_callback):
    """
    CSVファイルを監視して、値が1になったらコールバックを呼び出す。
    """
    while True:
        try:
            with open("spotApp/judge.csv", "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    if "1" in row:  # 値が1の場合に画面遷移
                        on_change_callback()
                        return  # 1度検出したら監視終了
        except FileNotFoundError:
            print(f"CSVファイルが見つかりません")
        time.sleep(0.5)

class CameraCaptureControl(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.capture = cv2.VideoCapture(0)
        self.latency = 1 / self.capture.get(cv2.CAP_PROP_FPS)

    def did_mount(self):
        self.running = True
        self.thread = threading.Thread(target=self.update_frame, args=(), daemon=True)
        self.thread.start()

    def will_unmount(self):
        self.running = False

    def update_frame(self):
        while self.capture.isOpened() and self.running:
            retval, frame = self.capture.read()
            if not retval:
                print("フレームを取得できませんでした")
                continue
            retval, frame = cv2.imencode(".jpg", frame)
            data = base64.b64encode(frame)
            self.image_control.src_base64 = data.decode()
            self.update()
            sleep(self.latency)

    def build(self):
        self.image_control = ft.Image(
            width=self.capture.get(cv2.CAP_PROP_FRAME_WIDTH),
            height=self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT),
            fit=ft.ImageFit.FIT_WIDTH,
        )
        return self.image_control
    
#------
#MediaPipeで親密度推定
#------
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

class FriendlyApp(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.capture = cv2.VideoCapture(0)
        self.latency = 1 / self.capture.get(cv2.CAP_PROP_FPS)

        # MediaPipe FaceMesh初期化
        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=2,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def did_mount(self):
        self.running = True
        self.thread = threading.Thread(target=self.update_frame, args=(), daemon=True)
        self.thread.start()

    def will_unmount(self):
        self.running = False
        self.capture.release()

    def update_frame(self):
        while self.capture.isOpened() and self.running:
            success, frame = self.capture.read()
            if not success:
                continue

            # フレームをRGBに変換して親密度を計算
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(frame_rgb)

            affinity = 0.0
            if results.multi_face_landmarks and len(results.multi_face_landmarks) == 2:
                face1 = results.multi_face_landmarks[0]
                face2 = results.multi_face_landmarks[1]

                smile1 = calculate_smile_score(face1)
                smile2 = calculate_smile_score(face2)
                gaze1 = calculate_gaze_direction(face1)
                gaze2 = calculate_gaze_direction(face2)
                gaze_match = calculate_gaze_match(gaze1, gaze2)
                mirroring = calculate_mirroring_score(face1, face2)
                center1 = calculate_face_center(face1)
                center2 = calculate_face_center(face2)
                distance = calculate_physical_distance(center1, center2)
                distance_score = calculate_distance_score(distance)

                affinity = calculate_affinity(smile1, smile2, gaze_match, mirroring, distance_score)

            # フレームのエンコードと更新
            retval, buffer = cv2.imencode(".jpg", frame)
            data = base64.b64encode(buffer).decode()
            self.image_control.src_base64 = data
            self.affinity_text.value = f"親密度: {affinity:.2f}"
            value = int(affinity)
            if value != 0:
                with open("spotApp/friendly.csv", mdoe='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(value)
            print(self.affinity_text.value)
            self.update()
            sleep(self.latency)

    def build(self):
        self.image_control = ft.Image(width=840, height=600, fit=ft.ImageFit.FIT_WIDTH)
        self.affinity_text = ft.Text(value="親密度: 計算中...", size=20)
        return ft.Column(controls=[self.image_control, self.affinity_text])

#---
#コレクションデータの取り方
#data = nowToken.get().to_dict()
#name = data.get("name")

#------
#メイン関数
#------
def main(page: ft.Page):
    #------
    #画面サイズ変数
    #------
    #macBookは1470*956
    #FullHDは1920*1080
    WIDTH = 1920
    HEIGHT = 1080
    BAR_HEIGHT = HEIGHT * 0.08

    page.title = "NeoTama SpotApp"
    page.window_minimizable = False
    page.window_maximizable = True
    page.window_resizable = True
    page.window_full_screen = True
    page.window_always_on_top = False
    page.window_prevent_close = True
    page.fonts = {
        "button": "spotApp/DotGothic16-Regular.ttf",
        "maru": "spotApp/MPLUSRounded1c-Medium.ttf",
        "title": "spotApp/DelaGothicOne-Regular.ttf",
    }
    def monitor_clap(callback_function):
        while True:
            if callback_function():  # 関数を呼び出して結果がTrueかどうか確認
                break
        open_4_mikuji()

    def monitor_friendly(callback_function):
        while True:
            if callback_function():  # 関数を呼び出して結果がTrueかどうか確認
                break
        open_3_photo()

    #------
    #各パーツの定義
    #------
    top_image = ft.Image(
        src="neotama_logo.png",
        height=HEIGHT*0.75
    )
    qr = ft.Image(
        src="qr.png",
        height=HEIGHT*0.6
    )
    exchange = ft.Image(
        src="exchange.png",
        height=HEIGHT*0.55
    )
    gakaku = ft.Image(
        src="photo.jpg",
        height=HEIGHT*0.55
    )
    music = ft.Audio(src="musicKosuke.mp3", autoplay=True)
    mikuji_result = ft.Image(
        src="mikuji_result.jpg",
        height=HEIGHT*0.6
    )
    clap = ft.Image(
        src="clap.gif",
        height=HEIGHT*0.55
    )

    #-----
    #画面表示部
    #------
    def route_change(e):
        page.views.clear()

        #00/トップページ
        page.views.append(
            ft.View(
                "/",
                [
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                top_image,
                                qr
                            ],alignment=ft.MainAxisAlignment.CENTER),
                            ft.Row([
                                ft.ElevatedButton(
                                    content=ft.Text(
                                        "スタート！",
                                        size=70,
                                        font_family="button"
                                    ),
                                    width=500,
                                    height=100,
                                    on_click=open_2_exchange
                                )
                            ],alignment=ft.MainAxisAlignment.CENTER),
                            ft.Row([
                                ft.ElevatedButton(
                                    content=ft.Text(
                                        "終了",
                                        size=25,
                                        font_family="button"
                                    ),
                                    width=120,
                                    height=80,
                                    on_click=exit_app
                                )
                            ],alignment=ft.MainAxisAlignment.START),
                        ],alignment=ft.MainAxisAlignment.CENTER, spacing=0),
                        width=WIDTH,
                        height=HEIGHT
                    )
                ],
                bgcolor=ft.Colors.GREEN_ACCENT_100
            )
        )

        if page.route == "/01_token":
            page.views.append(
                ft.View(
                    "/01_token",
                    [
                        page.appbar,
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(
                                        "トークンをウェアプリで入力してください",
                                        size=60,
                                        color=ft.colors.BLACK,
                                        font_family="maru",
                                        weight=ft.FontWeight.W_900
                                    )
                                ]),
                                ft.Row([
                                    ft.Text(
                                        "(ウェブアプリで操作完了後に次へを押してください。",
                                        size=30,
                                        color=ft.colors.BLACK,
                                        font_family="maru",
                                        weight=ft.FontWeight.W_100
                                    )
                                ]),
                                ft.Row([
                                    qr,
                                    ft.Text(
                                        global_token,
                                        size=250,
                                        color=ft.colors.BLACK,
                                        font_family="title"
                                    )
                                ], ft.MainAxisAlignment.CENTER),
                                ft.Row([
                                    ft.ElevatedButton(
                                        content=ft.Text(
                                            "次へ進む",
                                            size=70,
                                            font_family="button"
                                        ),
                                        width=450,
                                        height=95,
                                        on_click=open_1_token2
                                    )
                                ], alignment=ft.MainAxisAlignment.CENTER),
                                ft.Row([
                                    ft.ElevatedButton(
                                    content=ft.Text(
                                        "もどる",
                                        size=25,
                                        font_family="button"
                                    ),
                                    width=120,
                                    height=75,
                                    on_click=open_4_mikuji_e
                                )
                                ], ft.MainAxisAlignment.START),
                            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                            width=WIDTH,
                            height=HEIGHT-BAR_HEIGHT
                        )
                    ],
                    bgcolor=ft.Colors.GREEN_ACCENT_100
                )
            )

        if page.route == "/01_token2":
            page.views.append(
                ft.View(
                    "/01_token2",
                    [
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.ElevatedButton(
                                    content=ft.Text(
                                        "初めから",
                                        size=25,
                                        font_family="maru"
                                    ),
                                    width=120,
                                    height=80,
                                    on_click=open_00_top
                                )
                                ], ft.MainAxisAlignment.END),
                                ft.Row([
                                    ft.Text(
                                        "2人目：トークンをウェアプリで入力してください",
                                        size=60,
                                        color=ft.colors.BLACK,
                                        font_family="maru",
                                        weight=ft.FontWeight.W_900
                                    )
                                ]),
                                ft.Row([
                                    ft.Text(
                                        "(入力しなくても先には進めます)",
                                        size=30,
                                        color=ft.colors.BLACK,
                                        font_family="maru",
                                        weight=ft.FontWeight.W_100
                                    )
                                ]),
                                ft.Row([
                                    qr,
                                    ft.Text(
                                        global_token2,
                                        size=250,
                                        color=ft.colors.BLACK,
                                        font_family="title"
                                    )
                                ], ft.MainAxisAlignment.CENTER),
                                ft.Row([
                                    ft.ElevatedButton(
                                        content=ft.Text(
                                            "次へ進む",
                                            size=70,
                                            font_family="button"
                                        ),
                                        width=450,
                                        height=100,
                                        on_click=open_2_exchange
                                    )
                                ], alignment=ft.MainAxisAlignment.CENTER)
                            ], alignment=ft.MainAxisAlignment.START),
                            width=WIDTH,
                            height=HEIGHT
                        )
                    ],
                    bgcolor=ft.Colors.GREEN_ACCENT_100
                )
            )

        #お年玉投入＆すだれダウン
        if page.route == "/02_exchange":
            page.views.append(
                ft.View(
                    "/02_exchange",
                    [
                        page.appbar,
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(
                                        "お年玉をボックスの中に入れてください",
                                        size=60,
                                        color=ft.colors.BLACK,
                                        font_family="maru",
                                        weight=ft.FontWeight.W_900
                                    )
                                ]),
                                ft.Row([
                                    ft.Text(
                                        "(入れたらボタンを押して少し待ってね)",
                                        size=30,
                                        color=ft.colors.BLACK,
                                        font_family="maru",
                                        weight=ft.FontWeight.W_100
                                    )
                                ]),
                                ft.Row([
                                    exchange
                                ], ft.MainAxisAlignment.CENTER),
                                ft.Row([
                                    ft.ElevatedButton(
                                        content=ft.Text(
                                            "次へ進む",
                                            size=70,
                                            font_family="button"
                                        ),
                                        width=450,
                                        height=100,
                                        on_click=open_3_photo
                                    )
                                ], alignment=ft.MainAxisAlignment.CENTER),
                                ft.Row([
                                    ft.ElevatedButton(
                                    content=ft.Text(
                                        "もどる",
                                        size=25,
                                        font_family="button"
                                    ),
                                    width=120,
                                    height=80,
                                    on_click=open_00_top
                                )
                                ], alignment=ft.MainAxisAlignment.START),
                            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                            width=WIDTH,
                            height=HEIGHT - BAR_HEIGHT
                        )
                    ],
                    bgcolor=ft.Colors.GREEN_ACCENT_100
                )
            )

        #拍手検知
        if page.route == "/03_photo":
            #take_photo(),
            music.release(),
            threading.Thread(target=monitor_clap, args=(wait_hands_clap,), daemon=True).start()
            page.views.append(
                ft.View(
                    "/03_photo",
                    [
                        page.appbar,
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(
                                        "てを2回たたいてみよう！",
                                        size=60,
                                        color=ft.colors.BLACK,
                                        font_family="maru",
                                        weight=ft.FontWeight.W_900
                                    )
                                ]),
                                ft.Row([
                                    ft.Text(
                                        "タイミングよくたたいてね",
                                        size=30,
                                        color=ft.colors.BLACK,
                                        font_family="maru",
                                        weight=ft.FontWeight.W_900
                                    )
                                ]),
                                ft.Row([
                                    clap
                                ], alignment=ft.MainAxisAlignment.CENTER),
                                ft.Row([
                                    ft.ElevatedButton(
                                    content=ft.Text(
                                        "もどる",
                                        size=25,
                                        font_family="button"
                                    ),
                                    width=120,
                                    height=80,
                                    on_click=open_2_exchange
                                )
                                ], alignment=ft.MainAxisAlignment.START),
                            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                            width=WIDTH,
                            height=HEIGHT - BAR_HEIGHT
                        )
                    ],
                    bgcolor=ft.colors.GREEN_ACCENT_100
                )
            )

        if page.route == "/04_mikuji":
            camera_control = CameraCaptureControl()
            page.views.append(
                ft.View(
                    "/04_mikuji",
                    [
                        page.appbar,
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(
                                        "写真を撮りましょう！",
                                        size=60,
                                        color=ft.colors.BLACK,
                                        font_family="maru",
                                        weight=ft.FontWeight.W_900
                                    )
                                ]),
                                ft.Row([
                                    ft.Text(
                                        "2人の親密度をはかります",
                                        size=30,
                                        color=ft.colors.BLACK,
                                        font_family="maru",
                                        weight=ft.FontWeight.W_900
                                    )
                                ]),
                                ft.Row([
                                    camera_control
                                ], alignment=ft.MainAxisAlignment.CENTER),
                                ft.Row([
                                    ft.ElevatedButton(
                                        content=ft.Text(
                                            "撮影開始！",
                                            size=70,
                                            font_family="button"
                                        ),
                                        width=1000,
                                        height=100,
                                        on_click=open_5_friendly
                                    )
                                ], alignment=ft.MainAxisAlignment.CENTER),
                                ft.Row([
                                    ft.ElevatedButton(
                                    content=ft.Text(
                                        "もどる",
                                        size=25,
                                        font_family="button"
                                    ),
                                    width=120,
                                    height=80,
                                    on_click=open_3_photo
                                )
                                ], alignment=ft.MainAxisAlignment.START),
                            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                            width=WIDTH,
                            height=HEIGHT - BAR_HEIGHT
                        )
                    ],
                    bgcolor=ft.colors.GREEN_ACCENT_100
                )
            )
            page.update()

        if page.route == "/05_friendly":
            friendly_score= FriendlyApp()
            page.views.append(
                ft.View(
                    "/05_friendly",
                    [
                        page.appbar,
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(
                                        "測定中！",
                                        size=60,
                                        color=ft.colors.BLACK,
                                        font_family="maru",
                                        weight=ft.FontWeight.W_900
                                    )
                                ]),
                                ft.Row([
                                    ft.Text(
                                        "2人の親密度をはかります",
                                        size=30,
                                        color=ft.colors.BLACK,
                                        font_family="maru",
                                        weight=ft.FontWeight.W_900
                                    )
                                ]),
                                ft.Row([
                                    friendly_score
                                ], alignment=ft.MainAxisAlignment.CENTER),
                                ft.Row([
                                    ft.ElevatedButton(
                                    content=ft.Text(
                                        "もどる",
                                        size=25,
                                        font_family="button"
                                    ),
                                    width=120,
                                    height=80,
                                    on_click=open_4_mikuji_e
                                )
                                ], alignment=ft.MainAxisAlignment.START),
                            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                            width=WIDTH,
                            height=HEIGHT - BAR_HEIGHT
                        )
                    ],
                    bgcolor=ft.colors.GREEN_ACCENT_100
                )
            )
            page.update()
            tm_gm = threading.Timer(5, lambda: open_6_completed())
            tm_gm.start()

        #戻るボタン未実装
        if page.route == "/06_completed":
            page.views.append(
                ft.View(
                    "/06_completed",
                    [
                        page.appbar,
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(
                                        "測定完了！",
                                        size=60,
                                        color=ft.colors.BLACK,
                                        font_family="maru",
                                        weight=ft.FontWeight.W_900
                                    )
                                ]),
                                ft.Row([
                                    ft.Text(
                                        "2人の親密度をはかります",
                                        size=30,
                                        color=ft.colors.BLACK,
                                        font_family="maru",
                                        weight=ft.FontWeight.W_900
                                    )
                                ]),
                                ft.Row([
                                    ft.ElevatedButton(
                                        content=ft.Text(
                                            "撮影開始！",
                                            size=70,
                                            font_family="button"
                                        ),
                                        width=1000,
                                        height=100,
                                        on_click=open_1_token
                                    )
                                ], alignment=ft.MainAxisAlignment.CENTER),
                                ft.Row([
                                    ft.ElevatedButton(
                                    content=ft.Text(
                                        "もどる",
                                        size=25,
                                        font_family="button"
                                    ),
                                    width=120,
                                    height=80,
                                    on_click=open_4_mikuji_e
                                )
                                ], alignment=ft.MainAxisAlignment.START),
                            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                            width=WIDTH,
                            height=HEIGHT - BAR_HEIGHT
                        )
                    ],
                    bgcolor=ft.colors.GREEN_ACCENT_100
                )
            )

        page.update()
        update_appbar()

    #------
    #ページのルーティング
    #------
    #終了
    def exit_app(e):
        page.window.destroy()

    #現在のページを削除して前のページに戻る
    def view_pop(e):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)
    
    #TOPページへ戻る
    def open_00_top(e):
        page.views.pop()
        top_view = page.views[0]
        music.release()
        page.go(top_view.route)

    #トークン発行画面
    def open_1_token(e):
        delete_all_documents_in_collection("Hard")
        global global_token
        global_token = rnd.randint(1000, 9999)
        data={"display_name": "", "id": "", "time_stamp": "", "url": ""}
        db.collection("Hard").document(str(global_token)).set(data)
        update_appbar()
        page.go("/01_token")

    #トークン発行画面
    def open_1_token2(e):
        global global_token2
        global_token2 = rnd.randint(1000, 9999)
        data={"display_name": "", "id": "", "time_stamp": "", "url": ""}
        db.collection("Hard").document(str(global_token2)).set(data)
        update_appbar()
        page.go("/01_token2")

    #交換画面
    def open_2_exchange(e):
        update_appbar()
        page.overlay.append(
            music
        )
        page.go("/02_exchange")

    #2ショット撮影
    def open_3_photo(e):
        page.go("/03_photo")

    #呪文検知、おみくじ結果出力
    def open_4_mikuji():
        page.go("/04_mikuji")

    #呪文検知、おみくじ結果出力
    def open_4_mikuji_e(e):
        page.go("/04_mikuji")

    #親密度計算
    def open_5_friendly(e):
        page.go("/05_friendly")

    #親密度結果
    def open_6_completed():
        page.go("/06_completed")

    #------
    #イベントの登録
    #------
    page.on_route_change = route_change
    page.on_view_pop = view_pop

    #------
    #起動後の処理
    #------
    page.go(page.route)

    #------
    #ログイン時のAppBar
    #------
    # AppBar更新
    def update_appbar():
        global display_out
        global display_out2
        if global_token is None:
            display_out = "ゲスト"  # トークン未生成時のデフォルト
        else:
            display_out = get_user_display_name(global_token)
            if display_out == "":
                display_out = "ゲスト"
        if global_token2 is None:
            display_out2 = "ゲスト"  # トークン未生成時のデフォルト
        else:
            display_out2 = get_user_display_name(global_token2)
            if display_out2 == "":
                display_out2 = "ゲスト"

        page.appbar = ft.AppBar(
            leading=ft.Container(
                ft.Image(src="NeoTama.png", height=BAR_HEIGHT, fit=ft.ImageFit.CONTAIN),
                margin=ft.margin.only(left=10)
            ),
            toolbar_height=BAR_HEIGHT,
            bgcolor=ft.colors.GREEN_ACCENT_200,
            title=ft.Row([
                ft.Text("ネオたま", font_family="title", color=ft.colors.BLACK, size=40, weight=ft.FontWeight.W_900)
            ])
        )
        page.update()

    
ft.app(target=main)

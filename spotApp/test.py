import flet as ft
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
import random as rnd

# Firebase 初期設定
cred = credentials.Certificate("spotApp/token.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# グローバル変数
global_token = None  # 現在のトークン番号

# Firebaseのドキュメント作成の前処理
data = {"display_name": "デフォルト名", "id": "", "time_stamp": "", "url": ""}

# Hardコレクションのデータを全て削除する
def delete_all_documents_in_collection(collection_name):
    docs = db.collection(collection_name).stream()
    for doc in docs:
        db.collection(collection_name).document(doc.id).delete()

# Firebaseからユーザーの表示名を取得する関数
def get_user_display_name(token):
    try:
        doc_ref = db.collection("Hard").document(str(token))
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            return data.get("display_name", "未登録")
        else:
            return "未登録"
    except Exception as e:
        print(f"Error fetching data: {e}")
        return "エラー"

# メイン関数
def main(page: ft.Page):
    global global_token

    # 画面サイズ
    WIDTH = 1920
    HEIGHT = 1080
    BAR_HEIGHT = HEIGHT * 0.08

    # ページ設定
    page.title = "NeoTama SpotApp"
    page.window_full_screen = True
    page.fonts = {
        "font": "/Users/hiratasoma/Documents/NeoTama_hackukosen2024/spotApp/DotGothic16-Regular.ttf",
        "maru": "/Users/hiratasoma/Documents/NeoTama_hackukosen2024/spotApp/MPLUSRounded1c-Regular.ttf",
        "title": "/Users/hiratasoma/Documents/NeoTama_hackukosen2024/spotApp/DelaGothicOne-Regular.ttf",
        "button": "/Users/hiratasoma/Documents/NeoTama_hackukosen2024/spotApp/YujiMai-Regular.ttf"
    }

    # 画像
    top_image = ft.Image(src="neotama_logo.png", height=HEIGHT * 0.75)
    qr = ft.Image(src="qr.png", height=HEIGHT * 0.6)
    exchange = ft.Image(src="exchange.png", height=HEIGHT * 0.6)

    # AppBar更新
    def update_appbar():
        display_name = get_user_display_name(global_token)
        page.appbar = ft.AppBar(
            leading=ft.Container(
                ft.Image(src="NeoTama.png", height=BAR_HEIGHT, fit=ft.ImageFit.CONTAIN),
                margin=ft.margin.only(left=10)
            ),
            toolbar_height=BAR_HEIGHT,
            bgcolor=ft.colors.GREEN_ACCENT_200,
            title=ft.Row([
                ft.Text("ネオたま", font_family="title", color=ft.colors.BLACK, size=40, weight=ft.FontWeight.W_900),
                ft.Text(f"{global_token} さん ({display_name})", font_family="font", color=ft.colors.BLACK, size=40)
            ])
        )
        page.update()

    # ページ遷移
    def route_change(e):
        page.views.clear()
        if page.route == "/":
            page.views.append(
                ft.View(
                    "/",
                    [
                        ft.Container(
                            content=ft.Column([
                                ft.Row([top_image, qr], alignment=ft.MainAxisAlignment.CENTER),
                                ft.Row([
                                    ft.ElevatedButton(
                                        content=ft.Text("交換を始める", size=70, font_family="button"),
                                        width=500, height=100, on_click=open_1_token
                                    )
                                ], alignment=ft.MainAxisAlignment.CENTER)
                            ], alignment=ft.MainAxisAlignment.CENTER)
                        )
                    ],
                    bgcolor=ft.colors.GREEN_ACCENT_100
                )
            )
        elif page.route == "/01_token":
            delete_all_documents_in_collection("Hard")
            global_token = rnd.randint(1000, 9999)
            db.collection("Hard").document(str(global_token)).set(data)
            page.views.append(
                ft.View(
                    "/01_token",
                    [
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.ElevatedButton(
                                        content=ft.Text("もどる", size=25, font_family="maru"),
                                        width=120, height=80, on_click=open_00_top
                                    )
                                ], alignment=ft.MainAxisAlignment.END),
                                ft.Row([ft.Text("トークンをウェアプリで入力してください", size=60, font_family="maru")]),
                                ft.Row([ft.Text("(入力しなくても先には進めます)", size=30, font_family="maru")]),
                                ft.Row([qr, ft.Text(str(global_token), size=250, font_family="title")], ft.MainAxisAlignment.CENTER),
                                ft.Row([
                                    ft.ElevatedButton(
                                        content=ft.Text("次へ進む", size=70, font_family="button"),
                                        width=450, height=100, on_click=open_2_exchange
                                    )
                                ], alignment=ft.MainAxisAlignment.CENTER)
                            ])
                        )
                    ],
                    bgcolor=ft.colors.GREEN_ACCENT_100
                )
            )
        elif page.route == "/02_exchange":
            page.views.append(
                ft.View(
                    "/02_exchange",
                    [
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.ElevatedButton(
                                        content=ft.Text("もどる", size=25, font_family="maru"),
                                        width=120, height=80, on_click=open_1_token
                                    )
                                ], alignment=ft.MainAxisAlignment.END),
                                ft.Row([exchange], alignment=ft.MainAxisAlignment.CENTER)
                            ])
                        )
                    ],
                    bgcolor=ft.colors.GREEN_ACCENT_100
                )
            )
        update_appbar()

    def view_pop(e):
        page.views.pop()
        page.go(page.views[-1].route)

    def open_00_top(e):
        page.views.pop()
        page.go("/")

    def open_1_token(e):
        page.go("/01_token")

    def open_2_exchange(e):
        page.go("/02_exchange")

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

ft.app(target=main)

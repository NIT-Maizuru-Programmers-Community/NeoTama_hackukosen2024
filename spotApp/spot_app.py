import flet as ft
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
import random as rnd

#------
#Firebase初期設定
#------
cred = credentials.Certificate("spotApp/token.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
# FirebaseのドキュメントIDを指定
nowToken = db.collection("Hard").document("token")

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
    page.window_always_on_top = True
    page.fonts = {
        "font": "/Users/hiratasoma/Documents/NeoTama_hackukosen2024/spotApp/DotGothic16-Regular.ttf",
        "maru": "/Users/hiratasoma/Documents/NeoTama_hackukosen2024/spotApp/MPLUSRounded1c-Regular.ttf",
        "title": "/Users/hiratasoma/Documents/NeoTama_hackukosen2024/spotApp/DelaGothicOne-Regular.ttf",
        "button": "/Users/hiratasoma/Documents/NeoTama_hackukosen2024/spotApp/YujiMai-Regular.ttf"
    }

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

    #------
    #ログイン時のAppBar
    #------
    page.appbar = ft.AppBar(
        leading=ft.Container(
            ft.Image(src="NeoTama.png", height=BAR_HEIGHT, fit=ft.ImageFit.CONTAIN),
            margin=ft.margin.only(left=10, top=0, bottom=0),
            padding=0
        ),
        toolbar_height=BAR_HEIGHT,
        bgcolor=ft.colors.GREEN_ACCENT_200,
        title=ft.Row([
            ft.Text(
                "ネオたま—お年玉v2.0—",
                font_family="title",
                color=ft.colors.BLACK,
                size=40,
                weight=ft.FontWeight.W_900
            )
        ])
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
                                        "交換を始める",
                                        size=50,
                                        font_family="button"
                                    ),
                                    height=80,
                                    on_click=open_1_token
                                )
                            ],alignment=ft.MainAxisAlignment.CENTER)
                        ],alignment=ft.MainAxisAlignment.CENTER, spacing=0),
                        width=WIDTH,
                        height=HEIGHT
                    )
                ],
                bgcolor=ft.Colors.GREEN_ACCENT_100
            )
        )

        if page.route == "/01_token":
            #トークン生成
            random = rnd.randint(1000,9999)
            page.views.append(
                ft.View(
                    "/01_token",
                    [
                        page.appbar,
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(
                                        "トークンを入力してください"
                                    )
                                ])
                            ])
                        )
                    ],
                    bgcolor=ft.Colors.GREEN_ACCENT_100
                )
            )

        page.update()

    #------
    #ページのルーティング
    #------
    #現在のページを削除して前のページに戻る
    def view_pop(e):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)
    
    #TOPページへ戻る
    def open_00_top(e):
        page.views.pop()
        top_view = page.views[0]
        page.go(top_view.route)

    #トークン発行画面
    def open_1_token(e):
        page.go("/01_token")

    #------
    #イベントの登録
    #------
    page.on_route_change = route_change
    page.on_view_pop = view_pop

    #------
    #起動後の処理
    #------
    page.go(page.route)
    
ft.app(target=main)        
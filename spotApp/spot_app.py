import flet as ft
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
import random as rnd
from camera import take_photo

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
data={"display_name": "", "id": "", "time_stamp": "", "url": ""}

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
    exchange = ft.Image(
        src="exchange.png",
        height=HEIGHT*0.55
    )
    gakaku = ft.Image(
        src="photo.jpg",
        height=HEIGHT*0.55
    )
    music = ft.Audio(src="musicKosuke.mp3", autoplay=True)

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
                                        size=70,
                                        font_family="button"
                                    ),
                                    width=500,
                                    height=100,
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
            page.views.append(
                ft.View(
                    "/01_token",
                    [
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.ElevatedButton(
                                    content=ft.Text(
                                        "もどる",
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
                                        "1人目：トークンをウェアプリで入力してください",
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
                                        height=100,
                                        on_click=open_1_token2
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
                                        "交換し合うものをボックスの中に入れてね",
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
                                        font_family="maru"
                                    ),
                                    width=120,
                                    height=80,
                                    on_click=open_1_token
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

        if page.route == "/03_photo":
            take_photo(),
            music.release(),
            page.views.append(
                ft.View(
                    "/03_photo",
                    [
                        page.appbar,
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(
                                        "写真を撮ります",
                                        size=60,
                                        color=ft.colors.BLACK,
                                        font_family="maru",
                                        weight=ft.FontWeight.W_900
                                    )
                                ]),
                                ft.Row([
                                    ft.Text(
                                        "カメラの画角に収まってね(ボタンを押すとカウントダウンが始まります)",
                                        size=30,
                                        color=ft.colors.BLACK,
                                        font_family="maru",
                                        weight=ft.FontWeight.W_900
                                    )
                                ]),
                                ft.Row([
                                    gakaku
                                ], alignment=ft.MainAxisAlignment.CENTER),
                                ft.Row([
                                    ft.ElevatedButton(
                                        content=ft.Text(
                                            "撮影する！",
                                            size=70,
                                            font_family="button"
                                        ),
                                        width=450,
                                        height=100,
                                        #on_click=open_3_photo
                                    )
                                ], alignment=ft.MainAxisAlignment.CENTER),
                                ft.Row([
                                    ft.ElevatedButton(
                                    content=ft.Text(
                                        "もどる",
                                        size=25,
                                        font_family="maru"
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

        page.update()
        update_appbar()

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
                ft.Text("ネオたま", font_family="title", color=ft.colors.BLACK, size=40, weight=ft.FontWeight.W_900),
                ft.Text(f"{display_out}さん＆{display_out2}さん", font_family="font", color=ft.colors.BLACK, size=40)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )
        page.update()

    
ft.app(target=main)

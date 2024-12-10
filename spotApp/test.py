import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials

# Firebase初期設定
cred = credentials.Certificate("spotApp/token.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# FirebaseのドキュメントIDを指定
nowToken = db.collection("Hard").document("token")

try:
    # データの取得
    doc = nowToken.get()
    if doc.exists:
        data = doc.to_dict()
        name = data.get("name", "名前が設定されていません")
        print("取得した名前:", name)
    else:
        print("指定されたドキュメントは存在しません。")
except Exception as e:
    print(f"エラーが発生しました: {e}")

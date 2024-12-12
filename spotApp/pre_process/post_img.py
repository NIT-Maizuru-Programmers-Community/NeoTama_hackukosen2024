import requests

def upload_image(image_path, server_url):
    with open(image_path, 'rb') as img:
        files = {'file': img}
        response = requests.post(server_url, files=files)
    return response

# 例: 画像のアップロード
image_path = "/Users/hiratasoma/Documents/NeoTama_hackukosen2024/spotApp/test_program/mikuji_result.jpg"
server_url = "http://tk2-109-55757.vs.sakura.ne.jp//upload.php"
response = upload_image(image_path, server_url)

if response.status_code == 200:
    print("Upload successful!")
    print("Image URL:", response.text)  # サーバーから画像URLを返す
else:
    print("Upload failed:", response.status_code)

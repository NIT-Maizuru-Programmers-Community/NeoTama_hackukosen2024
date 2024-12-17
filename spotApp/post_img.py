import requests

def upload_image(image_path, server_url):
    with open(image_path, 'rb') as img:
        files = {'file': img}
        response = requests.post(server_url, files=files)
    return response

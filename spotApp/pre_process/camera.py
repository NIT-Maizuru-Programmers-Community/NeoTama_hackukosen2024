import cv2

camera_index = 0  # USBカメラのインデックス
cap = cv2.VideoCapture(camera_index)

if not cap.isOpened():
    print(f"Failed to open camera with index {camera_index}")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    cv2.imshow("USB Camera", frame)

    # 'q'キーで終了
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

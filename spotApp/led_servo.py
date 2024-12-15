import serial
import time

# シリアルポートの設定
ser = serial.Serial('COM3', 9600)

def led_servo(command):
    time.sleep(2)

    # コマンドを送信
    ser.write(str(command).encode())

    # 応答を取得
    try:
        raw_response = ser.readline()
        response = raw_response.decode('utf-8', errors='replace').strip()  # 'replace'でデコード不能な文字を置換
        print("Response:", response)
    except Exception as e:
        print("Error decoding response:", e)



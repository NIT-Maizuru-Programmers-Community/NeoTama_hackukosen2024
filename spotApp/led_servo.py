# Python バージョン
# Python 3.12.3

# 導入ライブラリ
# pyserial 3.5
# time python ver 3.7以上に標準搭載

#Code

import serial
import time

def send_command(ser, command):
    ser.write(command.encode())
    print(f"Sent: {command}")

def led_servo(command):
    # シリアルポートの設定
    port = "COM3"  # 適切なポートを指定
    baudrate = 9600

    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # シリアル通信の初期化待ち
        print(f"Connected to {port} at {baudrate} baud.")
    except serial.SerialException as e:
        print(f"Failed to connect: {e}")
        return

    print("1: 赤色LED\n2: 青色LED\n3: 緑色LED\n4: 虹色アニメーション\nq: LED消灯 (終了)\n8: サーボを開く\n9: サーボを閉じる")

    if command in ['1', '2', '3', '4', 'q', '8', '9']:
        send_command(ser, command)
        response = ser.readline().decode().strip()
        if response:
            print(f"Received: {response}")
        if command == 'q':
            print("終了します。")
    elif command.lower() == 'exit':
        print("終了します。")
    else:
        print("無効なコマンドです。有効なコマンドを入力してください。")

    ser.close()

#if __name__ == "__main__":
#    main()

main('q')
import serial
import time
import csv
import os

def send_command(ser, command):
    ser.write(command.encode())
    print(f"Sent: {command}")

def read_csv(file_path):
    """CSVファイルの内容をリストとして返す"""
    with open(file_path, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        return [row[0].strip() for row in reader if row]  # 空行をスキップしてリスト化

def main():
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

    # CSVファイルのパス
    csv_file = "judge.csv"
    
    # 最初のCSVファイルの内容を読み込む
    last_content = read_csv(csv_file)
    last_mod_time = os.path.getmtime(csv_file)  # 最後の変更時刻を取得
    
    while True:
        # CSVファイルの変更時刻を確認
        current_mod_time = os.path.getmtime(csv_file)
        
        if current_mod_time > last_mod_time:
            # ファイルが変更されていた場合
            print("CSVファイルが変更されました。処理を開始します。")
            last_mod_time = current_mod_time  # 最後の変更時刻を更新

            # 新しい内容を読み込み
            current_content = read_csv(csv_file)
            if current_content != last_content:
                # 内容が変更された場合のみ実行
                for command in current_content:
                    if command in ['1', '2', '3', '4', 'q', '8', '9']:
                        send_command(ser, command)
                        response = ser.readline().decode().strip()
                        if response:
                            print(f"Received: {response}")

                        if command == 'q':
                            print("終了コマンドを受信。プログラムを終了します。")
                            break
                    else:
                        print(f"無効なコマンドです: {command}")

                # 新しい内容を記録
                last_content = current_content

        time.sleep(1)  # 1秒ごとにファイルの変更を監視

    ser.close()

if __name__ == "__main__":
    main()

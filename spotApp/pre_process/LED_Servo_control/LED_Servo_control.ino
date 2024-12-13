/*Arduino Code
Arduino IDE 2.3.3

ライブラリ
Adafruit NeoPixel 1.12.3
*/


#include <Adafruit_NeoPixel.h>

// === LED制御設定 ===
#define LED_PIN 6          // NeoPixel接続ピン
#define NUM_PIXELS 60      // LEDの数
#define BRIGHTNESS 50      // 明るさ (0~255)

// === サーボ制御設定 ===
const int IN1 = 3;        // IN1ピンをD3に
const int IN2 = 4;        // IN2ピンをD4に

// === グローバル変数 ===
Adafruit_NeoPixel pixels(NUM_PIXELS, LED_PIN, NEO_GRB + NEO_KHZ800);
uint32_t currentColor = pixels.Color(0, 0, 0); // 現在の色（デフォルトは消灯）
bool isOpen = false;      // 現在の状態を追跡するフラグ（false: 閉、true: 開）
bool isRainbow = false;   // 虹色アニメーションのフラグ

void setup() {
  // シリアル通信の初期化
  Serial.begin(9600);

  // LEDピンの初期化
  pixels.begin();
  pixels.setBrightness(BRIGHTNESS);
  setAllPixels(currentColor); // 初期状態を適用

  // サーボピンの初期化
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);

  Serial.println("セットアップ完了: LEDおよびサーボ制御が可能です。");
}

void loop() {
  if (Serial.available() > 0) {        // シリアル通信でデータが送られてきた場合
    char command = Serial.read();     // 1文字を読み取る

    // LED制御コマンド
    if (command == '1' || command == '2' || command == '3' || command == 'q' || command == '4') {
      changeColor(command);
    }
    // サーボ制御コマンド
    else if (command == '8') {
      if (!isOpen) {                  // 現在閉じている場合のみ実行
        Serial.println("『あける』動作を開始します。");
        open();
        isOpen = true;                // 状態を「開」に更新
      } else {
        Serial.println("すでに開いています。同じ操作は無効です。");
      }
    } else if (command == '9') {
      if (isOpen) {                   // 現在開いている場合のみ実行
        Serial.println("『とじる』動作を開始します。");
        close();
        isOpen = false;               // 状態を「閉」に更新
      } else {
        Serial.println("すでに閉じています。同じ操作は無効です。");
      }
    } else {
      Serial.println("無効な入力です。有効なコマンドを入力してください。");
    }
  }

  // 虹色アニメーションが有効な場合
  if (isRainbow) {
    showRainbowCycle(10); // 虹色アニメーションを実行
  }
}

// === LED制御関数 ===
void changeColor(char command) {
  // コマンドに応じた色を設定
  switch (command) {
    case '1': 
      currentColor = pixels.Color(255, 0, 0); // 赤
      isRainbow = false;
      break;
    case '2': 
      currentColor = pixels.Color(0, 0, 255); // 青
      isRainbow = false;
      break;
    case '3': 
      currentColor = pixels.Color(0, 255, 0); // 緑
      isRainbow = false;
      break;
    case 'q': 
      currentColor = pixels.Color(0, 0, 0); // 消灯
      isRainbow = false;
      break;
    case '4': 
      isRainbow = true;  // 虹色アニメーションを有効化
      Serial.println("虹色アニメーションを開始します。");
      return;
    default: 
      return; // 無効なコマンドの場合は何もしない
  }

  setAllPixels(currentColor); // 全LEDの色を更新
}

void setAllPixels(uint32_t color) {
  for (int i = 0; i < NUM_PIXELS; i++) {
    pixels.setPixelColor(i, color);
  }
  pixels.show();
}

// === サーボ制御関数 ===
void open() {
  digitalWrite(IN1, HIGH); 
  digitalWrite(IN2, LOW);
  delay(5100);                        // 5.5秒動作

  digitalWrite(IN1, LOW); 
  digitalWrite(IN2, LOW);
  delay(2000);                        // 停止状態で2秒待機
}

void close() {
  digitalWrite(LED_BUILTIN, HIGH);    // LEDを点灯
  digitalWrite(IN1, LOW); 
  digitalWrite(IN2, HIGH);
  delay(5050);                        // 5.6秒動作

  digitalWrite(LED_BUILTIN, LOW);     // LEDを消灯
  digitalWrite(IN1, LOW); 
  digitalWrite(IN2, LOW);
  delay(2000);                        // 停止状態で2秒待機
}

// === 虹色アニメーション関数 ===
void showRainbowCycle(int delayMs) {
  static uint16_t j = 0;  // アニメーションの進行状態
  for (int i = 0; i < NUM_PIXELS; i++) {
    uint32_t color = Wheel((i * 256 / NUM_PIXELS + j) & 255);
    pixels.setPixelColor(i, color);
  }
  pixels.show();
  j = (j + 1) & 255;  // 進行を更新
  delay(delayMs);
}

// === RGB値を取得するヘルパー関数 ===
uint32_t Wheel(byte WheelPos) {
  WheelPos = 255 - WheelPos;
  if (WheelPos < 85) {
    return pixels.Color(255 - WheelPos * 3, 0, WheelPos * 3);
  } else if (WheelPos < 170) {
    WheelPos -= 85;
    return pixels.Color(0, WheelPos * 3, 255 - WheelPos * 3);
  } else {
    WheelPos -= 170;
    return pixels.Color(WheelPos * 3, 255 - WheelPos * 3, 0);
  }
}

#define LED_COUNT 8
const int ledPins[LED_COUNT] = {2, 3, 4, 5, 6, 7, 8, A0}; // LED 핀 배열

void setup() {
  // 모든 LED 핀을 출력으로 설정하고 끔 (HIGH는 OFF)
  for (int i = 0; i < LED_COUNT; i++) {
    pinMode(ledPins[i], OUTPUT);
    digitalWrite(ledPins[i], HIGH); // 초기 상태 OFF
  }
  Serial.begin(9600); // 시리얼 통신 시작
}

void loop() {
  static String message = ""; // 초기값으로 빈 문자열

  if (Serial.available() > 0) {
    message = Serial.readString(); // 메시지 읽기
    message.trim(); // 공백 제거

    if (message == "0000") {
      for (int i = 0; i < LED_COUNT; i++) {
        digitalWrite(ledPins[i], HIGH); // 모든 LED ON
      }
    } else if (message == "1111") {
      for (int i = 0; i < LED_COUNT; i++) {
        digitalWrite(ledPins[i], LOW); // 모든 LED OFF
      }
    } else if (message == "1000") {
      for (int i = 0; i < LED_COUNT; i++) {
        digitalWrite(ledPins[i], (i == 4) ? LOW : HIGH); // LED1 OFF, 나머지 ON
      }
    } else if (message == "0100") {
      for (int i = 0; i < LED_COUNT; i++) {
        digitalWrite(ledPins[i], (i == 0) ? LOW : HIGH); // LED5 OFF, 나머지 ON
      }
    } else if (message == "0010") {
      for (int i = 0; i < LED_COUNT; i++) {
        digitalWrite(ledPins[i], (i == 6) ? LOW : HIGH); // LED8 OFF, 나머지 ON
      }
    } else if (message == "0001") {
      for (int i = 0; i < LED_COUNT; i++) {
        digitalWrite(ledPins[i], (i == 2) ? LOW : HIGH); // LED3 OFF, 나머지 ON
      }
    } else if (message == "1100") {
      for (int i = 0; i < LED_COUNT; i++) {
        digitalWrite(ledPins[i], (i == 0 || i == 4) ? LOW : HIGH); // LED1, LED5 OFF, 나머지 ON
      }
    } else if (message == "1010") {
      for (int i = 0; i < LED_COUNT; i++) {
        digitalWrite(ledPins[i], (i == 4 || i == 6) ? LOW : HIGH); // LED5, LED8 OFF, 나머지 ON
      }
    } else if (message == "1001") {
      for (int i = 0; i < LED_COUNT; i++) {
        digitalWrite(ledPins[i], (i == 2 || i == 4) ? LOW : HIGH); // LED3, LED5 OFF, 나머지 ON
      }
    } else if (message == "0110") {
      for (int i = 0; i < LED_COUNT; i++) {
        digitalWrite(ledPins[i], (i == 0 || i == 6) ? LOW : HIGH); // LED1, LED8 OFF, 나머지 ON
      }
    } else if (message == "0101") {
      for (int i = 0; i < LED_COUNT; i++) {
        digitalWrite(ledPins[i], (i >= 0 && i <= 3) ? LOW : HIGH); // LED1~LED4 OFF, 나머지 ON
      }
    } else if (message == "0011") {
      for (int i = 0; i < LED_COUNT; i++) {
        digitalWrite(ledPins[i], (i == 2 || i == 6) ? LOW : HIGH); // LED3, LED8 OFF, 나머지 ON
      }
    } else if (message == "1110") {
      for (int i = 0; i < LED_COUNT; i++) {
        digitalWrite(ledPins[i], (i == 0 || i == 4 || i == 6) ? LOW : HIGH); // 배열 기준 LED 2, 3, 6, 8 끄기 (LOW), 나머지 켜기 (HIGH)
      }
    } else if (message == "1101") {
      for (int i = 0; i < LED_COUNT; i++) {
        digitalWrite(ledPins[i], (i >= 0 && i <= 4) ? LOW : HIGH); // LED1~LED5 OFF, 나머지 ON
      }
    } else if (message == "1011") {
      for (int i = 0; i < LED_COUNT; i++) {
        digitalWrite(ledPins[i], (i == 2 || i == 4 || i == 6) ? LOW : HIGH); // LED3, LED5, LED8 OFF, 나머지 ON
      }
    } else if (message == "0111") {
      for (int i = 0; i < LED_COUNT; i++) {
        digitalWrite(ledPins[i], (i >= 0 && i <= 3 || i == 6) ? LOW : HIGH); // LED1~LED4, LED8 OFF, 나머지 ON
      }
    } 
  }
}


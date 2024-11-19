#include <Servo.h>
#include <SPI.h>
#include <MFRC522.h>
#include <LiquidCrystal.h>

#define SS_PIN_IN 9  // 입구 RFid
#define SS_PIN_RIGHT_1 8  // 오른쪽 1번 자리
#define SS_PIN_RIGHT_2 7  // 오른쪽 2번 자리
#define RST_PIN 10  // RFID 리셋 필

MFRC522 rfid_in(SS_PIN_IN, RST_PIN); // 입구 RFID 리더기
MFRC522 rfid_right_1(SS_PIN_RIGHT_1, RST_PIN); // 오른쪽 1번 자리 RFID 리더기
MFRC522 rfid_right_2(SS_PIN_RIGHT_2, RST_PIN); // 오른쪽 2번 자리 RFID 리더기
Servo myServo;

LiquidCrystal lcd(A0, A1, A2, A3, A4, A5);

unsigned long previousMillis = 0;
const long interval = 5000;
bool isGateOpen = false;
String lastRfidTag_in = "";
String lastRfidTag_right_1 = "";
String lastRfidTag_right_2 = "";
int count = 0;

void readRfidTag_in(MFRC522 &rfid) {
  // RFID 태깅 읽기
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    String rfidTag_in = "IN:";
    for (byte i = 0; i < rfid.uid.size; i++) {
      rfidTag_in += String(rfid.uid.uidByte[i], DEC);
      if (i < rfid.uid.size - 1) {
        rfidTag_in += " ";
      }
    }
    if (rfidTag_in != lastRfidTag_in) {
      lastRfidTag_in = rfidTag_in;
      Serial.println(rfidTag_in); // RFID 태그 출력
    }
  }
}

void readRfidTag_right_1(MFRC522 &rfid) {
  // RFID 태깅 읽기
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    String rfidTag_right_1 = "RIGHT_1:";
    for (byte i = 0; i < rfid.uid.size; i++) {
      rfidTag_right_1 += String(rfid.uid.uidByte[i], DEC);
      if (i < rfid.uid.size - 1) {
        rfidTag_right_1 += " ";
      }
    }
    if (rfidTag_right_1 != lastRfidTag_right_1) {
      lastRfidTag_right_1 = rfidTag_right_1;
      Serial.println(rfidTag_right_1);
    }
  }
}

void readRfidTag_right_2(MFRC522 &rfid) {
  // RFID 태깅 읽기
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    String rfidTag_right_2 = "RIGHT_2:";
    for (byte i = 0; i < rfid.uid.size; i++) {
      rfidTag_right_2 += String(rfid.uid.uidByte[i], DEC);
      if (i < rfid.uid.size - 1) {
        rfidTag_right_2 += " ";
      }
    }
    if (rfidTag_right_2 != lastRfidTag_right_2) {
      lastRfidTag_right_2 = rfidTag_right_2;
      Serial.println(rfidTag_right_2);
    }
  }
}

void updateLCD(int currentCount, int maxCount) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Parking Status:");
  lcd.setCursor(0, 1);
  lcd.print(currentCount);
  lcd.print(" Used, ");
  lcd.print(maxCount - currentCount);
  lcd.print(" Free");
}

void setup() {
  String lastRfidTag_in = "";
  String lastRfidTag_right_1 = "";
  String lastRfidTag_right_2 = "";
  myServo.attach(2); // D2 필에 서보모터 연결
  Serial.begin(9600); // 시리얼 통신 시작
  myServo.write(90);  // 90도가 닫혀있는 상태
  SPI.begin();
  // lcd.begin(16, 2);
  // lcd.print("Welcome!"); // 초기 메시지 표시
  lcd.begin(16, 2); // LCD 크기 설정 (16x2)
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Parking Status:"); // 첫 줄 메시지
  lcd.setCursor(0, 1);
  lcd.print("0 Used, 8 Free"); // 초기 값 직접 출력
  pinMode(A0, OUTPUT);
  pinMode(A1, OUTPUT);
  pinMode(A2, OUTPUT);
  pinMode(A3, OUTPUT);
  pinMode(A4, OUTPUT);
  pinMode(A5, OUTPUT);
  rfid_in.PCD_Init(); // 입구 RFID 초기화
  rfid_right_1.PCD_Init(); // 오른쪽 1번 자리 RFID 초기화
  rfid_right_2.PCD_Init(); // 오른쪽 2번 자리 RFID 초기화
}

void loop() {
  unsigned long currentMillis = millis();
  
  static int maxCount = 8;    // 최대 자리 수 설정

  // 각 RFID 리더기에서 태깅 읽기
  readRfidTag_in(rfid_in);
  readRfidTag_right_1(rfid_right_1);
  readRfidTag_right_2(rfid_right_2);

  // command를 loop 함수 내에서 유효한 변수로 선언
  static String command = ""; // 초기값으로 빈 문자열

  // 시리얼 데이터를 읽어서 서보모터 제어 및 자리 수 갱신
  if (Serial.available() > 0) {
    command = Serial.readString(); // String으로 데이터 읽기
    command.trim(); // 공백 문자 제거

    // 서보모터 열기
    if (command == "open") {
      myServo.write(180);          // 차단기를 열다 (180도)
      previousMillis = currentMillis; // 차단기를 연 시간 기록
      isGateOpen = true;
    }
  }

  // 차단기를 닫는 타이밍 체크
  if (isGateOpen && (currentMillis - previousMillis >= interval)) {
    myServo.write(90);  // 차단기를 다시 닫다 (90도)
    isGateOpen = false;
  }

  // 자리 수 갱신
  if (command == "up") {
    count++; // count 증가 (최대 값 제한)
    updateLCD(count, maxCount);    // LCD 갱신
    command = "";                  // 처리 후 초기화
  }
  if (command == "down") {
    count--;        // count 감소 (최소 값 제한)
    updateLCD(count, maxCount);    // LCD 갱신
    command = "";                  // 처리 후 초기화
  }
}

// LCD 갱신 함수
// void updateLCD(int currentCount, int maxCount) {
//   lcd.clear();                     // 화면 초기화
//   lcd.setCursor(0, 0);             // 첫 줄
//   lcd.print("Welcome!");           // "Welcome!" 출력
//   lcd.setCursor(0, 1);             // 둘째 줄
//   lcd.print(currentCount);         // 현재 count 출력
//   lcd.print("/");
//   lcd.print(maxCount);             // 최대 count 출력
// }











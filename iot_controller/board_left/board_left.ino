#include <Servo.h>
#include <SPI.h>
#include <MFRC522.h>
#include <LiquidCrystal.h>

#define SS_PIN_EXIT 9  // 입구 RFid
#define SS_PIN_LEFT_1 8  // 왼쪽 1번 자리
#define SS_PIN_LEFT_2 7  // 왼쪽 2번 자리
#define SS_PIN_Join 6  // 왼쪽 3번 자리
#define RST_PIN 10  // RFID 리셋 필

MFRC522 rfid_exit(SS_PIN_EXIT, RST_PIN); // 입구 RFID 리더기
MFRC522 rfid_left_1(SS_PIN_LEFT_1, RST_PIN); // 왼쪽 1번 자리 RFID 리더기
MFRC522 rfid_left_2(SS_PIN_LEFT_2, RST_PIN); // 왼쪽 2번 자리 RFID 리더기


Servo myServo;

LiquidCrystal lcd(A0, A1, A2, A3, A4, A5);

unsigned long previousMillis = 0;
const long interval = 5000;
bool isGateOpen = false;
String lastRfidTag_exit = "";
String lastRfidTag_left_1 = "";
String lastRfidTag_left_2 = "";

unsigned long chargeDisplayStartTime = 0; // 요금 표시 시작 시간
bool isDisplayingCharge = false;         // 요금 표시 상태
//int count =0;

void readRfidTag_exit(MFRC522 &rfid) {
  // RFID 태깅 읽기
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    String rfidTag_exit = "EXIT:";
    for (byte i = 0; i < rfid.uid.size; i++) {
      rfidTag_exit += String(rfid.uid.uidByte[i], DEC);
      if (i < rfid.uid.size - 1) {
        rfidTag_exit += " ";
      }
    }
    if (rfidTag_exit != lastRfidTag_exit) {
      lastRfidTag_exit = rfidTag_exit;
      Serial.println(rfidTag_exit); // RFID 태그 출력
    }
  }
}

void readRfidTag_left_1(MFRC522 &rfid) {
  // RFID 태깅 읽기
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    String rfidTag_left_1 = "LEFT_1:";
    for (byte i = 0; i < rfid.uid.size; i++) {
      rfidTag_left_1 += String(rfid.uid.uidByte[i], DEC);
      if (i < rfid.uid.size - 1) {
        rfidTag_left_1 += " ";
      }
    }
    if (rfidTag_left_1 != lastRfidTag_left_1) {
      lastRfidTag_left_1 = rfidTag_left_1;
      Serial.println(rfidTag_left_1);
    }
  }
}

void readRfidTag_left_2(MFRC522 &rfid) {
  // RFID 태깅 읽기
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    String rfidTag_left_2 = "LEFT_2:";
    for (byte i = 0; i < rfid.uid.size; i++) {
      rfidTag_left_2 += String(rfid.uid.uidByte[i], DEC);
      if (i < rfid.uid.size - 1) {
        rfidTag_left_2 += " ";
      }
    }
    if (rfidTag_left_2 != lastRfidTag_left_2) {
      lastRfidTag_left_2 = rfidTag_left_2;
      Serial.println(rfidTag_left_2);
    }
  }
}

void displayCharge(String amount) {
  lcd.clear(); // LCD 화면 초기화
  lcd.setCursor(0, 0);
  lcd.print("Total Charge:"); // 첫 줄 메시지
  lcd.setCursor(0, 1);
  lcd.print(amount);          // 요금 출력
  lcd.print(" won");          // "won" 추가
}


void setup() {
  String lastRfidTag_exit = "";
  String lastRfidTag_left_1 = "";
  String lastRfidTag_left_2 = "";
  pinMode(A0, OUTPUT);
  pinMode(A1, OUTPUT);
  pinMode(A2, OUTPUT);
  pinMode(A3, OUTPUT);
  pinMode(A4, OUTPUT);
  pinMode(A5, OUTPUT);
  // 서보모터 연결 필 설정
  myServo.attach(2); // D2 필에 서보모터 연결
  myServo.write(90);
  
  SPI.begin();
    // 90도가 닫혀있는 상태
  lcd.begin(16, 2);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Have a nice day!"); // 초기 메시지 표시
  
  Serial.begin(9600); // 시리얼 통신 시작
 
  rfid_exit.PCD_Init(); // 입구 RFID 초기화
  rfid_left_1.PCD_Init(); // 오른쪽 1번 자리 RFID 초기화
  rfid_left_2.PCD_Init(); // 오른쪽 2번 자리 RFID 초기화
}

void loop() {
  unsigned long currentMillis = millis();

  // 각 RFID 리더기에서 태깅 읽기
  readRfidTag_exit(rfid_exit);
  readRfidTag_left_1(rfid_left_1);
  readRfidTag_left_2(rfid_left_2);
  static String command = ""; 
  // 시리얼 데이터를 읽어서 서보모터 제어
  if (Serial.available() > 0) {
    String command = Serial.readString();
    command.trim(); // 공백 문자 제거

    if (command == "open") {
      myServo.write(0); // 레프트는 0이 열리는거 90이 닫히는거
      previousMillis = currentMillis; // 차단기를 열 시간을 기록
      isGateOpen = true;
    }

    if (command.startsWith("charge_")) {
      String chargeAmount = command.substring(7); // "charge_" 이후 값 추출
      displayCharge(chargeAmount);               // LCD에 요금 표시
      chargeDisplayStartTime = currentMillis;    // 요금 표시 시작 시간 기록
      isDisplayingCharge = true;                 // 요금 표시 상태 활성화
    }
  }

  // 차단기를 닫는 타이밍 체크
  if (isGateOpen && (currentMillis - previousMillis >= interval)) {
    myServo.write(90);  // 차단기를 다시 닫다 (90도)
    isGateOpen = false;
  }

  // 8초가 지난 후 요금 표시를 초기 메시지로 복원
  if (isDisplayingCharge && (currentMillis - chargeDisplayStartTime >= 8000)) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Have a nice day!");
    isDisplayingCharge = false; // 요금 표시 상태 종료
  }
}
  //left에는 필요없는 함수 
  // // 자리 수 갱신
  // if (command == '2') {
  //   if (count < maxCount) count++; // count 증가 (최대 값 제한)
  //   updateLCD(count, maxCount);    // LCD 갱신
  //   command = '\0';                // 처리 후 초기화
  // }
  // if (command == '3') {
  //   if (count > 0) count--;        // count 감소 (최소 값 제한)
  //   updateLCD(count, maxCount);    // LCD 갱신
  //   command = '\0';                // 처리 후 초기화
  // }








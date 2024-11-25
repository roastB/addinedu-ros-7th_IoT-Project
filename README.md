## **주차관제시스템 : 주차 경로 안내 및 주차장 모니터링**

### 1.프로젝트 소개
#### 1-1.프로젝트 개요
차량의 주차 편의를 높이고, 효율적인 주차 공간 활용을 위해 설계된 스마트 주차 시스템입니다.<br />
차량 접근을 감지하여 주차 가능 여부를 판단하고, 자동으로 차단기를 제어합니다.<br /> 
또한, 주차 자리를 찾는 사용자를 위해 LED 불빛으로 주차 위치를 쉽게 안내합니다.<br />
GUI를 통해 각 주차장의 실시간 운영 상태와 통계를 명확하게 확인할 수 있으며,<br /> 
출차 시에는 주차 요금을 자동으로 계산하여 이용 시간과 요금을 간편하게 관리할 수 있습니다.<br /> 
#### 1-2.기술 스택
|분류|기술|
|---|---|
|개발환경|<img src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=white"/> <img src="https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=Ubuntu&logoColor=white"/>|
|언어|<img src="https://img.shields.io/badge/C++-F01F7A?style=for-the-badge&logo=cplusplus&logoColor=white"/> <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=white"/>|
|GUI|<img src="https://img.shields.io/badge/PYQT-41CD52?style=for-the-badge&logo=cplusplus&logoColor=white"/>|
|데이터베이스|<img src="https://img.shields.io/badge/MYSQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white"/>|
|하드웨어|<img src="https://img.shields.io/badge/arduino-00878F?style=for-the-badge&logo=arduino&logoColor=white"/>|
|협업 툴|<img src="https://img.shields.io/badge/github-181717?style=for-the-badge&logo=github&logoColor=white"/> <img src="https://img.shields.io/badge/git-F05032?style=for-the-badge&logo=git&logoColor=white"/> <img src="https://img.shields.io/badge/confluence-172B4D?style=for-the-badge&logo=confluence&logoColor=white"/> <img src="https://img.shields.io/badge/jira-0052CC?style=for-the-badge&logo=jira&logoColor=white"/> <img src="https://img.shields.io/badge/slack-4A154B?style=for-the-badge&logo=slack&logoColor=white"/> |
#### 1-3. 팀원 구성
|구분|이름|업무|
|---|---|---|
|팀장|유재현|MCU - RFID 및 시리얼통신 기초 구현<br />Zira, Confluence 관리 , 테스트 케이스 구성 및 검증|
|팀원|공도웅|MCU - IO - 주차관제시스템 아두이노 하드웨어 / 소프트웨어 설계<br />IO - 아두이노 / 데이터베이스 시리얼 통신 구현|
|팀원|조성현|GUI - GUI - 주차기록 Tab 구현 / 모니터링화면 주차장 실시간 안내 LED 구현<br />GIT - 버전 관리|
|팀원|윤민섭|GUI - GUI - 회원등록, 모니터링 Tab 구현 / 클라이언트 서버 구현<br />DB - 데이터베이스 구성, 주차정보, 회원정보 관리|
|팀원|장윤정|GUI - 회원등록, 모니터링, 주차 기록 tab 디자인
### 2.프로젝트 설계
#### 2-1. 기능리스트
|번호|기능|설명|
|---|---|---|
|1|입출차 관리|•입차 제한<br />•입출차 기록|
|2|주차 경로 유도|•주차 경로 안내등을 통해 자리를 안내|
|3|주차장 실시간 모니터링|•주차 자리 상태 표시<br />•주차 차량의 회원정보 표시 : 이름, 전화번호, 주차위치, 입출차시간 등등|
|4|주차 자리 상태 표시|•주차 자리 여부 판단 가능|
|5|주차장 기록 관리|•조건별 상세정보 검색<br />•해당 자리의 입출차 시간 정보 확인|

#### 2-2. 시스템구성도

![image](https://github.com/user-attachments/assets/12b3725c-2d2e-4264-b5c2-be5966010df3)

#### 2-3. 3D 모델링

![image](https://github.com/user-attachments/assets/36e0a39a-e9df-4d56-8762-fad37c7325ad)

### 3.프로젝트 구현

#### 3-1. DB

![image](https://github.com/user-attachments/assets/238a0643-fcf1-4ff1-a102-6097023b4f6c)

#### 3-2. 주차장 제작

![image](https://github.com/user-attachments/assets/41b51ecf-ef9a-4f5b-b757-77031d6a9c63)

#### 3-2. IO

![image](https://github.com/user-attachments/assets/92be24f7-c180-473b-887f-ec9d7c5f3edf)

![image](https://github.com/user-attachments/assets/8452a9ff-039e-4eb0-b995-987ad476c26d)

![image](https://github.com/user-attachments/assets/428e1322-c961-45db-81ef-496da1707528)

#### 3-3. GUI

![image](https://github.com/user-attachments/assets/776c591a-4fd3-44b3-8866-13eb08f3160e)

![image](https://github.com/user-attachments/assets/a5bc29d9-3493-405a-8a60-d454bd686ad5)

![image](https://github.com/user-attachments/assets/e49ab16a-e36d-4f24-80e4-84f5ac80ab60)

![image](https://github.com/user-attachments/assets/d2e54e64-9f4e-4d9b-b20e-b6a1b9dbed56)

### 4.프로젝트 결과

### 4-1. 테스트 케이스 결과

|No|Input|Output|Result|
|---|---|---|---|
|1|입구 RFID 리더기에 차량 RFID Key 인식|- 입구 차단기 상승 및 하강<br />- 입구 LCD 주차가능 대수 업데이트|PASS|
|2|각 주차위치 RFID 리더기에 차량 RFID Key 인식|- 주차 완료 자리 주차 경로 LED 소등<br />- IoT Admin GUI 주차 자리 표시 버튼 색상 자동 전환<br />- 주차 자리 표시 버튼 클릭 시 상세정보 표시|PASS|
|3|출차 RFID 리더기에 차량 RFID Key 인식|- 출차 차단기 상승 및 하강<br />- 주차 가능 자리 주차 경로 LED 점등<br />- 출구 LCD 주차금액 안내<br />- IoT Admin GUI 주차 자리 표시 버튼 색상 자동 전환|PASS|
|4|IoT Admin GUI “Parking Log” 탭 검색 조건 입력|- 상세 검색 결과 출력|PASS|
|5|IoT User GUI 주차 정보 검색|- 상세 검색 결과 출력|PASS|

### 4-2. 기능 작동 영상
[https://www.youtube.com/watch?v=a8bJivGECbU](https://www.youtube.com/watch?v=a8bJivGECbU)

### 4-3. 발표자료
[https://docs.google.com/presentation/d/1Cbgnzgge9zj94wtTtIY1QZwocBo0pep31wvHPXRNmMU/edit?usp=sharing](https://docs.google.com/presentation/d/1Cbgnzgge9zj94wtTtIY1QZwocBo0pep31wvHPXRNmMU/edit?usp=sharing)

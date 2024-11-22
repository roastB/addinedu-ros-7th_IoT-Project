import serial
import time
import mysql.connector
import re
from datetime import datetime,timedelta

# pyserial 라이브러리 사용
# Arduino와의 통신 설정
arduino_port_left = '/dev/ttyACM2'  # 사용 중인 포트 확인 필요 (예: COM3 또는 /dev/ttyACM0)
arduino_port_right = '/dev/ttyACM3'
arduino_port_join = '/dev/ttyACM1'
baud_rate = 9600
ser1 = serial.Serial(arduino_port_left, baud_rate)
ser2 = serial.Serial(arduino_port_right, baud_rate)
ser3 = serial.Serial(arduino_port_join, baud_rate)

# joiner = pu1(main_window=None)

remote = mysql.connector.connect(
            host = "******",
            port = 3306,
            user = "***",
            password = "***",
            database = "***"
        )
cur = remote.cursor()

def send_command_to_arduino_1(command):
    """
    Arduino로 명령을 전송하는 함수
    """
    ser1.write(command.encode())
    time.sleep(0.1)  # 전송 후 약간의 지연
    
def send_command_to_arduino_2(command):
    """
    Arduino로 명령을 전송하는 함수
    """
    ser2.write(command.encode())
    time.sleep(0.1)  # 전송 후 약간의 지연
    
def send_command_to_arduino_3(command):
    """
    Arduino로 명령을 전송하는 함수
    """
    ser3.write(command.encode())
    time.sleep(0.1)  # 전송 후 약간의 지연

def handle_parking_led():
    # 데이터베이스 조회 상태에 따라 LED 패턴 메시지를 생성하고 Arduino로 전송하는 함수
    sql = "SELECT location FROM parklog WHERE exit_log IS NULL"
    cur.execute(sql)
    results = cur.fetchall()
    locations = [result[0] for result in results]

    valid_locations = {"LEFT_1", "LEFT_2", "RIGHT_1", "RIGHT_2"}
    filtered_locations = [loc for loc in locations if loc in valid_locations]

    if not filtered_locations:
        message = "0000"
    elif filtered_locations == ["LEFT_1"]:
        message = "1000"
    elif filtered_locations == ["LEFT_2"]:
        message = "0100"
    elif filtered_locations == ["RIGHT_1"]:
        message = "0010"
    elif filtered_locations == ["RIGHT_2"]:
        message = "0001"
    elif set(filtered_locations) == {"LEFT_1", "LEFT_2"}:
        message = "1100"
    elif set(filtered_locations) == {"LEFT_1", "RIGHT_1"}:
        message = "1010"
    elif set(filtered_locations) == {"LEFT_1", "RIGHT_2"}:
        message = "1001"
    elif set(filtered_locations) == {"LEFT_2", "RIGHT_1"}:
        message = "0110"
    elif set(filtered_locations) == {"LEFT_2", "RIGHT_2"}:
        message = "0101"
    elif set(filtered_locations) == {"RIGHT_1", "RIGHT_2"}:
        message = "0011"
    elif set(filtered_locations) == {"LEFT_1", "LEFT_2", "RIGHT_1"}:
        message = "1110"
    elif set(filtered_locations) == {"LEFT_1", "LEFT_2", "RIGHT_2"}:
        message = "1101"
    elif set(filtered_locations) == {"LEFT_1", "RIGHT_1", "RIGHT_2"}:
        message = "1011"
    elif set(filtered_locations) == {"LEFT_2", "RIGHT_1", "RIGHT_2"}:
        message = "0111"
    elif all(loc in filtered_locations for loc in ["LEFT_1", "LEFT_2", "RIGHT_1", "RIGHT_2"]):
        message = "1111"
    #print(locations)
    #print(filtered_locations)
    #print(message)
    send_command_to_arduino_3(message)

    return message


def check_rfid_in_database(rfid_tag):
    """
    MySQL 데이터베이스에서 RFID 태그가 존재하는지 확인하는 함수
    """
    ##########
    connection = mysql.connector.connect(
            host = "*****",
            port = "*****",
            user = "****",
            password = "****",
            database = "****"
    )
    try:
        cursor = connection.cursor()
        sql = "SELECT UID FROM membership WHERE UID = %s"
        cursor.execute(sql, (rfid_tag,))
        result = cursor.fetchone()
        if result is not None:
            #print(f"[디버그] 데이터베이스에서 조회한 결과: {result[0]}, 타입: {type(result[0])}")
            return result[0] == rfid_tag
        else:
            #print("[디버그] 데이터베이스에서 조회한 결과가 없습니다.")
            return False
    finally:
        cursor.close()
        connection.close()
        
# IN / EXIT인지만 판단
def check_reader(reader_id, rfid_tag):
    if reader_id == 'IN':
        #send_command_to_arduino_2('2')
        update_entry(rfid_tag)
        
    elif reader_id == "EXIT":
        #send_command_to_arduino_2('3')
        exitCheck(rfid_tag)
        
    else:
        return False

def update_entry(rfid_tag):
    # sql = """insert into parklog (id, name, phone, car_num, location, entry_log)
    #     select m.id, m.name, m.phone, m.car_num, 'NY', current_timestamp from membership m
    #     where m.UID = %s; """
    
    sql = """INSERT INTO parklog (user_id, car_id, location, entry_log)
            SELECT m.user_id, c.car_id, 'NY', CURRENT_TIMESTAMP
            FROM membership m
            JOIN car c ON m.user_id = c.user_id
            WHERE m.UID = %s;"""

    cur.execute(sql, (rfid_tag,))
    remote.commit()



# 출입구 제외한 네 자리 판단
def parkCheck(reader_id, RFID):

    #parklist = {'LEFT_1': False, 'LEFT_2':False, 'RIGHT_1':False, 'RIGHT_2':False}
    
    # sql = """insert into parklog (id, name, phone, car_num, location, entry_log)
    # select m.id, m.name, m.phone, m.car_num, %s, current_timestamp from membership m
    # where m.RFID = %s;"""
    if reader_id == "IN" or reader_id == "EXIT":
        return
    else:
        sql = """update parklog p join membership m on p.user_id = m.user_id set p.location = %s where m.UID = %s and p.location = 'NY'"""
        #print("디버깅 중!!: reader_id = ",reader_id)
        if reader_id == 'IN' or reader_id == "EXIT":
            pass
        else:
            cur.execute(sql, (reader_id, RFID))

        remote.commit()

# 출차 시간 업데이트 + 금액업데이트 
def exitCheck(RFID):
    # sql_get_entry = "select m.kind, p.entry_log from parklog p join membership m on m.id = p.id where m.RFID = %s and p.entry_log is not NULL and p.exit_log is NULL"
    sql_get_entry = """SELECT c.kind_name, p.entry_log , c.car_num
                        FROM parklog p
                        JOIN membership m ON m.user_id = p.user_id
                        JOIN car c ON c.user_id = m.user_id
                        WHERE m.UID = %s
                        AND p.entry_log IS NOT NULL
                        AND p.exit_log IS NULL;"""
    # sql_get_entry = "select c.kind_name, p.entry_log from parklog p join membership m on m.user_id = p.user_id where m.UID = %s and p.entry_log is not NULL and p.exit_log is NULL"
    cur.execute(sql_get_entry, (RFID,))
    result = cur.fetchall()
    kind = result[0][0]
    dt_entry = result[0][1]
    dt_carnum = result[0][2]
    dt_now = datetime.now()
    dt_entry = dt_entry + timedelta(hours=9)
    match kind:
        case "EV":
            fee = 75
        case "경차":
            fee = 50
        case default:
            fee = 100
    try:
        dt_day = (dt_now-dt_entry).days*1440  #일을 분으로 변환
    except:
        pass
    dt_time = (dt_now-dt_entry).seconds//60 #시분초를 분으로 변환
    dt_fee = (dt_day + dt_time) * fee
    sql_update_charge = "update parklog p join membership m on p.user_id = m.user_id set charge = %s where m.UID = %s and exit_log is NULL"
    cur.execute(sql_update_charge, (dt_fee, RFID))
    sql = "update parklog p join membership m on p.user_id = m.user_id set exit_log = current_timestamp where m.UID = %s and exit_log is NULL"
    print(dt_fee)
    print(dt_carnum)
    send_command_to_arduino_1(f"ch_{dt_fee}_car_{dt_carnum}")
    cur.execute(sql, (RFID,))
    remote.commit()


print("RFID 태그를 대 주세요.")
while True:
    if ser1.in_waiting > 0:
        read_serial = ser1.readline().decode().strip()
        if read_serial:
            # ':'를 기준으로 데이터 나누기
            parts = read_serial.split(":", 1)
            if len(parts) == 2:
                reader_id, rfid_tag = parts
                print(f"리더기 ID: {reader_id}, 태그 값: {rfid_tag}")
                parkCheck(reader_id, rfid_tag)
                time.sleep(1)
                handle_parking_led()
                print(rfid_tag)
                if reader_id == "EXIT":
                    check_reader(reader_id, rfid_tag)
                    time.sleep(1)
                    if check_rfid_in_database(rfid_tag):
                        print("RFID 태그가 데이터베이스에 존재합니다. 서보모터를 움직입니다.")
                        ### 가격처리하는걸 구성해야한다. 이건 1번 아두이노에 구성을해야한다.
                        send_command_to_arduino_1("open")
                        time.sleep(1)
                        send_command_to_arduino_2("down")
                        handle_parking_led()

                    
    if ser2.in_waiting > 0:
        read_serial = ser2.readline().decode().strip()
        if read_serial:
            # ':'를 기준으로 데이터 나누기
            parts = read_serial.split(":", 1)
            if len(parts) == 2:
                reader_id, rfid_tag = parts
                print(f"리더기 ID: {reader_id}, 태그 값: {rfid_tag}")
                parkCheck(reader_id, rfid_tag)
                time.sleep(1)
                handle_parking_led()
                if reader_id == "IN":
                    check_reader(reader_id, rfid_tag)
                    if check_rfid_in_database(rfid_tag):
                        print("RFID 태그가 데이터베이스에 존재합니다. 서보모터를 움직입니다.")
                        send_command_to_arduino_2("open")
                        time.sleep(1)
                        send_command_to_arduino_2("up")
    
                        
    # if ser3.in_waiting > 0:
    #     read_serial = ser3.readline().decode().strip()
    #     print(read_serial)
    #     if read_serial:
    #         # ':'를 기준으로 데이터 나누기
    #         parts = read_serial.split(":", 1)
    #         if len(parts) == 2:
    #             reader_id, rfid_tag = parts
    #             print(f"리더기 ID: {reader_id}, 태그 값: {rfid_tag}")
    #             MyRFID = rfid_tag
    #             print(MyRFID)
                

                    


ser1.close()
ser2.close()
ser3.close()
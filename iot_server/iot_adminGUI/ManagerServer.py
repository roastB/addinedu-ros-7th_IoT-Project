import mysql.connector
import socket
import mysql.connector
from datetime import timedelta
import json

remote = mysql.connector.connect(
            host = "msdb.cvyy46quatrs.ap-northeast-2.rds.amazonaws.com",
            port = 3306,
            user = "root",
            password = "Dbsalstjq128!",
            database = "iot"
        )

cur = remote.cursor()

host = '192.168.2.117'
port = 65433   

# 소켓 생성
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(5)        

while True:
    
    client_socket, address = server_socket.accept()
    info = client_socket.recv(1024).decode('utf-8')
    name = info.split(',')[0]
    phone = info.split(',')[1]
    sql = "select m.id, m.name, m.phone, m.car_num, p.location, p.entry_log, p.exit_log, p.charge from membership m join parklog  p on m.id = p.id where m.name = %s and m.phone = %s"
    cur.execute(sql, (name, phone))
    result = cur.fetchall()
    num = len(result)
    res = {}
    
    for i in range(num):
        trans_res = list(result[i])
        try:
            trans_res[5]=str(result[i][5]+timedelta(hours=9))
        except:
            pass
        try:
            trans_res[6]=str(result[i][6]+timedelta(hours=9))
        except:
            pass
        result[i] = tuple(trans_res)
        res[i] = result[i]
        print(res[i])

    res = json.dumps(res, ensure_ascii=False).encode('utf-8')

    client_socket.send(res)
    client_socket.close()

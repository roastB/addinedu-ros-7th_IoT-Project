import mysql.connector
import socket
import mysql.connector
from datetime import timedelta
import json

remote = mysql.connector.connect(
            host = "-----",
            port = 3306,
            user = "k",
            password = "----",
            database = "----"
    )

cur = remote.cursor()

host = 'yout host'
port = 'your port' 

# 소켓 생성
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(5)        

print(f"Server is running on {host}:{port}")

while True:
    
    client_socket, address = server_socket.accept()
    print(f"Connection established with {address}")
    
    
    info = client_socket.recv(1024).decode('utf-8')
    name = info.split(',')[0]
    phone = info.split(',')[1]
    print("name from json:",name)
    print("phone from json:",phone)
    print(f"Received from client: {info}")
    sql = "select m.user_id, m.name, m.phone, c.car_num, p.location, p.entry_log, p.exit_log, p.charge from membership m join parklog p on m.id = p.id join car c on m.user_id = c.user_id where m.name = %s and m.phone = %s"
    cur.execute(sql, (name, phone))
    result = cur.fetchall()
    print(result)
    print(len(result))
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

    print(res)
    res = json.dumps(res, ensure_ascii=False).encode('utf-8')

    client_socket.send(res)
    client_socket.close()

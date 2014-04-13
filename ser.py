import time
import socket
import rs


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind(('', 9090))
s.listen(1000)

thread1=rs.myThread()
print('1')
thread1.start()

thread1.prin.writer('M114')

while True:
    conn, addr = s.accept()
    print(addr)
    while True:
        data = conn.recv(1024)
	if not data:
            break
	conn.send(data)
    conn.close()
    print('close')

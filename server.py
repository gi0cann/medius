import socket

LOCAL_HOST = ''
LOCAL_PORT = 80
REMOTE_HOST = b'example.com'
REMOTE_PORT = 80
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((LOCAL_HOST, LOCAL_PORT))
    server.listen(1)
    while True:
        conn, addr = server.accept()
        with conn:
            print('Connected by', addr)
            data = conn.recv(1024)
            if data:
                print(data)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                    client.connect((REMOTE_HOST, REMOTE_PORT))
                    client.send(data.replace(b'localhost', REMOTE_HOST))
                    rdata = client.recv(1024)
                    print(rdata)
                conn.sendall(rdata)


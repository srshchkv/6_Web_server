import socket
import threading
import os

def handle_client(conn):
    try:
        data = conn.recv(8192)
        request = data.decode()
        headers = request.split('\n')
        filename = headers[0].split()[1]

        if filename == '/':
            filename = '/index.html'

        filepath = '.' + filename
        if os.path.exists(filepath) and filename.endswith(('.html', '.css', '.js')):
            with open(filepath, 'rb') as file:
                response = file.read()
            status_line = "HTTP/1.1 200 OK\n"
            content_type = "Content-Type: text/html\n"
        else:
            response = b"<h1>404 Not Found</h1>"
            status_line = "HTTP/1.1 404 Not Found\n"
            content_type = "Content-Type: text/html\n"

        conn.sendall(status_line.encode())
        conn.sendall(content_type.encode())
        conn.sendall(b"\n")
        conn.sendall(response)
    finally:
        conn.close()

def start_server(port=8080):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', port))
    sock.listen(5)
    print(f"Server started on port {port}...")

    while True:
        conn, addr = sock.accept()
        print(f"Connected by {addr}")
        client_thread = threading.Thread(target=handle_client, args=(conn,))
        client_thread.start()

if __name__ == "__main__":
    start_server()

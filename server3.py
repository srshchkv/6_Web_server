import socket
import threading
import os
import json
import time
import mimetypes

# Загрузка конфигурации из файла
with open('config.json') as config_file:
    config = json.load(config_file)

PORT = config['port']
WORKING_DIRECTORY = config['working_directory']
MAX_REQUEST_SIZE = config['max_request_size']
ALLOWED_FILE_TYPES = config['allowed_file_types']

def log_request(client_address, requested_file, status_code):
    """
    Функция для записи логов запросов.
    """
    with open('server.log', 'a') as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {client_address} - {requested_file} - {status_code}\n")

def handle_client(conn, addr):
    """
    Функция для обработки запросов клиентов.
    """
    try:
        # Получение данных от клиента
        data = conn.recv(MAX_REQUEST_SIZE)
        if not data:
            return

        # Разбор HTTP-запроса
        request = data.decode()
        headers = request.split('\n')
        filename = headers[0].split()[1]

        # Установка имени файла по умолчанию
        if filename == '/':
            filename = '/index.html'

        # Полный путь к файлу
        filepath = os.path.join(WORKING_DIRECTORY, filename.lstrip('/'))
        file_ext = os.path.splitext(filepath)[1]

        # Проверка существования файла и допустимости типа файла
        if not os.path.exists(filepath):
            response = b"<h1>404 Not Found</h1>"
            status_line = "HTTP/1.1 404 Not Found\n"
            content_type = "Content-Type: text/html\n"
            status_code = 404
        elif file_ext not in ALLOWED_FILE_TYPES:
            response = b"<h1>403 Forbidden</h1>"
            status_line = "HTTP/1.1 403 Forbidden\n"
            content_type = "Content-Type: text/html\n"
            status_code = 403
        else:
            # Чтение содержимого файла
            with open(filepath, 'rb') as file:
                response = file.read()
            status_line = "HTTP/1.1 200 OK\n"
            content_type = f"Content-Type: {mimetypes.guess_type(filepath)[0]}\n"
            status_code = 200

        # Формирование заголовков ответа
        response_headers = (
            status_line +
            content_type +
            f"Date: {time.strftime('%a, %d %b %Y %H:%M:%S GMT')}\n" +
            "Server: CustomPythonServer\n" +
            f"Content-Length: {len(response)}\n" +
            "Connection: close\n\n"
        )

        # Отправка заголовков и содержимого
        conn.sendall(response_headers.encode())
        conn.sendall(response)
        log_request(addr[0], filename, status_code)
    finally:
        conn.close()

def start_server(port=PORT):
    """
    Функция для запуска сервера.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', port))
    sock.listen(5)
    print(f"Сервер запущен на порту {port}...")

    while True:
        conn, addr = sock.accept()
        print(f"Подключен клиент {addr}")
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()

if __name__ == "__main__":
    start_server()

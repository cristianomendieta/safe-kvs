import socket

SERVER_HOST = 'localhost'
SERVER_PORT = 8080

def send_request_without_tls():
     # cria um socket TCP/IP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    client_socket.connect((SERVER_HOST, SERVER_PORT))

    message = "Tentativa de envio"

    client_socket.send(message.encode(encoding='utf-8'))

    # recebe resposta
    response = client_socket.recv(4096)
    print(f'Resposta do servidor: {response.decode(encoding="utf-8")}')

    client_socket.close()

if __name__ == '__main__':
    send_request_without_tls()
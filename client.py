import socket
import ssl
import json

CLIENT_CERTFILE = './resources/client.crt'
CLIENT_KEYFILE = './resources/client.key'
SERVER_CERTFILE = './resources/server.crt'

SERVER_HOST = 'localhost'
SERVER_PORT = 8080

class Client:
    def __init__(self):
        self.socket = None

    def connect(self):
        # cria um socket TCP/IP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=SERVER_CERTFILE)
            context.load_cert_chain(certfile=CLIENT_CERTFILE, keyfile=CLIENT_KEYFILE)

            # estabelece uma conexão SSL/TLS segura
            secure_socket = context.wrap_socket(self.socket, server_hostname=SERVER_HOST)
            secure_socket.connect((SERVER_HOST, SERVER_PORT))
            return secure_socket

        except ssl.SSLError as e:
            print(f"Erro de SSL ao conectar ao servidor: {e}")
            return None

    def send_request(self, request):
        secure_socket = self.connect()

        if secure_socket:
            try:
                # envia requisição
                secure_socket.send(json.dumps(request).encode(encoding='utf-8'))

                # recebe resposta
                response = secure_socket.recv(4096)
                print(f'Resposta do servidor: {response.decode(encoding="utf-8")}')

            finally:
                # encerra conexão com o servidor
                secure_socket.shutdown(socket.SHUT_RDWR)
                secure_socket.close()

if __name__ == '__main__':
    request = {'operation': 'get', 'key': 'data1'}

    client = Client()

    client.send_request(request)
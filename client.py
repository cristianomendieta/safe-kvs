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

    def send_request(self, request, secure_socket):
        if secure_socket:
            # envia requisição
            secure_socket.send(json.dumps(request).encode(encoding='utf-8'))

            # recebe resposta
            response = secure_socket.recv(4096)
            print(f'Resposta do servidor: {response.decode(encoding="utf-8")}')

    def menu_interface(self):
        print("1. Create")
        print("2. Get")
        print("3. Update")
        print("4. Delete")
        print("5. Exit")

        try:
            choice = input("Enter choice: ")
            choice = int(choice)
        except ValueError:
            choice = 0
        return choice

    def request_create(self, secure_socket, client):
        print("Enter value: ")
        value = input()
        request = {'operation': 'create', 'value': value}
        client.send_request(request, secure_socket)

    def request_get(self, secure_socket, client):
        print("Enter key: ")
        key = input()
        request = {'operation': 'get', 'key': key}
        client.send_request(request, secure_socket)

    def request_update(self, secure_socket, client):
        print("Enter key: ")
        key = input()
        print("Enter value: ")
        value = input()
        print(value)
        request = {'operation': 'update', 'key': key, 'value': value}
        client.send_request(request, secure_socket)

    def request_delete(self, secure_socket, client):
        print("Enter key: ")
        key = input()
        request = {'operation': 'delete', 'key': key}
        client.send_request(request, secure_socket)

if __name__ == '__main__':
    client = Client()
    secure_socket = client.connect()

    userInput = 0
    while userInput != 5:
        userInput = int(client.menu_interface())
        if userInput == 1:
            client.request_create(secure_socket, client)
        elif userInput == 2:
            client.request_get(secure_socket, client)
        elif userInput == 3:
            client.request_update(secure_socket, client)
        elif userInput == 4:
            client.request_delete(secure_socket, client)
        else:
            print("Invalid input")
    
    secure_socket.shutdown(socket.SHUT_RDWR)
    secure_socket.close()
    print("Connection closed")
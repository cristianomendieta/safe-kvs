import socket
import ssl
import json
from cryptography.fernet import Fernet
import argparse


ROGUE_CLIENT_CERTFILE = './resources/invasor.crt'
ROGUE_CLIENT_KEYFILE = './resources/invasor.key'
CLIENT_CERTFILE = './resources/client.crt'
CLIENT_KEYFILE = './resources/client.key'
SERVER_CERTFILE = './resources/server.crt'

SERVER_HOST = 'localhost'
SERVER_PORT = 8080

KEY = b'xuIqO3jsp4oYrMYnxZq0fSoP2j1hyttmAe5sCHcj6w8='

cipher_suite = Fernet(KEY)

class Client:
    def __init__(self, modify_message, client_flag):
        self.socket = None
        self.modify_message = modify_message
        self.client_flag = client_flag

    def connect(self):
        
        if self.client_flag:
            CLIENT_KEYFILE = ROGUE_CLIENT_KEYFILE
            CLIENT_CERTFILE = ROGUE_CLIENT_CERTFILE

        try:
            # cria um socket TCP/IP
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

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
            request = json.dumps(request).encode(encoding='utf-8')

            mensagem_criptografada = cipher_suite.encrypt(request)
            if self.modify_message:
                # Alterar alguns bytes aleatórios na mensagem criptografada
                mensagem_alterada = bytearray(mensagem_criptografada)
                mensagem_alterada[5] = 42  # Altera o sexto byte 

                # envia requisição
                secure_socket.send(mensagem_alterada)

            else:
                # envia requisição
                secure_socket.send(mensagem_criptografada)

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
            choice = input("Insira a opção: ")
            choice = int(choice)
        except ValueError:
            choice = 0
        return choice

    def request_create(self, secure_socket, client):
        print("Insira o valor no formato json: ")
        value = input()
        request = {'operation': 'create', 'value': value}
        client.send_request(request, secure_socket)

    def request_get(self, secure_socket, client):
        print("Insira a chave: ")
        key = input()
        request = {'operation': 'get', 'key': key}
        client.send_request(request, secure_socket)

    def request_update(self, secure_socket, client):
        print("Insira a chave: ")
        key = input()
        print("Insira o valor no formato json: ")
        value = input()
        print(value)
        request = {'operation': 'update', 'key': key, 'value': value}
        client.send_request(request, secure_socket)

    def request_delete(self, secure_socket, client):
        print("Insira a chave: ")
        key = input()
        request = {'operation': 'delete', 'key': key}
        client.send_request(request, secure_socket)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--modify_bytes', default=False, action='store', help='modify message bytes')
    parser.add_argument('-c', '--client', action='store_true',  help='define client')

    args = parser.parse_args()
        
    client = Client(args.modify_bytes, args.client)
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
        elif userInput == 5:
            print("Encerrando conexão com o servidor...")
        else:
            print("Valor inválido")
    
    secure_socket.shutdown(socket.SHUT_RDWR)
    secure_socket.close()
    print("Conexão finalizada")
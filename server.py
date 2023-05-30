import socket
import ssl
import json

CLIENT_CERTFILE = './resources/client.crt'
CLIENT_KEYFILE = './resources/client.key'
SERVER_CERTFILE = './resources/server.crt'
SERVER_KEYFILE = './resources/server.key'

SERVER_HOST = 'localhost'
SERVER_PORT = 8080

DB_PATH = './db.json'

class Server:
    def __init__(self):
        self.socket = None
        self.data = self.load_data(DB_PATH)

    def load_data(self, path):
        with open(path, 'r') as f:
            return json.load(f)

    def start(self):
        # cria um socket TCP/IP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.bind((SERVER_HOST, SERVER_PORT))

        # aguarda conexão de clientes
        self.socket.listen(1)
        print(f'Servidor aguardando conexões em {SERVER_HOST}:{SERVER_PORT}...')

        while True:
            client_socket, client_address = self.socket.accept()
            print(f'Conexão estabelecida com {client_address}')

            try:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                context.load_cert_chain(certfile=SERVER_CERTFILE, keyfile=SERVER_KEYFILE)

                # estabelece uma conexão SSL/TLS
                secure_socket = context.wrap_socket(client_socket, server_side=True)

                self.handle_client(secure_socket)

            finally:
                # encerra conexão com o cliente
                secure_socket.shutdown(socket.SHUT_RDWR)
                secure_socket.close()

    def handle_client(self, connection):
        while True:
            # recebe a solicitação do cliente
            request = connection.recv(4096)
            if not request:
                break

            request_data = json.loads(request.decode('utf-8'))

            operation = request_data.get('operation')

            # realiza a operação de consulta no servidor
            if operation == 'get':
                key = request_data.get('key')
                value = self.get_value(key)
                response = {'status': 'success', 'message': 'Valor obtido com sucesso', 'value': value}

            # realiza a operação de update no servidor
            elif operation == 'update':
                key = request_data.get('key')
                value = request_data.get('value')
                self.update_value(key, value)
                response = {'status': 'success', 'message': 'Valor definido com sucesso'}

            # realiza a operação de delete no servidor
            elif operation == 'delete':
                key = request_data.get('key')
                self.delete_key(key)
                response = {'status': 'success', 'message': 'Chave excluída com sucesso'}

            else:
                response = {'status': 'error', 'message': 'Operação inválida'}

            # Enviar a resposta para o cliente
            connection.send(json.dumps(response, ensure_ascii=False).encode(encoding='utf-8'))

    def get_value(self, key):
        return self.data.get(key)

    def update_value(self, key):
        pass

    def delete_key(self, key):
        pass

if __name__ == '__main__':
    server = Server()

    server.start()

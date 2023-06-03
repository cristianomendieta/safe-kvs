import socket
import ssl
import json
import pandas as pd
from cryptography.fernet import Fernet

CLIENT_CERTFILE = './resources/client.crt'
CLIENT_KEYFILE = './resources/client.key'
SERVER_CERTFILE = './resources/server.crt'
SERVER_KEYFILE = './resources/server.key'

SERVER_HOST = 'localhost'
SERVER_PORT = 8080

DB_PATH = './db.csv'

KEY = b'xuIqO3jsp4oYrMYnxZq0fSoP2j1hyttmAe5sCHcj6w8='

cipher_suite = Fernet(KEY)


class CryptographyException(Exception):
    def __init__(self, message):
        self.message = message

class Server:
    def __init__(self):
        self.socket = None
        self.data = self.load_data(DB_PATH)

    def load_data(self, path):
        data = pd.read_csv(path)

        return data

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
                context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                context.verify_mode = ssl.CERT_REQUIRED
                context.load_cert_chain(certfile=SERVER_CERTFILE, keyfile=SERVER_KEYFILE)
                context.load_verify_locations(cafile=CLIENT_CERTFILE)

                # estabelece uma conexão SSL/TLS
                secure_socket = context.wrap_socket(client_socket, server_side=True)

                self.handle_client(secure_socket)

                # encerra conexão com o cliente
                print("Encerrando conexão com o cliente...")
                secure_socket.shutdown(socket.SHUT_RDWR)
                secure_socket.close()

            except ssl.SSLError as e:
                print(f"Erro de SSL ao conectar ao servidor: {e}")
            except CryptographyException as e:
                print(f"Erro de criptografia: {e}")


    def handle_client(self, connection):
        while True:
            # recebe a solicitação do cliente
            request = connection.recv(4096)

            if not request:
                print("Conexão encerrada pelo cliente")
                return
            try:
                mensagem_descriptografada = cipher_suite.decrypt(request)
            except:
                raise CryptographyException('Falha na descriptografia. A mensagem foi alterada.')

            request_data = json.loads(mensagem_descriptografada.decode('utf-8'))

            operation = request_data.get('operation')

            # realiza a operação de criação no servidor
            if operation == 'create':
                print("Requisição de criação recebida")
                value = request_data.get('value')
                response = self.create_value(value)
                
            # realiza a operação de consulta no servidor
            elif operation == 'get':
                key = request_data.get('key')
                response = self.get_value(key)

            # realiza a operação de update no servidor
            elif operation == 'update':
                key = request_data.get('key')
                value = request_data.get('value')
                response = self.update_value(key, value)

            # realiza a operação de delete no servidor
            elif operation == 'delete':
                key = request_data.get('key')
                response = self.delete_key(key)

            else:
                response = {'status': 'error', 'message': 'Operação inválida'}

            # Enviar a resposta para o cliente
            connection.send(json.dumps(response, ensure_ascii=False).encode(encoding='utf-8'))

    def create_value(self, value):
        try:
            value_to_create = json.loads(value)

            new_id = self.data['id'].max() + 1
            value_to_create['id'] = new_id
            self.data = pd.concat([self.data, pd.DataFrame([value_to_create])], ignore_index=True)
            self.data.to_csv('db.csv', index=False)
            response = {'status': 'success', 'message': 'Registro criado com sucesso'}
        except Exception as e:
            print(e)
            response = {'status': 'error', 'message': 'Não foi possível criar o registro'}

        return response

    def get_value(self, key):
        try:
            data_key = self.data.loc[self.data['id'] == int(key)].to_dict('records')
            if data_key:
                response = {'status': 'success', 'message': 'Valor obtido com sucesso', 'value': data_key[0]}
            else:
                response = {'status': 'error', 'message': 'Chave não encontrada'}
        except Exception as e:
            print(e)
            response = {'status': 'error', 'message': 'Não foi possível obter o registro'}

        return response
                
    def update_value(self, key, value):
        try:
            data_key = self.data.loc[self.data['id'] == int(key)].to_dict('records')

            if data_key:
                values_to_update = json.loads(value)
                for k, val in values_to_update.items():
                    self.data.loc[self.data['id'] == int(key), k] = val
                self.data.to_csv('db.csv', index=False)
                response = {'status': 'success', 'message': 'Registro atualizado com sucesso'}
            else:
                response = {'status': 'error', 'message': 'Chave não encontrada'}
        except Exception as e:
            print(e)
            response = {'status': 'error', 'message': 'Não foi possível atualizar o registro'}

        return response

    def delete_key(self, key):
        try: 
            if self.data.loc[self.data['id'] == int(key)].empty:
                response = {'status': 'error', 'message': 'Chave não encontrada'}
            else:
                data_drop_key = self.data.loc[self.data['id'] != int(key)]
                data_drop_key.to_csv('db.csv', index=False)
                response = {'status': 'success', 'message': f"Chave {key} excluída com sucesso"}
        except Exception as e:
            print(e)
            response = {'status': 'error', 'message': 'Não foi possível excluir o registro'}

        return response
    
if __name__ == '__main__':
    server = Server()

    server.start()

from concurrent import futures
from msvcrt import kbhit
import time
import grpc
import SD_pb2
import SD_pb2_grpc
import RWLock
import ast
import threading
import datetime
import logging
lock = RWLock.RWLock()
dicionario = {}
class GreeterServicer(SD_pb2_grpc.GreeterServicer):
    def set(request, request2):            
        lock.writer_acquire()

        try: 
            if request.cid_id in dicionario:
                return SD_pb2.HelloReply(dados_client='ERROR',
                cid_id = dicionario[request.cid_id][0])
            else:
                #dicionario = dict(zip(str(request.cid_id) , request2.dados_client))
                dicionario[request.cid_id] = request2.dados_client
                    
                #dicionario[request2.dados_client] = (request.dados_client)
                print(">>", dicionario)

                return SD_pb2.HelloReply(dados_client='SUCCESS')
        finally:
            lock.writer_release()
    def get(client_id):

        thread_read = ThreadRead()
        thread_read.start()

        try:
            if client_id.cid_id in dicionario:
                dados = dicionario.get(client_id.cid_id)
                if(dados == ''):
                    print('Não existe o CID: ', {client_id.cid_id})
                    return SD_pb2.HelloReply(dados_client='ERROR')
                else:
                    print('O valor do CID é: ', {client_id.cid_id}, 'Dados do Cliente:', {dados})

        finally:
            lock.reader_release()

    def SayHello(self, request, context):
        print("SayHello Request Made:")
        print(request)
        hello_reply = SD_pb2.HelloReply()
        hello_reply.message = f"{request.greeting} {request.name}"

        return hello_reply
    

def menu():
    while True:
        #channel = grpc.insecure_channel('localhost:50051')
        #stub = SD_pb2_grpc.GreeterServicer(channel)

        print("1 - Cadastrar cliente")
        print("2 - Get cliente")
        print("0 - Sair do programa")

        inp = input("Escolha a opcao: ")

        if inp.lower() == '0':
            break
        if inp == "1":
            valor_digitado = input("Digite o valor: ")
            dados_cliente = input("Digite a descrição: ")
            response = GreeterServicer.set(SD_pb2.HelloReply(cid_id = int(valor_digitado)), SD_pb2.HelloReply(dados_client = dados_cliente))
            print("Inserção: " + response.dados_client + " - " + str(response.cid_id))
            #thread_read = ThreadRead()
            print(dicionario)
            thread_write = ThreadWrite(dicionario)
            #thread_read.setDaemon(True)
            #thread_write.setDaemon(True)
            #thread_read.start()
            thread_write.start()
        elif inp == "2":
            print("Digite o CID do cliente: ")
            id = input()

            response = GreeterServicer.get(SD_pb2.HelloReply(cid_id = int(id)))
            if(response == 'ERROR'):
                print('Não existe o CID: ' + response.client_id)
                break
        else:
            print('Opção inválida!')
            print('\n')



class ThreadRead (threading.Thread):
   def __init__(self):
      threading.Thread.__init__(self)

   def run(self):
      print ("Starting ThreadRead")
      read_db()
      print ("Exiting ThreadRead")

class ThreadWrite(threading.Thread):
    def __init__(self,counter):
        threading.Thread.__init__(self)
        self.counter = counter
    def run(self):
        print('Starting ThreadWrite')
        write_db(self.counter)
        print('Exiting ThreadWrite')

def read_db():
    lock.writer_acquire
    try:
        f = open('file.txt','r')
        global dicionario
        dicionario = ast.literal_eval(f.read())
        
    finally:
        lock.writer_release

def write_db(t):
    while True:
        lock.writer_acquire()
        try:
            f = open('file.txt','w')
            f.write(str(dicionario))
            f.close()
            
        finally:
            lock.writer_release()


#***************************************************************************************

def open_serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    SD_pb2_grpc.add_GreeterServicer_to_server(GreeterServicer(), server)
    server.add_insecure_port("localhost:50051")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    menu()
    logging.basicConfig()

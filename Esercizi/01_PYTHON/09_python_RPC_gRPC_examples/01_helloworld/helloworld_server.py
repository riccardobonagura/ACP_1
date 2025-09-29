from concurrent import futures  # Importa il modulo futures per la gestione del thread pool

import grpc                    # Importa la libreria grpc per la comunicazione RPC
import helloworld_pb2          # Importa le classi generate dal file .proto (messaggi)
import helloworld_pb2_grpc     # Importa le classi generate dal file .proto (servizi)

### crea una classe Greeter che implementa il servizio GreeterServicer
### in questo caso implementiamo il metodo SayHello

class Greeter(helloworld_pb2_grpc.GreeterServicer):  # Definisce la classe Greeter che estende GreeterServicer
    def SayHello(self, request, context):            # Implementa il metodo SayHello richiesto dal servizio
        print("[server] SayHello method invoked, returning response...")  # Logga che il metodo è stato invocato
        return helloworld_pb2.HelloReply(message="Hello, %s!" % request.name)
        # Restituisce una risposta HelloReply con il messaggio "Hello, <nome>!"

### implemento il metodo serve() che sarà invocato come prima funzione dal main

def serve():

    # mi istanzio un oggetto server da grpc
    # ALERT: i ThreadPool sono quelli del package concurrent e non multiprocess. Alcune diff in: https://stackoverflow.com/questions/20776189/concurrent-futures-vs-multiprocessing-in-python-3
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Crea un server grpc usando un pool di thread per gestire le richieste (massimo 10 thread)

    # aggiungo al server l'oggetto istanza del mio sercizio Greeter
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    # Registra l'implementazione del servizio Greeter al server gRPC

    # faccio il bind con localhost al primo porto libero
    port = server.add_insecure_port("0.0.0.0:0")
    # Assegna il server a una porta libera su tutte le interfacce (0.0.0.0:0)

    # avvio il server
    server.start()
    # Avvia il server e comincia ad ascoltare le richieste

    print("Server started, listening on " + str(port))
    # Stampa la porta su cui il server sta ascoltando

    # attendo che il server termini
    server.wait_for_termination()
    # Blocca il thread principale finché il server non viene terminato


if __name__ == "__main__":
    serve()
    # Se il file viene eseguito direttamente, avvia la funzione serve() per far partire il server

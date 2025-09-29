from __future__ import print_function  # Importa la funzione print compatibile con Python 2 e 3

import logging       # Importa il modulo logging per eventuali log
import sys           # Importa il modulo sys per accedere agli argomenti della riga di comando
import grpc          # Importa la libreria grpc per la comunicazione RPC
import helloworld_pb2        # Importa le classi generate dal file .proto (messaggi)
import helloworld_pb2_grpc   # Importa le classi generate dal file .proto (servizi)

def run():
	
	print("Will try to greet world ...")  # Stampa messaggio di avvio

	# creo un canale verso il server RPC
	with grpc.insecure_channel("localhost:" + sys.argv[1]) as channel: 
		# Crea un canale non sicuro verso il server su localhost e porta passata come argomento

		# creo uno stub (GreeterStub, ovvero ${NOMESERVIZIO}Stub) per invocare tutti i metodi implementati nel servizio
		stub = helloworld_pb2_grpc.GreeterStub(channel)
		# Crea lo stub Greeter per poter chiamare i metodi del servizio Greeter definiti nel .proto

		response = stub.SayHello(helloworld_pb2.HelloRequest(name="you"))
		# Invoca il metodo SayHello del servizio Greeter passando una richiesta HelloRequest con il campo name="you"
		# Riceve la risposta dal server

		print("[CLIENT] SayHello invoked Greeter client received: " + response.message)
		# Stampa il messaggio ricevuto nella risposta del server

			
if __name__ == "__main__":
	run()  # Se il file è eseguito come script principale, chiama la funzione run

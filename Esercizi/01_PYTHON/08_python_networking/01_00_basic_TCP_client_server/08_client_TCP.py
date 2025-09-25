import socket #per avere i metodi socket.socket
import sys    #per l'interfacciamento con il terminale
import time  # Import time module for latency measurement

def client(PORT):

    IP = 'localhost'    #convenzione per client e server sulla stessa macchina
    BUFFER_SIZE = 1024 #max lunghezza messaggio
    MESSAGE = "Hello, World!\n"

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #crea socket #campo 1: protocollo IPv4 campo 2: stream TCP
    s.connect((IP, PORT)) #aggancio ad indirizzo e numero di porto

    start_time = time.time()  # Record the time before sending the request
    s.send(MESSAGE.encode("utf-8")) #utf-8 per avere una convezione comune sui due lati

    data = s.recv(BUFFER_SIZE)
    end_time = time.time()  # Record the time after receiving the reply

    latency = (end_time - start_time) * 1000  # Convert to milliseconds

    print(f"Received data: {data.decode('utf-8')}")
    print(f"Round-trip latency: {latency:.3f} ms")

    #s.close()

if __name__ == "__main__": #invalidazione in eventuali import
    try:
        PORT = int(sys.argv[1])  # Convert input to integer #acquisisce il numero di porto, dal server
    except (IndexError, ValueError):
        print("Please specify a valid PORT as an argument.")
        sys.exit(1)

    while True:
        client(PORT)
        time.sleep(1)

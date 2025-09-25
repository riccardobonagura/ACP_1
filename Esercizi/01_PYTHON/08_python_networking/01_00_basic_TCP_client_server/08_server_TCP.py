"""
# emulazione network delay in un sistema Linux
sudo apt update && sudo apt install iproute2 -y 

## add delay on loopback
sudo tc qdisc add dev lo root netem delay 1000ms

## add corruption of 10% of traffic on loopback
sudo tc qdisc add dev lo root netem corrupt 10%

## add drop of 20% of traffic on loopback
sudo tc qdisc add dev lo root netem drop 10%

## remove delay on loopback
sudo tc qdisc del dev lo root

## list tc rules
sudo tc qdisc show
"""

import socket

IP = '0.0.0.0' #come localhost
PORT = 0 #porto scelto dal so
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((IP, PORT)) #collegamento
s.listen(1)

cur_port = s.getsockname()[1]
# Il metodo getsockname() restituisce un tuple che rappresenta l’indirizzo
# e la porta locale a cui il socket è collegato.
# Per socket IPv4: restituisce una tupla del tipo 
# ('indirizzo_ip', porta), ad esempio ('127.0.0.1', 50000),
# con [1] prendiamo il numero di porto.


print("server on: ", IP, "port: ", cur_port)

# Ciclo infinito per accettare continuamente nuove connessioni dai client
while True:
    # Accetta una nuova connessione. 
    # 'conn' è un nuovo socket usato per comunicare col client,
    # 'addr' è una tupla che contiene (indirizzo IP, porta) del client.
    conn, addr = s.accept()
    
    # Stampa l'indirizzo del client che si è connesso (come stringa)
    print("client addr: " + str(addr))
    
    # Stampa l'indirizzo del client con formattazione alternativa
    print('Connection address: {}'.format(addr))
    
    # Messaggio da inviare al client come risposta
    toClient = "The world never says hello back!\n"
    
    # Riceve dati dal client. 
    # BUFFER_SIZE definisce la quantità massima di byte da leggere (costante definita altrove)
    data = conn.recv(BUFFER_SIZE)
    
    # Stampa i dati ricevuti dal client, decodificandoli da bytes a stringa UTF-8
    print("received data: " + data.decode("utf-8"))
    
    # Invia il messaggio di risposta al client, codificandolo in UTF-8 (da stringa a bytes)
    conn.send(toClient.encode("utf-8"))
    
    # Chiude la connessione col client (ma il server rimane in ascolto per nuovi client)
    conn.close()

# Quando il ciclo termina (ad esempio per una condizione esterna), chiude il socket principale del server
s.close()

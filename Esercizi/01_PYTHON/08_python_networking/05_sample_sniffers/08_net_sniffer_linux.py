import socket, sys  # Importa i moduli necessari per la comunicazione di rete e la gestione del sistema

try:
    # Viene tentata la creazione di una socket di tipo RAW a livello Ethernet (link layer).
    # AF_PACKET: lavora al livello 2 del modello OSI (Ethernet).
    # SOCK_RAW: riceve pacchetti "grezzi" senza elaborazione.
    # socket.ntohs(0x0003): ETH_P_ALL, cattura TUTTI i pacchetti indipendentemente dal protocollo.
    # Nota: servono privilegi di amministratore/root per creare una socket RAW.
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))  # 0x0003 sta per ogni protocollo supportato

except socket.error as msg:
    # Gestione degli errori: se la creazione fallisce, stampa il messaggio e termina il programma.
    print("Socket could not be created. Error Code : " + str(msg[0]) + " Message " + msg[1])
    sys.exit()

# Ciclo infinito che permette di ricevere e stampare i pacchetti di rete continuamente.
while True:
    # Riceve fino a 4096 byte di dati dall'interfaccia di rete e li stampa.
    # Ogni pacchetto ricevuto include sia i dati che l'indirizzo sorgente.
    print(s.recvfrom(4096))

#### ESERCIZIO PROD_CONS con SEMAFORI - VERSIONE CLASSLESS, DIDATTICA, CON COMMENTI PER IL RIPASSO

import threading
import time
from random import randint

# --- CONFIGURAZIONE ---
N_PRODUCERS = 10
N_CONSUMERS = 10
QUEUE_SIZE = 5

# --- CODA E SEMAFORI ---
queue = []  # Coda condivisa (bounded buffer)

mutex = threading.Semaphore(1)      # Mutex per mutua esclusione su tutta la coda (1=libero, 0=occupato)
empty = threading.Semaphore(QUEUE_SIZE)  # Conta spazi liberi (parte da QUEUE_SIZE)
full = threading.Semaphore(0)            # Conta item disponibili (parte da 0)

# --- FUNZIONI UTILITY ---
def produce_item():
    """Genera un item casuale e lo restituisce."""
    return randint(0, 100)

def producer():
    """
    Thread produttore:
    1. Attende che ci sia spazio libero (empty).
    2. Acquisisce il mutex.
    3. Produce e inserisce un item nella coda.
    4. Rilascia il mutex.
    5. Segnala che c'è un nuovo item disponibile (full.release).
    """
    thread_name = threading.current_thread().name
    print(f"[{thread_name}] Started producer")

    empty.acquire()  # Blocca se la coda è piena
    with mutex:
        item = produce_item()
        queue.append(item)
        print(f"[{thread_name}] Produced {item} | Queue: {queue}")
        time.sleep(1)  # Simula tempo produzione (NON PRIMA di acquire!)
    full.release()  # Sblocca consumer

def consumer():
    """
    Thread consumatore:
    1. Attende che ci sia almeno un item disponibile (full).
    2. Acquisisce il mutex.
    3. Consuma (estrae) un item dalla coda.
    4. Rilascia il mutex.
    5. Segnala che c'è uno spazio libero in più (empty.release).
    """
    thread_name = threading.current_thread().name
    print(f"[{thread_name}] Started consumer")

    full.acquire()  # Blocca se la coda è vuota
    with mutex:
        item = queue.pop(0)
        print(f"[{thread_name}] Consumed {item} | Queue: {queue}")
        time.sleep(1)  # Simula tempo consumo
    empty.release()  # Sblocca producer

def main():
    producers = []
    consumers = []

    # Avvio tutti i consumer (si mettono subito in attesa su full se la coda è vuota)
    for i in range(N_CONSUMERS):
        t = threading.Thread(target=consumer, name=f"Consumer-{i}")
        t.start()
        consumers.append(t)

    # Avvio tutti i producer
    for i in range(N_PRODUCERS):
        t = threading.Thread(target=producer, name=f"Producer-{i}")
        t.start()
        producers.append(t)

    # Join su tutti i thread
    for t in producers:
        t.join()
    for t in consumers:
        t.join()

if __name__ == '__main__':
    main()

"""
==================== NOTE PRATICHE E D'ESAME ====================

- Producer e consumer lavorano su una coda condivisa, con accesso protetto da un mutex (semaforo binario).
- Il semaforo 'empty' tiene traccia degli spazi disponibili (inizialmente QUEUE_SIZE).
- Il semaforo 'full' tiene traccia degli item pronti (inizialmente 0).
- Ogni producer fa: empty.acquire -> mutex -> append -> mutex release -> full.release
- Ogni consumer fa: full.acquire -> mutex -> pop(0) -> mutex release -> empty.release
- Se il mutex viene dimenticato, si rischiano race condition e corruzione della coda (es. due thread fanno pop/append contemporaneamente).
- L'ordine di avvio (prima consumer, poi producer) fa sì che i consumer si mettano subito in attesa (full==0), poi i producer li sbloccano.
- L'effetto batch (blocchi di produzioni/consumi consecutivi) deriva dallo scheduler e dalla concorrenza: non è richiesta alternanza uno-a-uno.
- Il pattern è identico se implementato con processi (usando multiprocessing.Semaphore/Queue), basta che la coda e i semafori siano condivisi.
- NON mettere sleep() prima di acquire: il thread deve dormire solo dopo aver acquisito le risorse necessarie.
- Usare nomi chiari aiuta a leggere i log e a interpretare la concorrenza.

PAROLE CHIAVE DA RICORDARE:
semaphore, mutex, acquire, release, race condition, deadlock, starvation, bounded buffer, producer, consumer, effetto batch

"""
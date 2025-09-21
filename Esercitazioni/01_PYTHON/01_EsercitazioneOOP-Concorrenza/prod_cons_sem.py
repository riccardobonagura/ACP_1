#### ESERCIZIO PROD_CONS con SEMAFORI con MULTITHREADING

import logging
import threading
import time
from random import randint

# --- COSTANTI E CONFIGURAZIONE ---
CONSUMER = 'Consumer'
PRODUCER = 'Producer'
N_CONSUMERS = 10
N_PRODUCERS = 10
QUEUE_SIZE = 5

# Inizializza logging per tracciare le operazioni dei thread
logging.basicConfig(level=logging.DEBUG, format='[%(threadName)-0s] %(message)s',)

# --- UTILITY CODA ---

def get_an_available_item(queue):
    # Estrae il primo elemento dalla coda (consumo)
    return queue.pop(0)

def make_an_item_available(queue):
    # Genera un item random, lo aggiunge in coda (produzione)
    item = randint(0, 100)
    queue.append(item)
    return item

# --- THREAD CONSUMATORE ---
class consumerThread(threading.Thread):
    """
    Ogni consumer:
      - attende che ci sia almeno un elemento da consumare (full)
      - acquisisce il mutex dei consumer
      - consuma un elemento
      - rilascia il mutex
      - segnala che c’è uno spazio libero (empty.release())
    """
    def __init__(self, mutex_C, empty, full, queue, name):
        threading.Thread.__init__(self, name=name)
        self.mutex_C = mutex_C
        self.empty = empty
        self.full = full
        self.queue = queue

    def run(self):
        logging.debug('\t\t\tStarted')

        logging.debug('\t\t\tChecking full semaphore ...')
        self.full.acquire()  
        # Si blocca qui se non ci sono elementi pronti da consumare (full == 0).
        # Se ci sono elementi, decrementa full e prosegue.

        # Acquisisce il mutex per la mutua esclusione tra consumatori
        with self.mutex_C: 
            logging.debug('\t\t\tAcquired mutex')
            time.sleep(1.0)  # Simula il tempo di consumo
            item = get_an_available_item(self.queue)
            logging.debug('\t\t\tItem: %r', item)
            logging.debug('\t\t\tRelease mutex')

        # Rilascia uno spazio libero nella coda (empty)
        self.empty.release()  
        logging.debug('\t\t\tReleased empty semaphore')

# --- THREAD PRODUTTORE ---
def produce_one_item(mutex_P, empty, full, queue):
    """
    Ogni producer:
      - attende che ci sia almeno uno spazio libero nella coda (empty)
      - acquisisce il mutex dei produttori
      - produce un elemento
      - rilascia il mutex
      - segnala che c’è un nuovo elemento disponibile (full.release())
    """
    logging.debug('Started')
    logging.debug('Checking empty semaphore...')
    empty.acquire()
    # Si blocca qui se non ci sono spazi liberi (empty == 0).
    # Se c’è almeno uno spazio, decrementa empty e prosegue.

    with mutex_P:  # Acquisisce il mutex per la mutua esclusione tra produttori
        logging.debug('Acquired mutex')
        time.sleep(1.0)  # Simula il tempo di produzione
        item = make_an_item_available(queue)
        logging.debug('Item: %r', item)
        logging.debug('Release mutex')

    # Rilascia un elemento pronto per essere consumato (full)
    full.release()
    logging.debug('Released full semaphore')

# --- MAIN THREAD ---
def main():
    # Coda condivisa come lista Python
    queue = [] 

    # Semafori per la mutua esclusione e il controllo della capacità
    mutex_P = threading.Semaphore()  # = 1, mutua esclusione tra produttori
    mutex_C = threading.Semaphore()  # = 1, mutua esclusione tra consumatori
    empty = threading.Semaphore(QUEUE_SIZE)  # inizialmente tutta la coda è libera
    full = threading.Semaphore(0)  # inizialmente nessun item è disponibile

    consumers = []
    producers = []

    # Avvio dei consumatori
    for i in range(N_CONSUMERS):
        name = CONSUMER + str(i)
        ct = consumerThread(mutex_C, empty, full, queue, name)
        ct.start()
        consumers.append(ct)

    # Avvio dei produttori
    for i in range(N_PRODUCERS):
        pt = threading.Thread(
            target=produce_one_item, 
            name=PRODUCER + str(i),
            args=(mutex_P, empty, full, queue),
        )
        pt.start()
        producers.append(pt)

    # Attendo la terminazione di tutti i consumer
    for i in range(N_CONSUMERS):
        consumers[i].join()

    # Attendo la terminazione di tutti i producer
    for i in range(N_PRODUCERS):
        producers[i].join()

if __name__ == '__main__':
    main()

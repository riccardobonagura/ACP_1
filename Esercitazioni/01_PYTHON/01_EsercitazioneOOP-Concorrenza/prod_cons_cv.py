#### ESERCIZIO PROD_CONS con variabili condition
# VERSIONE ANNOTATA: commenti dettagliati per ripasso e tracce d'esame
# - Pattern produttore/consumatore con thread Python
# - Sincronizzazione tramite Condition Variable (CV)
# - Best practice, errori da evitare, spiegazione di ogni passo

import logging
import threading
import time
from random import randint

# Costanti: nomi thread, dimensione coda, numeri di produttori/consumatori
CONSUMER = 'Consumer'
PRODUCER = 'Producer'
N_CONSUMERS = 10
N_PRODUCERS = 10
QUEUE_SIZE = 5

# Configurazione logging: mostra nome thread e messaggio, utile per tracing multithread
logging.basicConfig(level=logging.DEBUG, format='[%(threadName)-0s] %(message)s',)

# --- UTILITY CODA ---

def an_item_is_available(queue):
    """True se la coda NON è vuota (almeno un item da consumare)."""
    return not (len(queue) == 0)

def a_space_is_available(queue):
    """True se la coda NON è piena (almeno uno spazio per produrre)."""
    return not (len(queue) == QUEUE_SIZE)

def get_an_available_item(queue):
    """Estrae e ritorna il primo elemento disponibile dalla coda."""
    return queue.pop(0)

def make_an_item_available(queue):
    """Genera un item random, lo aggiunge in coda e lo ritorna."""
    item = randint(0, 100)
    queue.append(item)
    return item

# --- THREAD CONSUMATORE ---
class consumerThread(threading.Thread):
    # Sottoclasse di Thread: buona pratica quando serve stato interno, logica complessa, più manutenzione

    def __init__(self, producer_cv, consumer_cv, queue, name):
        # Attributi: CV, coda, nome
        threading.Thread.__init__(self, name=name)
        self.producer_cv = producer_cv
        self.consumer_cv = consumer_cv
        self.queue = queue

    def run(self):
        logging.debug('\t\t\tStarted')
        # Entrata in sezione critica: acquisisco lock associato alla consumer_cv
        with self.consumer_cv:
            logging.debug('\t\t\tObtained lock')

            # --- BEST PRACTICE: usare SEMPRE ciclo WHILE attorno a .wait() ---
            # - Serve per gestire risvegli spurii (thread risvegliato senza notify) e race tra molti thread
            # - Se si usasse IF, due consumer potrebbero consumare lo stesso elemento o fallire con pop su lista vuota
            while not an_item_is_available(self.queue):
                logging.debug('\t\t\tWaiting')
                self.consumer_cv.wait()  # Rilascia lock e si sospende su questa CV

            # SOLO ora posso consumare: simulo il tempo di consumo
            # --- ERRORE DA EVITARE: non mettere sleep() dentro il while, altrimenti tengo lock inutilmente e rallento sistema ---
            time.sleep(1.0)
            item = get_an_available_item(self.queue)
            logging.debug('\t\t\tItem: %r', item)

            # NOTIFICO i produttori: ora c'è spazio in coda
            # - notify() risveglia UNO solo tra i produttori in attesa (efficiente, evita storm di risvegli inutili)
            # - notify_all() risveglierebbe tutti (si usa solo in casi particolari)
            logging.debug('\t\t\tNotify')
            self.producer_cv.notify()

        # Uscita da "with": rilascio lock, altri thread possono entrare
        logging.debug('\t\t\tReleased lock')

# --- THREAD PRODUTTORE ---
def produce_one_item(producer_cv, consumer_cv, queue):
    # Funzione target: va bene per thread "usa e getta" semplici, senza stato interno
    logging.debug('Started')

    # Entrata in sezione critica: acquisisco lock tramite producer_cv
    with producer_cv:
        logging.debug('Obtained lock')

        # --- BEST PRACTICE: while su .wait()! Vedi motivi sopra ---
        while not a_space_is_available(queue):
            logging.debug('Waiting')
            producer_cv.wait()  # Rilascia lock e si sospende

        # SOLO ora posso produrre
        time.sleep(1.0)
        item = make_an_item_available(queue)
        logging.debug('Item: %r', item)

        # NOTIFICO un consumer: ora c'è almeno un item da consumare
        logging.debug('Notify')
        consumer_cv.notify()

    logging.debug('Released lock')

# --- MAIN THREAD ---
def main():
    # Inizializzo coda condivisa
    queue = []

    # Creo UN SOLO lock condiviso per entrambe le CV: garantisce mutua esclusione su tutta la coda
    # --- ERRORE DA EVITARE: chiamare wait/notify senza possedere il lock -> RuntimeError e race condition! ---
    cv_lock = threading.Lock()
    producer_cv = threading.Condition(lock=cv_lock)
    consumer_cv = threading.Condition(lock=cv_lock)

    consumers = []
    producers = []

    # --- AVVIO CONSUMER ---
    # - I due for sono sequenziali: sono sicuro che tutti i consumer sono creati prima dei producer,
    #   MA non è garantito che siano tutti già attivi (dipende dallo scheduler, non importa per la correttezza)
    for i in range (N_CONSUMERS):
        name=CONSUMER+str(i)
        ct = consumerThread(producer_cv, consumer_cv, queue, name)
        ct.start()
        consumers.append(ct)  # Ordine tra start() e append() non influisce

    # --- AVVIO PRODUCER ---
    for i in range (N_PRODUCERS):
        pt = threading.Thread(
            target=produce_one_item,
            name=PRODUCER+str(i),
            args=(producer_cv, consumer_cv, queue),
        )
        pt.start()
        producers.append(pt)

    # --- JOIN: attendo terminazione di TUTTI i consumer ---
    for i in range (N_CONSUMERS):
        consumers[i].join()

    # --- JOIN: attendo terminazione di TUTTI i producer ---
    for i in range (N_PRODUCERS):
        producers[i].join()

# --- AVVIO PROGRAMMA ---
if __name__ == '__main__':
    main()

"""
================== NOTE DI RIPASSO (da portare all'esame) ==================

PATTERN PRODUTTORE/CONSUMATORE:
- Producer produce item se c'è spazio; consumer consuma se c'è almeno un item.
- Coda condivisa a capacità limitata (bounded queue): evitare overflow o consumi su coda vuota.
- Sincronizzazione tramite Condition Variable (Condition + Lock):
    - .wait() -> thread si sospende e rilascia lock
    - .notify() -> risveglia uno dei thread sospesi su quella CV
    - SEMPRE usare ciclo while attorno a .wait() per evitare risvegli spurii e race tra thread

ERRORI DA EVITARE:
- Usare IF invece di WHILE attorno a .wait() -> bug e race condition.
- Mettere sleep() dentro il while -> lock tenuto troppo a lungo, sistema lento o deadlock.
- Chiamare wait/notify senza possedere il lock -> RuntimeError.
- Più producer di quanti la coda possa contenere senza abbastanza consumer -> deadlock (thread sospesi in attesa per sempre).

BEST PRACTICE:
- Sottoclasse Thread per consumer se serve stato interno/logica complessa; funzione target per producer "semplici".
- Logging dettagliato con nomi thread per capire come avviene la sincronizzazione.
- Due for separati per avviare thread: sono sempre sequenziali, ma il "vero" avvio dipende dallo scheduler.
- Ogni notify risveglia solo chi serve, non tutti (efficienza).

TRANSFER VERSO SISTEMI DISTRIBUITI:
- In sistemi come STOMP/JMS/gRPC, la coda è gestita da un broker/server, i client fanno SEND (producer) o SUBSCRIBE (consumer).
- Le stesse regole valgono per la sincronizzazione, ma la mutua esclusione è implementata dal middleware (non da lock locali).
- La gestione della capacità (QUEUE_SIZE) può essere locale, oppure demandata a controlli di flusso del broker/server.

PAROLE CHIAVE:
- condition variable, wait, notify, lock, mutua esclusione, deadlock, risveglio spurio, bounded queue, race condition, pattern produttore-consumatore

================== NOTE SULLA SUCCESSIONE DELLE ATTIVAZIONI "A BATCH" ==================

Perché produttori e consumatori lavorano "a blocchi" (batch), invece che alternarsi uno a uno?

- All’avvio, tutti i consumer partono per primi (perché sono creati e avviati prima), acquisiscono il lock in sequenza e trovano la coda vuota: vanno tutti subito in attesa (wait).
- Poi partono tutti i producer. Il primo producer acquisisce il lock, produce un item, notifica un consumer e rilascia il lock. Tuttavia, quando esce dal with, il lock può essere acquisito sia da altri producer che da consumer risvegliati.
- In pratica, con molti thread pronti, è molto probabile che altri producer (che sono tutti nello stato "ready" e non sospesi) riescano ad acquisire il lock uno dopo l'altro, producendo rapidamente fino a riempire la coda. Solo quando la coda è piena, i producer restanti vanno in attesa.
- A quel punto i consumer che erano stati notificati possono finalmente acquisire il lock, consumare e notificare i producer a loro volta. Anche qui, l'acquisizione del lock non è garantita in ordine stretto: spesso si osserva un blocco di consumer che svuota tutta la coda.
- Questo fenomeno è dovuto al fatto che le Condition Variable non garantiscono priorità tra thread risvegliati: il lock va semplicemente al prossimo thread "ready" nello scheduling del sistema operativo.
- Il risultato è un'alternanza a blocchi: prima una sequenza di produzioni, poi una sequenza di consumi, e così via (batch), non uno a uno.

CONCETTO DA PORTARE ALL’ESAME:
- L’effetto batch è fisiologico in presenza di molti thread concorrenti e dipende sia dalla logica delle Condition Variable sia dallo scheduling del sistema operativo.
- L’alternanza uno-a-uno tra producer e consumer non è garantita (e nemmeno richiesta dalla correttezza della soluzione), conta solo che la coda non venga mai letta vuota o scritta piena, e che nessun thread rimanga bloccato per sempre senza motivo.

"""


================================================================================
README - Ripasso Produttore/Consumatore, Concorrenza & Pattern Distribuiti
================================================================================

PANORAMICA GENERALE
-------------------
Questa giornata di studio ha riguardato a fondo il paradigma produttore/consumatore
in Python, con particolare attenzione ai pattern e alle best practice di
programmazione concorrente e ai loro errori tipici.

Abbiamo visto:
- Differenza tra gestione con Condition Variable (CV) e con Semaphore.
- Strutture e flussi standard del pattern bounded buffer.
- Analisi di codice con annotazioni step by step.
- Domande critiche per la comprensione (con le tue risposte e le aggiunte di Copilot).
- Riflessione continua su errori da evitare e sulle buone pratiche.
- Inizio del transfer concettuale verso sistemi distribuiti (magazzino/proxy/skeleton, broker JMS/STOMP).

--------------------------------------------------------------------------------
SINTESI DEI PRINCIPALI CONCETTI AFFRONTATI
--------------------------------------------------------------------------------
- **Pattern produttore/consumatore:** risolve il problema della comunicazione e coordinamento tra chi produce dati e chi li consuma, su una coda a capacità limitata (bounded buffer).
- **Concorrenza locale:** thread/processi accedono in modo sicuro a risorse condivise, usando semafori, mutex, condition variable.
- **Sincronizzazione:** garantire accesso corretto, evitare race condition, deadlock e starvation.
- **Effetto batch:** alternanza non perfetta tra produttori e consumatori, dovuta allo scheduling e non alla logica di correttezza.
- **Transfer verso distribuito:** pattern identico, ma la sincronizzazione è gestita dal server/broker, i client sono solo endpoint.

--------------------------------------------------------------------------------
DOMANDE CRITICHE: RISPOSTE, COMMENTI E AGGIUNTE
--------------------------------------------------------------------------------

1. **Che differenza c’è tra una Condition Variable e un Semaphore?**
   - *Tua risposta:*  
     La gestione dei semafori prevede 4 costrutti di controllo, due per la concorrenza (mutex), su cui viene chiamato il with, e due per l'accesso alle risorse (acquire/release). La gestione con cv richiede solo due variabili di controllo e un costrutto while per assicurare l’accesso alla risorsa condivisa solo in caso di disponibilità; la sincronizzazione avviene tramite metodi wait e notify.
   - *Aggiunta Copilot:*  
     Il semaphore è un contatore di risorse, può implementare anche un mutex (se inizializzato a 1), mentre la Condition Variable si associa a un lock/mutex e serve per mettere in attesa (wait) o risvegliare (notify) thread su una certa condizione. La CV non conta le risorse, ma coordina l’attesa su una condizione specifica.

2. **Nel pattern produttore/consumatore, perché ogni consumer deve poter notificare i producer (e viceversa)?**
   - *Tua risposta:*  
     Perché entrambi devono attendere il verificarsi di una condizione che è in possesso dell'altra entità: il consumatore deve essere avvisato dal produttore quando un item è stato prodotto, il consumatore avvisa quando ha consumato, attivando il produttore per una nuova produzione.
   - *Aggiunta Copilot:*  
     Ogni gruppo notifica l’altro per evitare attese indefinite e sbloccare chi può procedere: producer notifica consumer quando produce, consumer notifica producer quando consuma e libera spazio.

3. **Perché si usa il ciclo while attorno a cv.wait() e non un semplice if?**
   - *Tua risposta:*  
     Perché altrimenti si creerebbe una race condition tra più istanze thread risvegliate.
   - *Aggiunta Copilot:*  
     Inoltre, il while protegge dai risvegli spurii: un thread può svegliarsi senza che la condizione sia cambiata. Il ciclo while garantisce che il thread controlli nuovamente la condizione prima di procedere.

4. **Cosa succede se due consumer vengono risvegliati contemporaneamente e la coda contiene un solo elemento?**
   - *Tua risposta:*  
     Race condition: solo uno dei due otterrà la risorsa e questo porta a RunTimeError.
   - *Aggiunta Copilot:*  
     L’altro thread cercherà di fare pop su una lista vuota (IndexError in Python). Da qui la necessità di usare il ciclo while.

5. **A cosa serve il lock condiviso tra le due Condition Variable?**
   - *Tua risposta:*  
     Ad impedire che consumo e produzione avvengano contemporaneamente.
   - *Aggiunta Copilot:*  
     Garantisce mutua esclusione su tutta la coda, sia lato produzione che consumo, prevenendo race condition.

6. **Che cosa succede se chiami wait() o notify() senza aver acquisito il lock associato?**
   - *Tua risposta:*  
     RunTimeError.
   - *Aggiunta Copilot:*  
     Inoltre si rischia una race condition se il lock non protegge la coda.

7. **Spiega con parole tue cosa si intende per “risveglio spurio” (spurious wakeup).**
   - *Tua risposta:*  
     È quando un thread si risveglia ma non ci sono le condizioni per cui esegua, quindi il programmatore deve garantire che torni a dormire senza fare danni.
   - *Aggiunta Copilot:*  
     Per questo il ciclo while attorno a wait() è fondamentale.

8. **Perché nel codice annotato i thread consumer sono implementati come sottoclassi di Thread mentre i producer sono semplici funzioni?**
   - *Tua risposta:*  
     Scelta arbitraria e didattica. Entrambe le soluzioni sono valide, la prima è più robusta, la seconda meno boilerplate e più leggera alla lettura.
   - *Aggiunta Copilot:*  
     La sottoclasse Thread è utile se serve stato interno o logica complessa, la funzione va bene per thread semplici.

9. **Perché il semaforo empty parte da QUEUE_SIZE e full da 0?**
   - *Tua risposta:*  
     Empty segna i posti liberi e all'inizio la coda è vuota, full segna i posti occupati quindi zero.
   - *Aggiunta Copilot:*  
     Ogni producer decrementa empty prima di produrre e incrementa full dopo; ogni consumer fa il contrario.

10. **Cosa succede se dimentichi il mutex e due thread modificano la coda contemporaneamente?**
    - *Tua risposta:*  
      Race condition: outcome non prevedibile.
    - *Aggiunta Copilot:*  
      Si rischia perdita di dati, corruzione dello stato della coda, possibili eccezioni.

11. **Descrivi il flusso di operazioni che avviene quando un producer deve produrre un item.**
    - *Tua risposta:*  
      1. Chiede con acquire di poter scrivere sulla coda  
      2. Aspetta una release se la coda è piena, altrimenti salta a 3  
      3. Acquisisce il mutex dei produttori, altrimenti aspetta in coda  
      4. Produce l'item e lo inserisce nella coda  
      5. Segnala con release ai consumatori che un nuovo item è disponibile
    - *Aggiunta Copilot:*  
      Sequenza corretta! Da ricordare: il mutex va acquisito dopo il semaforo per proteggere solo la sezione critica.

12. **Cosa succede se avvii prima tutti i consumer e poi tutti i producer? L’output sarà alternato uno a uno? Perché?**
    - *Tua risposta:*  
      L'output sarà ordinato a gruppi di 5 perché appena un produttore avrà finito ce ne sarà subito un altro pronto per eseguire che batte sul tempo il consumatore che si risveglia.
    - *Aggiunta Copilot:*  
      L’effetto batch nasce perché molti thread dello stesso tipo sono in stato ready, lo scheduler li fa avanzare in gruppo.

13. **Come si trasferisce il pattern dei semafori in un contesto distribuito (es. server JMS, STOMP)?**
    - *Tua risposta:*  
      Il server consuma e il client produce.
    - *Aggiunta Copilot:*  
      In realtà il broker/server gestisce la coda e la logica di sincronizzazione; i client sono produttori o consumatori che si bloccano quando non possono procedere, ma il blocco è gestito dal middleware.

14. **In che modo l’effetto “batch” nasce dallo scheduling e non dalla logica del pattern?**
    - *Tua risposta:*  
      Spiegato sopra.
    - *Aggiunta Copilot:*  
      Dipende dal fatto che molti thread vengono risvegliati insieme e lo scheduler decide chi avanza, non la logica stessa del codice.

15. **Cosa succede se il numero di producer è molto maggiore della capacità della coda e non ci sono abbastanza consumer attivi?**
    - *Tua risposta:*  
      Deadlock, i producer non fanno mai join e il main attende senza fine.
    - *Aggiunta Copilot:*  
      I producer restano bloccati su empty.acquire(), il sistema si blocca se non ci sono consumer che svuotano la coda.

--------------------------------------------------------------------------------
COME QUESTI PATTERNS VENGONO INTEGRATI NEI SISTEMI DISTRIBUITI
--------------------------------------------------------------------------------

- Nei sistemi distribuiti (es. magazzino con Proxy/Skeleton, broker JMS, STOMP, gRPC):
    - Il ruolo di coda, mutex/semaforo viene assunto dal server/broker.
    - I client fanno richieste di produzione/prelievo, ma non gestiscono direttamente la sincronizzazione.
    - La logica di "bounded buffer" viene replicata lato server: il server controlla capacità, blocca le richieste se la coda è piena/vuota, notifica i client quando possono procedere.
    - Lo schema di attesa, notifica e batch rimane fondamentale, ma implementato su componenti distribuiti e non solo su thread locali.
    - In esercizi d’esame, aspettati sempre una domanda su come il pattern visto in locale si trasferisce su architetture distribuite!

--------------------------------------------------------------------------------
CONSIGLI DI STUDIO E RIPASSO
--------------------------------------------------------------------------------
- Prima padroneggia la concorrenza locale (thread/processi, mutex/CV/Semaphore).
- Allenati a leggere log e output per capire l’effetto batch.
- Nella scrittura delle soluzioni, cura sempre la chiarezza del flusso e dei nomi.
- Quando studi i sistemi distribuiti, cerca sempre il transfer: la logica della coda non cambia, cambiano solo gli endpoint e il contesto di esecuzione.
- Rivedi periodicamente queste domande critiche, integrando i dettagli delle aggiunte Copilot.

================================================================================

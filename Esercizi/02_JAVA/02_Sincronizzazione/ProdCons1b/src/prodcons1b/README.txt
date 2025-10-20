# ProdCons1b - Producer-Consumer con Sincronizzazione

Implementazione del problema **Producer-Consumer** in Java utilizzando meccanismi 
di sincronizzazione con `synchronized`, `wait()` e `notifyAll()`.

Coordinare thread che producono e consumano dati da un buffer condiviso, 
evitando race condition e garantendo la corretta sincronizzazione.


### Componenti Principali

```
┌─────────────┐         ┌──────────┐         ┌─────────────┐
│  Producer   │────────>│  Buffer  │<────────│  Consumer   │
│   Thread    │ produci │ (shared) │ consuma │   Thread    │
└─────────────┘         └──────────┘         └─────────────┘
```

### 1. **Buffer.java** - Risorsa Condivisa
Gestisce la sincronizzazione tra produttori e consumatori.

**Stato Interno:**
- `content`: valore long contenente il timestamp di produzione
- `full`: flag booleano che indica se il buffer è pieno o vuoto
  - `false` = buffer vuoto (può essere prodotto)
  - `true` = buffer pieno (può essere consumato)

**Metodi Sincronizzati:**

#### `synchronized void produci()`
```java
while (full) {
    wait();  // Attende se buffer pieno
}
content = System.currentTimeMillis();
full = true;
notifyAll();  // Notifica i consumatori
```

**Comportamento:**
1. Se il buffer è pieno (`full == true`), il produttore si mette in attesa
2. Quando può procedere, produce un timestamp
3. Imposta `full = true`
4. Sveglia tutti i thread in attesa

#### `synchronized void consuma()`
```java
while (!full) {
    wait();  // Attende se buffer vuoto
}
System.out.println("consumato = " + content);
full = false;
notifyAll();  // Notifica i produttori
```

**Comportamento:**
1. Se il buffer è vuoto (`full == false`), il consumatore si mette in attesa
2. Quando può procedere, consuma il contenuto
3. Imposta `full = false`
4. Sveglia tutti i thread in attesa

### 2. **Producer.java** - Thread Produttore
```java
public void run() {
    buffer.produci();
}
```

Thread che invoca il metodo `produci()` sul buffer condiviso.

### 3. **Consumer.java** - Thread Consumatore
```java
public void run() {
    buffer.consuma();
}
```

Thread che invoca il metodo `consuma()` sul buffer condiviso.

### 4. **Test.java** - Classe di Test Interattiva
Interfaccia da linea di comando che permette di creare dinamicamente produttori e consumatori.

**Input:**
- `0` → Crea un nuovo Consumer
- `1` → Crea un nuovo Producer

## 🔄 Meccanismo di Sincronizzazione

### Monitor Java (Intrinsic Lock)
Ogni oggetto Java ha un **monitor** implicito utilizzato dai metodi `synchronized`.

```java
synchronized void produci() { ... }
```
È equivalente a:
```java
void produci() {
    synchronized(this) { ... }
}
```

### Pattern Wait-Notify

#### Loop di Attesa (Wait Loop)
```java
while (condizione_non_soddisfatta) {
    wait();
}
```

**Perché `while` e non `if`?**
- Protezione da **spurious wakeup** (risveglio spontaneo)
- Possibili interruzioni tra `notify()` e risveglio
- Multipli thread potrebbero essere risvegliati contemporaneamente

#### Notifica
```java
notifyAll();  // Sveglia TUTTI i thread in attesa
```

**Perché `notifyAll()` invece di `notify()`?**
- `notify()` sveglia UN SOLO thread casuale
- Con `notifyAll()` si garantisce che sia produttori che consumatori vengano notificati
- Evita situazioni di deadlock con thread multipli

## 🎯 Flusso di Esecuzione

### Scenario: Buffer Inizialmente Vuoto

```
1. Producer_1 invoca produci()
   → buffer vuoto (full=false)
   → produce content = timestamp
   → full = true
   → notifyAll()

2. Consumer_1 invoca consuma()
   → buffer pieno (full=true)
   → consuma content
   → full = false
   → notifyAll()

3. Consumer_2 invoca consuma()
   → buffer vuoto (full=false)
   → wait()... ⏳

4. Producer_2 invoca produci()
   → buffer vuoto (full=false)
   → produce nuovo content
   → full = true
   → notifyAll()
   → Consumer_2 si risveglia ✓
```

## 💻 Esempio di Utilizzo

### Compilazione
```bash
cd Esercizi/02_JAVA/02_Sincronizzazione/ProdCons1b/src
javac prodcons1b/*.java
```

### Esecuzione
```bash
java prodcons1b.Test
```

### Sessione Interattiva
```
0 (C) /1 (P) >> 1
								producer_1:  invocazione produci
								producer_1:  prodotto = 1729450944123

0 (C) /1 (P) >> 0
		consumer_1:  invocazione consuma
		consumer_1:  consumato = 1729450944123

0 (C) /1 (P) >> 0
		consumer_2:  invocazione consuma
		consumer_2:  in attesa (buffer vuoto)

0 (C) /1 (P) >> 1
								producer_2:  invocazione produci
								producer_2:  prodotto = 1729450950456
		consumer_2:  consumato = 1729450950456
```


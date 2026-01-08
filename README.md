# Forest Fire Automaton

## Opis problema

**Forest Fire Automaton** je simulaciona aplikacija zasnovana na **celularnim automatima**, čiji je cilj modelovanje širenja požara u šumskom ekosistemu pomoću lokalnih pravila i diskretne simulacije u vremenu. Sistem demonstrira kako jednostavna lokalna pravila mogu dovesti do kompleksnog i nepredvidivog globalnog ponašanja, što je osnovni princip celularnih automata.

Aplikacija rešava sledeće probleme i izazove:

- Modelovanje kompleksnih sistema  
- Diskretna simulacija u vremenu  
- Analiza emergentnog ponašanja  
- Vizualizacija algoritama  
- Eksperimentisanje sa parametrima  
- Poređenje sekvencijalnih i paralelnih implementacija  

Rešenje je implementirano korišćenjem **programskih jezika Python i Rust**, sa posebnim fokusom na **paralelizaciju i analizu performansi**.

---

## Model celularnog automata

### Stanja ćelija

Svaka ćelija u mreži može biti u jednom od sledećih stanja:

- **Empty** – Prazno polje  
- **Tree** – Drvo  
- **Burning** – Drvo koje trenutno gori  

---

### Pravila prelaza

Pravila simulacije se primenjuju **sinhrono** na sve ćelije u svakom vremenskom koraku:

1. Ćelija u stanju **Burning** prelazi u stanje **Empty**
2. Ćelija u stanju **Tree** prelazi u stanje **Burning** ako bar jedan od njenih suseda gori
3. Ćelija u stanju **Tree** može spontano da se zapali sa verovatnoćom **p**
4. Ćelija u stanju **Empty** može izrasti u **Tree** sa verovatnoćom **g**

---

## Implementacija rešenja

### Python implementacija

U programskom jeziku **Python** implementirane su sledeće verzije:

- **Sekvencijalna verzija**
  - Iterativno ažuriranje stanja mreže
  - Generisanje fajlova sa stanjima sistema po iteracijama

- **Paralelna verzija**
  - Paralelizacija korišćenjem `multiprocessing` biblioteke
  - Podela mreže po redovima/blokovima
  - Sinhronizacija rezultata po iteracijama

Rezultat svake simulacije je **datoteka koja sadrži promene stanja sistema po iteracijama**, namenjena daljoj analizi i vizualizaciji.

---

### Rust implementacija

U programskom jeziku **Rust** implementirane su sledeće verzije:

- **Sekvencijalna verzija**
  - Efikasna obrada dvodimenzionalne mreže
  - Determinističko generisanje stanja po iteracijama

- **Paralelna verzija**
  - Paralelizacija uz oslonac na **niti (threads)**
  - Podela mreže na nezavisne segmente
  - Sinhrona razmena podataka između niti

Kao i u Python verziji, rezultat simulacije su **datoteke sa stanjima sistema po iteracijama**.

---

## Eksperimenti skaliranja

### Strong Scaling

- Fiksna veličina problema 
- Povećavanje broja procesa / niti
- Merenje ubrzanja paralelizovane verzije u odnosu na sekvencijalnu

Eksperimenti se sprovode odvojeno za:
- Python implementaciju
- Rust implementaciju

---

### Weak Scaling

- Povećavanje veličine problema proporcionalno broju procesa / niti
- Analiza održavanja performansi pri većem opterećenju
- Poređenje ponašanja Python i Rust implementacija

---

## Vizualizacija rezultata

Vizualizacija simulacije se vrši **na osnovu prethodno generisanih datoteka**, bez direktnog učešća simulacionog koda.

- Vizualizacija stanja sistema po iteracijama
- Prikaz evolucije požara kroz vreme
- Implementacija vizualizacije u **Rust okruženju**
- Moguća upotreba biblioteka:
  - `plotters`
  - `pixels`
  - `macroquad`

---

## Arhitektura sistema

### Glavne komponente

#### Grid Engine
- **Odgovornost:** Čuvanje i ažuriranje stanja mreže  
- **Implementacija:** 2D niz  
- **Funkcionalnosti:** Pristup ćelijama, računanje suseda, sinhroni update  

#### Simulation Engine
- **Odgovornost:** Primena pravila celularnog automata  
- **Funkcionalnosti:** Iteracije simulacije, generisanje sledećeg stanja mreže  

#### Parallel Engine
- **Odgovornost:** Paralelizacija računanja  
- **Python:** `multiprocessing`  
- **Rust:** `std::thread`  

#### Renderer
- **Odgovornost:** Vizualizacija rezultata  
- **Funkcionalnosti:** Prikaz stanja sistema po iteracijama  

---

## Tehnologije

- **Programski jezici:** Python, Rust  
- **Paradigma:** Cellular Automata  
- **Python paralelizacija:** `multiprocessing`  
- **Rust paralelizacija:** Threads (`std::thread`)  
- **Randomizacija:** `rand` Rust, `random` Python
- **Vizualizacija:** Plotters / pixels / macroquad  
- **Build sistem:** Cargo  

---

## Cilj projekta

Cilj projekta je:

- Implementacija i poređenje **sekvencijalnih i paralelnih rešenja**
- Analiza performansi kroz **jako i slabo skaliranje**
- Praktična primena **celularnih automata** u Python i Rust jezicima
- Razumevanje uticaja paralelizacije na simulaciju kompleksnih sistema

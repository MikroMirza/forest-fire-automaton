# Forest Fire Automaton

## Opis problema

**Forest Fire Automaton** je simulaciona aplikacija zasnovana na **celularnim automatima**, čiji je cilj modelovanje širenja požara u šumskom ekosistemu pomoću lokalnih pravila i diskretne simulacije u vremenu. Sistem demonstrira kako jednostavna lokalna pravila mogu dovesti do kompleksnog i nepredvidivog globalnog ponašanja, što je osnovni princip celularnih automata.

Aplikacija rešava sledeće probleme i izazove:

- Modelovanje kompleksnih sistema  
- Diskretna simulacija u vremenu  
- Analiza emergentnog ponašanja  
- Vizualizacija algoritama  
- Eksperimentisanje sa parametrima  

Rešenje je implementirano kao **monolitna simulaciona aplikacija** koja koristi dvodimenzionalnu mrežu (grid) ćelija. Svaka ćelija predstavlja deo šume i može se nalaziti u jednom od diskretnih stanja.

Simulacija se odvija u diskretnim vremenskim koracima, pri čemu se novo stanje svake ćelije računa isključivo na osnovu:

- njenog trenutnog stanja  
- stanja njenih susednih ćelija  
- definisanih verovatnoća  

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

## Arhitektura sistema

### Glavne komponente

#### Grid Engine
- **Odgovornost:** Čuvanje i ažuriranje stanja mreže  
- **Implementacija:** 2D niz  
- **Funkcionalnosti:** Pristup ćelijama, računanje suseda, sinhroni update  

#### Simulation Engine
- **Odgovornost:** Primena pravila celularnog automata  
- **Funkcionalnosti:** Iteracije simulacije, generisanje sledećeg stanja mreže  

#### Random Engine
- **Odgovornost:** Generisanje slučajnih događaja  
- **Funkcionalnosti:** Verovatnoća paljenja i rasta stabala  

#### Renderer
- **Odgovornost:** Vizualizacija trenutnog stanja simulacije  
- **Funkcionalnosti:** Prikaz mreže u realnom vremenu (različite boje za stanja)  

#### Configuration Module
- **Odgovornost:** Parametrizacija simulacije  
- **Funkcionalnosti:** Veličina mreže, verovatnoće, brzina simulacije  

---

## Tehnologije

- **Programski jezik:** Rust  
- **Paradigma:** Cellular Automata  
- **Randomizacija:** `rand` crate  
- **Vizualizacija:**  
  - Terminal (ASCII) **ili**
  - `pixels` / `macroquad` / `bevy`  
- **Build sistem:** Cargo  

---

## Funkcionalnosti sistema

- Inicijalizacija šumske mreže sa definisanom gustinom stabala  
- Pokretanje i pauziranje simulacije  
- Prikaz simulacije u realnom vremenu  
- Podešavanje verovatnoće:
  - spontanog paljenja  
  - rasta novih stabala  
- Reset simulacije  
- Praćenje broja:
  - stabala  
  - zapaljenih ćelija  
  - praznih polja  

---

## Način rada simulacije

1. Sistem inicijalizuje mrežu zadate veličine  
2. Za svaki vremenski korak:
   - računa se sledeće stanje svake ćelije  
   - primenjuju se pravila celularnog automata  
3. Novo stanje se renderuje  
4. Proces se ponavlja dok korisnik ne zaustavi simulaciju  

---

## Cilj projekta

Cilj projekta je demonstracija praktične primene **celularnih automata** i diskretnih simulacija u programskom jeziku **Rust**, kao i razumevanje kako jednostavna lokalna pravila mogu proizvesti kompleksno globalno ponašanje sistema.

# Používateľská dokumentácia

## O programe

Tento program načíta cestovný poriadok (jízdní řády) z databázy PID (Pražská integrovaná doprava) a určí 5 najfrekventovanejších medzizastávkových úsekov v zadaný deň. Program umožňuje stiahnuť si najnovšie dostupné dáta v prípade, že ich používateľ potrebuje.

## Použitie

Na funkčný priebeh programu je potrebné mať v jednom adresári skripty `ukol2_gtfs.py` a `datagetter.py`. V prípade, že ma používateľ vlastné dáta z databázy PID, musí ich vložiť k nutným skriptom do zložky `gtfs/`. V jednom adresári tak budú `ukol2_gtfs.py`, `datagetter.py` a priečinok `gtfs/`, v ktorom budú uložené jednotlivé `.txt` súbory z databázy. Povinné `.txt` súbory, ktoré v tomto adresári byť musia, sú nasledujúce:
- `stops.txt`,
- `stop_times.txt`,
- `trips.txt`,
- `routes.txt`,
- `calendar.txt`.

Ak používateľ vlastné dáta nemá, program mu umožní stiahnuť si najnovšie dostupné dáta. Po spustení programu používateľ zadá `Y` ako súhlas alebo `N` ako nesúhlas na stiahnutie nových dát; akákoľvek iná odpoveď nie je platná a program sa ukončí. `Y` a `N` je možné zadať aj ako `y` a `n`.

Program následne načíta a spracuje dostupné dáta. Používateľa sa opýta na dátum, pre ktorý chce najfrekventovanejšie úseky určiť: žiadaný dátum je nutné zadať vo formáte `dd.mm.yyyy`, teda deň, mesiac a rok oddelené bodkou. Iný formát nebude akceptovaný a program sa v tom prípade ukončí.

Do terminálu sa následne vypíše 5 najfrekventovanejších medzizastávkových úsekov zoradených zostupne, pričom je dodaný aj celkový počet spojov a vymenované linky, ktoré daným úsekom prechádzajú.
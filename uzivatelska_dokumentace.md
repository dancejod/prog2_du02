# Pouzivatelska dokumentacia

## O programe

Tento program nacita cestovny poriadok (jizdni rady) z databazy PID a urci 5 najfrekventovanejsich medzizastavkovych usekov v zadany den. Program umoznuje stiahnut si najnovsie pristupne data v pripade, ak ich pouzivatel potrebuje.

## Pouzitie

Na funkcny priebeh programu je nutne mat v jednom adresari skripty `ukol2_gtfs.py` a `datagetter.py`. V pripade, ze ma pouzivatel vlastne data z databazy PID, musi ich vlozit k nutnym skriptom do zlozky `gtfs/`. V jednom adresari tak budu `ukol2_gtfs.py`, `datagetter.py` a priecinok `gtfs/`, v ktorom budu ulozene jednotlive `.txt` subory z databazy. Povinne `.txt` subory, ktore v tomto adresari byt musia, su nasledovne:
- `stops.txt`,
- `stop_times.txt`,
- `trips.txt`,
- `routes.txt` a
- `calendar.txt`.

Ak pouzivatel vlastne data nema, program mu umozni stiahnut si najnovsie dostupne data. Po spusteni programu pouzivatel zada `Y` ako suhlas alebo `N` ako nesuhlas na stiahnutie novych dat; akakolvek ina odpoved nie je platna a program sa ukonci. `Y` a `N` je mozne zadat aj ako `y` a `n`.

Program nasledne nacita a spracuje dostupne data. Pouzivatela sa opyta na datum, pre ktory chce najfrekventovanejsie useky urcit: ziadany datum je nutne zadat vo formate `dd.mm.yyyy`, teda den, mesiac a rok oddelene bodkou. Iny format nebude akceptovany a program sa v tom pripade ukonci.

Do terminalu sa nasledne vypise 5 najfrekventovanejsich medzizastavkovych usekov zoradenych zostupne, pricom je dodany aj celkovy pocet spojov a vymenovane linky, ktore danym usekom prechadzaju.
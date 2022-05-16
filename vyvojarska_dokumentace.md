# Vývojářská dokumentace

Program využívá 2 skripty: `ukol2_gtfs.py` a `datagetter.py`. 

Skript `datagetter.py` slouží na stažení nejnovějších dostupných dat, pokud je uživatel vyžaduje. Nachází se v něm funkce, která je zavoláná v hlavním skriptu.

Na začátku hlavního skriptu `ukol2_gtfs.py` jsou implementované globální metody, které konvertují string na objekt třídy `date` za využití knihovny `datetime`:
- `convert_user_date(date_user)` - konvertuje datum v parametru `date_user` zadané ve formátu `dd.mm.yyyy`,
- `convert_int_date(date_int)` - konvertuje datum v parametru `date_int` z existujícího souboru ve formátu `YYYYMMDD`.

Dále je zde implementována metoda `daterange(start,end)`, která bere na vstupu 2 objekty třídy `date` a vrací set objektů této třídy dat v intervalu mezi vstupními daty. Ty jsou použity při určování aktivity spojů.

Program pracuje s 5 vstupními soubory, které jsou uloženy v složce `gtfs/`. Jde o textové soubory `stops.txt`, `trips.txt`, `stop_times.txt`, `routes.txt` a `calendar.txt`. Program otevře přísušný .txt soubor z GTFS databáze a uloží data příslušným způsobem. Aby se s daty lépe pracovalo, byly vytvořeny násedující třídy objektů:
- `Stop`
- `Route`
- `Service`
- `Trip`
- `StopTime`
- `StopSegment`

## Třída Stop
Pracuje z daty načtenými ze souboru `stops.txt`. Jde o zastávky z jízdních řádů.

### Atributy:
- `id` (string) - ID zastávky.
- `name` (string) - Název zastávky.

## Třída Route
Pracuje s daty načtenými ze souboru `routes.txt`. Nachází se v něm linky z jízdních řádů.

### Atributy:
- `id` (string) - ID linky.
- `name` (string) - Název linky.

## Třída Service
Pracuje s daty načtenými ze souboru `calendar.txt`. V datech jsou služby odpovědné za funkčnost spojů v určené dny.

### Atributy:
- `id` (string) - ID služby, která sprovozňuje spoje.
- `service_days` (set) - obsahuje objekty třídy date odpovídající datům, kdy daná služba funguje

Pro získání service_days je implementována třídní metoda `get_service(cls, service_row)`, která má na vstupu parametr `service_row`, což je řádek z csv.DictReaderu. Metoda za použití globální funkce `convert_int_date(date_int)` konvertuje datum prvního a posledního dne fungujícího servicu z původního souboru na objekty třídy `date`. Potom je pomocí metody `daterange(start,end)` získán set dní z intervalu dat, která jsou pro každý service dána ve vstupním souboru. Dále z původních dat uloží do seznamu informaci o tom, zda service funguje daný den v týdnu, seznam je oindexovaný 0–6 což odpovídá dnům pondělí–neděle. Výstupem je objekt třídy `Service`, který obsahuje informaci o dnech, ve kterých daná služba odpovědná za spoj funguje.

## Třída Trip
Pracuje s daty načtenými ze souboru `trips.txt`. V datech se nachází spoje z jízdních řádů. Třídě jsou posunuty objekty tříd `Route` a `Service`.

### Atributy
- `trip_id` (str) - ID spoje.
- `route` (object) - Objekt třídy `Route`. Zachovává informaci o lince, ke které spoj patří.
- `service` (object) - Objekt třídy `Service`. Zachovává informaci o funkčnosti spoje počas týdne.

## Třída StopTime
Pracuje s daty načtenými ze souboru `stop_times.txt`. V datech se nachází informace o zastávkách a jejich pořadí v daném spoji. Třídě jsou posunuty objekty tříd `Trip` a `Stop`.

### Atributy
- `trip` (object) - Objekt třídy `Trip`. Zachovává informaci o uvažovaném spoji.
- `stop` (object) - Objekt třídy `Stop`. Zachovává informaci o zastávkách, kterými spoj prochází.
- `stop_sequence` (string) - Číslem vyjádřené pořadí zastávky v spoji.

## Třída StopSegment
Pracuje s objekty tříd `Trip`, `Stop` a `Route`. Jsou v něj implementovány metody, které společně vyhodnotí nejfrekventovanější úseky.

### Atributy
- `from_stop` (object) - Objekt třídy `Stop`. Představuje výchozí zastávku.
- `to_stop` (object) - Objekt třídy `Stop`. Představuje zastávku, která nasleduje hned po zastávce `from_stop` v rámci jedného spoje.
- `trips` (object) - Objekt třídy `Trip`. Zachovává informaci o spoji a funkčnosti spoje během týdnu.
- `routes` (object) - Objekt třídy `Rouute`. Zachovává informaci o lince, ke které spoj patří.

V implementované class metodě `get_segment_dict(cls, data_stop_times,date_string)` se vytvoří během cyklu objekty `StopSegment`, z kterých již lze extrahovat informaci o nejfrekventovanejších úsecích. Cyklus projde všechny objekty třídy `StopTimes` v předaném seznamu `data_stop_times` a vytváří pomocí nich dvojice zastávek, které za sebou bezprostředně nasledují a představují jeden mezizastávkový úsek. 


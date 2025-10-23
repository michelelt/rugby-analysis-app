Rugby Analysis App

Questa applicazione desktop è uno strumento per annotare e rivedere eventi di partite di rugby. È sviluppata in Python usando PyQt6 per l'interfaccia grafica e fornisce due modalità di riproduzione video per i link YouTube: un embed iframe e una riproduzione diretta tramite yt-dlp + QMediaPlayer.

Questo README spiega come installare, avviare e utilizzare l'applicazione, insieme a una panoramica delle funzionalità e consigli di risoluzione problemi.

## Requisiti

- macOS / Linux / Windows con Python 3.11 (o compatibile)
- dipendenze elencate in `app/requirements.txt` (PyQt6, yt-dlp, ecc.)
- accesso internet per la riproduzione di video YouTube quando si usa la modalità stream/embed

Nota: la modalità stream utilizza `yt-dlp` per estrarre URL di streaming diretti; alcune piattaforme o versioni di Qt possono richiedere codec aggiuntivi o configurazioni multimediali.

## Installazione

Apri un terminale nella cartella del progetto e crea un virtualenv (opzionale ma consigliato):

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r app/requirements.txt
```

## Avvio

Esegui l'applicazione:

```bash
python app/app.py
```

All'avvio l'app può chiederti di inserire un link YouTube: puoi incollare un URL (es. `https://www.youtube.com/watch?v=...` o `https://youtu.be/...`) oppure lasciare il valore di default per usare un video dimostrativo.

## Panoramica delle funzionalità

- Interfaccia principale con due aree affiancate:
  - Sinistra: form per inserire eventi (data, squadre, minuto, tipo evento, commento, Video URL, ecc.)
  - Destra: tabella degli eventi (filtrata per i campi fissi della sessione) e un riquadro video ridimensionabile
- Due modalità video selezionabili in alto a destra:
  - Embed (YouTube iframe): ottimo per compattezza e semplicità
  - Stream (Direct link): usa `yt-dlp` per ottenere un flusso diretto e riprodurlo con `QMediaPlayer`
- Click su una riga della tabella: carica il video associato all'evento e riproduce a partire dal minuto indicato
- Pulsante "Add Video": precompila il dialog con l'URL attualmente caricato nel player e permette di assegnarlo al campo del form
- Salvataggio eventi: il tasto "Salva Evento" inserisce un nuovo evento (o aggiorna se si sta modificando)
- Match: puoi salvare una sessione come Match (Save Match), che raggruppa eventi con gli stessi campi fissi (data, squadra home/away, minuto kickoff). Usa "Change Match" per aprire o creare un match esistente.

## Struttura del progetto (sintesi)

- `app/` — codice applicazione
  - `app.py` — entrypoint dell'app
  - `ui/` — componenti UI (main_window, player, selector)
  - `core/` — DB, servizi e utilità
  - `controllers/` — piccoli wrapper tra UI e servizi
- `tests/` — test automatici (parser, smoke test placeholder)

## Note tecniche importanti

- Il database è SQLite e viene creato nella root del progetto come `analisi_rugby.db` (vedi `app/core/database.py`).
- La colonna `video_url` è persistita nella tabella `eventi`. Se hai vecchi database, l'avvio esegue una migrazione leggera che aggiunge `video_url` e `match_id` se mancanti.
- Il comportamento di seek nella modalità embed richiede che il player abbia già caricato un URL base; l'app ora carica esplicitamente l'URL dell'evento prima di chiedere il seek quando necessario.

## Risoluzione problemi

- "Nessun video caricato per il seek" (o messaggi simili): significa che l'iframe embed o il player stream non aveva ancora un URL caricato; prova a cliccare la riga dell'evento una seconda volta o usa il pulsante "Add Video" per assegnare il link all'evento. L'ultima versione dell'app dovrebbe caricare automaticamente l'URL dell'evento quando clicchi la riga.
- Errori relativi a `yt-dlp` o a codec multimediali nella modalità stream: assicurati che `yt-dlp` sia installato e aggiornato e che il sistema abbia i codec necessari (su macOS spesso il supporto multimediale Qt è sufficiente; in altri casi potrebbe essere necessario installare ffmpeg o plugin aggiuntivi).
- Problemi di permessi o file DB: se vuoi ripartire da zero, chiudi l'app e rimuovi `analisi_rugby.db` (attenzione: perderai i dati). L'app lo ricreerà al prossimo avvio.

## Testing

I test sono presenti in `tests/` per verificare funzioni di utilità come il parser del campo minuto. In ambiente di sviluppo con GUI disponibile, puoi eseguire i test con:

```bash
pytest -q
```

Nota: gli smoke test per i player richiedono un ambiente grafico e potrebbero essere saltati in CI headless.

## Prossimi miglioramenti possibili

- Migliorare l'editor dei match (interfaccia dedicata)
- Migliorare i messaggi di feedback utente e i log delle migrazioni DB
- Aggiungere esportazione CSV/Excel per le analisi offline


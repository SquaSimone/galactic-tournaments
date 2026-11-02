-- Stagioni generate dall'app (sezione "Genera stagione").
-- Tiene traccia di quale template di sorteggio è stato usato per ogni stagione,
-- così da non ripetere lo stesso template nelle ultime 5 stagioni.
-- NB: l'app crea comunque questa tabella a runtime (CREATE TABLE IF NOT EXISTS),
-- così funziona anche su volumi DB già inizializzati senza ri-eseguire le migrazioni.

CREATE TABLE IF NOT EXISTS stagioni_generate (
    stagione     INTEGER PRIMARY KEY,
    template_idx INTEGER NOT NULL
);

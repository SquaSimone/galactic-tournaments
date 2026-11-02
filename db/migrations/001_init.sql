-- Tabella partite: una riga per ogni partita estratta dal file Excel.
-- Le classifiche e i ranking vengono ricalcolati al volo dalle partite,
-- quindi non vengono persistiti qui.

CREATE TABLE IF NOT EXISTS partite (
    id              SERIAL PRIMARY KEY,
    stagione        INTEGER NOT NULL,
    giornata        TEXT NOT NULL,
    squadra_casa    TEXT NOT NULL,
    risultato       TEXT NOT NULL,
    squadra_trasferta TEXT NOT NULL,
    tipo            TEXT,
    ordine          INTEGER DEFAULT 0,
    "Competizione"  TEXT,
    campo           TEXT
);

CREATE INDEX IF NOT EXISTS idx_partite_stagione
    ON partite (stagione);

CREATE INDEX IF NOT EXISTS idx_partite_competizione
    ON partite ("Competizione");

CREATE INDEX IF NOT EXISTS idx_partite_squadre
    ON partite (squadra_casa, squadra_trasferta);

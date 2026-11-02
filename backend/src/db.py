"""
Connessione PostgreSQL e helper per salvataggio/lettura partite.
"""
import os
from sqlalchemy import create_engine, text, bindparam
from sqlalchemy.engine import Engine
import pandas as pd

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://galactic:changeme_in_production@localhost:5435/galactic_tournaments",
)

_engine: Engine | None = None


def get_engine() -> Engine:
    """Lazy-init e riusa una singola Engine."""
    global _engine
    if _engine is None:
        _engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    return _engine


def salva_partite(df_partite: pd.DataFrame, stagione: int) -> int:
    """
    Salva il DataFrame partite nella tabella `partite` aggiungendo la colonna
    stagione. Se esistono già righe per quella stagione, vengono prima
    eliminate (idempotente per ri-importazione).

    Restituisce il numero di righe inserite.
    """
    if df_partite.empty:
        return 0

    df = df_partite.copy()
    df["stagione"] = stagione

    # giornata può essere Categorical → converto a stringa per il DB
    if "giornata" in df.columns:
        df["giornata"] = df["giornata"].astype(str)

    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM partite WHERE stagione = :s"), {"s": stagione})
        df.to_sql("partite", conn, if_exists="append", index=False)
    return len(df)


def leggi_partite(stagione: int | None = None) -> pd.DataFrame:
    """Carica le partite dal DB. Se `stagione` è None, ritorna tutte.

    Applica l'ordine canonico delle giornate (GIORNATE_ORDER) così che
    Andata e Ritorno di ogni round siano consecutivi (anziché tutte le
    Andate seguite da tutti i Ritorni).
    """
    from src.estrattore import GIORNATE_ORDER
    engine = get_engine()
    if stagione is None:
        df = pd.read_sql("SELECT * FROM partite", engine)
    else:
        df = pd.read_sql(
            "SELECT * FROM partite WHERE stagione = %(s)s",
            engine,
            params={"s": stagione},
        )

    if not df.empty and "giornata" in df.columns:
        df["giornata"] = pd.Categorical(
            df["giornata"], categories=GIORNATE_ORDER, ordered=True
        )
        df = df.sort_values(
            ["stagione", "giornata", "ordine"], na_position="last"
        ).reset_index(drop=True)
        # Riconverto in stringa per la serializzazione JSON downstream
        df["giornata"] = df["giornata"].astype(str)

    return df


def stagioni_presenti() -> list[int]:
    """Elenco delle stagioni già caricate nel DB."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT DISTINCT stagione FROM partite ORDER BY stagione"))
        return [row[0] for row in result]


def sostituisci_partite_competizione(
    righe: list[dict], stagione: int, competizione: str, giornate: list[str]
) -> int:
    """Inserisce le righe-partita generate per una stagione, rimuovendo prima
    SOLO quelle della stessa competizione e nelle `giornate` indicate
    (idempotente per ri-generazione). Non tocca le altre competizioni né le
    altre fasi della stessa competizione.

    Restituisce il numero di righe inserite.
    """
    if not righe:
        return 0

    df = pd.DataFrame(righe)
    df["stagione"] = stagione

    del_stmt = text(
        'DELETE FROM partite '
        'WHERE stagione = :s AND "Competizione" = :c AND giornata IN :g'
    ).bindparams(bindparam("g", expanding=True))

    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(del_stmt, {"s": stagione, "c": competizione, "g": giornate})
        df.to_sql("partite", conn, if_exists="append", index=False)
    return len(df)


def aggiorna_risultato(partita_id: int, risultato: str) -> bool:
    """Aggiorna il risultato di una singola partita. True se ha modificato una riga."""
    engine = get_engine()
    with engine.begin() as conn:
        res = conn.execute(
            text("UPDATE partite SET risultato = :r WHERE id = :id"),
            {"r": risultato, "id": partita_id},
        )
    return res.rowcount > 0


def info_partite(ids: list[int]) -> list[dict]:
    """Per ogni id, ritorna stagione/Competizione/giornata (righe non trovate
    vengono semplicemente omesse)."""
    if not ids:
        return []
    engine = get_engine()
    stmt = text(
        'SELECT id, stagione, "Competizione", giornata FROM partite WHERE id IN :ids'
    ).bindparams(bindparam("ids", expanding=True))
    with engine.connect() as conn:
        rows = conn.execute(stmt, {"ids": ids}).mappings().all()
    return [dict(r) for r in rows]


def elimina_partite_competizione(stagione: int, competizione: str) -> int:
    """Elimina tutte le partite di una competizione per una stagione
    (usato per invalidare SuperCup/Cup of 10 quando cambia un risultato
    a monte). Ritorna il numero di righe eliminate."""
    engine = get_engine()
    with engine.begin() as conn:
        res = conn.execute(
            text('DELETE FROM partite WHERE stagione = :s AND "Competizione" = :c'),
            {"s": stagione, "c": competizione},
        )
    return res.rowcount


def partite_giornata(stagione: int, competizione: str, giornata: str) -> list[dict]:
    """Tutte le partite di una giornata/competizione/stagione (per ordine)."""
    engine = get_engine()
    stmt = text(
        'SELECT id, ordine, squadra_casa, squadra_trasferta, risultato, campo '
        'FROM partite '
        'WHERE stagione = :s AND "Competizione" = :c AND giornata = :g'
    )
    with engine.connect() as conn:
        rows = conn.execute(stmt, {"s": stagione, "c": competizione, "g": giornata}).mappings().all()
    return [dict(r) for r in rows]


def sostituisci_squadra_partita(partita_id: int, vecchia: str, nuova: str) -> bool:
    """In una partita, sostituisce `vecchia` con `nuova` (in squadra_casa o
    squadra_trasferta, qualunque sia) e azzera il risultato. Aggiorna anche
    `campo` se coincideva col nome della vecchia squadra (partite non neutre).
    True se ha modificato una riga."""
    engine = get_engine()
    with engine.begin() as conn:
        res = conn.execute(
            text(
                "UPDATE partite SET "
                "  squadra_casa = CASE WHEN squadra_casa = :vecchia THEN :nuova ELSE squadra_casa END, "
                "  squadra_trasferta = CASE WHEN squadra_trasferta = :vecchia THEN :nuova ELSE squadra_trasferta END, "
                "  campo = CASE WHEN campo = :vecchia THEN :nuova ELSE campo END, "
                "  risultato = '' "
                "WHERE id = :id"
            ),
            {"vecchia": vecchia, "nuova": nuova, "id": partita_id},
        )
    return res.rowcount > 0


# ── Persistenza dei template di sorteggio usati per stagione ────────────────
# Crea la tabella a runtime (CREATE TABLE IF NOT EXISTS), così funziona anche su
# volumi DB già inizializzati senza ri-eseguire le migrazioni.

def _ensure_generazione_table(conn) -> None:
    conn.execute(text(
        "CREATE TABLE IF NOT EXISTS stagioni_generate ("
        "  stagione     INTEGER PRIMARY KEY,"
        "  template_idx INTEGER NOT NULL"
        ")"
    ))


def template_recenti(limit: int = 5) -> list[int]:
    """Indici dei template usati nelle ultime `limit` stagioni generate,
    ordinati dalla più vecchia alla più recente."""
    engine = get_engine()
    with engine.begin() as conn:
        _ensure_generazione_table(conn)
        rows = conn.execute(
            text(
                "SELECT template_idx FROM stagioni_generate "
                "ORDER BY stagione DESC LIMIT :n"
            ),
            {"n": limit},
        ).fetchall()
    return [r[0] for r in reversed(rows)]


def registra_template(stagione: int, template_idx: int) -> None:
    """Memorizza (o aggiorna) quale template è stato usato per una stagione."""
    engine = get_engine()
    with engine.begin() as conn:
        _ensure_generazione_table(conn)
        conn.execute(
            text(
                "INSERT INTO stagioni_generate (stagione, template_idx) "
                "VALUES (:s, :t) "
                "ON CONFLICT (stagione) DO UPDATE SET template_idx = EXCLUDED.template_idx"
            ),
            {"s": stagione, "t": template_idx},
        )

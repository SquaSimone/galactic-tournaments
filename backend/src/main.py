"""
FastAPI entry point.
"""
import math
import random
import re
import tempfile
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src import estrattore, sorteggio
from src.db import (
    leggi_partite,
    salva_partite,
    stagioni_presenti,
    sostituisci_partite_competizione,
    aggiorna_risultato,
    info_partite,
    elimina_partite_competizione,
    partite_giornata,
    sostituisci_squadra_partita,
    template_recenti,
    registra_template,
)


# Mappa Competizione → giornata che identifica la finale (per determinare
# la vincitrice della competizione di una stagione).
COMPETIZIONE_FINALI = {
    "galactic league":          "Finale League",
    "galactic cup":             "Finale Cup",
    "Kings League":             "Final Four - Finale",
    "galactic champions cup":   "Fase 3 - Finale",
    "intergalactic supercup":   "Finale SuperCup",
    "cup of 8":                 "Finale Cup of 8",
    "cup of 10":                "Finale Cup of 10",
}

# ── Cascata di invalidazione: SuperCup e Cup of 10 dipendono dai risultati
# delle 4 coppe principali (per stabilire chi vi partecipa/qualifica) e dal
# risultato della SuperCup stessa (per la Cup of 10). Se l'utente corregge un
# risultato "decisivo" (cioè una partita di una fase a eliminazione diretta,
# non una semplice partita di girone/fase a punti), le competizioni che ne
# dipendono non sono più coerenti con i dati e vanno azzerate, per essere
# rigenerate manualmente dall'utente.
#
# Giornate "decisive" = quelle che determinano un passaggio del turno (knock-out).
# Le giornate di sola fase a gironi/punti (Giornate 1-8 League, gironi Kings
# League, Fase 1/2 Champions Cup) NON sono incluse: contribuiscono a una
# classifica cumulata ma nessuna singola partita "decide" un passaggio diretto.
GIORNATE_DECISIVE_PRINCIPALI = {
    "galactic league": {
        "Play Off - Andata", "Play Off - Ritorno",
        "Ottavi League - Andata", "Ottavi League - Ritorno",
        "Quarti League - Andata", "Quarti League - Ritorno",
        "Semifinale League - Andata", "Semifinale League - Ritorno",
        "Finale League",
    },
    "galactic cup": {
        "Turno 1", "Turno 2", "Ottavi di Finale",
        "Quarti di Finale - Andata", "Quarti di Finale - Ritorno",
        "Semifinale - Andata", "Semifinale - Ritorno",
        "Finale Cup",
    },
    "Kings League": {
        "Playoff Lega B - Semifinali", "Playoff Lega B - Finale",
        "Playout Lega A - Finali", "Playout Lega B - Finali",
        "Playoff/Playout B-C - Turno 1", "Playoff/Playout B-C - Turno 2",
        "Playoff/Playout A-B - Turno 1", "Playoff/Playout A-B - Turno 2",
        "Final Four - Semifinali", "Final Four - Finale",
    },
    "galactic champions cup": {
        "Fase 3 - Ottavi di Finale", "Fase 3 - Quarti di Finale",
        "Fase 3 - Semifinale", "Fase 3 - Finale",
    },
}

# La SuperCup è interamente "decisiva" (sempre knockout): qualunque modifica
# a un suo risultato invalida la Cup of 10 (che dipende dal ranking
# qualificazione, costruito anche sull'esito della SuperCup).
COMPETIZIONI_CASCATA = set(GIORNATE_DECISIVE_PRINCIPALI.keys())


# ── Propagazione automatica del vincitore nei bracket a tabellone fisso ─────
# Per i turni in cui l'abbinamento del turno SUCCESSIVO è una funzione fissa
# e nota dell'`ordine` (non dipende da un sorteggio casuale non recuperabile),
# se cambia il vincitore di una sfida del turno N, sostituiamo la vecchia
# squadra con la nuova nel turno N+1 (stesso slot), azzerando il punteggio di
# quella sfida lì - e ripetiamo a cascata nei turni successivi.
#
# Ogni voce: (giornata_o_coppia, tipo) dove tipo è "single" (gara secca) o
# "legs" (andata/ritorno, sfida indicizzata per `ordine`). La funzione che
# combina l'ordine del turno N nel turno N+1 è SEMPRE k -> k // 2 per le
# voci elencate qui (i casi con sorteggio/abbinamento variabile - es. Playoff
# League, Turno 1/2 Cup, gironi e playoff/playout Kings League - sono
# volutamente esclusi: non c'è un seed salvato da cui ricostruire
# l'abbinamento, quindi l'utente li gestisce a mano).
BRACKET_CASCATA = {
    "galactic league": [
        (("Ottavi League - Andata", "Ottavi League - Ritorno"), "legs"),
        (("Quarti League - Andata", "Quarti League - Ritorno"), "legs"),
        (("Semifinale League - Andata", "Semifinale League - Ritorno"), "legs"),
        ("Finale League", "single"),
    ],
    "galactic cup": [
        ("Ottavi di Finale", "single"),
        (("Quarti di Finale - Andata", "Quarti di Finale - Ritorno"), "legs"),
        (("Semifinale - Andata", "Semifinale - Ritorno"), "legs"),
        ("Finale Cup", "single"),
    ],
    "galactic champions cup": [
        ("Fase 3 - Ottavi di Finale", "single"),
        ("Fase 3 - Quarti di Finale", "single"),
        ("Fase 3 - Semifinale", "single"),
        ("Fase 3 - Finale", "single"),
    ],
    "Kings League": [
        ("Final Four - Semifinali", "single"),
        ("Final Four - Finale", "single"),
    ],
    "intergalactic supercup": [
        ("Semifinale SuperCup", "single"),
        ("Finale SuperCup", "single"),
    ],
}


def _winner_of_match(row) -> Optional[str]:
    """Vincitore di un singolo match (gestisce rigori)."""
    ris = str(row["risultato"]).strip()
    m = re.match(r"^(\d+)-(\d+)", ris)
    if not m:
        return None
    gc, gt = int(m.group(1)), int(m.group(2))
    if "(" in ris:
        mp = re.search(r"\((\d+)-(\d+)\)", ris)
        if mp:
            a, b = int(mp.group(1)), int(mp.group(2))
            return row["squadra_casa"] if a > b else row["squadra_trasferta"]
    if gc > gt:
        return row["squadra_casa"]
    if gc < gt:
        return row["squadra_trasferta"]
    return None

app = FastAPI(title="Galactic Tournaments API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/stagioni")
def get_stagioni():
    """Stagioni già caricate nel DB."""
    return {"stagioni": stagioni_presenti()}


def _stagione_da_filename(filename: str) -> int | None:
    """Estrae il numero stagione da 'Stagione X.xlsm' o simili."""
    m = re.search(r"stagione\s*(\d+)", filename, re.IGNORECASE)
    return int(m.group(1)) if m else None


@app.post("/api/upload")
async def upload(
    file: UploadFile = File(...),
    stagione: int | None = Form(None),
):
    """
    Riceve un file Excel di stagione, lo processa con estrai_partite_giornate,
    salva su DB con la colonna stagione e ritorna un riepilogo.

    Se `stagione` non viene passata, la deduce dal nome file.
    """
    if not file.filename:
        raise HTTPException(400, "File senza nome")

    # Stagione: usa quella passata, altrimenti deduci dal nome file
    if stagione is None:
        stagione = _stagione_da_filename(file.filename)
    if stagione is None:
        raise HTTPException(
            400,
            "Stagione non specificata e non deducibile dal nome file "
            "(atteso 'Stagione X.xlsm')",
        )

    # Salva il file su disco temporaneo (pandas/openpyxl richiedono un path)
    suffix = Path(file.filename).suffix or ".xlsm"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        df_partite = estrattore.estrai_partite_giornate(tmp_path)
    except Exception as e:
        raise HTTPException(500, f"Errore durante l'estrazione: {e}")
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    if df_partite is None or len(df_partite) == 0:
        raise HTTPException(500, "Nessuna partita estratta dal file")

    # Riepilogo per Competizione (prima del salvataggio)
    riepilogo = (
        df_partite.groupby("Competizione", observed=True)
        .size()
        .to_dict()
    )

    # Salva su DB
    inserite = salva_partite(df_partite, stagione)

    return {
        "stagione": stagione,
        "filename": file.filename,
        "partite_totali": int(inserite),
        "partite_per_competizione": {k: int(v) for k, v in riepilogo.items()},
    }


# ── Generazione stagione (sorteggio) ────────────────────────────────────────
LEAGUE_GIORNATE = [f"Giornata {i}" for i in range(1, 9)]


class GeneraLeagueRequest(BaseModel):
    stagione: Optional[int] = None
    seed: Optional[int] = None  # opzionale, per generazioni riproducibili (test)


@app.post("/api/genera/league-phase")
def genera_league_phase(req: GeneraLeagueRequest):
    """
    Genera (sorteggia) la fase a gironi della Galactic League di una stagione:
    4 fasce da 9 dal ranking cumulato della stagione PRECEDENTE, un template tra
    i 40 (evitando quelli delle ultime 5 stagioni), posizioni rimescolate a caso.
    Scrive le 144 partite con risultato vuoto. Idempotente: rigenerando si
    sostituiscono solo le Giornate 1-8 della Galactic League.
    """
    presenti = stagioni_presenti()
    stagione = req.stagione if req.stagione is not None else (
        max(presenti) + 1 if presenti else 1
    )
    if stagione < 2:
        raise HTTPException(
            400,
            "La generazione richiede il ranking cumulato della stagione precedente "
            "(disponibile dalla stagione 2 in poi).",
        )

    cum = get_ranking_cumulato(stagione - 1)
    squadre = [r["SQUADRA"] for r in cum.get("ranking", [])]
    if len(squadre) != sorteggio.NUM_SQUADRE:
        raise HTTPException(
            409,
            f"Il ranking cumulato della stagione {stagione - 1} ha {len(squadre)} "
            f"squadre, ne servono {sorteggio.NUM_SQUADRE}. Importa/controlla le "
            f"stagioni precedenti.",
        )

    rng = random.Random(req.seed)  # seed None → casuale di sistema
    recenti = template_recenti(sorteggio.RECENT_WINDOW)
    template_idx = sorteggio.scegli_template(recenti, rng)
    fasce = sorteggio.build_fasce(squadre)
    righe = sorteggio.calendario_da_template(fasce, template_idx, rng)

    inserite = sostituisci_partite_competizione(
        righe, stagione, "galactic league", LEAGUE_GIORNATE
    )
    registra_template(stagione, template_idx)

    return {
        "stagione": stagione,
        "template": template_idx,
        "partite_inserite": inserite,
        "fasce": fasce,
    }


class RisultatoUpdate(BaseModel):
    id: int
    risultato: str


class RisultatiBatch(BaseModel):
    risultati: list[RisultatoUpdate]


def _step_index_giornata(competizione: str, giornata: str) -> Optional[int]:
    """Indice del turno (in BRACKET_CASCATA[competizione]) a cui appartiene
    `giornata`, oppure None se la competizione/giornata non è nella mappa."""
    steps = BRACKET_CASCATA.get(competizione)
    if not steps:
        return None
    for i, (g, _) in enumerate(steps):
        giornate_step = (g,) if isinstance(g, str) else g
        if giornata in giornate_step:
            return i
    return None


def _vincitori_step(stagione: int, competizione: str, step_idx: int) -> dict[int, Optional[str]]:
    """Vincitore per `ordine` del turno indicato (gestisce sia gara secca sia
    andata/ritorno)."""
    giornata, tipo = BRACKET_CASCATA[competizione][step_idx]
    if tipo == "single":
        out = {}
        for row in partite_giornata(stagione, competizione, giornata):
            out[int(row["ordine"])] = _winner_of_match(row)
        return out
    # legs: aggrego andata/ritorno per ordine
    g_and, g_rit = giornata
    andate = {int(r["ordine"]): r for r in partite_giornata(stagione, competizione, g_and)}
    ritorni = {int(r["ordine"]): r for r in partite_giornata(stagione, competizione, g_rit)}
    out = {}
    for k, a in andate.items():
        r = ritorni.get(k)
        out[k] = _aggregato_vincitore(a, r) if r else None
    return out


def _squadre_step(stagione: int, competizione: str, step_idx: int) -> dict[int, dict]:
    """Per ogni `ordine` del turno, le righe-partita coinvolte (1 per 'single',
    2 - andata/ritorno - per 'legs'), indicizzate per ordine."""
    giornata, tipo = BRACKET_CASCATA[competizione][step_idx]
    if tipo == "single":
        out = {}
        for row in partite_giornata(stagione, competizione, giornata):
            out[int(row["ordine"])] = {"single": row}
        return out
    g_and, g_rit = giornata
    out: dict[int, dict] = {}
    for row in partite_giornata(stagione, competizione, g_and):
        out.setdefault(int(row["ordine"]), {})["andata"] = row
    for row in partite_giornata(stagione, competizione, g_rit):
        out.setdefault(int(row["ordine"]), {})["ritorno"] = row
    return out


def _propaga_bracket(stagione: int, competizione: str, giornata_modificata: str) -> list[str]:
    """Se `giornata_modificata` appartiene a un turno con propagazione
    automatica nota (vedi BRACKET_CASCATA), confronta il vincitore di ogni
    sfida del turno con la squadra attualmente presente nello slot
    corrispondente del turno successivo: se sono diversi, sostituisce (e
    azzera SOLO il punteggio della/e partita/e coinvolta/e nel turno
    successivo). Ripete a cascata sui turni seguenti.

    Ritorna la lista delle giornate effettivamente toccate dalla
    propagazione (utile per includerle nella valutazione della cascata di
    invalidazione SuperCup/Cup of 10).
    """
    step_idx = _step_index_giornata(competizione, giornata_modificata)
    if step_idx is None:
        return []

    steps = BRACKET_CASCATA[competizione]
    toccate: list[str] = []

    while step_idx + 1 < len(steps):
        vincitori = _vincitori_step(stagione, competizione, step_idx)
        next_giornata, next_tipo = steps[step_idx + 1]
        next_squadre = _squadre_step(stagione, competizione, step_idx + 1)

        cambiato_qualcosa = False
        for k, vincitore in vincitori.items():
            if vincitore is None:
                continue  # sfida ancora non decisa: niente da propagare per questo slot
            next_k = k // 2
            slot = next_squadre.get(next_k)
            if not slot:
                continue  # il turno successivo non è ancora stato generato

            if next_tipo == "single":
                row = slot.get("single")
                if row is None:
                    continue
                lato_casa = (k % 2 == 0)  # convenzione: slot pari -> casa, dispari -> trasferta
                attuale = row["squadra_casa"] if lato_casa else row["squadra_trasferta"]
                if attuale and attuale != vincitore:
                    if sostituisci_squadra_partita(row["id"], attuale, vincitore):
                        cambiato_qualcosa = True
                        g = next_giornata if isinstance(next_giornata, str) else next_giornata[0]
                        if g not in toccate:
                            toccate.append(g)
            else:
                # legs: il vincitore del turno precedente entra come "lato k%2"
                # sia in andata sia in ritorno (stessa coppia, ruoli invertiti).
                lato_casa = (k % 2 == 0)
                for leg_key, g_leg in (("andata", next_giornata[0]), ("ritorno", next_giornata[1])):
                    row = slot.get(leg_key)
                    if row is None:
                        continue
                    # In ritorno i ruoli casa/trasferta sono invertiti rispetto all'andata.
                    casa_e_il_lato = lato_casa if leg_key == "andata" else (not lato_casa)
                    attuale = row["squadra_casa"] if casa_e_il_lato else row["squadra_trasferta"]
                    if attuale and attuale != vincitore:
                        if sostituisci_squadra_partita(row["id"], attuale, vincitore):
                            cambiato_qualcosa = True
                            if g_leg not in toccate:
                                toccate.append(g_leg)

        if not cambiato_qualcosa:
            break
        step_idx += 1

    return toccate


@app.put("/api/partite/risultati")
def aggiorna_risultati(batch: RisultatiBatch):
    """Aggiorna in blocco il risultato di una o più partite (per id).

    Se una delle partite modificate appartiene a un turno con tabellone
    fisso (vedi BRACKET_CASCATA), propaga automaticamente il nuovo vincitore
    nei turni successivi della stessa competizione, sostituendo la squadra
    e azzerando il punteggio delle sfide toccate (a cascata).

    Se una delle partite modificate (originale o toccata dalla propagazione)
    è una giornata "decisiva" di una delle 4 coppe principali, oppure una
    partita della SuperCup, le competizioni che ne dipendono (SuperCup/Cup
    di 10, oppure solo Cup of 10) vengono azzerate per quella stagione: i
    dati non sarebbero più coerenti finché non vengono rigenerate
    manualmente.
    """
    ids = [u.id for u in batch.risultati]
    info_prima = {r["id"]: r for r in info_partite(ids)}

    aggiornate = 0
    for u in batch.risultati:
        if aggiorna_risultato(u.id, u.risultato):
            aggiornate += 1

    # Propagazione automatica nei bracket a tabellone fisso.
    giornate_toccate_extra = []  # (stagione, competizione, giornata)
    for u in batch.risultati:
        meta = info_prima.get(u.id)
        if not meta:
            continue
        comp = meta["Competizione"]
        giornata = meta["giornata"]
        stagione = meta["stagione"]
        toccate = _propaga_bracket(stagione, comp, giornata)
        for g in toccate:
            giornate_toccate_extra.append({"Competizione": comp, "giornata": g, "stagione": stagione})

    # Determina, per ogni stagione coinvolta, se serve invalidare a cascata
    # (includendo sia le modifiche originali sia quelle propagate).
    stagioni_da_invalidare_tutto = set()   # → azzera supercup + cup of 10
    stagioni_da_invalidare_cup10 = set()   # → azzera solo cup of 10
    da_valutare = list(info_prima.values()) + giornate_toccate_extra
    for meta in da_valutare:
        comp = meta["Competizione"]
        giornata = meta["giornata"]
        stagione = meta["stagione"]
        if comp in COMPETIZIONI_CASCATA and giornata in GIORNATE_DECISIVE_PRINCIPALI[comp]:
            stagioni_da_invalidare_tutto.add(stagione)
        elif comp == "intergalactic supercup":
            stagioni_da_invalidare_cup10.add(stagione)

    invalidato = []
    for stagione in stagioni_da_invalidare_tutto:
        n1 = elimina_partite_competizione(stagione, "intergalactic supercup")
        n2 = elimina_partite_competizione(stagione, "cup of 10")
        if n1 or n2:
            invalidato.append({
                "stagione": stagione,
                "competizioni_azzerate": ["intergalactic supercup", "cup of 10"],
            })
    # Evita di azzerare due volte la Cup of 10 per stagioni già coperte sopra.
    for stagione in stagioni_da_invalidare_cup10 - stagioni_da_invalidare_tutto:
        n = elimina_partite_competizione(stagione, "cup of 10")
        if n:
            invalidato.append({
                "stagione": stagione,
                "competizioni_azzerate": ["cup of 10"],
            })

    return {"aggiornate": aggiornate, "invalidato": invalidato, "propagato": giornate_toccate_extra}


# ── Export / Import (backup e trasferimento, in JSON) ───────────────────────
EXPORT_TIPO = "galactic-tournaments-export"


class ImportPartiteRequest(BaseModel):
    partite: list[dict]
    tipo: Optional[str] = None
    versione: Optional[int] = None
    stagioni: Optional[list] = None


def _export_payload(df) -> dict:
    if df.empty:
        return {"tipo": EXPORT_TIPO, "versione": 1, "stagioni": [], "partite": []}
    stagioni = sorted({int(s) for s in df["stagione"].unique()})
    df2 = df.drop(columns=["id"], errors="ignore")
    return {"tipo": EXPORT_TIPO, "versione": 1, "stagioni": stagioni, "partite": _df_to_records(df2)}


@app.get("/api/export/stagione/{stagione}")
def export_stagione(stagione: int):
    """Esporta in JSON tutte le partite di una stagione (backup / trasferimento)."""
    df = leggi_partite(stagione)
    if df.empty:
        raise HTTPException(404, f"Nessuna partita per la stagione {stagione}.")
    return _export_payload(df)


@app.get("/api/export/tutto")
def export_tutto():
    """Esporta in JSON tutte le partite di tutte le stagioni (backup completo)."""
    return _export_payload(leggi_partite(None))


@app.post("/api/import/partite")
def import_partite(payload: ImportPartiteRequest):
    """Importa partite da un file JSON esportato. Per ogni stagione presente nel
    file, sostituisce completamente le partite di quella stagione nel DB."""
    partite = payload.partite or []
    if not partite:
        raise HTTPException(400, "Nessuna partita da importare nel file.")
    per_stagione: dict = {}
    for r in partite:
        s = r.get("stagione")
        if s is None:
            continue
        per_stagione.setdefault(int(s), []).append(r)
    if not per_stagione:
        raise HTTPException(400, "Le partite del file non hanno il campo 'stagione'.")

    totale = 0
    for s, righe in per_stagione.items():
        df = pd.DataFrame(righe).drop(columns=["id", "stagione"], errors="ignore")
        totale += salva_partite(df, s)  # cancella e reinserisce la stagione
    return {"stagioni": sorted(per_stagione.keys()), "partite_importate": totale}


# ── Fase a eliminazione Galactic League (generazione round-by-round) ─────────
# Il "ramo" del tabellone è codificato nel campo `ordine` di ogni partita
# (Ottavi A=0..H=7; Quarti 0..3; Semifinali 0..1; Finale 0), così ogni turno si
# ricostruisce dai vincitori del precedente. Schema confermato dall'utente.
LEAGUE_KO_ROUNDS = [
    ("playoff",    "Play Off",    ["Play Off - Andata", "Play Off - Ritorno"]),
    ("ottavi",     "Ottavi",      ["Ottavi League - Andata", "Ottavi League - Ritorno"]),
    ("quarti",     "Quarti",      ["Quarti League - Andata", "Quarti League - Ritorno"]),
    ("semifinali", "Semifinali",  ["Semifinale League - Andata", "Semifinale League - Ritorno"]),
    ("finale",     "Finale",      ["Finale League"]),
]


def _giornate_state(df, giornate: list[str]) -> dict:
    """Stato di un insieme di giornate: esiste (almeno una partita), completo
    (tutte con risultato parsabile), n (numero partite)."""
    if df.empty:
        return {"esiste": False, "completo": False, "n": 0}
    sub = df[df["giornata"].isin(giornate)]
    n = len(sub)
    if n == 0:
        return {"esiste": False, "completo": False, "n": 0}
    completo = all(re.match(r"^\d+-\d+", str(x).strip()) for x in sub["risultato"])
    return {"esiste": True, "completo": bool(completo), "n": n}


def _winners_by_ordine(df, andata_g: str, ritorno_g: str) -> dict:
    """Vincitore (aggregato andata/ritorno) di ogni sfida, indicizzato per il
    `ordine` (= ramo del tabellone)."""
    andate = df[df["giornata"] == andata_g]
    ritorni = df[df["giornata"] == ritorno_g]
    out: dict = {}
    for _, a in andate.iterrows():
        k = int(a["ordine"])
        match = ritorni[ritorni["ordine"] == k]
        if match.empty:
            continue
        out[k] = _aggregato_vincitore(a, match.iloc[0])
    return out


def _riga_ko(giornata: str, casa: str, trasf: str, ordine: int, tipo: str,
             neutro: bool = False) -> dict:
    return {
        "giornata": giornata,
        "squadra_casa": casa,
        "risultato": "",
        "squadra_trasferta": trasf,
        "tipo": tipo,
        "ordine": ordine,
        "Competizione": "galactic league",
        "campo": "Neutro" if neutro else casa,
    }


def _coppia_andata_ritorno(rows: list, g_and: str, g_rit: str, ordine: int,
                           casa_andata: str, casa_ritorno: str, tipo: str) -> None:
    """Aggiunge andata (casa_andata in casa) e ritorno (casa_ritorno in casa)."""
    rows.append(_riga_ko(g_and, casa_andata, casa_ritorno, ordine, tipo))
    rows.append(_riga_ko(g_rit, casa_ritorno, casa_andata, ordine, tipo))


def _genera_round_league(round_key: str, pos_to_team: dict, df, rng) -> list:
    """Costruisce le righe-partita (risultato vuoto) del turno richiesto, a
    partire dalla classifica del girone (pos_to_team) e dai vincitori dei turni
    già giocati. I sorteggi binari sono rifatti qui con `rng`."""
    rows: list = []

    if round_key == "playoff":
        # 4 gruppi: {hi1,hi2} x {lo1,lo2}; incrocio binario; testa alta ospita il ritorno.
        gruppi = [(9, 10, 23, 24), (11, 12, 21, 22), (13, 14, 19, 20), (15, 16, 17, 18)]
        for i, (h1, h2, l1, l2) in enumerate(gruppi):
            if rng.random() < 0.5:
                primo, secondo = (h1, l2), (h2, l1)
            else:
                primo, secondo = (h1, l1), (h2, l2)
            # "primo" (testa alta del gruppo) → ramo i (A..D); "secondo" → ramo i+4 (E..H)
            for ramo_idx, (hp, lp) in ((i, primo), (i + 4, secondo)):
                high, low = pos_to_team[hp], pos_to_team[lp]
                _coppia_andata_ritorno(
                    rows, "Play Off - Andata", "Play Off - Ritorno",
                    ramo_idx, low, high, "Play Off",  # high (testa alta) ospita il ritorno
                )
        return rows

    if round_key == "ottavi":
        winners = _winners_by_ordine(df, "Play Off - Andata", "Play Off - Ritorno")
        coppie = {0: (7, 8), 1: (5, 6), 2: (3, 4), 3: (1, 2)}  # rami A,B,C,D ↔ E,F,G,H
        seed_ramo: dict = {}
        for p in range(4):
            hi, lo = coppie[p]
            if rng.random() < 0.5:
                seed_ramo[p], seed_ramo[p + 4] = hi, lo
            else:
                seed_ramo[p], seed_ramo[p + 4] = lo, hi
        for k in range(8):
            pw = winners.get(k)
            if pw is None:
                raise HTTPException(409, "Risultati del Play Off incompleti.")
            seed = pos_to_team[seed_ramo[k]]
            _coppia_andata_ritorno(
                rows, "Ottavi League - Andata", "Ottavi League - Ritorno",
                k, pw, seed, "Final Phase",  # testa di serie ospita il ritorno
            )
        return rows

    if round_key == "quarti":
        winners = _winners_by_ordine(df, "Ottavi League - Andata", "Ottavi League - Ritorno")
        for q in range(4):  # 1.0=A-B, 2.0=C-D, 3.0=E-F, 4.0=G-H
            left, right = winners.get(2 * q), winners.get(2 * q + 1)
            if left is None or right is None:
                raise HTTPException(409, "Risultati degli Ottavi incompleti.")
            _coppia_andata_ritorno(
                rows, "Quarti League - Andata", "Quarti League - Ritorno",
                q, left, right, "Final Phase",  # slot sinistro ospita l'andata, destro il ritorno
            )
        return rows

    if round_key == "semifinali":
        winners = _winners_by_ordine(df, "Quarti League - Andata", "Quarti League - Ritorno")
        for s in range(2):  # 1.0-2.0 e 3.0-4.0
            left, right = winners.get(2 * s), winners.get(2 * s + 1)
            if left is None or right is None:
                raise HTTPException(409, "Risultati dei Quarti incompleti.")
            _coppia_andata_ritorno(
                rows, "Semifinale League - Andata", "Semifinale League - Ritorno",
                s, left, right, "Final Phase",
            )
        return rows

    if round_key == "finale":
        winners = _winners_by_ordine(df, "Semifinale League - Andata", "Semifinale League - Ritorno")
        a, b = winners.get(0), winners.get(1)
        if a is None or b is None:
            raise HTTPException(409, "Risultati delle Semifinali incompleti.")
        rows.append(_riga_ko("Finale League", a, b, 0, "Final Phase", neutro=True))
        return rows

    raise HTTPException(400, f"Turno sconosciuto: {round_key}")


@app.get("/api/genera/league-stato")
def get_league_stato(stagione: int):
    """Stato della Galactic League di una stagione (per la UI di generazione):
    girone + ogni turno della fase a eliminazione, e quale turno è generabile."""
    df = leggi_partite(stagione)
    gruppo = _giornate_state(df, LEAGUE_GIORNATE)

    rounds = []
    prossimo = prossimo_label = None
    prossimo_abilitato = False
    prev_completo = gruppo["completo"]
    for key, label, giornate in LEAGUE_KO_ROUNDS:
        st = _giornate_state(df, giornate)
        rounds.append({"key": key, "label": label, **st})
        if prossimo is None and not st["esiste"]:
            prossimo, prossimo_label = key, label
            prossimo_abilitato = prev_completo
        prev_completo = st["completo"]

    return {
        "stagione": stagione,
        "gruppo": gruppo,
        "rounds": rounds,
        "prossimo": prossimo,
        "prossimo_label": prossimo_label,
        "prossimo_abilitato": prossimo_abilitato,
    }


@app.post("/api/genera/league-knockout")
def genera_league_knockout(req: GeneraLeagueRequest):
    """Genera il prossimo turno della fase a eliminazione della Galactic League
    (Play Off → Ottavi → Quarti → Semifinali → Finale), dalla classifica del
    girone e dai vincitori dei turni precedenti. Richiede il turno precedente
    completo."""
    presenti = stagioni_presenti()
    stagione = req.stagione if req.stagione is not None else (max(presenti) if presenti else 0)
    df = leggi_partite(stagione)

    gruppo = _giornate_state(df, LEAGUE_GIORNATE)
    if not gruppo["esiste"]:
        raise HTTPException(400, "Genera prima la fase a gironi.")
    if not gruppo["completo"]:
        raise HTTPException(
            409, "Completa i risultati di tutte le 8 giornate prima della fase a eliminazione."
        )

    next_key = next_label = next_giornate = None
    prev_completo, prev_label = gruppo["completo"], "fase a gironi"
    for key, label, giornate in LEAGUE_KO_ROUNDS:
        st = _giornate_state(df, giornate)
        if not st["esiste"]:
            next_key, next_label, next_giornate = key, label, giornate
            break
        prev_completo, prev_label = st["completo"], label
    if next_key is None:
        raise HTTPException(409, "La fase a eliminazione è già completa (Finale generata).")
    if not prev_completo:
        raise HTTPException(
            409, f"Completa i risultati del turno precedente ({prev_label}) prima di generare {next_label}."
        )

    df_cl = estrattore.costruisci_classifica_galactic_league(df)
    if df_cl is None or len(df_cl) < 24:
        raise HTTPException(409, "Classifica del girone incompleta (servono almeno 24 squadre).")
    pos_to_team = {int(r["Posizione"]): r["SQUADRA"] for _, r in df_cl.iterrows()}

    rng = random.Random(req.seed)
    righe = _genera_round_league(next_key, pos_to_team, df, rng)
    inserite = sostituisci_partite_competizione(righe, stagione, "galactic league", next_giornate)
    return {"stagione": stagione, "round": next_key, "label": next_label, "partite_inserite": inserite}


# ── Galactic Cup (generazione round-by-round) ───────────────────────────────
# Turno 1: le 8 ultime della classifica League della stagione PRECEDENTE.
# Turno 2: le altre 28 + le 4 vincitrici del Turno 1 (in trasferta, slot fissi
# alle partite 0/4/8/12). Poi Ottavi (secca) → Quarti/Semi (andata-ritorno) →
# Finale (neutra). Il ramo del tabellone è codificato in `ordine`.
CUP_ROUNDS = [
    ("turno1",     "Turno 1",     ["Turno 1"]),
    ("turno2",     "Turno 2",     ["Turno 2"]),
    ("ottavi",     "Ottavi",      ["Ottavi di Finale"]),
    ("quarti",     "Quarti",      ["Quarti di Finale - Andata", "Quarti di Finale - Ritorno"]),
    ("semifinali", "Semifinali",  ["Semifinale - Andata", "Semifinale - Ritorno"]),
    ("finale",     "Finale",      ["Finale Cup"]),
]


def _riga_cup(giornata: str, casa: str, trasf: str, ordine: int, neutro: bool = False) -> dict:
    return {
        "giornata": giornata,
        "squadra_casa": casa,
        "risultato": "",
        "squadra_trasferta": trasf,
        "tipo": "Cup",
        "ordine": ordine,
        "Competizione": "galactic cup",
        "campo": "Neutro" if neutro else casa,
    }


def _coppia_cup(rows: list, g_and: str, g_rit: str, ordine: int, top: str, bottom: str) -> None:
    """Andata in casa al 'top' (squadra in alto), ritorno in casa al 'bottom'."""
    rows.append(_riga_cup(g_and, top, bottom, ordine))
    rows.append(_riga_cup(g_rit, bottom, top, ordine))


def _winners_single_by_ordine(df, giornata: str) -> dict:
    """Vincitore di ogni gara secca di un turno, indicizzato per `ordine`."""
    out: dict = {}
    for _, row in df[df["giornata"] == giornata].iterrows():
        out[int(row["ordine"])] = _winner_of_match(row)
    return out


def _classifica_league_precedente(stagione: int):
    """Mappa posizione→squadra della classifica Galactic League della stagione
    precedente (serve come seeding della Galactic Cup). None se non disponibile."""
    if stagione <= 1:
        return None
    df_prev = leggi_partite(stagione - 1)
    if df_prev.empty:
        return None
    cl = estrattore.costruisci_classifica_galactic_league(df_prev)
    if cl is None or len(cl) < 36:
        return None
    return {int(r["Posizione"]): r["SQUADRA"] for _, r in cl.iterrows()}


def _genera_round_cup(round_key: str, stagione: int, df, rng) -> list:
    rows: list = []

    if round_key == "turno1":
        pos = _classifica_league_precedente(stagione)
        if pos is None:
            raise HTTPException(409, "Serve la Galactic League completa della stagione precedente.")
        ultime8 = [pos[p] for p in range(29, 37)]  # pos. 29-36
        rng.shuffle(ultime8)
        for k in range(4):
            a, b = ultime8[2 * k], ultime8[2 * k + 1]
            if rng.random() < 0.5:
                a, b = b, a  # casa casuale
            rows.append(_riga_cup("Turno 1", a, b, k))
        return rows

    if round_key == "turno2":
        pos = _classifica_league_precedente(stagione)
        if pos is None:
            raise HTTPException(409, "Serve la Galactic League completa della stagione precedente.")
        altre28 = [pos[p] for p in range(1, 29)]  # pos. 1-28
        rng.shuffle(altre28)
        winners = _winners_single_by_ordine(df, "Turno 1")
        idx = 0
        for m in range(16):
            if m % 4 == 0:  # partite 0,4,8,12: vincitrice T1 in trasferta, slot fisso
                w = winners.get(m // 4)
                if w is None:
                    raise HTTPException(409, "Risultati del Turno 1 incompleti (le parità richiedono i rigori, es. 1-1 (4-3)).")
                home = altre28[idx]; idx += 1
                rows.append(_riga_cup("Turno 2", home, w, m))  # squadra di pos.1-28 in casa
            else:
                a, b = altre28[idx], altre28[idx + 1]; idx += 2
                if rng.random() < 0.5:
                    a, b = b, a
                rows.append(_riga_cup("Turno 2", a, b, m))
        return rows

    if round_key == "ottavi":
        winners = _winners_single_by_ordine(df, "Turno 2")
        for j in range(8):  # accoppia in ordine (m0-m1), (m2-m3), ...
            top, bottom = winners.get(2 * j), winners.get(2 * j + 1)
            if top is None or bottom is None:
                raise HTTPException(409, "Risultati del Turno 2 incompleti (le parità richiedono i rigori).")
            rows.append(_riga_cup("Ottavi di Finale", top, bottom, j))  # 'top' in casa
        return rows

    if round_key == "quarti":
        winners = _winners_single_by_ordine(df, "Ottavi di Finale")
        for j in range(4):
            top, bottom = winners.get(2 * j), winners.get(2 * j + 1)
            if top is None or bottom is None:
                raise HTTPException(409, "Risultati degli Ottavi incompleti (le parità richiedono i rigori).")
            _coppia_cup(rows, "Quarti di Finale - Andata", "Quarti di Finale - Ritorno", j, top, bottom)
        return rows

    if round_key == "semifinali":
        winners = _winners_by_ordine(df, "Quarti di Finale - Andata", "Quarti di Finale - Ritorno")
        for j in range(2):
            top, bottom = winners.get(2 * j), winners.get(2 * j + 1)
            if top is None or bottom is None:
                raise HTTPException(409, "Risultati dei Quarti incompleti.")
            _coppia_cup(rows, "Semifinale - Andata", "Semifinale - Ritorno", j, top, bottom)
        return rows

    if round_key == "finale":
        winners = _winners_by_ordine(df, "Semifinale - Andata", "Semifinale - Ritorno")
        a, b = winners.get(0), winners.get(1)
        if a is None or b is None:
            raise HTTPException(409, "Risultati delle Semifinali incompleti.")
        rows.append(_riga_cup("Finale Cup", a, b, 0, neutro=True))
        return rows

    raise HTTPException(400, f"Turno sconosciuto: {round_key}")


@app.get("/api/genera/cup-stato")
def get_cup_stato(stagione: int):
    """Stato della Galactic Cup di una stagione e quale turno è generabile.
    Il Turno 1 richiede la classifica Galactic League della stagione precedente."""
    df = leggi_partite(stagione)
    prev_ok = _classifica_league_precedente(stagione) is not None

    rounds = []
    prossimo = prossimo_label = None
    prossimo_abilitato = False
    prev_completo = prev_ok  # prerequisito del Turno 1
    for key, label, giornate in CUP_ROUNDS:
        st = _giornate_state(df, giornate)
        rounds.append({"key": key, "label": label, **st})
        if prossimo is None and not st["esiste"]:
            prossimo, prossimo_label = key, label
            prossimo_abilitato = prev_completo
        prev_completo = st["completo"]

    return {
        "stagione": stagione,
        "prev_disponibile": prev_ok,
        "rounds": rounds,
        "prossimo": prossimo,
        "prossimo_label": prossimo_label,
        "prossimo_abilitato": prossimo_abilitato,
    }


@app.post("/api/genera/cup-round")
def genera_cup_round(req: GeneraLeagueRequest):
    """Genera il prossimo turno della Galactic Cup (Turno 1 → Turno 2 → Ottavi →
    Quarti → Semifinali → Finale). Il Turno 1 richiede la Galactic League completa
    della stagione precedente; gli altri turni il turno precedente completo."""
    presenti = stagioni_presenti()
    stagione = req.stagione if req.stagione is not None else (max(presenti) if presenti else 0)
    df = leggi_partite(stagione)

    prev_ok = _classifica_league_precedente(stagione) is not None
    next_key = next_label = next_giornate = None
    prev_completo, prev_label = prev_ok, "Galactic League della stagione precedente"
    for key, label, giornate in CUP_ROUNDS:
        st = _giornate_state(df, giornate)
        if not st["esiste"]:
            next_key, next_label, next_giornate = key, label, giornate
            break
        prev_completo, prev_label = st["completo"], label
    if next_key is None:
        raise HTTPException(409, "La Galactic Cup è già completa (Finale generata).")
    if not prev_completo:
        if next_key == "turno1":
            raise HTTPException(409, "Serve la Galactic League completa della stagione precedente.")
        raise HTTPException(
            409, f"Completa i risultati del turno precedente ({prev_label}) prima di generare {next_label}."
        )

    rng = random.Random(req.seed)
    righe = _genera_round_cup(next_key, stagione, df, rng)
    inserite = sostituisci_partite_competizione(righe, stagione, "galactic cup", next_giornate)
    return {"stagione": stagione, "round": next_key, "label": next_label, "partite_inserite": inserite}


# ── Galactic Kings League — Fase 1 (gironi) ─────────────────────────────────
# Formato S5+: Lega A 4 gironi (16), Lega B 3 (12), Lega C 2 (8) = 36.
# Composizione delle leghe = quella della stagione PRECEDENTE + promo/retrocessioni
# (lette dagli esiti già calcolati da costruisci_esiti_kings_league).
# Fasce: dentro ogni lega, ordine per ranking cumulato e split a metà.
# Schedule girone (doppio girone bilanciato, casa elencata prima), posizioni 0-3:
KINGS_SCHEDULE = [
    (0, 1), (2, 3),   # G1
    (1, 3), (0, 2),   # G2
    (2, 1), (3, 0),   # G3
    (1, 0), (3, 2),   # G4
    (1, 2), (0, 3),   # G5
    (3, 1), (2, 0),   # G6
]
KINGS_LEGHE = [("Lega A", 4), ("Lega B", 3), ("Lega C", 2)]
KINGS_GIRONE_GIORNATE = [
    f"Fase 1 - {lega} - Girone {chr(65 + i)}"
    for lega, n in KINGS_LEGHE for i in range(n)
]


def _kings_membership(stagione: int):
    """Composizione delle leghe (squadra → 'Lega A/B/C') per `stagione`, derivata
    dalla Kings League della stagione PRECEDENTE applicando promo/retrocessioni
    (dai 'colori' di costruisci_esiti_kings_league). None se non disponibile."""
    if stagione <= 1:
        return None
    df_prev = leggi_partite(stagione - 1)
    if df_prev.empty:
        return None
    df_class = estrattore.costruisci_classifica_kings_league(df_prev)
    if df_class is None or len(df_class) == 0:
        return None
    colore = estrattore.costruisci_esiti_kings_league(df_prev, df_class)
    prev_lega = {r["SQUADRA"]: r["Lega"] for r in df_class.to_dict("records")}

    nxt = {}
    for team, lega in prev_lega.items():
        c = colore.get(team, "neutro")
        if lega == "Lega A":
            nxt[team] = "Lega B" if c == "arancione" else "Lega A"
        elif lega == "Lega B":
            nxt[team] = "Lega A" if c == "verde" else ("Lega C" if c == "arancione" else "Lega B")
        elif lega == "Lega C":
            nxt[team] = "Lega B" if c == "verde" else "Lega C"
        else:
            nxt[team] = lega
    return nxt


def _genera_kings_gironi(stagione: int, rng) -> list:
    membership = _kings_membership(stagione)
    if membership is None:
        raise HTTPException(409, "Serve la Kings League completa della stagione precedente.")

    counts = {"Lega A": 0, "Lega B": 0, "Lega C": 0}
    for l in membership.values():
        if l in counts:
            counts[l] += 1
    if counts != {"Lega A": 16, "Lega B": 12, "Lega C": 8}:
        raise HTTPException(
            409,
            f"Composizione leghe non valida dalla stagione precedente: {counts} "
            f"(attese Lega A 16, Lega B 12, Lega C 8). Verifica che la Kings League "
            f"della stagione precedente sia completa (gironi + spareggi).",
        )

    cum = get_ranking_cumulato(stagione - 1)
    pos_of = {r["SQUADRA"]: r["POSIZIONE"] for r in cum.get("ranking", [])}

    rows: list = []
    for lega, n_gironi in KINGS_LEGHE:
        teams = sorted(
            [t for t, l in membership.items() if l == lega],
            key=lambda t: pos_of.get(t, 9999),
        )
        if len(teams) != n_gironi * 4:
            raise HTTPException(409, f"{lega}: {len(teams)} squadre, attese {n_gironi * 4}.")
        meta = len(teams) // 2
        fascia1, fascia2 = teams[:meta], teams[meta:]
        rng.shuffle(fascia1)
        rng.shuffle(fascia2)
        for g in range(n_gironi):
            four = fascia1[2 * g:2 * g + 2] + fascia2[2 * g:2 * g + 2]
            rng.shuffle(four)  # posizioni 1-4 casuali
            girone = f"Fase 1 - {lega} - Girone {chr(65 + g)}"
            for ordine, (h, a) in enumerate(KINGS_SCHEDULE):
                rows.append({
                    "giornata": girone,
                    "squadra_casa": four[h],
                    "risultato": "",
                    "squadra_trasferta": four[a],
                    "tipo": "Kings League",
                    "ordine": ordine,
                    "Competizione": "Kings League",
                    "campo": four[h],
                })
    return rows


# Fasi finali Kings (gare secche, campo neutro). Tre step: gironi → finali1 → finali2.
KINGS_FINALI_1 = [
    "Final Four - Semifinali",
    "Playoff/Playout A-B - Turno 1",
    "Playoff/Playout B-C - Turno 1",
]
KINGS_FINALI_2 = [
    "Final Four - Finale",
    "Playoff/Playout A-B - Turno 2",
    "Playoff/Playout B-C - Turno 2",
]
KINGS_STEPS = [
    ("gironi",  "Gironi (Fase 1)",                          KINGS_GIRONE_GIORNATE),
    ("finali1", "Semifinali Final Four + Spareggi (1° turno)", KINGS_FINALI_1),
    ("finali2", "Finale Final Four + Spareggi (2° turno)",     KINGS_FINALI_2),
]


def _riga_kings_neutro(giornata: str, casa: str, trasf: str, ordine: int, tipo: str) -> dict:
    return {
        "giornata": giornata, "squadra_casa": casa, "risultato": "",
        "squadra_trasferta": trasf, "tipo": tipo, "ordine": ordine,
        "Competizione": "Kings League", "campo": "Neutro",
    }


def _pair_random(teams: list, rng) -> list:
    t = list(teams)
    rng.shuffle(t)
    return [(t[i], t[i + 1]) for i in range(0, len(t), 2)]


def _kings_pos(recs: list, lega: str, pos: int) -> list:
    return [r["SQUADRA"] for r in recs if r["Lega"] == lega and r["Posizione"] == pos]


def _kings_sorted_pos(recs: list, lega: str, pos: int, cum_pos: dict) -> list:
    """Squadre a (lega, pos) ordinate per: PT desc, DIFF desc, GF desc, GS asc,
    ranking cumulato asc — la 'migliore' è la prima."""
    sub = [r for r in recs if r["Lega"] == lega and r["Posizione"] == pos]
    sub.sort(key=lambda r: (-r["PT"], -r["DIFF"], -r["GF"], r["GS"], cum_pos.get(r["SQUADRA"], 9999)))
    return [r["SQUADRA"] for r in sub]


def _losers_single(df, giornata: str) -> list:
    """Perdenti delle gare secche di una giornata (errore se parità senza rigori)."""
    out = []
    for _, row in df[df["giornata"] == giornata].iterrows():
        w = _winner_of_match(row)
        if w is None:
            raise HTTPException(
                409, f"'{giornata}': una partita è in parità senza vincitore — aggiungi i rigori (es. 1-1 (4-3))."
            )
        out.append(row["squadra_trasferta"] if w == row["squadra_casa"] else row["squadra_casa"])
    return out


def _kings_cum_pos(stagione: int) -> dict:
    cum = get_ranking_cumulato(stagione - 1)
    return {r["SQUADRA"]: r["POSIZIONE"] for r in cum.get("ranking", [])}


def _genera_kings_finali1(stagione: int, df, rng) -> list:
    cl = estrattore.costruisci_classifica_kings_league(df)
    if cl is None or len(cl) == 0:
        raise HTTPException(409, "Classifica dei gironi Kings mancante.")
    recs = cl.to_dict("records")
    cum_pos = _kings_cum_pos(stagione)

    a_firsts = _kings_pos(recs, "Lega A", 1)
    a_thirds = _kings_pos(recs, "Lega A", 3)
    b_thirds = _kings_sorted_pos(recs, "Lega B", 3, cum_pos)  # migliore in testa
    c_seconds = _kings_pos(recs, "Lega C", 2)
    if len(a_firsts) != 4 or len(a_thirds) != 4 or len(b_thirds) != 3 or len(c_seconds) != 2:
        raise HTTPException(409, "Classifica dei gironi Kings incompleta.")

    rows = []
    for o, (h, a) in enumerate(_pair_random(a_firsts, rng)):
        rows.append(_riga_kings_neutro("Final Four - Semifinali", h, a, o, "Kings League Final Four"))
    for o, (h, a) in enumerate(_pair_random(a_thirds, rng)):
        rows.append(_riga_kings_neutro("Playoff/Playout A-B - Turno 1", h, a, o, "Kings League Playoff/Playout A-B"))
    # Turno 1 B-C: le 2 terze rimanenti di Lega B si affrontano tra loro
    # (vince → salva in B, perde → Turno 2) e, separatamente, le 2 seconde
    # di Lega C si affrontano tra loro (vince → promossa in B, perde →
    # Turno 2). Le due partite NON vanno mischiate tra loro.
    b_rimanenti = b_thirds[1:]  # esclude la miglior terza di B (resta in B)
    h, a = _pair_random(b_rimanenti, rng)[0]
    rows.append(_riga_kings_neutro("Playoff/Playout B-C - Turno 1", h, a, 0, "Kings League Playoff/Playout B-C"))
    h, a = _pair_random(c_seconds, rng)[0]
    rows.append(_riga_kings_neutro("Playoff/Playout B-C - Turno 1", h, a, 1, "Kings League Playoff/Playout B-C"))
    return rows


def _genera_kings_finali2(stagione: int, df, rng) -> list:
    cl = estrattore.costruisci_classifica_kings_league(df)
    recs = cl.to_dict("records") if cl is not None else []
    cum_pos = _kings_cum_pos(stagione)

    rows = []
    # Final Four — Finale (vincenti delle semifinali)
    ffw = _winners_single_by_ordine(df, "Final Four - Semifinali")
    fa, fb = ffw.get(0), ffw.get(1)
    if fa is None or fb is None:
        raise HTTPException(409, "Semifinali Final Four incomplete (parità → aggiungi i rigori).")
    rows.append(_riga_kings_neutro("Final Four - Finale", fa, fb, 0, "Kings League Final Four"))

    # Playoff/Playout A-B — Turno 2: perdenti A (Turno 1) vs 2 peggiori seconde di B
    ab_losers = _losers_single(df, "Playoff/Playout A-B - Turno 1")
    b_seconds = _kings_sorted_pos(recs, "Lega B", 2, cum_pos)  # migliore in testa (promossa diretta)
    ab_b = b_seconds[1:]  # le 2 peggiori seconde
    if len(ab_losers) != 2 or len(ab_b) != 2:
        raise HTTPException(409, "Dati incompleti per il Turno 2 A-B.")
    rng.shuffle(ab_losers)
    rng.shuffle(ab_b)
    for o in range(2):  # incrocio: perdente A vs seconda B
        rows.append(_riga_kings_neutro("Playoff/Playout A-B - Turno 2", ab_losers[o], ab_b[o], o, "Kings League Playoff/Playout A-B"))

    # Playoff/Playout B-C — Turno 2: i 2 perdenti del Turno 1
    bc_losers = _losers_single(df, "Playoff/Playout B-C - Turno 1")
    if len(bc_losers) != 2:
        raise HTTPException(409, "Dati incompleti per il Turno 2 B-C.")
    rows.append(_riga_kings_neutro("Playoff/Playout B-C - Turno 2", bc_losers[0], bc_losers[1], 0, "Kings League Playoff/Playout B-C"))
    return rows


@app.get("/api/genera/kings-stato")
def get_kings_stato(stagione: int):
    """Stato della Kings League: gironi (Fase 1) → semifinali/spareggi (1° turno)
    → finale/spareggi (2° turno). Indica quale step è generabile."""
    df = leggi_partite(stagione)
    prev_ok = _kings_membership(stagione) is not None

    rounds = []
    prossimo = prossimo_label = prossimo_hint = None
    prossimo_abilitato = False
    prev_completo = prev_ok  # prerequisito dei gironi
    for key, label, giornate in KINGS_STEPS:
        st = _giornate_state(df, giornate)
        rounds.append({"key": key, "label": label, **st})
        if prossimo is None and not st["esiste"]:
            prossimo, prossimo_label = key, label
            prossimo_abilitato = prev_completo
            if not prev_completo and key == "gironi":
                prossimo_hint = "Serve la Kings League completa della stagione precedente."
        prev_completo = st["completo"]

    done_message = None
    if prossimo is None:
        done_message = ("Kings League completa (gironi + fasi finali). "
                        "Promo/retrocessioni pronte per la stagione successiva.")
    return {
        "stagione": stagione,
        "prev_disponibile": prev_ok,
        "rounds": rounds,
        "prossimo": prossimo,
        "prossimo_label": prossimo_label,
        "prossimo_abilitato": prossimo_abilitato,
        "prossimo_hint": prossimo_hint,
        "done_message": done_message,
    }


@app.post("/api/genera/kings-round")
def genera_kings_round(req: GeneraLeagueRequest):
    """Genera il prossimo step della Kings League (gironi → finali1 → finali2)."""
    presenti = stagioni_presenti()
    stagione = req.stagione if req.stagione is not None else (max(presenti) if presenti else 0)
    df = leggi_partite(stagione)
    prev_ok = _kings_membership(stagione) is not None

    next_key = next_label = next_giornate = None
    prev_completo, prev_label = prev_ok, "Kings League della stagione precedente"
    for key, label, giornate in KINGS_STEPS:
        st = _giornate_state(df, giornate)
        if not st["esiste"]:
            next_key, next_label, next_giornate = key, label, giornate
            break
        prev_completo, prev_label = st["completo"], label
    if next_key is None:
        raise HTTPException(409, "La Kings League è già completa (fasi finali generate).")
    if not prev_completo:
        if next_key == "gironi":
            raise HTTPException(409, "Serve la Kings League completa della stagione precedente.")
        raise HTTPException(
            409, f"Completa i risultati del turno precedente ({prev_label}) prima di generare {next_label}."
        )

    rng = random.Random(req.seed)
    if next_key == "gironi":
        righe = _genera_kings_gironi(stagione, rng)
    elif next_key == "finali1":
        righe = _genera_kings_finali1(stagione, df, rng)
    else:
        righe = _genera_kings_finali2(stagione, df, rng)
    inserite = sostituisci_partite_competizione(righe, stagione, "Kings League", next_giornate)
    return {"stagione": stagione, "round": next_key, "label": next_label, "partite_inserite": inserite}


# ── Galactic Champions Cup — Fase 1 (6 gironi da 6) ─────────────────────────
# 36 squadre in 6 fasce (ranking cumulato), 1 per fascia per girone (sorteggio).
# Doppio girone: ogni coppia 2 volte (casa/trasferta), mai 3 gare di fila stesso campo.
CHAMPIONS_FASE1_GIORNATE = [f"Fase 1 - Girone {chr(65 + i)}" for i in range(6)]
CHAMPIONS_FASE2_GIORNATE = [f"Fase 2 - Girone {chr(65 + i)}" for i in range(6)]
CHAMPIONS_STEPS = [
    ("fase1",  "Fase 1 (gironi)",      CHAMPIONS_FASE1_GIORNATE),
    ("fase2",  "Fase 2 (gironi)",      CHAMPIONS_FASE2_GIORNATE),
    ("ottavi", "Fase 3 — Ottavi",      ["Fase 3 - Ottavi di Finale"]),
    ("quarti", "Fase 3 — Quarti",      ["Fase 3 - Quarti di Finale"]),
    ("semi",   "Fase 3 — Semifinali",  ["Fase 3 - Semifinale"]),
    ("finale", "Fase 3 — Finale",      ["Fase 3 - Finale"]),
]

# Abbinamento delle 4 migliori terze a WB/WC/WE/WF negli Ottavi (sistema UEFA):
# chiave = i 4 gironi (ordinati) da cui provengono le terze qualificate;
# valore = (terza di WB, terza di WC, terza di WE, terza di WF).
CHAMPIONS_THIRDS_TABLE = {
    ("A", "B", "C", "D"): ("A", "D", "B", "C"),
    ("A", "B", "C", "E"): ("A", "E", "B", "C"),
    ("A", "B", "C", "F"): ("A", "F", "B", "C"),
    ("A", "B", "D", "E"): ("D", "E", "A", "B"),
    ("A", "B", "D", "F"): ("D", "F", "A", "B"),
    ("A", "B", "E", "F"): ("E", "F", "B", "A"),
    ("A", "C", "D", "E"): ("E", "D", "C", "A"),
    ("A", "C", "D", "F"): ("F", "D", "C", "A"),
    ("A", "C", "E", "F"): ("E", "F", "C", "A"),
    ("A", "D", "E", "F"): ("E", "F", "D", "A"),
    ("B", "C", "D", "E"): ("E", "D", "B", "C"),
    ("B", "C", "D", "F"): ("F", "D", "C", "B"),
    ("B", "C", "E", "F"): ("F", "E", "C", "B"),
    ("B", "D", "E", "F"): ("F", "E", "D", "B"),
    ("C", "D", "E", "F"): ("F", "E", "D", "C"),
}

# Round-robin a 6 (metodo del cerchio), posizioni 0-5.
_RR6_ROUNDS = [
    [(0, 5), (1, 4), (2, 3)],
    [(0, 4), (5, 3), (1, 2)],
    [(0, 3), (4, 2), (5, 1)],
    [(0, 2), (3, 1), (4, 5)],
    [(0, 1), (2, 5), (3, 4)],
]


def _schedule_girone6(rng) -> list:
    """Doppio girone (10 giornate) per 6 squadre (posizioni 0-5): ogni coppia due
    volte (una per campo); nessuna squadra gioca 3+ gare di fila in casa o fuori.
    Ritorna lista (giornata_idx 0-9, home_pos, away_pos), ordinata per giornata."""
    for _ in range(2000):
        leg1 = []  # per round: lista di (home, away)
        for rnd in _RR6_ROUNDS:
            leg1.append([(a, b) if rng.random() < 0.5 else (b, a) for (a, b) in rnd])

        venue = {t: [None] * 10 for t in range(6)}
        for r, md in enumerate(leg1):
            for (h, a) in md:
                venue[h][r] = "H"; venue[a][r] = "A"
                venue[h][r + 5] = "A"; venue[a][r + 5] = "H"  # ritorno a campi invertiti

        ok = True
        for t in range(6):
            seq = venue[t]
            if any(seq[i] == seq[i + 1] == seq[i + 2] for i in range(8)):
                ok = False
                break
        if not ok:
            continue

        matches = []
        for r, md in enumerate(leg1):
            for (h, a) in md:
                matches.append((r, h, a))
                matches.append((r + 5, a, h))
        matches.sort(key=lambda x: x[0])
        return matches
    raise HTTPException(500, "Impossibile generare un calendario valido per il girone Champions.")


def _genera_champions_fase1(stagione: int, rng) -> list:
    cum = get_ranking_cumulato(stagione - 1)
    order = [r["SQUADRA"] for r in cum.get("ranking", [])]
    if len(order) != 36:
        raise HTTPException(
            409, f"Il ranking cumulato della stagione {stagione - 1} ha {len(order)} squadre, ne servono 36."
        )
    fasce = [list(order[f * 6:(f + 1) * 6]) for f in range(6)]
    for f in fasce:
        rng.shuffle(f)

    rows = []
    for g in range(6):
        teams = [fasce[f][g] for f in range(6)]  # una squadra per fascia
        rng.shuffle(teams)  # posizioni 0-5 casuali
        girone = f"Fase 1 - Girone {chr(65 + g)}"
        for ordine, (_md, h, a) in enumerate(_schedule_girone6(rng)):
            rows.append({
                "giornata": girone,
                "squadra_casa": teams[h],
                "risultato": "",
                "squadra_trasferta": teams[a],
                "tipo": "Champions Cup",
                "ordine": ordine,
                "Competizione": "galactic champions cup",
                "campo": teams[h],
            })
    return rows


def _assegna_fascia_gironi(teams: list, origins_per_girone: list, origin: dict, rng):
    """Assegna i team di una fascia ai gironi (uno per girone) evitando che due
    squadre dello stesso girone di Fase 1 finiscano insieme. None se impossibile."""
    ng = len(origins_per_girone)
    used = [False] * ng
    result: list = []

    def bt(i: int) -> bool:
        if i == len(teams):
            return True
        gorder = list(range(ng))
        rng.shuffle(gorder)
        for g in gorder:
            if used[g] or origin[teams[i]] in origins_per_girone[g]:
                continue
            used[g] = True
            result.append((g, teams[i]))
            if bt(i + 1):
                return True
            used[g] = False
            result.pop()
        return False

    return result if bt(0) else None


def _draw_champions_fase2(fasce: list, origin: dict, rng) -> list:
    """Sorteggia 6 gironi da 4 (una squadra per fascia) col vincolo: niente due
    squadre dello stesso girone di Fase 1 nello stesso girone di Fase 2."""
    ng = 6
    for _ in range(2000):
        gironi = [[] for _ in range(ng)]
        origins = [set() for _ in range(ng)]
        ok = True
        for fascia in fasce:
            teams = list(fascia)
            rng.shuffle(teams)
            assegn = _assegna_fascia_gironi(teams, origins, origin, rng)
            if assegn is None:
                ok = False
                break
            for g, t in assegn:
                gironi[g].append(t)
                origins[g].add(origin[t])
        if ok:
            return gironi
    raise HTTPException(500, "Sorteggio Fase 2 Champions non riuscito (vincolo stesso girone di Fase 1).")


def _genera_champions_fase2(stagione: int, df, rng) -> list:
    cl1 = estrattore.costruisci_classifica_galactic_champions_cup(df, fase=1)
    if cl1 is None or len(cl1) == 0:
        raise HTTPException(409, "Classifica della Fase 1 Champions mancante.")
    recs = cl1.to_dict("records")
    firsts  = [r["SQUADRA"] for r in recs if r["Posizione"] == 1]
    seconds = [r["SQUADRA"] for r in recs if r["Posizione"] == 2]
    rest    = [r["SQUADRA"] for r in recs if r["Posizione"] in (3, 4)]
    origin  = {r["SQUADRA"]: r["Girone"] for r in recs if r["Posizione"] in (1, 2, 3, 4)}
    if len(firsts) != 6 or len(seconds) != 6 or len(rest) != 12:
        raise HTTPException(409, "Fase 1 Champions incompleta (servono 6 gironi con tutti i risultati).")

    cum_pos = {r["SQUADRA"]: r["POSIZIONE"] for r in get_ranking_cumulato(stagione - 1).get("ranking", [])}
    rest.sort(key=lambda t: cum_pos.get(t, 9999))  # migliori (cumulato) per prime
    fasce = [firsts, seconds, rest[:6], rest[6:]]  # fascia 1,2,3,4

    gironi = _draw_champions_fase2(fasce, origin, rng)
    rows = []
    for g, teams4 in enumerate(gironi):
        girone = f"Fase 2 - Girone {chr(65 + g)}"
        # round robin singolo (4 squadre → 6 partite), gara secca campo neutro
        pairs = [(i, j) for i in range(4) for j in range(i + 1, 4)]
        for ordine, (i, j) in enumerate(pairs):
            rows.append({
                "giornata": girone,
                "squadra_casa": teams4[i],
                "risultato": "",
                "squadra_trasferta": teams4[j],
                "tipo": "Champions Cup",
                "ordine": ordine,
                "Competizione": "galactic champions cup",
                "campo": "Neutro",
            })
    return rows


def _riga_champions_neutro(giornata: str, casa: str, trasf: str, ordine: int) -> dict:
    return {
        "giornata": giornata, "squadra_casa": casa, "risultato": "",
        "squadra_trasferta": trasf, "tipo": "Champions Cup", "ordine": ordine,
        "Competizione": "galactic champions cup", "campo": "Neutro",
    }


def _girone_letter(g: str) -> str:
    return str(g).split()[-1]


def _genera_champions_fase3_ottavi(stagione: int, df) -> list:
    """Ottavi di Finale della Champions Cup (sistema UEFA, abbinamenti
    deterministici): 6 vincenti gironi (W), 6 seconde (R), 4 migliori terze."""
    cl2 = estrattore.costruisci_classifica_galactic_champions_cup(df, fase=2)
    if cl2 is None or len(cl2) == 0:
        raise HTTPException(409, "Classifica della Fase 2 Champions mancante.")
    recs = cl2.to_dict("records")
    W = {_girone_letter(r["Girone"]): r["SQUADRA"] for r in recs if r["Posizione"] == 1}
    R = {_girone_letter(r["Girone"]): r["SQUADRA"] for r in recs if r["Posizione"] == 2}

    df_terze = estrattore.costruisci_classifica_migliori_terze_champions_cup(
        df, _cumulato_tiebreak_map(stagione)
    )
    top4 = df_terze.head(4).to_dict("records") if df_terze is not None else []
    third_by_group = {_girone_letter(r["Girone"]): r["SQUADRA"] for r in top4}

    if len(W) != 6 or len(R) != 6 or len(third_by_group) != 4:
        raise HTTPException(409, "Fase 2 Champions incompleta (servono 6 gironi con tutti i risultati).")
    key = tuple(sorted(third_by_group.keys()))
    if key not in CHAMPIONS_THIRDS_TABLE:
        raise HTTPException(409, "Impossibile determinare le 4 migliori terze.")
    tbl = CHAMPIONS_THIRDS_TABLE[key]  # (terza di WB, WC, WE, WF)
    t_wb, t_wc, t_we, t_wf = (third_by_group[g] for g in tbl)

    # Match 1..8 (ordine 0..7)
    ottavi = [
        (W["B"], t_wb),   # M1: WB v 3
        (W["A"], R["C"]),  # M2: WA v RC
        (W["F"], t_wf),   # M3: WF v 3
        (R["D"], R["E"]),  # M4: RD v RE
        (W["E"], t_we),   # M5: WE v 3
        (W["D"], R["F"]),  # M6: WD v RF
        (W["C"], t_wc),   # M7: WC v 3
        (R["A"], R["B"]),  # M8: RA v RB
    ]
    return [_riga_champions_neutro("Fase 3 - Ottavi di Finale", h, a, o) for o, (h, a) in enumerate(ottavi)]


def _genera_champions_fase3_round(round_key: str, df) -> list:
    """Quarti/Semifinali/Finale della Champions Cup, a tabellone fisso dai
    vincitori (gare secche, campo neutro)."""
    if round_key == "quarti":
        prev_g, giornata, pairs = "Fase 3 - Ottavi di Finale", "Fase 3 - Quarti di Finale", [(0, 1), (2, 3), (4, 5), (6, 7)]
    elif round_key == "semi":
        prev_g, giornata, pairs = "Fase 3 - Quarti di Finale", "Fase 3 - Semifinale", [(0, 1), (2, 3)]
    else:  # finale
        prev_g, giornata, pairs = "Fase 3 - Semifinale", "Fase 3 - Finale", [(0, 1)]
    w = _winners_single_by_ordine(df, prev_g)
    rows = []
    for ordine, (i, j) in enumerate(pairs):
        a, b = w.get(i), w.get(j)
        if a is None or b is None:
            raise HTTPException(409, f"'{prev_g}': risultati incompleti (le parità richiedono i rigori).")
        rows.append(_riga_champions_neutro(giornata, a, b, ordine))
    return rows


def _cumulato_prev_ok(stagione: int) -> bool:
    if stagione <= 1:
        return False
    try:
        return len(get_ranking_cumulato(stagione - 1).get("ranking", [])) == 36
    except Exception:
        return False


@app.get("/api/genera/champions-stato")
def get_champions_stato(stagione: int):
    """Stato della Galactic Champions Cup. Per ora gestisce la Fase 1 (gironi);
    Fase 2 e Fase 3 arriveranno dopo."""
    df = leggi_partite(stagione)
    prev_ok = _cumulato_prev_ok(stagione)

    rounds = []
    prossimo = prossimo_label = prossimo_hint = None
    prossimo_abilitato = False
    prev_completo = prev_ok
    for key, label, giornate in CHAMPIONS_STEPS:
        st = _giornate_state(df, giornate)
        rounds.append({"key": key, "label": label, **st})
        if prossimo is None and not st["esiste"]:
            prossimo, prossimo_label = key, label
            prossimo_abilitato = prev_completo
            if not prev_completo:
                prossimo_hint = "Serve il ranking cumulato della stagione precedente (36 squadre)."
        prev_completo = st["completo"]

    done_message = None
    if prossimo is None:
        done_message = "Galactic Champions Cup completa (Fasi 1, 2 e 3)."
    return {
        "stagione": stagione,
        "prev_disponibile": prev_ok,
        "rounds": rounds,
        "prossimo": prossimo,
        "prossimo_label": prossimo_label,
        "prossimo_abilitato": prossimo_abilitato,
        "prossimo_hint": prossimo_hint,
        "done_message": done_message,
    }


@app.post("/api/genera/champions-round")
def genera_champions_round(req: GeneraLeagueRequest):
    """Genera il prossimo step della Champions Cup (per ora: Fase 1 gironi)."""
    presenti = stagioni_presenti()
    stagione = req.stagione if req.stagione is not None else (max(presenti) if presenti else 0)
    df = leggi_partite(stagione)

    next_key = next_label = next_giornate = None
    prev_completo, prev_label = _cumulato_prev_ok(stagione), "ranking cumulato stagione precedente"
    for key, label, giornate in CHAMPIONS_STEPS:
        st = _giornate_state(df, giornate)
        if not st["esiste"]:
            next_key, next_label, next_giornate = key, label, giornate
            break
        prev_completo, prev_label = st["completo"], label
    if next_key is None:
        raise HTTPException(409, "La Galactic Champions Cup è già completa (Finale generata).")
    if not prev_completo:
        if next_key == "fase1":
            raise HTTPException(409, "Serve il ranking cumulato della stagione precedente (36 squadre).")
        raise HTTPException(409, f"Completa i risultati del turno precedente ({prev_label}) prima di generare {next_label}.")

    rng = random.Random(req.seed)
    if next_key == "fase1":
        righe = _genera_champions_fase1(stagione, rng)
    elif next_key == "fase2":
        righe = _genera_champions_fase2(stagione, df, rng)
    elif next_key == "ottavi":
        righe = _genera_champions_fase3_ottavi(stagione, df)
    else:  # quarti / semi / finale
        righe = _genera_champions_fase3_round(next_key, df)
    inserite = sostituisci_partite_competizione(righe, stagione, "galactic champions cup", next_giornate)
    return {"stagione": stagione, "round": next_key, "label": next_label, "partite_inserite": inserite}


# ── Intergalactic SuperCup ──────────────────────────────────────────────────
# Semifinale 1: Vincitrice Galactic League vs Vincitrice Galactic Cup
# Semifinale 2: Vincitrice Kings League vs Vincitrice Galactic Champions Cup
# Finale: vincenti delle due semifinali. Tutte gare secche, campo neutro.
# Plurivincitore: rappresenta solo il torneo più importante (League > Champions >
# Cup > Kings); lo slot liberato va alla squadra col ranking stagionale parziale
# (4 coppe, SuperCup esclusa) più alto, non già partecipante.
SUPERCUP_STEPS = [
    ("semifinali", "Semifinali", ["Semifinale SuperCup"]),
    ("finale",     "Finale",     ["Finale SuperCup"]),
]
# (chiave interna comp → giornata della finale che ne determina la vincitrice)
SUPERCUP_FONTI = {
    "GL": "Finale League",
    "CC": "Fase 3 - Finale",
    "GC": "Finale Cup",
    "KL": "Final Four - Finale",
}
SUPERCUP_IMPORTANZA = ["GL", "CC", "GC", "KL"]  # ordine di importanza decrescente


def _riga_supercup(giornata: str, casa: str, trasf: str, ordine: int) -> dict:
    return {
        "giornata": giornata, "squadra_casa": casa, "risultato": "",
        "squadra_trasferta": trasf, "tipo": "SuperCup", "ordine": ordine,
        "Competizione": "intergalactic supercup", "campo": "Neutro",
    }


def _vincitore_finale(df, giornata: str) -> Optional[str]:
    rows = df[df["giornata"] == giornata]
    return _winner_of_match(rows.iloc[0]) if len(rows) > 0 else None


def _supercup_pronta(df) -> bool:
    """True se le 4 coppe principali hanno la finale giocata (con vincitrice)."""
    if df.empty:
        return False
    return all(_vincitore_finale(df, g) is not None for g in SUPERCUP_FONTI.values())


def _genera_supercup_semifinali(stagione: int, df, rng) -> list:
    winners = {comp: _vincitore_finale(df, g) for comp, g in SUPERCUP_FONTI.items()}
    if any(v is None for v in winners.values()):
        raise HTTPException(409, "Servono i vincitori delle 4 coppe principali (finali giocate).")

    # Ogni squadra rappresenta solo il torneo più importante che ha vinto.
    team_best = {}
    for comp in SUPERCUP_IMPORTANZA:
        t = winners[comp]
        if t not in team_best:
            team_best[t] = comp

    slot_team, participants, vacant = {}, set(), []
    for comp in SUPERCUP_IMPORTANZA:
        t = winners[comp]
        if team_best[t] == comp:
            slot_team[comp] = t
            participants.add(t)
        else:
            vacant.append(comp)  # slot da riempire con un sostituto

    if vacant:
        df_r, df_max = _calcola_ranking_stagione(
            stagione, _cumulato_tiebreak_map(stagione), consenti_parziale=True
        )
        if df_r is None:
            raise HTTPException(409, "Ranking stagionale parziale non calcolabile (4 coppe complete?).")
        df_sorted = estrattore.aggiungi_posizione_e_percentuale(df_r, df_max)
        ordine_rank = df_sorted.sort_values("POSIZIONE")["SQUADRA"].tolist()
        subs = [t for t in ordine_rank if t not in participants]
        for comp in vacant:
            if not subs:
                raise HTTPException(409, "Squadre sostitute insufficienti.")
            s = subs.pop(0)
            slot_team[comp] = s
            participants.add(s)

    return [
        _riga_supercup("Semifinale SuperCup", slot_team["GL"], slot_team["GC"], 0),  # SF1
        _riga_supercup("Semifinale SuperCup", slot_team["KL"], slot_team["CC"], 1),  # SF2
    ]


def _genera_supercup_finale(df) -> list:
    w = _winners_single_by_ordine(df, "Semifinale SuperCup")
    a, b = w.get(0), w.get(1)
    if a is None or b is None:
        raise HTTPException(409, "Semifinali SuperCup incomplete (le parità richiedono i rigori).")
    return [_riga_supercup("Finale SuperCup", a, b, 0)]


@app.get("/api/genera/supercup-stato")
def get_supercup_stato(stagione: int):
    df = leggi_partite(stagione)
    prev_ok = _supercup_pronta(df)

    rounds = []
    prossimo = prossimo_label = prossimo_hint = None
    prossimo_abilitato = False
    prev_completo = prev_ok
    for key, label, giornate in SUPERCUP_STEPS:
        st = _giornate_state(df, giornate)
        rounds.append({"key": key, "label": label, **st})
        if prossimo is None and not st["esiste"]:
            prossimo, prossimo_label = key, label
            prossimo_abilitato = prev_completo
            if not prev_completo and key == "semifinali":
                prossimo_hint = "Servono le finali giocate di League, Cup, Kings e Champions."
        prev_completo = st["completo"]

    done_message = None
    if prossimo is None:
        done_message = "Intergalactic SuperCup completa."
    return {
        "stagione": stagione,
        "prev_disponibile": prev_ok,
        "rounds": rounds,
        "prossimo": prossimo,
        "prossimo_label": prossimo_label,
        "prossimo_abilitato": prossimo_abilitato,
        "prossimo_hint": prossimo_hint,
        "done_message": done_message,
    }


@app.post("/api/genera/supercup-round")
def genera_supercup_round(req: GeneraLeagueRequest):
    presenti = stagioni_presenti()
    stagione = req.stagione if req.stagione is not None else (max(presenti) if presenti else 0)
    df = leggi_partite(stagione)

    next_key = next_label = next_giornate = None
    prev_completo, prev_label = _supercup_pronta(df), "finali delle 4 coppe principali"
    for key, label, giornate in SUPERCUP_STEPS:
        st = _giornate_state(df, giornate)
        if not st["esiste"]:
            next_key, next_label, next_giornate = key, label, giornate
            break
        prev_completo, prev_label = st["completo"], label
    if next_key is None:
        raise HTTPException(409, "La Intergalactic SuperCup è già completa (Finale generata).")
    if not prev_completo:
        if next_key == "semifinali":
            raise HTTPException(409, "Servono le finali giocate di League, Cup, Kings e Champions.")
        raise HTTPException(409, f"Completa i risultati del turno precedente ({prev_label}) prima di generare {next_label}.")

    rng = random.Random(req.seed)
    righe = _genera_supercup_semifinali(stagione, df, rng) if next_key == "semifinali" else _genera_supercup_finale(df)
    inserite = sostituisci_partite_competizione(righe, stagione, "intergalactic supercup", next_giornate)
    return {"stagione": stagione, "round": next_key, "label": next_label, "partite_inserite": inserite}


# ── Cup of 10 ───────────────────────────────────────────────────────────────
# Seeding dal ranking STAGIONALE completo (1°-10°). Richiede la stagione finita
# (tutte e 5 le competizioni principali, SuperCup inclusa).
# Ottavi: A=7v10, B=8v9 (casa al meglio classificato).
# Quarti: C=1 vs vinc(B), D=4v5, E=2 vs vinc(A), F=3v6 (casa al meglio classificato).
# Semifinali: G=C-D, H=E-F (neutro). Finale: G-H (neutro).
CUP10_STEPS = [
    ("ottavi",     "Ottavi (preliminare)", ["Ottavi Cup of 10"]),
    ("quarti",     "Quarti",               ["Quarti Cup of 10"]),
    ("semifinali", "Semifinali",           ["Semifinale Cup of 10"]),
    ("finale",     "Finale",               ["Finale Cup of 10"]),
]


def _riga_cup10(giornata: str, casa: str, trasf: str, ordine: int, neutro: bool) -> dict:
    return {
        "giornata": giornata, "squadra_casa": casa, "risultato": "",
        "squadra_trasferta": trasf, "tipo": "Cup of 10", "ordine": ordine,
        "Competizione": "cup of 10", "campo": "Neutro" if neutro else casa,
    }


def _seasonal_ranking_order(stagione: int):
    """Squadre ordinate per ranking STAGIONALE completo (pos. 1 → 36), o None se
    la stagione non è completa (mancano competizioni)."""
    df_r, df_max = _calcola_ranking_stagione(stagione, _cumulato_tiebreak_map(stagione))
    if df_r is None:
        return None
    df_sorted = estrattore.aggiungi_posizione_e_percentuale(df_r, df_max).sort_values("POSIZIONE")
    return df_sorted["SQUADRA"].tolist()


def _genera_cup10_ottavi(stagione: int) -> list:
    order = _seasonal_ranking_order(stagione)
    if order is None or len(order) < 10:
        raise HTTPException(409, "Serve il ranking stagionale completo (tutte le competizioni della stagione).")
    p = lambda n: order[n - 1]  # noqa: E731  (1-based → squadra)
    return [
        _riga_cup10("Ottavi Cup of 10", p(7), p(10), 0, neutro=False),  # A: 7 vs 10
        _riga_cup10("Ottavi Cup of 10", p(8), p(9), 1, neutro=False),   # B: 8 vs 9
    ]


def _genera_cup10_quarti(stagione: int, df) -> list:
    order = _seasonal_ranking_order(stagione)
    if order is None or len(order) < 10:
        raise HTTPException(409, "Serve il ranking stagionale completo.")
    p = lambda n: order[n - 1]  # noqa: E731
    w = _winners_single_by_ordine(df, "Ottavi Cup of 10")
    wA, wB = w.get(0), w.get(1)
    if wA is None or wB is None:
        raise HTTPException(409, "Risultati degli Ottavi Cup of 10 incompleti (parità → rigori).")
    return [
        _riga_cup10("Quarti Cup of 10", p(1), wB,   0, neutro=False),  # C: 1 vs vinc(B)
        _riga_cup10("Quarti Cup of 10", p(4), p(5), 1, neutro=False),  # D: 4 vs 5
        _riga_cup10("Quarti Cup of 10", p(2), wA,   2, neutro=False),  # E: 2 vs vinc(A)
        _riga_cup10("Quarti Cup of 10", p(3), p(6), 3, neutro=False),  # F: 3 vs 6
    ]


def _genera_cup10_round(round_key: str, df) -> list:
    if round_key == "semifinali":
        prev, giornata, pairs = "Quarti Cup of 10", "Semifinale Cup of 10", [(0, 1), (2, 3)]
    else:  # finale
        prev, giornata, pairs = "Semifinale Cup of 10", "Finale Cup of 10", [(0, 1)]
    w = _winners_single_by_ordine(df, prev)
    rows = []
    for ordine, (i, j) in enumerate(pairs):
        a, b = w.get(i), w.get(j)
        if a is None or b is None:
            raise HTTPException(409, f"'{prev}': risultati incompleti (le parità richiedono i rigori).")
        rows.append(_riga_cup10(giornata, a, b, ordine, neutro=True))
    return rows


@app.get("/api/genera/cup10-stato")
def get_cup10_stato(stagione: int):
    df = leggi_partite(stagione)
    prev_ok = _seasonal_ranking_order(stagione) is not None

    rounds = []
    prossimo = prossimo_label = prossimo_hint = None
    prossimo_abilitato = False
    prev_completo = prev_ok
    for key, label, giornate in CUP10_STEPS:
        st = _giornate_state(df, giornate)
        rounds.append({"key": key, "label": label, **st})
        if prossimo is None and not st["esiste"]:
            prossimo, prossimo_label = key, label
            prossimo_abilitato = prev_completo
            if not prev_completo and key == "ottavi":
                prossimo_hint = "Serve la stagione completa (League, Cup, Kings, Champions, SuperCup)."
        prev_completo = st["completo"]

    done_message = None
    if prossimo is None:
        done_message = "Cup of 10 completa. La stagione è interamente generata! 🎉"
    return {
        "stagione": stagione,
        "prev_disponibile": prev_ok,
        "rounds": rounds,
        "prossimo": prossimo,
        "prossimo_label": prossimo_label,
        "prossimo_abilitato": prossimo_abilitato,
        "prossimo_hint": prossimo_hint,
        "done_message": done_message,
    }


@app.post("/api/genera/cup10-round")
def genera_cup10_round(req: GeneraLeagueRequest):
    presenti = stagioni_presenti()
    stagione = req.stagione if req.stagione is not None else (max(presenti) if presenti else 0)
    df = leggi_partite(stagione)

    next_key = next_label = next_giornate = None
    prev_completo, prev_label = _seasonal_ranking_order(stagione) is not None, "stagione completa"
    for key, label, giornate in CUP10_STEPS:
        st = _giornate_state(df, giornate)
        if not st["esiste"]:
            next_key, next_label, next_giornate = key, label, giornate
            break
        prev_completo, prev_label = st["completo"], label
    if next_key is None:
        raise HTTPException(409, "La Cup of 10 è già completa (Finale generata).")
    if not prev_completo:
        if next_key == "ottavi":
            raise HTTPException(409, "Serve la stagione completa (League, Cup, Kings, Champions, SuperCup).")
        raise HTTPException(409, f"Completa i risultati del turno precedente ({prev_label}) prima di generare {next_label}.")

    if next_key == "ottavi":
        righe = _genera_cup10_ottavi(stagione)
    elif next_key == "quarti":
        righe = _genera_cup10_quarti(stagione, df)
    else:  # semifinali / finale
        righe = _genera_cup10_round(next_key, df)
    inserite = sostituisci_partite_competizione(righe, stagione, "cup of 10", next_giornate)
    return {"stagione": stagione, "round": next_key, "label": next_label, "partite_inserite": inserite}


@app.get("/api/galactic-league/classifica")
def get_classifica_league(stagione: int):
    """
    Classifica League Phase (Giornate 1-8) della Galactic League per una stagione.
    Restituisce: Posizione, SQUADRA, W, D, L, PT, GF, GS, DIFF.
    """
    df = leggi_partite(stagione)
    if df.empty:
        return {"stagione": stagione, "classifica": []}
    df_cl = estrattore.costruisci_classifica_galactic_league(df)
    return {"stagione": stagione, "classifica": _df_to_records(df_cl)}


@app.get("/api/kings-league/classifica")
def get_classifica_kings_league(stagione: int):
    """
    Classifiche dei gironi Kings League (Lega A/B/C) per una stagione, con un
    campo 'colore' per ogni squadra che codifica l'esito
    (promozione/retrocessione/playout):
      verde · verde_chiaro · giallo · arancione · neutro.
    """
    df = leggi_partite(stagione)
    if df.empty:
        return {"stagione": stagione, "classifica": []}
    df_cl = estrattore.costruisci_classifica_kings_league(df)
    if df_cl is None or len(df_cl) == 0:
        return {"stagione": stagione, "classifica": []}
    colori = estrattore.costruisci_esiti_kings_league(df, df_cl)
    records = _df_to_records(df_cl)
    for r in records:
        r["colore"] = colori.get(r["SQUADRA"], "neutro")
    return {"stagione": stagione, "classifica": records}


@app.get("/api/champions-cup/classifica")
def get_classifica_champions_cup(stagione: int, fase: int = 1):
    """
    Classifiche dei gironi della Galactic Champions Cup per stagione e fase,
    con un campo 'colore' per ogni squadra.

    Fase 1 (6 gironi da 6): le migliori 4 passano alla Fase 2, le ultime 2 sono
    eliminate. Colori:
      1ª            → verde       (fascia 1 nel sorteggio della Fase 2)
      2ª-4ª         → neutro      (qualificate alla Fase 2)
      ultime 2      → arancione   (eliminate)

    Fase 2 (6 gironi da 4, gara secca):
      1ª            → verde
      2ª            → verde_chiaro
      3ª            → verde_chiaro se tra le 4 migliori terze, altrimenti arancione
      4ª            → arancione
    """
    df = leggi_partite(stagione)
    if df.empty:
        return {"stagione": stagione, "fase": fase, "classifica": []}
    df_cl = estrattore.costruisci_classifica_galactic_champions_cup(df, fase=fase)
    if df_cl is None or len(df_cl) == 0:
        return {"stagione": stagione, "fase": fase, "classifica": []}
    records = _df_to_records(df_cl)
    # Dimensione di ogni girone, per individuare le ultime 2 posizioni (Fase 1).
    size = {}
    for r in records:
        size[r["Girone"]] = max(size.get(r["Girone"], 0), r["Posizione"])
    # 4 migliori terze (Fase 2): stessa logica usata dal ranking.
    top_terze = set()
    if fase == 2:
        df_terze = estrattore.costruisci_classifica_migliori_terze_champions_cup(
            df, _cumulato_tiebreak_map(stagione)
        )
        if df_terze is not None and len(df_terze) > 0:
            top_terze = set(df_terze.head(4)["SQUADRA"])
    for r in records:
        pos, n = r["Posizione"], size[r["Girone"]]
        if fase == 1:
            r["colore"] = "verde" if pos == 1 else ("arancione" if pos >= n - 1 else "neutro")
        elif fase == 2:
            if pos == 1:
                r["colore"] = "verde"
            elif pos == 2:
                r["colore"] = "verde_chiaro"
            elif pos == 3:
                r["colore"] = "verde_chiaro" if r["SQUADRA"] in top_terze else "arancione"
            else:
                r["colore"] = "arancione"
        else:
            r["colore"] = "neutro"
    return {"stagione": stagione, "fase": fase, "classifica": records}


def _calcola_raggiungimenti(competizione: str, stages: dict,
                            finale_giornata: str, sort_keys: list,
                            filter_key: str) -> list:
    """
    Statistiche cumulate (su TUTTE le stagioni) di una competizione a
    eliminazione: per ogni squadra conta quante volte ha raggiunto ciascuno
    `stage` (= ha disputato almeno una partita di quel turno) e quante volte
    ha vinto il titolo (vincitrice di `finale_giornata`).

    - stages: dict {chiave_stage: [label giornata, ...]}
    - sort_keys: ordine di ordinamento (desc) prima del nome
    - filter_key: include solo le squadre con quello stage > 0
    """
    keys = list(stages.keys())
    stats: dict[str, dict] = {}

    def ensure(team: str) -> dict:
        if team not in stats:
            stats[team] = {"SQUADRA": team, "vittorie": 0, **{k: 0 for k in keys}}
        return stats[team]

    for s in stagioni_presenti():
        df = leggi_partite(s)
        if df.empty:
            continue
        comp = df[df["Competizione"] == competizione]
        if comp.empty:
            continue
        for stage, giornate in stages.items():
            sub = comp[comp["giornata"].isin(giornate)]
            teams = set(sub["squadra_casa"]) | set(sub["squadra_trasferta"])
            for t in teams:
                if t is None or (isinstance(t, float) and pd.isna(t)):
                    continue
                ensure(t)[stage] += 1
        finale = comp[comp["giornata"] == finale_giornata]
        if len(finale) > 0:
            w = _winner_of_match(finale.iloc[0])
            if w:
                ensure(w)["vittorie"] += 1

    risultato = [v for v in stats.values() if v.get(filter_key, 0) > 0]
    risultato.sort(key=lambda r: tuple(-r[k] for k in sort_keys) + (r["SQUADRA"],))
    return risultato


@app.get("/api/galactic-league/raggiungimenti")
def get_raggiungimenti_league():
    """
    Fase a eliminazione Galactic League, cumulato su tutte le stagioni.
    Solo squadre arrivate almeno una volta agli Ottavi.
    """
    stages = {
        "ottavi":     ["Ottavi League - Andata", "Ottavi League - Ritorno"],
        "quarti":     ["Quarti League - Andata", "Quarti League - Ritorno"],
        "semifinali": ["Semifinale League - Andata", "Semifinale League - Ritorno"],
        "finali":     ["Finale League"],
    }
    risultato = _calcola_raggiungimenti(
        "galactic league", stages, "Finale League",
        ["vittorie", "finali", "semifinali", "quarti", "ottavi"], "ottavi",
    )
    return {"raggiungimenti": risultato}


@app.get("/api/galactic-league/raggiungimenti-posizione")
def get_raggiungimenti_posizione_league():
    """
    Per ogni posizione della fase a gironi (League Phase, 1..24) della Galactic
    League, quante volte — cumulato su tutte le stagioni — la squadra che
    occupava quella posizione ha raggiunto ciascuna fase a eliminazione
    (ottavi, quarti, semifinali, finali) e quante volte ha vinto il titolo.
    """
    stages = {
        "ottavi":     ["Ottavi League - Andata", "Ottavi League - Ritorno"],
        "quarti":     ["Quarti League - Andata", "Quarti League - Ritorno"],
        "semifinali": ["Semifinale League - Andata", "Semifinale League - Ritorno"],
        "finali":     ["Finale League"],
    }
    keys = list(stages.keys())
    MAX_POS = 24
    per_pos = {
        p: {"posizione": p, "vittorie": 0, **{k: 0 for k in keys}}
        for p in range(1, MAX_POS + 1)
    }

    for s in stagioni_presenti():
        df = leggi_partite(s)
        if df.empty:
            continue
        comp = df[df["Competizione"] == "galactic league"]
        if comp.empty:
            continue
        # Mappa squadra → posizione nella League Phase di questa stagione.
        df_cl = estrattore.costruisci_classifica_galactic_league(df)
        pos_of = {}
        if df_cl is not None and len(df_cl) > 0:
            for _, cr in df_cl.iterrows():
                pos_of[cr["SQUADRA"]] = int(cr["Posizione"])
        # Per ogni fase, le squadre che vi hanno disputato almeno una partita.
        for stage, giornate in stages.items():
            sub = comp[comp["giornata"].isin(giornate)]
            teams = set(sub["squadra_casa"]) | set(sub["squadra_trasferta"])
            for t in teams:
                if t is None or (isinstance(t, float) and pd.isna(t)):
                    continue
                p = pos_of.get(t)
                if p in per_pos:
                    per_pos[p][stage] += 1
        # Vincitrice della finale.
        finale = comp[comp["giornata"] == "Finale League"]
        if len(finale) > 0:
            w = _winner_of_match(finale.iloc[0])
            p = pos_of.get(w) if w else None
            if p in per_pos:
                per_pos[p]["vittorie"] += 1

    return {"raggiungimenti": [per_pos[p] for p in range(1, MAX_POS + 1)]}


@app.get("/api/galactic-cup/raggiungimenti")
def get_raggiungimenti_cup():
    """
    Fase a eliminazione Galactic Cup, cumulato su tutte le stagioni.
    Mappatura turni → step: Turno 2 = Sedicesimi (32 squadre), Ottavi di Finale
    = Ottavi (16), Quarti/Semifinale (andata-ritorno), Finale Cup.
    Il Turno 1 è preliminare e non è uno step con nome.
    Solo squadre arrivate almeno una volta ai Sedicesimi.
    """
    stages = {
        "sedicesimi": ["Turno 2"],
        "ottavi":     ["Ottavi di Finale"],
        "quarti":     ["Quarti di Finale - Andata", "Quarti di Finale - Ritorno"],
        "semifinali": ["Semifinale - Andata", "Semifinale - Ritorno"],
        "finali":     ["Finale Cup"],
    }
    risultato = _calcola_raggiungimenti(
        "galactic cup", stages, "Finale Cup",
        ["vittorie", "finali", "semifinali", "quarti", "ottavi", "sedicesimi"],
        "sedicesimi",
    )
    return {"raggiungimenti": risultato}


@app.get("/api/champions-cup/raggiungimenti")
def get_raggiungimenti_champions_cup():
    """
    Fase a eliminazione (Fase 3) della Galactic Champions Cup, cumulato su tutte
    le stagioni. Tutte gare secche: Ottavi → Quarti → Semifinale → Finale.
    Solo squadre arrivate almeno una volta agli ottavi.
    """
    stages = {
        "ottavi":     ["Fase 3 - Ottavi di Finale"],
        "quarti":     ["Fase 3 - Quarti di Finale"],
        "semifinali": ["Fase 3 - Semifinale"],
        "finali":     ["Fase 3 - Finale"],
    }
    risultato = _calcola_raggiungimenti(
        "galactic champions cup", stages, "Fase 3 - Finale",
        ["vittorie", "finali", "semifinali", "quarti", "ottavi"], "ottavi",
    )
    return {"raggiungimenti": risultato}


@app.get("/api/partite/conteggi")
def conteggi_partite(stagione: int):
    """
    Conteggio partite + vincitrice (se identificabile) per ogni Competizione
    di una stagione. Usato per popolare le card della vista 'Competizioni'.
    """
    df = leggi_partite(stagione)
    if df.empty:
        return {"stagione": stagione, "conteggi": {}}

    conteggi = {}
    for comp, group in df.groupby("Competizione"):
        vincitrice = None
        finale_giornata = COMPETIZIONE_FINALI.get(comp)
        if finale_giornata:
            finale_rows = group[group["giornata"] == finale_giornata]
            if len(finale_rows) > 0:
                vincitrice = _winner_of_match(finale_rows.iloc[0])
        conteggi[str(comp)] = {
            "partite": int(len(group)),
            "vincitrice": vincitrice,
        }
    return {"stagione": stagione, "conteggi": conteggi}


@app.get("/api/partite")
def get_partite(stagione: int, competizione: Optional[str] = None):
    """
    Lista partite di una stagione, opzionalmente filtrata per Competizione.
    """
    df = leggi_partite(stagione)
    if competizione:
        df = df[df["Competizione"] == competizione]
    if df.empty:
        return {"stagione": stagione, "competizione": competizione, "partite": []}

    # Pandas può avere NaN/NaT/numpy types — convertiamo in tipi Python puliti
    records = df.to_dict("records")
    cleaned = []
    for r in records:
        row = {}
        for k, v in r.items():
            if v is None or (isinstance(v, float) and math.isnan(v)) or pd.isna(v):
                row[k] = None
            else:
                row[k] = v
        cleaned.append(row)
    return {"stagione": stagione, "competizione": competizione, "partite": cleaned}


def _df_to_records(df: pd.DataFrame) -> list:
    """Converte un DataFrame in lista di dict puliti per JSON (NaN → None)."""
    out = []
    for r in df.to_dict("records"):
        row = {}
        for k, v in r.items():
            if v is None or (isinstance(v, float) and math.isnan(v)) or pd.isna(v):
                row[k] = None
            else:
                row[k] = v
        out.append(row)
    return out


def _calcola_ranking_stagione(stagione: int, thirds_tiebreak: Optional[dict] = None,
                              consenti_parziale: bool = False):
    """
    Calcola il ranking completo di una singola stagione.
    Restituisce (df_ranking, df_ranking_max) oppure (None, None) se la
    stagione non è caricata.

    `thirds_tiebreak`: mappa {SQUADRA: ranking_cumulato} usata come ultimo
    spareggio per le "migliori terze" della Champions Cup. Se None (default,
    es. quando chiamata dal calcolo del cumulato stesso) si usa la logica base
    senza il tiebreak cumulato → nessuna ricorsione.
    """
    df_partite = leggi_partite(stagione)
    if df_partite.empty:
        return None, None

    # Una stagione produce un ranking stagionale SOLO se contiene tutte le 5
    # competizioni che vi concorrono. Le stagioni parziali (es. generate dalla
    # sezione "Genera Stagione" ma non ancora complete) non hanno un ranking
    # stagionale: ritorniamo (None, None) e tutti i chiamati le saltano.
    # (Cup of 8/10 non concorre al ranking, quindi non è richiesta.)
    # `consenti_parziale=True` salta questa guardia: usato per il ranking
    # parziale al termine delle 4 coppe (SuperCup esclusa) per la SuperCup.
    if not consenti_parziale:
        COMP_RICHIESTE_RANKING = {
            "galactic league", "galactic cup", "Kings League",
            "galactic champions cup", "intergalactic supercup",
        }
        comp_presenti = set(df_partite["Competizione"].dropna().unique())
        if not COMP_RICHIESTE_RANKING.issubset(comp_presenti):
            return None, None

    df_class_league = estrattore.costruisci_classifica_galactic_league(df_partite)
    df_r_league    = estrattore.costruisci_ranking_galactic_league(df_partite, df_class_league)
    df_r_cup       = estrattore.costruisci_ranking_galactic_cup(df_partite, df_class_league)
    df_r_kings     = estrattore.costruisci_ranking_kings_league(df_partite, df_class_league)
    df_r_champions = estrattore.costruisci_ranking_galactic_champions_cup(df_partite, df_class_league, thirds_tiebreak)
    df_r_supercup  = estrattore.costruisci_ranking_intergalactic_supercup(df_partite, df_class_league)

    df_ranking = (df_r_league
                  .merge(df_r_cup,       on="SQUADRA")
                  .merge(df_r_kings,     on="SQUADRA")
                  .merge(df_r_champions, on="SQUADRA")
                  .merge(df_r_supercup,  on="SQUADRA"))
    df_ranking = estrattore.aggiungi_totale_ranking(df_ranking)

    df_ranking_max = estrattore.aggiungi_totale_ranking(
        estrattore.costruisci_ranking_max(df_partite)
    )
    return df_ranking, df_ranking_max


def _cumulato_tiebreak_map(stagione: int) -> dict:
    """
    Mappa {SQUADRA: ranking_cumulato} fino alla stagione PRECEDENTE, usata come
    ultimo spareggio per le migliori terze della Champions Cup.
    Vuota per la stagione 1 (nessuna stagione precedente). Il cumulato è
    calcolato in modalità "base" (le sue chiamate interne a
    _calcola_ranking_stagione non applicano questo tiebreak) → niente ricorsione.
    """
    if stagione <= 1:
        return {}
    try:
        cum = get_ranking_cumulato(stagione - 1)
        return {r["SQUADRA"]: r.get("TOTALE", 0.0) for r in cum.get("ranking", [])}
    except Exception:
        return {}


@app.get("/api/ranking")
def get_ranking(stagione: int):
    """
    Ranking stagionale completo: 36 squadre con punteggio per competizione,
    totale, posizione (1..36) e percentuale rispetto al massimo teorico.
    """
    df_ranking, df_ranking_max = _calcola_ranking_stagione(
        stagione, _cumulato_tiebreak_map(stagione)
    )
    if df_ranking is None:
        return {"stagione": stagione, "ranking": [], "max": None}

    df_ranking = estrattore.aggiungi_posizione_e_percentuale(df_ranking, df_ranking_max)
    return {
        "stagione": stagione,
        "ranking": _df_to_records(df_ranking),
        "max":     _df_to_records(df_ranking_max)[0] if not df_ranking_max.empty else None,
    }


# Pesi per il ranking cumulato: stagione corrente fino a 4 stagioni precedenti
PESI_CUMULATO = [1.0, 0.9, 0.8, 0.7, 0.6]


@app.get("/api/ranking/cumulato")
def get_ranking_cumulato(stagione: int):
    """
    Ranking cumulato pesato sulle ultime 5 stagioni (corrente + 4 precedenti).
    Pesi: corrente × 1.0, precedente × 0.9, ..., 4-anni-fa × 0.6.
    Disponibile da stagione 2 in poi (in S1 ha un solo addendo).
    """
    if stagione < 1:
        raise HTTPException(400, "stagione deve essere >= 1")

    # Stagioni effettivamente da considerare (non sotto la 1)
    stagioni_incluse = []  # lista di (stagione_n, peso)
    for i, peso in enumerate(PESI_CUMULATO):
        s = stagione - i
        if s >= 1:
            stagioni_incluse.append((s, peso))
    # ordine: dalla più vecchia alla corrente (utile per la UI)
    stagioni_incluse.reverse()

    # Carica ranking di ogni stagione (solo TOTALE per squadra)
    per_squadra: dict[str, dict[str, float]] = {}  # team -> {f"S{n}": totale}
    pesi_per_stagione: dict[int, float] = {s: p for s, p in stagioni_incluse}
    stagioni_caricate = []

    for s, _peso in stagioni_incluse:
        df_r, _ = _calcola_ranking_stagione(s)
        if df_r is None:
            continue  # stagione non in DB
        stagioni_caricate.append(s)
        for _, row in df_r.iterrows():
            team = row["SQUADRA"]
            tot  = float(row["TOTALE"])
            per_squadra.setdefault(team, {})[f"S{s}"] = round(tot, 2)

    # Calcola il totale pesato per squadra
    risultato = []
    for team, dati in per_squadra.items():
        totale = 0.0
        for s in stagioni_caricate:
            totale += dati.get(f"S{s}", 0.0) * pesi_per_stagione[s]
        risultato.append({
            "SQUADRA": team,
            **{f"S{s}": dati.get(f"S{s}", 0.0) for s in stagioni_caricate},
            "TOTALE": round(totale, 2),
        })

    # Ordina per TOTALE desc.
    # Tie-break (anche a parità di valore arrotondato): punteggio della
    # stagione più recente desc, poi precedente, e così via.
    # Tie-break finale: nome alfabetico per stabilità.
    stagioni_dal_recente = list(reversed(stagioni_caricate))

    def sort_key(r):
        key = [-r["TOTALE"]]
        for s in stagioni_dal_recente:
            v = r.get(f"S{s}", 0)
            key.append(-float(v) if isinstance(v, (int, float)) else 0)
        key.append(r["SQUADRA"])
        return tuple(key)

    risultato.sort(key=sort_key)
    for i, r in enumerate(risultato, start=1):
        r["POSIZIONE"] = i

    return {
        "stagione": stagione,
        "stagioni_incluse": [
            {"stagione": s, "peso": pesi_per_stagione[s]} for s in stagioni_caricate
        ],
        "ranking": risultato,
    }


@app.get("/api/squadre/stats")
def get_squadre_stats(stagione: int):
    """
    Per ogni squadra (36 canoniche), statistiche aggregate della stagione su
    TUTTE le competizioni: V/P/S, gol fatti/subiti, punteggio ranking.
    I match decisi ai rigori contano come pareggio per V/P/S.
    Ordine: alfabetico per squadra.
    """
    df = leggi_partite(stagione)
    stats: dict[str, dict] = {
        sq: {"SQUADRA": sq, "V": 0, "P": 0, "S": 0, "GF": 0, "GS": 0, "PTS": 0.0}
        for sq in sorted(estrattore.SQUADRE_CANONICHE)
    }

    if not df.empty:
        for _, row in df.iterrows():
            ris = str(row["risultato"]).strip()
            m = re.match(r"^(\d+)-(\d+)", ris)
            if not m:
                continue
            gc, gt = int(m.group(1)), int(m.group(2))
            casa = row["squadra_casa"]
            trasf = row["squadra_trasferta"]

            if casa in stats:
                stats[casa]["GF"] += gc
                stats[casa]["GS"] += gt
            if trasf in stats:
                stats[trasf]["GF"] += gt
                stats[trasf]["GS"] += gc

            if gc > gt:
                if casa in stats:  stats[casa]["V"]  += 1
                if trasf in stats: stats[trasf]["S"] += 1
            elif gc < gt:
                if casa in stats:  stats[casa]["S"]  += 1
                if trasf in stats: stats[trasf]["V"] += 1
            else:
                if casa in stats:  stats[casa]["P"]  += 1
                if trasf in stats: stats[trasf]["P"] += 1

    # Punteggio ranking stagionale
    df_r, _ = _calcola_ranking_stagione(stagione)
    if df_r is not None:
        for _, row in df_r.iterrows():
            sq = row["SQUADRA"]
            if sq in stats:
                stats[sq]["PTS"] = round(float(row["TOTALE"]), 2)

    squadre = list(stats.values())
    return {"stagione": stagione, "squadre": squadre}


def _vincitori_competizioni(stagione: int) -> dict:
    """Per ogni competizione di una stagione, ritorna il vincitore (se identificabile)."""
    df = leggi_partite(stagione)
    out = {}
    if df.empty:
        return out
    for comp, group in df.groupby("Competizione"):
        finale_giornata = COMPETIZIONE_FINALI.get(comp)
        if not finale_giornata:
            continue
        finale_rows = group[group["giornata"] == finale_giornata]
        if len(finale_rows) > 0:
            out[str(comp)] = _winner_of_match(finale_rows.iloc[0])
    return out


def _vps_squadra_stagione(stagione: int, squadra: str) -> dict:
    """V/P/S per una squadra in una stagione (rigori → pareggio)."""
    df = leggi_partite(stagione)
    out = {"V": 0, "P": 0, "S": 0}
    if df.empty:
        return out
    for _, row in df.iterrows():
        casa = row["squadra_casa"]
        trasf = row["squadra_trasferta"]
        if casa != squadra and trasf != squadra:
            continue
        ris = str(row["risultato"]).strip()
        m = re.match(r"^(\d+)-(\d+)", ris)
        if not m:
            continue
        gc, gt = int(m.group(1)), int(m.group(2))
        is_home = casa == squadra
        if gc == gt:
            out["P"] += 1
        elif (gc > gt) == is_home:
            out["V"] += 1
        else:
            out["S"] += 1
    return out


def _comp_key_trofeo(comp: str) -> str:
    """Normalizza 'cup of 8' / 'cup of 10' → 'cup' per il conteggio trofei."""
    return "cup" if comp in ("cup of 8", "cup of 10") else comp


# Punti "Star Points" per ogni trofeo/medaglia
STAR_POINTS_TROFEI = {
    "galactic league":          5.00,
    "galactic cup":             2.50,
    "Kings League":             2.00,
    "galactic champions cup":   3.75,
    "intergalactic supercup":   0.75,
    "cup":                      1.25,
}
STAR_POINTS_MEDAGLIE = {
    "oro":     0.25,
    "argento": 0.10,
    "bronzo":  0.05,
}


def _calcola_star_points(trofei: dict, medaglie: dict) -> float:
    tot = 0.0
    for k, n in trofei.items():
        tot += n * STAR_POINTS_TROFEI.get(k, 0.0)
    for k, n in medaglie.items():
        tot += n * STAR_POINTS_MEDAGLIE.get(k, 0.0)
    return round(tot, 2)


@app.get("/api/cumulato/squadre")
def get_cumulato_squadre(stagione_max: Optional[int] = None):
    """
    Statistiche cumulate per ogni squadra calcolate sulle stagioni <= stagione_max:
    - trofei vinti per competizione
    - medaglie: numero di volte 1°/2°/3° nel ranking stagionale
    - cumulato_attuale: punteggio ranking cumulato calcolato a stagione_max
    Se stagione_max è omesso, usa la stagione più recente caricata.
    """
    stagioni_all = stagioni_presenti()
    stats = {
        sq: {
            "SQUADRA": sq,
            "trofei": {
                "galactic league": 0,
                "galactic cup": 0,
                "Kings League": 0,
                "galactic champions cup": 0,
                "intergalactic supercup": 0,
                "cup": 0,
            },
            "medaglie": {"oro": 0, "argento": 0, "bronzo": 0},
            "totale_trofei": 0,
            "cumulato_attuale": 0.0,
            "posizione_cumulato": None,
            "star_points": 0.0,
        }
        for sq in sorted(estrattore.SQUADRE_CANONICHE)
    }

    if not stagioni_all:
        return {"stagioni": [], "stagione_corrente": None, "squadre": list(stats.values())}

    if stagione_max is None or stagione_max > max(stagioni_all):
        stagione_max = max(stagioni_all)

    stagioni = [s for s in stagioni_all if s <= stagione_max]

    for s in stagioni:
        # Trofei: vincitori delle 6 competizioni
        for comp, winner in _vincitori_competizioni(s).items():
            if winner and winner in stats:
                k = _comp_key_trofeo(comp)
                if k in stats[winner]["trofei"]:
                    stats[winner]["trofei"][k] += 1

        # Medaglie: top 3 del ranking stagionale
        df_r, df_max = _calcola_ranking_stagione(s)
        if df_r is not None:
            df_sorted = estrattore.aggiungi_posizione_e_percentuale(df_r, df_max)
            for _, row in df_sorted.iterrows():
                pos = int(row["POSIZIONE"])
                sq = row["SQUADRA"]
                if sq not in stats:
                    continue
                if pos == 1:
                    stats[sq]["medaglie"]["oro"] += 1
                elif pos == 2:
                    stats[sq]["medaglie"]["argento"] += 1
                elif pos == 3:
                    stats[sq]["medaglie"]["bronzo"] += 1

    # Totale trofei (somma delle 6 competizioni) e Star Points
    for sq in stats:
        stats[sq]["totale_trofei"] = sum(stats[sq]["trofei"].values())
        stats[sq]["star_points"] = _calcola_star_points(
            stats[sq]["trofei"], stats[sq]["medaglie"]
        )

    # Cumulato attuale = cumulato calcolato a stagione_max
    last_s = stagione_max
    cum = get_ranking_cumulato(last_s)
    for r in cum.get("ranking", []):
        sq = r["SQUADRA"]
        if sq in stats:
            stats[sq]["cumulato_attuale"] = r["TOTALE"]
            stats[sq]["posizione_cumulato"] = r.get("POSIZIONE")

    return {
        "stagioni": stagioni_all,
        "stagione_corrente": last_s,
        "squadre": list(stats.values()),
    }


@app.get("/api/cumulato/squadra/{nome}")
def get_cumulato_squadra(nome: str):
    """
    Drill-down di una squadra: per ogni stagione caricata restituisce
    V/P/S, punteggio ranking, posizione ranking, numero di titoli vinti.
    """
    if nome not in estrattore.SQUADRE_CANONICHE:
        raise HTTPException(404, f"Squadra '{nome}' non riconosciuta")

    stagioni = stagioni_presenti()
    rows = []
    for s in stagioni:
        vps = _vps_squadra_stagione(s, nome)

        pts = None
        pos = None
        df_r, df_max = _calcola_ranking_stagione(s)
        if df_r is not None:
            df_sorted = estrattore.aggiungi_posizione_e_percentuale(df_r, df_max)
            match = df_sorted[df_sorted["SQUADRA"] == nome]
            if len(match) > 0:
                pts = round(float(match.iloc[0]["TOTALE"]), 2)
                pos = int(match.iloc[0]["POSIZIONE"])

        vincitori = _vincitori_competizioni(s)
        titoli = [comp for comp, w in vincitori.items() if w == nome]

        rows.append({
            "stagione": s,
            "V": vps["V"],
            "P": vps["P"],
            "S": vps["S"],
            "PTS": pts,
            "POS": pos,
            "titoli": len(titoli),
            "titoli_dettaglio": titoli,
        })

    return {"squadra": nome, "stagioni": rows}


def _loser_of_match(row) -> Optional[str]:
    """Sconfitta di un singolo match (None se finisce in parità senza rigori)."""
    w = _winner_of_match(row)
    if w is None:
        return None
    if w == row["squadra_casa"]:
        return row["squadra_trasferta"]
    if w == row["squadra_trasferta"]:
        return row["squadra_casa"]
    return None


def _pos_ranking_stagionale(stagione: int, squadra: str) -> Optional[int]:
    """
    Posizione della squadra nel ranking stagionale della stessa stagione,
    usata come posizione di qualifica per i tornei a invito di fine stagione
    (Cup of 8/10).
    """
    df_r, df_max = _calcola_ranking_stagione(stagione)
    if df_r is None:
        return None
    df_sorted = estrattore.aggiungi_posizione_e_percentuale(df_r, df_max)
    match = df_sorted[df_sorted["SQUADRA"] == squadra]
    if len(match) > 0:
        return int(match.iloc[0]["POSIZIONE"])
    return None


def _flip_risultato(ris: str) -> str:
    """Inverte tutti i pair X-Y nel risultato (gestisce supplementari e rigori).
    Es. '1-2 [0-1] (3-4)' → '2-1 [1-0] (4-3)'.
    """
    return re.sub(r"(\d+)-(\d+)", lambda m: f"{m.group(2)}-{m.group(1)}", ris)


def _aggregato_vincitore(andata_row, ritorno_row) -> Optional[str]:
    """
    Vincitore di una sfida andata/ritorno calcolato sull'aggregato.
    Pareggio aggregato → decide il risultato del ritorno (rigori inclusi).
    """
    def parse(ris: str):
        m = re.match(r"^(\d+)-(\d+)", str(ris))
        return (int(m.group(1)), int(m.group(2))) if m else (None, None)

    a_gc, a_gt = parse(andata_row["risultato"])
    r_gc, r_gt = parse(ritorno_row["risultato"])
    if a_gc is None or r_gc is None:
        return None

    a_casa = andata_row["squadra_casa"]
    a_trasf = andata_row["squadra_trasferta"]
    # In ritorno i ruoli sono invertiti rispetto all'andata
    casa_agg = a_gc + r_gt
    trasf_agg = a_gt + r_gc

    if casa_agg > trasf_agg:
        return a_casa
    if casa_agg < trasf_agg:
        return a_trasf
    # Aggregato pari → decide il ritorno (anche rigori)
    return _winner_of_match(ritorno_row)


def _semifinaliste_due_legs(comp_df, andata_g: str, ritorno_g: str) -> list[str]:
    """Perdenti delle due semifinali andata/ritorno (per GL e GC)."""
    andate = comp_df[comp_df["giornata"] == andata_g]
    ritorni = comp_df[comp_df["giornata"] == ritorno_g].copy()
    used_ritorno_idx: set = set()
    perdenti: list[str] = []
    for _, andata in andate.iterrows():
        pair = {andata["squadra_casa"], andata["squadra_trasferta"]}
        for idx, ritorno in ritorni.iterrows():
            if idx in used_ritorno_idx:
                continue
            if {ritorno["squadra_casa"], ritorno["squadra_trasferta"]} == pair:
                used_ritorno_idx.add(idx)
                winner = _aggregato_vincitore(andata, ritorno)
                if winner is not None:
                    losers = list(pair - {winner})
                    if losers:
                        perdenti.append(losers[0])
                break
    return perdenti


def _semifinaliste_match_unico(comp_df, semi_g: str) -> list[str]:
    """Perdenti delle semifinali a partita secca."""
    out = []
    for _, row in comp_df[comp_df["giornata"] == semi_g].iterrows():
        loser = _loser_of_match(row)
        if loser:
            out.append(loser)
    return out


def _ranking_pre_supercup(stagione: int) -> Optional[list[str]]:
    """
    Squadre ordinate per ranking stagionale ESCLUDENDO i punti della SuperCup
    (che al momento delle sostituzioni non è ancora stata giocata).
    Tie-break: nome squadra alfabetico.
    """
    df_r, _ = _calcola_ranking_stagione(stagione)
    if df_r is None:
        return None
    df = df_r.copy()
    df["TOTALE_PRE"] = df["TOTALE"] - df["intergalactic supercup"]
    df = df.sort_values(
        by=["TOTALE_PRE", "SQUADRA"],
        ascending=[False, True],
        ignore_index=True,
    )
    return df["SQUADRA"].tolist()


def _ruoli_supercup(stagione: int) -> dict[str, str]:
    """
    Per la SuperCup di una stagione, ritorna mapping team → ruolo:
    "Vincente <Coppa>" se la squadra ha vinto una delle 4 coppe principali
    (rappresenta quella con star points più alti se ne ha vinta più di una);
    "Sostituente <Coppa>" per le squadre che riempiono gli slot lasciati
    liberi (presi dal ranking stagionale in ordine, escluse le già qualificate).
    Le coppe in ordine di star points (alta priorità prima):
      Galactic League (5.00) > Champions Cup (3.75) > Galactic Cup (2.50) > Kings League (2.00).
    """
    coppe_ordinate = [
        ("Galactic League",        "galactic league"),
        ("Galactic Champions Cup", "galactic champions cup"),
        ("Galactic Cup",           "galactic cup"),
        ("Galactic Kings League",  "Kings League"),
    ]

    vincitori = _vincitori_competizioni(stagione)

    # 1) Assegna ogni squadra alla coppa di valore più alto che ha vinto
    team_to_cup: dict[str, str] = {}     # team → nice name
    cups_filled: set[str] = set()        # comp_key delle coppe i cui slot sono già rappresentati dal vincitore stesso
    for nice, comp_key in coppe_ordinate:
        winner = vincitori.get(comp_key)
        if winner is None:
            continue
        if winner in team_to_cup:
            # già rappresenta una coppa con star points più alti
            continue
        team_to_cup[winner] = nice
        cups_filled.add(comp_key)

    # 2) Per ogni coppa il cui slot è libero (in ordine di priorità star),
    #    assegna la squadra più in alto nel ranking stagionale PRE-SuperCup
    #    (esclusi i punti della SuperCup, non ancora giocata) non già qualificata.
    qualified: set[str] = set(team_to_cup.keys())
    sub_to_cup: dict[str, str] = {}
    ranking_order = _ranking_pre_supercup(stagione)
    if ranking_order is not None:
        rank_idx = 0
        for nice, comp_key in coppe_ordinate:
            if comp_key in cups_filled:
                continue
            while rank_idx < len(ranking_order):
                candidate = ranking_order[rank_idx]
                rank_idx += 1
                if candidate not in qualified:
                    qualified.add(candidate)
                    sub_to_cup[candidate] = nice
                    break

    ruoli = {team: f"Vincente {nice}" for team, nice in team_to_cup.items()}
    for team, nice in sub_to_cup.items():
        ruoli[team] = f"Sostituente {nice}"
    return ruoli


# Configurazione per ogni competizione "semplice" (finale a partita secca)
STORICO_CONFIG = {
    "league": {
        "comp": "galactic league",
        "finale_g": "Finale League",
        "semi_legs": ("Semifinale League - Andata", "Semifinale League - Ritorno"),
    },
    "galactic-cup": {
        "comp": "galactic cup",
        "finale_g": "Finale Cup",
        "semi_legs": ("Semifinale - Andata", "Semifinale - Ritorno"),
    },
    "kings-league": {
        "comp": "Kings League",
        "finale_g": "Final Four - Finale",
        "semi_single": "Final Four - Semifinali",
    },
    "champions-cup": {
        "comp": "galactic champions cup",
        "finale_g": "Fase 3 - Finale",
        "semi_single": "Fase 3 - Semifinale",
    },
    "supercup": {
        "comp": "intergalactic supercup",
        "finale_g": "Finale SuperCup",
        "semi_single": "Semifinale SuperCup",
    },
}


@app.get("/api/storico-comp/{competizione}")
def get_storico_generico(competizione: str):
    """
    Storico di una competizione (esclusa Cup of 8/10 che ha endpoint dedicato).
    Per ogni stagione caricata: vincitrice, runner-up, risultato finale e
    le 2 semifinaliste (perdenti delle semifinali). Il risultato è espresso
    nella forma 'Vincitrice — Runner-up' (i pair X-Y vengono invertiti se
    la vincitrice giocava in trasferta).
    """
    if competizione not in STORICO_CONFIG:
        raise HTTPException(404, f"Competizione '{competizione}' non gestita")
    cfg = STORICO_CONFIG[competizione]

    out = []
    for s in stagioni_presenti():
        df = leggi_partite(s)
        record = {
            "stagione": s,
            "competizione": competizione,
            "vincitrice": None,
            "runner_up": None,
            "risultato": None,
            "semifinaliste": [],
        }
        if df.empty:
            out.append(record)
            continue

        comp_df = df[df["Competizione"] == cfg["comp"]]
        if comp_df.empty:
            out.append(record)
            continue

        # Finale (sempre partita secca per le competizioni gestite qui)
        finale_rows = comp_df[comp_df["giornata"] == cfg["finale_g"]]
        if len(finale_rows) > 0:
            row = finale_rows.iloc[0]
            vincitrice = _winner_of_match(row)
            runner_up = _loser_of_match(row)
            ris_raw = str(row["risultato"])
            risultato = (
                _flip_risultato(ris_raw)
                if vincitrice is not None and vincitrice == row["squadra_trasferta"]
                else ris_raw
            )
            record["vincitrice"] = vincitrice
            record["runner_up"] = runner_up
            record["risultato"] = risultato

        # Semifinaliste
        if "semi_single" in cfg:
            record["semifinaliste"] = _semifinaliste_match_unico(comp_df, cfg["semi_single"])
        else:
            andata_g, ritorno_g = cfg["semi_legs"]
            record["semifinaliste"] = _semifinaliste_due_legs(comp_df, andata_g, ritorno_g)

        # Ruoli (solo per SuperCup: spiegano da quale coppa proviene ciascuna partecipante)
        if competizione == "supercup":
            record["ruoli"] = _ruoli_supercup(s)

        # Posizione nella fase a gironi (solo Galactic League): per ogni squadra
        # presente nell'albo d'oro, il piazzamento nella League Phase (Giornate 1-8).
        if competizione == "league":
            posizioni_lp = {}
            df_cl = estrattore.costruisci_classifica_galactic_league(df)
            if df_cl is not None and len(df_cl) > 0:
                for _, cr in df_cl.iterrows():
                    posizioni_lp[cr["SQUADRA"]] = int(cr["Posizione"])
            record["posizioni_league_phase"] = posizioni_lp

        out.append(record)

    return {"competizione": competizione, "storico": out}


def _partecipanti_cup(cup_df, cup_name: str, stagione: int) -> list[dict]:
    """
    Per ogni squadra che ha partecipato alla Cup of 8 / Cup of 10:
    - posizione_ranking nel ranking stagionale
    - fasi_giocate: lista delle fasi a cui ha preso parte
    - vinto_torneo: True se ha vinto la finale
    Le fasi possibili sono: 'ottavi' (solo Cup of 10), 'quarti', 'semifinale', 'finale'.
    """
    stages_map = {
        "cup of 8": [
            ("quarti",     "Quarti Cup of 8"),
            ("semifinale", "Semifinale Cup of 8"),
            ("finale",     "Finale Cup of 8"),
        ],
        "cup of 10": [
            ("ottavi",     "Ottavi Cup of 10"),
            ("quarti",     "Quarti Cup of 10"),
            ("semifinale", "Semifinale Cup of 10"),
            ("finale",     "Finale Cup of 10"),
        ],
    }
    stages = stages_map.get(cup_name, [])

    teams_stages: dict[str, list[str]] = {}
    winner: Optional[str] = None
    for stage_name, giornata in stages:
        stage_rows = cup_df[cup_df["giornata"] == giornata]
        for _, row in stage_rows.iterrows():
            casa = row["squadra_casa"]
            trasf = row["squadra_trasferta"]
            teams_stages.setdefault(casa, []).append(stage_name)
            teams_stages.setdefault(trasf, []).append(stage_name)
            if stage_name == "finale":
                w = _winner_of_match(row)
                if w:
                    winner = w

    out = []
    for team, fasi in teams_stages.items():
        out.append({
            "squadra": team,
            "posizione_ranking": _pos_ranking_stagionale(stagione, team),
            "fasi_giocate": fasi,
            "vinto_torneo": team == winner,
        })
    return out


@app.get("/api/storico/cup")
def get_storico_cup():
    """
    Storico Cup of 8 / Cup of 10 per ogni stagione:
    vincitrice, runner-up, risultato finale, semifinaliste (i due perdenti
    delle semifinali) e posizione della vincitrice nel ranking di qualifica
    (cumulato della stagione precedente).
    """
    out = []
    for s in stagioni_presenti():
        df = leggi_partite(s)
        if df.empty:
            out.append({
                "stagione": s,
                "competizione": None,
                "vincitrice": None,
                "runner_up": None,
                "semifinaliste": [],
                "posizione_qualifica": None,
                "partecipanti": [],
            })
            continue

        comp_set = set(df["Competizione"].unique())
        if "cup of 10" in comp_set:
            cup_name = "cup of 10"
            finale_g = "Finale Cup of 10"
            semi_g = "Semifinale Cup of 10"
        elif "cup of 8" in comp_set:
            cup_name = "cup of 8"
            finale_g = "Finale Cup of 8"
            semi_g = "Semifinale Cup of 8"
        else:
            out.append({
                "stagione": s,
                "competizione": None,
                "vincitrice": None,
                "runner_up": None,
                "semifinaliste": [],
                "posizione_qualifica": None,
                "partecipanti": [],
            })
            continue

        cup_df = df[df["Competizione"] == cup_name]

        vincitrice = None
        runner_up = None
        risultato = None
        finale_rows = cup_df[cup_df["giornata"] == finale_g]
        if len(finale_rows) > 0:
            row = finale_rows.iloc[0]
            vincitrice = _winner_of_match(row)
            runner_up = _loser_of_match(row)
            ris_raw = str(row["risultato"])
            # Se la vincitrice giocava in trasferta, inverti il risultato
            # in modo che si legga "Vincitrice — Runner-up"
            if vincitrice is not None and vincitrice == row["squadra_trasferta"]:
                risultato = _flip_risultato(ris_raw)
            else:
                risultato = ris_raw

        semifinaliste: list[str] = []
        semi_rows = cup_df[cup_df["giornata"] == semi_g]
        for _, row in semi_rows.iterrows():
            sq = _loser_of_match(row)
            if sq:
                semifinaliste.append(sq)

        pos_qualifica = _pos_ranking_stagionale(s, vincitrice) if vincitrice else None
        partecipanti = _partecipanti_cup(cup_df, cup_name, s)

        out.append({
            "stagione": s,
            "competizione": cup_name,
            "vincitrice": vincitrice,
            "runner_up": runner_up,
            "risultato": risultato,
            "semifinaliste": semifinaliste,
            "posizione_qualifica": pos_qualifica,
            "partecipanti": partecipanti,
        })

    return {"storico": out}


@app.get("/api/h2h")
def get_h2h(squadra: str, avversaria: str):
    """
    Tutte le partite tra due squadre, attraverso tutte le stagioni caricate.
    Ritorna ogni partita con stagione, competizione, giornata, casa/trasferta,
    risultato e campo (Casa/Trasferta/Neutro).
    """
    if squadra == avversaria:
        raise HTTPException(400, "Le due squadre devono essere diverse")
    if squadra not in estrattore.SQUADRE_CANONICHE:
        raise HTTPException(404, f"Squadra '{squadra}' non riconosciuta")
    if avversaria not in estrattore.SQUADRE_CANONICHE:
        raise HTTPException(404, f"Avversaria '{avversaria}' non riconosciuta")

    partite: list[dict] = []
    for s in stagioni_presenti():
        df = leggi_partite(s)
        if df.empty:
            continue
        mask = (
            ((df["squadra_casa"] == squadra) & (df["squadra_trasferta"] == avversaria))
            | ((df["squadra_casa"] == avversaria) & (df["squadra_trasferta"] == squadra))
        )
        for _, row in df[mask].iterrows():
            campo = row.get("campo")
            if campo is None or (isinstance(campo, float) and math.isnan(campo)) or pd.isna(campo):
                campo = None
            partite.append({
                "stagione": s,
                "Competizione": str(row["Competizione"]),
                "giornata": str(row["giornata"]),
                "squadra_casa": str(row["squadra_casa"]),
                "squadra_trasferta": str(row["squadra_trasferta"]),
                "risultato": str(row["risultato"]),
                "campo": campo,
            })

    return {"squadra": squadra, "avversaria": avversaria, "partite": partite}


@app.get("/api/albo-oro")
def get_albo_oro():
    """
    Albo d'oro: per ogni stagione caricata, restituisce:
      - vincitori delle 6 competizioni
      - top 3 del ranking stagionale (1°, 2°, 3°)
      - 1° del ranking cumulato di quella stagione
    """
    stagioni = stagioni_presenti()
    albo = []

    for s in stagioni:
        # Vincitori competizioni
        vincitori = _vincitori_competizioni(s)

        # Ranking stagionale → top 3
        df_r, df_max = _calcola_ranking_stagione(s)
        top3 = []
        if df_r is not None:
            df_r_sorted = estrattore.aggiungi_posizione_e_percentuale(df_r, df_max)
            for _, row in df_r_sorted.head(3).iterrows():
                top3.append(str(row["SQUADRA"]))

        # Ranking cumulato di quella stagione → primo classificato
        primo_cumulato = None
        try:
            cum = get_ranking_cumulato(s)
            if cum.get("ranking"):
                primo_cumulato = cum["ranking"][0]["SQUADRA"]
        except Exception:
            pass

        # Ranking cumulato per Star Points → primo classificato a quella stagione
        primo_star = None
        try:
            cs = get_cumulato_squadre(s)
            squadre = [sq for sq in cs.get("squadre", []) if sq.get("star_points", 0)]
            if squadre:
                primo_star = max(squadre, key=lambda x: x["star_points"])["SQUADRA"]
        except Exception:
            pass

        albo.append({
            "stagione": s,
            "vincitori": vincitori,
            "top3_ranking": top3,
            "primo_cumulato": primo_cumulato,
            "primo_star": primo_star,
        })

    return {"albo": albo}

"""
Generazione del calendario di una nuova stagione (sorteggio).

Fetta 1: fase a gironi (League Phase) della Galactic League — 8 giornate, via
template precalcolati portati da galactic-manager (vedi league_templates.json).

La fase a eliminazione (Play Off → Finale) sarà la Fetta 2.
"""
import json
import os
import random
from typing import Optional

NUM_FASCE = 4
TEAMS_PER_FASCIA = 9
NUM_SQUADRE = NUM_FASCE * TEAMS_PER_FASCIA  # 36
RECENT_WINDOW = 5  # non ripetere un template usato nelle ultime 5 stagioni

_TEMPLATES: Optional[list] = None


def carica_templates() -> list:
    """Carica (una sola volta) i 40 template dal JSON.

    Ogni template è una lista di 144 match nella forma
    [giornata(1-8), posizioneCasa(0-35), posizioneTrasferta(0-35)] su posizioni
    astratte: le posizioni 0-8 sono la fascia 1, 9-17 la fascia 2, ecc.
    """
    global _TEMPLATES
    if _TEMPLATES is None:
        path = os.path.join(os.path.dirname(__file__), "league_templates.json")
        with open(path, encoding="utf-8") as f:
            _TEMPLATES = json.load(f)
    return _TEMPLATES


def numero_templates() -> int:
    return len(carica_templates())


def build_fasce(squadre_ordinate: list[str]) -> list[list[str]]:
    """Divide le 36 squadre (ordinate per ranking, pos. 1 → 36) in 4 fasce da 9.

    Fascia 1 = pos. 1-9, fascia 2 = 10-18, fascia 3 = 19-27, fascia 4 = 28-36.
    """
    if len(squadre_ordinate) != NUM_SQUADRE:
        raise ValueError(
            f"Servono esattamente {NUM_SQUADRE} squadre, ricevute {len(squadre_ordinate)}"
        )
    return [
        list(squadre_ordinate[f * TEAMS_PER_FASCIA:(f + 1) * TEAMS_PER_FASCIA])
        for f in range(NUM_FASCE)
    ]


def scegli_template(recenti: list[int], rng: random.Random) -> int:
    """Sceglie un indice di template evitando quelli usati nelle ultime
    RECENT_WINDOW stagioni. Se non ne resta nessuno disponibile, pesca tra tutti.

    `recenti` è atteso dalla stagione più vecchia alla più recente.
    """
    n = numero_templates()
    esclusi = set(recenti[-RECENT_WINDOW:])
    disponibili = [i for i in range(n) if i not in esclusi]
    pool = disponibili if disponibili else list(range(n))
    return rng.choice(pool)


def calendario_da_template(fasce: list[list[str]], template_idx: int,
                           rng: random.Random) -> list[dict]:
    """Mappa le posizioni astratte 0..35 alle squadre reali (rimescolando ogni
    fascia in modo indipendente) e produce le righe-partita del girone, con
    risultato vuoto, pronte per l'inserimento in `partite`.
    """
    templates = carica_templates()
    if not (0 <= template_idx < len(templates)):
        raise ValueError(f"template_idx {template_idx} fuori range")

    pos_to_team: list[Optional[str]] = [None] * NUM_SQUADRE
    for pot_index, teams_in_pot in enumerate(fasce):
        shuffled = list(teams_in_pot)
        rng.shuffle(shuffled)
        for i, team in enumerate(shuffled):
            pos_to_team[pot_index * TEAMS_PER_FASCIA + i] = team

    righe = []
    for giornata, h_pos, a_pos in templates[template_idx]:
        casa = pos_to_team[h_pos]
        trasf = pos_to_team[a_pos]
        righe.append({
            "giornata":          f"Giornata {giornata}",
            "squadra_casa":      casa,
            "risultato":         "",
            "squadra_trasferta": trasf,
            "tipo":              "League",
            "ordine":            0,
            "Competizione":      "galactic league",
            "campo":             casa,
        })
    return righe

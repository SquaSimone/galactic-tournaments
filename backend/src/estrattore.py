# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 14:48:13 2026

@author: simonesquaglia
"""
"""""
Voglio creare un’app per la raccolta, gestione e analisi di partite di calcio basata su tornei personalizzati che attualmente gestisco tramite file Excel.

Struttura generale

Esiste un “mondo” fisso composto da 36 squadre.

Le squadre non vengono mai sostituite (salvo future modifiche manuali).

Ogni stagione è composta da 7 fogli Excel:

6 fogli di competizioni

1 foglio di ranking stagionale

Caricando un file Excel completo di una stagione, l’app deve:

leggere automaticamente tutte le partite

aggiornare statistiche e ranking

I risultati delle partite possono avere questi formati:
X-Y: partita terminata ai tempi regolamentari X-Y[X1-Y1]: Partita terminata ai supplementari, X1-Y1 risultato al termine dei tempi regolamentari, X-Y: risultato al termine dei supplementari X-Y(A-B): Partita terminata ai rigori: X-Y: risultato al termine dei supplementari, (A-B): risultato dei rigori X-Y[X1-Y1](A-B): Partita terminata ai supplementari, X1-Y1 risultato al termine dei tempi regolamentari, X-Y: risultato al termine dei supplementari, (A-B): risultato dei rigori


Competizioni
1. Galactic League

36 squadre divise in 4 fasce da 9 squadre

Ogni squadra affronta 2 squadre per ogni fascia

1 partita in casa

1 in trasferta

Totale: 8 partite (4 casa, 4 trasferta)

Punteggi:

Vittoria: 3 punti

Pareggio: 1 punto

Sconfitta: 0 punti

Classifica League Phase

1–8 → qualificate direttamente agli ottavi

9–24 → playoff di accesso agli ottavi

25–28 → eliminate

29–36 → eliminate + playoff Galactic Cup

Fase finale

Playoff → Ottavi → Quarti → Semifinali → Finale

Andata/ritorno fino alle semifinali

Finale secca in campo neutro

Le fasi si leggono da sinistra a destra nel foglio Excel

2. Galactic Cup

Squadre 29–36 → turno preliminare

Tutte le altre → direttamente ai sedicesimi

Formato

Preliminare, Sedicesimi, Ottavi: partita secca

squadra in alto = gioca in casa

Dai Quarti:

andata/ritorno

squadra in alto: prima in casa, poi in trasferta

Finale secca in campo neutro

3. Galactic Kings League

Le 36 squadre sono divise in leghe.

Prime 4 stagioni

2 leghe: A, B, C

Dalla 5ª stagione

3 leghe: A, B, C

Formato gironi

Formato vecchio:

Lega A: 4 gironi

Lega B: 5 gironi

Formato nuovo:

Lega A: 4 gironi

Lega B: 3 gironi

Lega C: 2 gironi

Regole

Le squadre affrontano solo il proprio girone

Andata/ritorno

Le prime di ogni girone di Lega A accedono alla fase finale

Fase finale

Semifinali e finale

Partite secche

Campo neutro

4. Galactic Champions Cup
Fase 1

36 squadre divise in 6 fasce

6 gironi da 6 squadre (1 per fascia)

Andata/ritorno contro tutte le squadre del girone

Totale: 10 partite

Passano le prime 4

Fase 2

Le prime classificate della fase 1 → fascia 1

Le altre fasce determinate dal ranking

6 gironi da 4 squadre (1 per fascia)

Partite secche in campo neutro

Passano:

prime 2 di ogni girone

4 migliori terze

Fase finale

16 squadre

Ottavi → Finale

Partite secche in campo neutro

5. Intergalactic SuperCup

Partecipano le vincitrici dei 4 tornei principali

Semifinali + Finale

Partite secche

Campo neutro

6. Ranking

Ranking stagionale

Ranking squadre:

combina ranking stagionale

ranking delle ultime 4 stagioni

7. Cup of 10 (Cup of 8 nelle prime 2 stagioni)
Prime 2 stagioni (Cup of 8)

1 vs 8

4 vs 5

2 vs 7

3 vs 6

Partite secche, in casa della squadra meglio classificata

Semifinali e finale: campo neutro

Dalla 3ª stagione (Cup of 10)

Turno preliminare

7 vs 10 (A)

8 vs 9 (B)

Partita secca, in casa della squadra più alta nel ranking

Turno successivo

1 vs vincente (A)

4 vs 5

2 vs vincente (B)

3 vs 6

Partita secca, in casa della squadra più alta nel ranking

Semifinali e finale:

Partita secca

Campo neutro

Obiettivo dell’app

L’app deve permettere di:

Archiviare tutte le partite di tutte le competizioni

Per ogni squadra:

vittorie

sconfitte

pareggi

gol fatti

gol subiti

Visualizzare:

quante volte due squadre si sono affrontate

in quali competizioni e stagioni

Caricando un file Excel stagionale completo:

aggiornare automaticamente statistiche

aggiornare ranking stagionali e storici

L’app deve essere pensata come database storico evolutivo, non solo come visualizzazione statica.

Se vuoi, nel prossimo messaggio posso:

semplificare il prompt per Lovable se lo vuoi più “AI-friendly”

dividerlo in step (MVP → versione avanzata)

oppure aiutarti a definire il modello dati (tabelle, relazioni, chiavi)
"""

#Voglio creare un’app per la raccolta, gestione e analisi di partite di calcio basata su tornei personalizzati che attualmente gestisco tramite file Excel.

#Struttura generale: Esiste un “mondo” fisso composto da 36 squadre. Le squadre non vengono mai sostituite (salvo future modifiche manuali).

#Ogni stagione è composta da 7 fogli Excel: 6 fogli di competizioni,1 foglio di ranking stagionale. Caricando un file Excel completo di una stagione, l’app deve:

#leggere automaticamente tutte le partite, aggiornare statistiche e ranking. I risultati delle partite possono avere questi formati:
#X-Y: partita terminata ai tempi regolamentari X-Y[X1-Y1]: Partita terminata ai supplementari, X1-Y1 risultato al termine dei tempi regolamentari, X-Y: risultato al termine dei supplementari X-Y(A-B): Partita terminata ai rigori: X-Y: risultato al termine dei supplementari, (A-B): risultato dei rigori X-Y[X1-Y1](A-B): Partita terminata ai supplementari, X1-Y1 risultato al termine dei tempi regolamentari, X-Y: risultato al termine dei supplementari, (A-B): risultato dei rigori
#Competizioni
#1. Galactic League

#36 squadre divise in 4 fasce da 9 squadre

#Ogni squadra affronta 2 squadre per ogni fascia

#1 partita in casa

#1 in trasferta

#Totale: 8 partite (4 casa, 4 trasferta)
#Punteggi:Vittoria: 3 punti Pareggio: 1 punto Sconfitta: 0 punti
#Classifica League Phase 1–8 → qualificate direttamente agli ottavi 9–24 → playoff di accesso agli ottavi 25–28 → eliminate 29–36 → eliminate + playoff Galactic Cup
#Fase finale Playoff → Ottavi → Quarti → Semifinali → Finale Andata/ritorno fino alle semifinali Finale secca in campo neutro
#Le fasi si leggono da sinistra a destra nel foglio Excel

#Iniziamo con il codice per leggere il file. Vorrei concentrarmi adesso sulla Galactic League, poi passeremo alle altre competizioni e al ranking.
import pandas as pd

# ════════════════════════════════════════════════════════════════════
# Lista canonica delle 36 squadre del mondo Galactic.
# Mai sostituite (salvo modifiche manuali) — vedi specifica originale.
# Serve come fonte di verità per l'auto-correzione dei typo nei fogli.
# ════════════════════════════════════════════════════════════════════
SQUADRE_CANONICHE = {
    'Akillians', 'Atletico Galaxy', 'Blue Tigers', 'Cyclops',
    'Elektras', 'Gyras', 'Hazars', 'JawBreakers',
    'Kobalts', 'Lightning', 'Nebolus', 'Oceanic',
    'OEM', 'Orion', 'Pirates', 'Pullsar',
    'Real Galactic', 'Red Devil', 'Red Tigers', 'Rykers',
    'Septel', 'Shadow', 'Shining Swarm', 'Snow Kids',
    'Stella Rossa', 'Team Paradisia', 'Tech Poznan', 'Tecnodroid',
    'TecnoFull', 'Thunder Bolts', 'Titanium', 'Twister',
    'Vacor', 'Vulcano', 'Wambas', 'Xenox',
}


# Ordine canonico delle giornate (per categorical sort).
# Andata + Ritorno consecutivi all'interno di ogni round.
GIORNATE_ORDER = [
    # Galactic League
    'Giornata 1', 'Giornata 2', 'Giornata 3', 'Giornata 4',
    'Giornata 5', 'Giornata 6', 'Giornata 7', 'Giornata 8',
    'Play Off - Andata', 'Play Off - Ritorno',
    'Ottavi League - Andata',    'Ottavi League - Ritorno',
    'Quarti League - Andata',    'Quarti League - Ritorno',
    'Semifinale League - Andata','Semifinale League - Ritorno',
    'Finale League',
    # Galactic Cup
    'Turno 1', 'Turno 2', 'Ottavi di Finale',
    'Quarti di Finale - Andata', 'Quarti di Finale - Ritorno',
    'Semifinale - Andata', 'Semifinale - Ritorno',
    'Finale Cup',
    # Kings League - gironi
    'Fase 1 - Lega A - Girone A', 'Fase 1 - Lega A - Girone B',
    'Fase 1 - Lega A - Girone C', 'Fase 1 - Lega A - Girone D',
    'Fase 1 - Lega B - Girone A', 'Fase 1 - Lega B - Girone B',
    'Fase 1 - Lega B - Girone C', 'Fase 1 - Lega B - Girone D',
    'Fase 1 - Lega B - Girone E',
    'Fase 1 - Lega C - Girone A', 'Fase 1 - Lega C - Girone B',
    # Kings League - fasi finali
    'Playoff Lega B - Semifinali',
    'Playoff Lega B - Finale',
    'Playout Lega A - Finali',
    'Playout Lega B - Finali',
    'Playoff/Playout B-C - Turno 1',
    'Playoff/Playout B-C - Turno 2',
    'Playoff/Playout A-B - Turno 1',
    'Playoff/Playout A-B - Turno 2',
    'Final Four - Semifinali',
    'Final Four - Finale',
    # Champions Cup
    'Fase 1 - Girone A', 'Fase 1 - Girone B', 'Fase 1 - Girone C',
    'Fase 1 - Girone D', 'Fase 1 - Girone E', 'Fase 1 - Girone F',
    'Fase 2 - Girone A', 'Fase 2 - Girone B', 'Fase 2 - Girone C',
    'Fase 2 - Girone D', 'Fase 2 - Girone E', 'Fase 2 - Girone F',
    'Fase 3 - Ottavi di Finale',
    'Fase 3 - Quarti di Finale',
    'Fase 3 - Semifinale',
    'Fase 3 - Finale',
    # SuperCup
    'Semifinale SuperCup', 'Finale SuperCup',
    # Cup of 8 / Cup of 10
    'Quarti Cup of 8', 'Semifinale Cup of 8', 'Finale Cup of 8',
    'Ottavi Cup of 10', 'Quarti Cup of 10', 'Semifinale Cup of 10', 'Finale Cup of 10',
]


def correggi_typo_squadre(df, canonici=SQUADRE_CANONICHE, cutoff=0.7):
    """
    Auto-correzione dei nomi squadra basata sulla lista canonica.

    Per ogni nome di squadra in df che NON appartiene a `canonici`:
      - prova a trovare il match più vicino con difflib (cutoff configurabile);
      - se trovato, sostituisce nel df (sia squadra_casa che squadra_trasferta);
      - se non trovato, segnala come warning a console.

    Modifica `df` in-place e restituisce il dizionario delle sostituzioni
    {nome_typo: nome_canonico} per uso programmatico.
    """
    import difflib
    tutti_nomi = set(df['squadra_casa'].dropna()) | set(df['squadra_trasferta'].dropna())
    sconosciuti = tutti_nomi - set(canonici)

    sostituzioni = {}
    falliti = []
    for name in sconosciuti:
        suggerimenti = difflib.get_close_matches(name, canonici, n=1, cutoff=cutoff)
        if suggerimenti:
            sostituzioni[name] = suggerimenti[0]
        else:
            falliti.append(name)

    if sostituzioni:
        df['squadra_casa']      = df['squadra_casa'].replace(sostituzioni)
        df['squadra_trasferta'] = df['squadra_trasferta'].replace(sostituzioni)
        print(f"\n✅ Correzioni typo nomi squadra ({len(sostituzioni)}):")
        for typo, canonico in sorted(sostituzioni.items()):
            print(f"     '{typo}' → '{canonico}'")

    if falliti:
        print(f"\n⚠️  Nomi squadra non riconosciuti (nessuna correzione possibile):")
        for f in sorted(falliti):
            print(f"     '{f}'")

    return sostituzioni


def leggi_file_excel(percorso_file):
    # Leggi il file Excel
    xls = pd.ExcelFile(percorso_file)
    
    # Crea un dizionario per memorizzare i dati di ogni foglio
    dati_stagione = {}
    
    # Itera su ogni foglio e leggi i dati
    for nome_foglio in xls.sheet_names:
        dati_stagione[nome_foglio] = xls.parse(nome_foglio)
    
    return dati_stagione


def estrai_gol(gol_str):
    """
    Estrae il numero di gol dalla stringa.
    Prende il PRIMO numero, prima di *, [, (, ecc.
    - "2" → 2
    - "2* [1]" → 2 (il numero prima di *, non dentro le parentesi)
    - "3 [3]" → 3 (il numero prima di [)
    - "0(2)" → 0 (il numero prima di ()
    - 3 (int) → 3
    """
    gol_str = str(gol_str).strip()
    
    # Estrai il primo numero prima di *, [, (, ecc
    gol_str_clean = gol_str.split('*')[0].split('[')[0].split('(')[0].strip()
    
    # Gestisci sia stringhe numeriche che numeri float/int
    if gol_str_clean:
        try:
            return int(float(gol_str_clean))
        except:
            pass
    
    return 0

def estrai_numero_tra_parentesi(text, parentesi_type='['):
    """
    Estrae il numero tra parentesi quadre o tonde.
    - "1 [1]" con '[' → "1"
    - "3* [1]" con '[' → "1"
    - "0(2)" con '(' → "2"
    """
    if not text or parentesi_type not in text:
        return None
    
    if parentesi_type == '[':
        start, end = '[', ']'
    else:
        start, end = '(', ')'
    
    idx_start = text.find(start)
    idx_end = text.find(end)
    
    if idx_start >= 0 and idx_end > idx_start:
        content = text[idx_start+1:idx_end].strip()
        return content
    
    return None

def estrai_gol_e_extra(gol_str):
    """
    Estrae i gol e tutte le informazioni aggiuntive (supplementari e rigori).
    Restituisce una tupla (gol, supplementari_val, rigor_val, ha_asterisco).
    - "2" → (2, None, None, False)
    - "1 [1]" → (1, "1", None, False) - supplementari
    - "3* [1]" → (3, "1", None, True) - supplementari + asterisco
    - "0(2)" → (0, None, "2", False) - rigori
    """
    original_str = str(gol_str).strip()
    gol_str = original_str
    
    # Controlla se c'è un asterisco (indica squadra che passa)
    ha_asterisco = '*' in gol_str
    gol_str = gol_str.replace('*', '')  # Rimuovi asterisco per l'elaborazione
    
    # Estrai il primo numero (gol)
    gol_str_clean = gol_str.split('[')[0].split('(')[0].strip()
    
    # Converti i gol a numero
    try:
        gol = int(float(gol_str_clean)) if gol_str_clean else 0
    except:
        gol = 0
    
    # Estrai supplementari e rigori
    supplementari = estrai_numero_tra_parentesi(gol_str, '[')
    rigori = estrai_numero_tra_parentesi(gol_str, '(')
    
    return (gol, supplementari, rigori, ha_asterisco)

def estrai_gol_e_rigori(gol_str):
    """
    Mantiene la funzione originale per compatibilità.
    Estrae i gol regolamentari e i rigori dalla stringa.
    """
    gol, extra = estrai_gol_e_extra(gol_str)
    
    # Estrai solo i rigori dalla parte extra
    rigori_str = None
    if extra and '(' in extra:
        idx_start = extra.find('(')
        rigori_str = extra[idx_start:]
    
    return (gol, rigori_str)



def estrai_galactic_cup(percorso_file):
    import re
    df = pd.read_excel(percorso_file, sheet_name='Galactic Cup', header=None)
    cup_matches = []

    def gv(cell):
        """Estrae il primo numero da una cella (per confronto validità)."""
        m = re.match(r'^(\d+)', str(cell).strip())
        return int(m.group(1)) if m else None

    def build_result(cell1, cell2):
        """
        Costruisce il risultato completo 'X-Y [X1-Y1] (A-B)' da due celle.
        cell1 = gol squadra in alto (casa), cell2 = gol squadra in basso (trasferta)
        
        Formato celle: 
          "2"        → 2
          "1 (2)"    → 1 (2) rigori
          "2 [0]"    → 2 [0] supplementari (il numero tra [] è il parziale ai 90')
          "2 [0](3)" → supplementari + rigori
        """
        s1 = str(cell1).strip()
        s2 = str(cell2).strip()
        
        # Estrai gol principali
        g1 = int(re.match(r'^(\d+)', s1).group(1))
        g2 = int(re.match(r'^(\d+)', s2).group(1))
        
        result = f'{g1}-{g2}'
        
        # Supplementari: cerca [X] in entrambe le celle
        supp1 = re.search(r'\[(\d+)\]', s1)
        supp2 = re.search(r'\[(\d+)\]', s2)
        if supp1 and supp2:
            result += f' [{supp1.group(1)}-{supp2.group(1)}]'
        elif supp1:
            result += f' [{supp1.group(1)}]'
        elif supp2:
            result += f' [{supp2.group(1)}]'
        
        # Rigori: cerca (X) in entrambe le celle
        rig1 = re.search(r'\((\d+)\)', s1)
        rig2 = re.search(r'\((\d+)\)', s2)
        if rig1 and rig2:
            result += f' ({rig1.group(1)}-{rig2.group(1)})'
        
        return result

    def sv(cell):
        s = str(cell).strip()
        return None if s in ('nan', '') else s

    # ── LATO SINISTRO: partite secche ────────────────────────────────
    def secche_sin(nome, col_s, col_g):
        i = 2
        while i < len(df) - 1:
            s1 = sv(df.iloc[i,   col_s]); g1 = gv(df.iloc[i,   col_g])
            s2 = sv(df.iloc[i+1, col_s]); g2 = gv(df.iloc[i+1, col_g])
            if s1 and g1 is not None and s2 and g2 is not None:
                cup_matches.append({
                    'giornata': f'{nome} (sinistro)',
                    'squadra_casa': s1,
                    'risultato': build_result(df.iloc[i, col_g], df.iloc[i+1, col_g]),
                    'squadra_trasferta': s2, 'tipo': 'Cup', 'ordine': 0
                })
                i += 2
            else:
                i += 1

    # ── LATO SINISTRO: andata/ritorno ────────────────────────────────
    def ar_sin(nome, col_s, col_ga, col_gr):
        i = 2
        while i < len(df) - 1:
            s1  = sv(df.iloc[i,   col_s]);  ga1 = gv(df.iloc[i,   col_ga]); gr1 = gv(df.iloc[i,   col_gr])
            s2  = sv(df.iloc[i+1, col_s]);  ga2 = gv(df.iloc[i+1, col_ga]); gr2 = gv(df.iloc[i+1, col_gr])
            if s1 and s2 and all(x is not None for x in [ga1, ga2, gr1, gr2]):
                cup_matches.append({
                    'giornata': f'{nome} - Andata (sinistro)',
                    'squadra_casa': s1,
                    'risultato': build_result(df.iloc[i, col_ga], df.iloc[i+1, col_ga]),
                    'squadra_trasferta': s2, 'tipo': 'Cup', 'ordine': 0
                })
                cup_matches.append({
                    'giornata': f'{nome} - Ritorno (sinistro)',
                    'squadra_casa': s2,
                    'risultato': build_result(df.iloc[i+1, col_gr], df.iloc[i, col_gr]),
                    'squadra_trasferta': s1, 'tipo': 'Cup', 'ordine': 1
                })
                i += 2
            else:
                i += 1

    # ── LATO DESTRO: partite secche ──────────────────────────────────
    def secche_des(nome, col_g, col_s):
        i = 2
        while i < len(df) - 1:
            g1 = gv(df.iloc[i,   col_g]); s1 = sv(df.iloc[i,   col_s])
            g2 = gv(df.iloc[i+1, col_g]); s2 = sv(df.iloc[i+1, col_s])
            if s1 and g1 is not None and s2 and g2 is not None:
                cup_matches.append({
                    'giornata': f'{nome} (destro)',
                    'squadra_casa': s1,
                    'risultato': build_result(df.iloc[i, col_g], df.iloc[i+1, col_g]),
                    'squadra_trasferta': s2, 'tipo': 'Cup', 'ordine': 0
                })
                i += 2
            else:
                i += 1

    # ── LATO DESTRO: andata/ritorno ──────────────────────────────────
    def ar_des(nome, righe_top, col_ga, col_gr, col_s):
        for i in righe_top:
            if i + 1 >= len(df):
                continue
            ga1 = gv(df.iloc[i,   col_ga]); gr1 = gv(df.iloc[i,   col_gr]); s1 = sv(df.iloc[i,   col_s])
            ga2 = gv(df.iloc[i+1, col_ga]); gr2 = gv(df.iloc[i+1, col_gr]); s2 = sv(df.iloc[i+1, col_s])
            if s1 and s2 and all(x is not None for x in [ga1, ga2, gr1, gr2]):
                cup_matches.append({
                    'giornata': f'{nome} - Ritorno (destro)',   # ← era Andata
                    'squadra_casa':      s2,
                    'risultato':         build_result(df.iloc[i+1, col_ga], df.iloc[i, col_ga]),
                    'squadra_trasferta': s1, 'tipo': 'Cup', 'ordine': 1   # ← ordine 1
                })
                cup_matches.append({
                    'giornata': f'{nome} - Andata (destro)',    # ← era Ritorno
                    'squadra_casa':      s1,
                    'risultato':         build_result(df.iloc[i, col_gr], df.iloc[i+1, col_gr]),
                    'squadra_trasferta': s2, 'tipo': 'Cup', 'ordine': 0   # ← ordine 0
                })

    # ════════════════════════════════════════════════════════════════
    # LATO SINISTRO
    secche_sin('Turno 1',          col_s=1,  col_g=2)
    secche_sin('Turno 2',          col_s=4,  col_g=5)
    secche_sin('Ottavi di Finale', col_s=7,  col_g=8)
    ar_sin    ('Quarti di Finale', col_s=10, col_ga=11, col_gr=12)
    ar_sin    ('Semifinale',       col_s=14, col_ga=15, col_gr=16)

    # Finale
    r = df.iloc[22]
    s1 = sv(r[18]); ris = str(r[19]).strip(); s2 = sv(r[20])
    if s1 and s2 and '-' in ris:
        cup_matches.append({
            'giornata': 'Finale Cup',
            'squadra_casa': s1, 'risultato': ris,
            'squadra_trasferta': s2, 'tipo': 'Cup', 'ordine': 0
        })

    # ════════════════════════════════════════════════════════════════
    # LATO DESTRO
    ar_des('Semifinale',       righe_top=[17],    col_ga=22, col_gr=23, col_s=24)
    ar_des('Quarti di Finale', righe_top=[9, 25], col_ga=26, col_gr=27, col_s=28)
    secche_des('Ottavi di Finale', col_g=30, col_s=31)
    secche_des('Turno 2',          col_g=33, col_s=34)
    secche_des('Turno 1',          col_g=36, col_s=37)

    return cup_matches


def estrai_galactic_kings_league(percorso_file):
    """
    Estrae le partite della Galactic Kings League dal foglio omonimo.
    
    Struttura:
    - Fase 1: gironi Lega A (4) + Lega B (5, o 3 dalla stagione 5) + Lega C (2, dalla stagione 5)
    - Playoff Lega B: Semifinali + Finale
    - Playout Lega A: Finali (2 partite secche)
    - Fase Finale (Final Four): Semifinali + Finale
    
    Formato partite gironi: ogni riga = 2 partite affiancate
    col_s1 | col_r1 (andata) | col_s2 | col_r2 (ritorno)
    """
    import re
    df = pd.read_excel(percorso_file, sheet_name='Galactic Kings League', header=None)
    matches = []

    def sv(cell):
        s = str(cell).strip()
        return None if s in ('nan', '') else s

    def is_result(cell):
        s = str(cell).strip()
        return bool(re.match(r'^\d+', s) and '-' in s)

    # ════════════════════════════════════════════════════════════════
    # GIRONI
    # ════════════════════════════════════════════════════════════════
    def parse_girone(lega, girone_nome, col_s1, col_r1, col_s2, col_r2, row_start, row_end):
        for idx in range(row_start, row_end):
            if idx >= len(df):
                break
            s1 = sv(df.iloc[idx, col_s1])
            r1 = sv(df.iloc[idx, col_r1]) if col_r1 < len(df.columns) else None
            s2 = sv(df.iloc[idx, col_s2]) if col_s2 < len(df.columns) else None
            r2 = sv(df.iloc[idx, col_r2]) if col_r2 < len(df.columns) else None

            if s1 and r1 and s2 and is_result(r1):
                # Andata: s1 in casa
                matches.append({
                    'giornata':          f'Fase 1 - {lega} - {girone_nome}',
                    'squadra_casa':      s1,
                    'risultato':         r1,
                    'squadra_trasferta': s2,
                    'tipo':              'Kings League',
                    'ordine':            0,
                    'Competizione':      'galactic kings league'
                })
                # Ritorno: s2 in casa
                if r2 and is_result(r2):
                    matches.append({
                        'giornata':          f'Fase 1 - {lega} - {girone_nome}',
                        'squadra_casa':      s2,
                        'risultato':         r2,
                        'squadra_trasferta': s1,
                        'tipo':              'Kings League',
                        'ordine':            0,
                        'Competizione':      'galactic kings league'
                    })

    def trova_riga_keyword(keyword, col_start=0, col_end=None):
        """Trova la riga che contiene la keyword in una colonna dell'intervallo."""
        if col_end is None:
            col_end = len(df.columns)
        for idx in range(len(df)):
            for col in range(col_start, col_end):
                cell = sv(df.iloc[idx, col])
                if cell and keyword.upper() in cell.upper():
                    return idx, col
        return None, None

    def trova_gironi_in_blocco(row_lega, n_gironi):
        """
        Cerca le intestazioni GIRONE X partendo dalla riga row_lega.
        Restituisce lista di (girone_nome, col_s1, col_r1, col_s2, col_r2, row_start, row_end).
        """
        gironi = []
        nomi_std = ['Girone A', 'Girone B', 'Girone C', 'Girone D', 'Girone E']

        # Cerca intestazioni girone nelle righe vicine all'header lega
        girone_headers = []
        for cerca_riga in range(row_lega, min(row_lega + 3, len(df))):
            for col in range(len(df.columns)):
                cell = sv(df.iloc[cerca_riga, col])
                if cell and 'GIRONE' in cell.upper():
                    girone_headers.append((cerca_riga, col))

        # Prendi solo i primi n_gironi trovati
        girone_headers = girone_headers[:n_gironi]

        for i, (gr_row, gr_col) in enumerate(girone_headers):
            col_s1 = gr_col
            col_r1 = gr_col + 1
            col_s2 = gr_col + 2
            col_r2 = gr_col + 3

            # row_start: salta righe classifica (header tabella)
            row_start = gr_row + 1
            while row_start < len(df):
                cell_s = sv(df.iloc[row_start, col_s1])
                cell_r = sv(df.iloc[row_start, col_r1]) if col_r1 < len(df.columns) else None
                if cell_s and cell_r and is_result(cell_r):
                    break  # Trovata prima riga di partite
                row_start += 1

            # row_end: fino alla prima riga vuota dopo le partite
            row_end = row_start
            empty_count = 0
            while row_end < len(df) and empty_count < 4:
                s1 = sv(df.iloc[row_end, col_s1])
                r1 = sv(df.iloc[row_end, col_r1]) if col_r1 < len(df.columns) else None
                if s1 and r1 and is_result(r1):
                    empty_count = 0
                    row_end += 1
                else:
                    empty_count += 1
                    row_end += 1

            nome = nomi_std[i] if i < len(nomi_std) else f'Girone {i+1}'
            gironi.append((nome, col_s1, col_r1, col_s2, col_r2, row_start, row_end))
            print(f"  → {nome}: righe {row_start}-{row_end}, colonne {col_s1}/{col_r1}/{col_s2}/{col_r2}")

        return gironi

    # ════════════════════════════════════════════════════════════════
    # RILEVAMENTO STRUTTURA STAGIONE
    # ════════════════════════════════════════════════════════════════
    ha_lega_c = any(
        sv(df.iloc[r, c]) and 'LEGA C' in sv(df.iloc[r, c]).upper()
        for r in range(len(df)) for c in range(len(df.columns))
        if sv(df.iloc[r, c])
    )

    leghe_config = [
        {'keyword': 'LEGA A', 'n_gironi': 4, 'nome': 'Lega A'},
        {'keyword': 'LEGA B', 'n_gironi': 3 if ha_lega_c else 5, 'nome': 'Lega B'},
    ]
    if ha_lega_c:
        leghe_config.append({'keyword': 'LEGA C', 'n_gironi': 2, 'nome': 'Lega C'})

    # ════════════════════════════════════════════════════════════════
    # ESTRAZIONE GIRONI
    # ════════════════════════════════════════════════════════════════
    for lega_cfg in leghe_config:
        row_lega, col_lega = trova_riga_keyword(lega_cfg['keyword'])
        if row_lega is None:
            print(f"⚠️  {lega_cfg['keyword']} non trovata")
            continue
        print(f"\n{lega_cfg['nome']} trovata a riga {row_lega}")
        gironi = trova_gironi_in_blocco(row_lega, lega_cfg['n_gironi'])
        for (girone_nome, col_s1, col_r1, col_s2, col_r2, row_start, row_end) in gironi:
            parse_girone(lega_cfg['nome'], girone_nome, col_s1, col_r1, col_s2, col_r2, row_start, row_end)

    # ════════════════════════════════════════════════════════════════
    # PARTITE SECCHE (Playoff, Playout, Final Four)
    # ════════════════════════════════════════════════════════════════
    def parse_partite_secche(giornata_nome, col_s1, col_r, col_s2, row_start, row_end, tipo):
        for idx in range(row_start, row_end):
            if idx >= len(df):
                break
            s1 = sv(df.iloc[idx, col_s1])
            r  = sv(df.iloc[idx, col_r])  if col_r  < len(df.columns) else None
            s2 = sv(df.iloc[idx, col_s2]) if col_s2 < len(df.columns) else None
            if s1 and r and s2 and is_result(r):
                matches.append({
                    'giornata':          giornata_nome,   # ← ora viene passato correttamente
                    'squadra_casa':      s1,
                    'risultato':         r,
                    'squadra_trasferta': s2,
                    'tipo':              tipo,
                    'ordine':            0,
                    'Competizione':      'galactic kings league'
                })

    def estrai_partite_sezione(header_keyword, sub_sections, col_s, col_r, col_t, row_limite_inf=None):
        row_header, _ = trova_riga_keyword(header_keyword)
        if row_header is None:
            print(f"⚠️  '{header_keyword}' non trovata")
            return

        row_fine = row_limite_inf if row_limite_inf else len(df)

        # Trova le righe di TUTTI i sub-header prima di estrarre le partite
        sub_rows = []
        for (sub_kw, giornata_nome, tipo, _) in sub_sections:
            row_sub = None
            for idx in range(row_header + 1, row_fine):
                cell = sv(df.iloc[idx, col_s])
                if cell and sub_kw.upper() == cell.upper():  # match esatto, non 'in'
                    row_sub = idx
                    break
            sub_rows.append(row_sub)

        # Estrai le partite di ogni sub-header
        for i, (sub_kw, giornata_nome, tipo, _) in enumerate(sub_sections):
            row_sub = sub_rows[i]
            if row_sub is None:
                print(f"  ⚠️  Sub-header '{sub_kw}' non trovato")
                continue

            row_start = row_sub + 1

            # row_end = inizio del prossimo sub-header (o row_fine se è l'ultimo)
            row_end = row_fine
            for j in range(i + 1, len(sub_rows)):
                if sub_rows[j] is not None:
                    row_end = sub_rows[j]
                    break

            print(f"  → '{giornata_nome}': righe {row_start}-{row_end}")
            parse_partite_secche(giornata_nome, col_s, col_r, col_t, row_start, row_end, tipo)

    # ────────────────────────────────────────────────────────────────
    # FASI FINALI — branch su ha_lega_c:
    #   S1-S4 (no Lega C): sezioni separate PLAYOFF LEGA B / PLAYOUT LEGA A /
    #     [PLAYOUT LEGA B in S4] / FASE FINALE
    #   S5+ (con Lega C): sezioni combinate PLAYOFF LEGA C - PLAYOUT LEGA B /
    #     PLAYOFF LEGA B - PLAYOUT LEGA A / FASE FINALE
    # ────────────────────────────────────────────────────────────────
    if ha_lega_c:
        # ====== S5+ ======
        row_bc, col_bc = trova_riga_keyword('PLAYOFF LEGA C - PLAYOUT LEGA B')
        row_ab, col_ab = trova_riga_keyword('PLAYOFF LEGA B - PLAYOUT LEGA A')
        row_ff, col_ff = trova_riga_keyword('FASE FINALE')

        if row_bc is not None:
            estrai_partite_sezione(
                header_keyword = 'PLAYOFF LEGA C - PLAYOUT LEGA B',
                sub_sections   = [
                    ('TURNO 1', 'Playoff/Playout B-C - Turno 1', 'Kings League Playoff/Playout B-C', 2),
                    ('TURNO 2', 'Playoff/Playout B-C - Turno 2', 'Kings League Playoff/Playout B-C', 1),
                ],
                col_s         = col_bc,
                col_r         = col_bc + 1,
                col_t         = col_bc + 2,
                row_limite_inf = row_ab if row_ab is not None else row_ff
            )

        if row_ab is not None:
            estrai_partite_sezione(
                header_keyword = 'PLAYOFF LEGA B - PLAYOUT LEGA A',
                sub_sections   = [
                    ('TURNO 1', 'Playoff/Playout A-B - Turno 1', 'Kings League Playoff/Playout A-B', 2),
                    ('TURNO 2', 'Playoff/Playout A-B - Turno 2', 'Kings League Playoff/Playout A-B', 2),
                ],
                col_s         = col_ab,
                col_r         = col_ab + 1,
                col_t         = col_ab + 2,
                row_limite_inf = row_ff
            )

        if row_ff is not None:
            estrai_partite_sezione(
                header_keyword = 'FASE FINALE',
                sub_sections   = [
                    ('SEMIFINALI', 'Final Four - Semifinali', 'Kings League Final Four', 5),
                    ('FINALE',     'Final Four - Finale',     'Kings League Final Four', 3),
                ],
                col_s         = col_ff,
                col_r         = col_ff + 1,
                col_t         = col_ff + 2,
                row_limite_inf = None
            )

        print(f"\nKings League matches totali: {len(matches)}")
        return pd.DataFrame(matches)

    # ====== S1-S4 (formato vecchio) ======
    row_playoff_b, col_playoff_b = trova_riga_keyword('PLAYOFF LEGA B')

    if row_playoff_b is not None:
        col_s = col_playoff_b      # colonna squadra1
        col_r = col_s + 1          # colonna risultato
        col_t = col_s + 2          # colonna squadra2

        # Trova le righe dei blocchi successivi per usarle come limite.
        # PLAYOUT LEGA B esiste dalla S4 in poi (retrocessioni Lega B verso
        # futura Lega C). Se non c'è (S1-S3) la ricerca ritorna None e i
        # row_limite_inf cadono sui blocchi successivi disponibili.
        row_playout_a,    _ = trova_riga_keyword('PLAYOUT LEGA A')
        row_playout_b,    _ = trova_riga_keyword('PLAYOUT LEGA B')
        row_fase_finale,  _ = trova_riga_keyword('FASE FINALE')

        # ── PLAYOFF LEGA B ───────────────────────────────────────────
        estrai_partite_sezione(
            header_keyword = 'PLAYOFF LEGA B',
            sub_sections   = [
                ('SEMIFINALI', 'Playoff Lega B - Semifinali', 'Kings League Playoff Lega B', 5),
                ('FINALE',     'Playoff Lega B - Finale',     'Kings League Playoff Lega B', 3),
            ],
            col_s         = col_s,
            col_r         = col_r,
            col_t         = col_t,
            row_limite_inf = row_playout_a  # non sconfinare nel Playout A
        )

        # ── PLAYOUT LEGA A ───────────────────────────────────────────
        # Limite inferiore = primo header successivo presente
        # (Playout Lega B se S4+, altrimenti Fase Finale)
        estrai_partite_sezione(
            header_keyword = 'PLAYOUT LEGA A',
            sub_sections   = [
                ('FINALI', 'Playout Lega A - Finali', 'Kings League Playout Lega A', 5),
            ],
            col_s         = col_s,
            col_r         = col_r,
            col_t         = col_t,
            row_limite_inf = row_playout_b if row_playout_b is not None else row_fase_finale
        )

        # ── PLAYOUT LEGA B (S4+) ─────────────────────────────────────
        # Esiste solo dalla stagione 4. In S1-S3 trova_riga_keyword
        # ritorna None e estrai_partite_sezione esce subito.
        estrai_partite_sezione(
            header_keyword = 'PLAYOUT LEGA B',
            sub_sections   = [
                ('FINALI', 'Playout Lega B - Finali', 'Kings League Playout Lega B', 5),
            ],
            col_s         = col_s,
            col_r         = col_r,
            col_t         = col_t,
            row_limite_inf = row_fase_finale  # non sconfinare nel Final Four
        )

        # ── FINAL FOUR ───────────────────────────────────────────────
        estrai_partite_sezione(
            header_keyword = 'FASE FINALE',
            sub_sections   = [
                ('SEMIFINALI', 'Final Four - Semifinali', 'Kings League Final Four', 5),
                ('FINALE',     'Final Four - Finale',     'Kings League Final Four', 3),
            ],
            col_s         = col_s,
            col_r         = col_r,
            col_t         = col_t,
            row_limite_inf = None
        )

    print(f"\nKings League matches totali: {len(matches)}")
    return pd.DataFrame(matches)




def estrai_galactic_champions_cup(percorso_file):
    """
    Estrae le partite della Galactic Champions Cup - Fase 1.
    
    Struttura foglio:
    - Fase 1: 6 gironi da 6 squadre (Girone A-F)
    - Formato identico alla Kings League:
      col_s1 | col_r1 (andata) | col_s2 | col_r2 (ritorno) per riga
    """
    import re
    df = pd.read_excel(percorso_file, sheet_name='Galactic Champions Cup', header=None)
    matches = []

    def sv(cell):
        s = str(cell).strip()
        return None if s in ('nan', '') else s

    def is_result(cell):
        s = str(cell).strip()
        return bool(re.match(r'^\d+', s) and '-' in s)

    def parse_girone(girone_nome, col_s1, col_r1, col_s2, col_r2, row_start, row_end):
        for idx in range(row_start, row_end):
            if idx >= len(df):
                break
            s1 = sv(df.iloc[idx, col_s1])
            r1 = sv(df.iloc[idx, col_r1]) if col_r1 < len(df.columns) else None
            s2 = sv(df.iloc[idx, col_s2]) if col_s2 < len(df.columns) else None
            r2 = sv(df.iloc[idx, col_r2]) if col_r2 < len(df.columns) else None

            if s1 and r1 and s2 and is_result(r1):
                # Andata: s1 in casa
                matches.append({
                    'giornata':          f'Fase 1 - {girone_nome}',
                    'squadra_casa':      s1,
                    'risultato':         r1,
                    'squadra_trasferta': s2,
                    'tipo':              'Champions Cup',
                    'ordine':            0,
                    'Competizione':      'galactic champions cup'
                })
                # Ritorno: s2 in casa
                if r2 and is_result(r2):
                    matches.append({
                        'giornata':          f'Fase 1 - {girone_nome}',
                        'squadra_casa':      s2,
                        'risultato':         r2,
                        'squadra_trasferta': s1,
                        'tipo':              'Champions Cup',
                        'ordine':            0,
                        'Competizione':      'galactic champions cup'
                    })

    # ════════════════════════════════════════════════════════════════
    # TROVA I GIRONI DELLA FASE 1
    # ════════════════════════════════════════════════════════════════
    nomi_std = ['Girone A', 'Girone B', 'Girone C', 'Girone D', 'Girone E', 'Girone F']

    # Cerca la riga "PRIMO TURNO" come delimitatore superiore della Fase 1
    row_primo_turno = None
    for idx in range(len(df)):
        for col in range(len(df.columns)):
            cell = sv(df.iloc[idx, col])
            if cell and 'PRIMO TURNO' in cell.upper():
                row_primo_turno = idx
                break
        if row_primo_turno is not None:
            break

    # Cerca le intestazioni GIRONE X nella riga successiva a PRIMO TURNO
    # (o nelle prime righe del foglio se PRIMO TURNO non c'è)
    row_cerca_inizio = 0 if row_primo_turno is None else row_primo_turno

    girone_headers = []
    for cerca_riga in range(row_cerca_inizio, min(row_cerca_inizio + 3, len(df))):
        for col in range(len(df.columns)):
            cell = sv(df.iloc[cerca_riga, col])
            if cell and 'GIRONE' in cell.upper():
                girone_headers.append((cerca_riga, col))

    print(f"\nGalactic Champions Cup - Fase 1: trovati {len(girone_headers)} gironi")

    for i, (gr_row, gr_col) in enumerate(girone_headers[:6]):
        col_s1 = gr_col
        col_r1 = gr_col + 1
        col_s2 = gr_col + 2
        col_r2 = gr_col + 3

        # row_start: salta righe di classifica
        row_start = gr_row + 1
        while row_start < len(df):
            cell_s = sv(df.iloc[row_start, col_s1])
            cell_r = sv(df.iloc[row_start, col_r1]) if col_r1 < len(df.columns) else None
            if cell_s and cell_r and is_result(cell_r):
                break
            row_start += 1

        # row_end: fermati alle righe vuote
        row_end = row_start
        empty_count = 0
        while row_end < len(df) and empty_count < 4:
            s1 = sv(df.iloc[row_end, col_s1])
            r1 = sv(df.iloc[row_end, col_r1]) if col_r1 < len(df.columns) else None
            if s1 and r1 and is_result(r1):
                empty_count = 0
                row_end += 1
            else:
                empty_count += 1
                row_end += 1

        nome = nomi_std[i] if i < len(nomi_std) else f'Girone {i+1}'
        print(f"  → {nome}: righe {row_start}-{row_end}, colonne {col_s1}/{col_r1}/{col_s2}/{col_r2}")
        parse_girone(nome, col_s1, col_r1, col_s2, col_r2, row_start, row_end)

    print(f"\nChampions Cup Fase 1 matches totali: {len(matches)}")

    # ════════════════════════════════════════════════════════════════
    # FASE 2 - 6 gironi da 4 squadre, partite secche in campo neutro
    # Layout per girone: 3 colonne (squadra_casa | risultato | squadra_trasferta)
    # ════════════════════════════════════════════════════════════════
    def parse_girone_fase2(girone_nome, col_s1, col_r, col_s2, row_start, row_end):
        for idx in range(row_start, row_end):
            if idx >= len(df):
                break
            s1 = sv(df.iloc[idx, col_s1])
            r  = sv(df.iloc[idx, col_r])  if col_r  < len(df.columns) else None
            s2 = sv(df.iloc[idx, col_s2]) if col_s2 < len(df.columns) else None
            if s1 and r and s2 and is_result(r):
                matches.append({
                    'giornata':          f'Fase 2 - {girone_nome}',
                    'squadra_casa':      s1,
                    'risultato':         r,
                    'squadra_trasferta': s2,
                    'tipo':              'Champions Cup',
                    'ordine':            0,
                    'Competizione':      'galactic champions cup'
                })

    # Cerca le intestazioni "Girone X" della Fase 2 (sotto l'ultima riga di Fase 1)
    fase1_last_row = max((r for r, _ in girone_headers[:6]), default=0)
    fase2_headers = []
    for idx in range(fase1_last_row + 1, len(df)):
        for col in range(len(df.columns)):
            cell = sv(df.iloc[idx, col])
            if cell and re.match(r'^Girone\s+[A-F]$', cell, re.IGNORECASE):
                fase2_headers.append((idx, col))

    print(f"\nGalactic Champions Cup - Fase 2: trovati {len(fase2_headers)} gironi")

    matches_fase1_count = len(matches)
    for i, (gr_row, gr_col) in enumerate(fase2_headers[:6]):
        col_s1 = gr_col
        col_r  = gr_col + 1
        col_s2 = gr_col + 2

        # row_start: salta righe di classifica fino alla prima partita
        row_start = gr_row + 1
        while row_start < len(df):
            cell_s = sv(df.iloc[row_start, col_s1])
            cell_r = sv(df.iloc[row_start, col_r]) if col_r < len(df.columns) else None
            if cell_s and cell_r and is_result(cell_r):
                break
            row_start += 1

        # row_end: fermati dopo righe vuote consecutive
        row_end = row_start
        empty_count = 0
        while row_end < len(df) and empty_count < 4:
            s1 = sv(df.iloc[row_end, col_s1])
            r  = sv(df.iloc[row_end, col_r]) if col_r < len(df.columns) else None
            if s1 and r and is_result(r):
                empty_count = 0
                row_end += 1
            else:
                empty_count += 1
                row_end += 1

        nome = nomi_std[i] if i < len(nomi_std) else f'Girone {i+1}'
        print(f"  → {nome}: righe {row_start}-{row_end}, colonne {col_s1}/{col_r}/{col_s2}")
        parse_girone_fase2(nome, col_s1, col_r, col_s2, row_start, row_end)

    print(f"\nChampions Cup Fase 2 matches totali: {len(matches) - matches_fase1_count}")

    # ════════════════════════════════════════════════════════════════
    # FASE 3 - Fase Finale (Ottavi → Quarti → Semifinali → Finale)
    # Tutte partite secche in campo neutro
    # Layout brackets a colonne fisse:
    #   Ottavi sinistra   F=5  G=6   (team | score), 4 match su 2 righe
    #   Quarti sinistra   H=7  I=8   (team | score), 2 match su 2 righe
    #   Semi sinistra     J=9  K=10  (team | score), 1 match su 2 righe
    #   Finale            K=10 L=11 M=12 (team1 | risultato | team2) UNA riga
    #   Semi destra       M=12 N=13  (score | team), 1 match su 2 righe
    #   Quarti destra     O=14 P=15  (score | team), 2 match su 2 righe
    #   Ottavi destra     Q=16 R=17  (score | team), 4 match su 2 righe
    # Offset relativi alla riga di inizio brackets (left ottavi):
    #   Ottavi: 0, 4, 8, 12   Quarti: 2, 10   Semi: 6   Finale: 10
    # ════════════════════════════════════════════════════════════════
    def parse_score_cell(s):
        """Parse '3', '2*[0]', '1(4)', '1[1]', '1*[0](4)' → dict con score/regular/penalties."""
        if not s:
            return None
        s = str(s).strip()
        m = re.match(r'^(\d+)', s)
        if not m:
            return None
        extra = re.search(r'\[(\d+)\]', s)
        pen   = re.search(r'\((\d+)\)', s)
        return {
            'score':     int(m.group(1)),
            'regular':   int(extra.group(1)) if extra else None,
            'penalties': int(pen.group(1))   if pen   else None,
        }

    def format_bracket_result(p1, p2):
        result = f"{p1['score']}-{p2['score']}"
        if p1['regular'] is not None and p2['regular'] is not None:
            result += f" [{p1['regular']}-{p2['regular']}]"
        if p1['penalties'] is not None and p2['penalties'] is not None:
            result += f" ({p1['penalties']}-{p2['penalties']})"
        return result

    def add_bracket_match(team1, score1, team2, score2, giornata, ordine):
        if not team1 or not team2 or not score1 or not score2:
            return False
        p1 = parse_score_cell(score1)
        p2 = parse_score_cell(score2)
        if not p1 or not p2:
            return False
        matches.append({
            'giornata':          giornata,
            'squadra_casa':      team1,
            'risultato':         format_bracket_result(p1, p2),
            'squadra_trasferta': team2,
            'tipo':              'Champions Cup',
            'ordine':            ordine,
            'Competizione':      'galactic champions cup'
        })
        return True

    # ════════════════════════════════════════════════════════════════
    # Layout brackets — varia tra stagioni:
    # Layout A (Stagione 1):  rounds contigui, ottavi sx F-G
    # Layout B (Stagione 2+): 1 col di gap fra rounds, ottavi sx D-E
    # ════════════════════════════════════════════════════════════════
    layouts = {
        'A': {  # Stagione 1
            'ottavi_sx': (5, 6),    # F-G  (team, score)
            'quarti_sx': (7, 8),    # H-I
            'semi_sx':   (9, 10),   # J-K
            'finale':    (10, 11, 12),  # K-L-M (team1, ris, team2)
            'semi_dx':   (13, 12),  # N-M  (team, score) — score a sx, team a dx
            'quarti_dx': (15, 14),  # P-O
            'ottavi_dx': (17, 16),  # R-Q
        },
        'B': {  # Stagione 2+ (1 col di gap)
            'ottavi_sx': (3, 4),    # D-E
            'quarti_sx': (6, 7),    # G-H
            'semi_sx':   (9, 10),   # J-K
            'finale':    (10, 11, 12),  # K-L-M
            'semi_dx':   (13, 12),  # N-M
            'quarti_dx': (16, 15),  # Q-P
            'ottavi_dx': (19, 18),  # T-S
        },
    }

    def trova_bracket_start(col_team, col_score):
        """Cerca la prima coppia di righe con team+score validi in (col_team, col_score)."""
        for idx in range(fase2_last_row + 1, len(df) - 1):
            if col_team >= len(df.columns) or col_score >= len(df.columns):
                return None
            t1 = sv(df.iloc[idx,     col_team])
            s1 = sv(df.iloc[idx,     col_score])
            t2 = sv(df.iloc[idx + 1, col_team])
            s2 = sv(df.iloc[idx + 1, col_score])
            if (t1 and s1 and t2 and s2
                    and re.match(r'^[A-Za-z]', t1)
                    and re.match(r'^\d',       s1)
                    and re.match(r'^[A-Za-z]', t2)
                    and re.match(r'^\d',       s2)):
                return idx
        return None

    fase2_last_row = max((r for r, _ in fase2_headers[:6]), default=0)

    # Rileva layout: prova A (F-G) poi B (D-E)
    bracket_start_row = None
    layout_key = None
    for key in ('A', 'B'):
        col_team, col_score = layouts[key]['ottavi_sx']
        start = trova_bracket_start(col_team, col_score)
        if start is not None:
            bracket_start_row = start
            layout_key = key
            break

    matches_before_fase3 = len(matches)
    if bracket_start_row is None:
        print("\nGalactic Champions Cup - Fase 3: brackets non trovati")
    else:
        print(f"\nGalactic Champions Cup - Fase 3: layout {layout_key}, "
              f"brackets a partire dalla riga {bracket_start_row}")
        b = bracket_start_row
        cols = layouts[layout_key]

        c_o_sx_t, c_o_sx_s = cols['ottavi_sx']
        c_q_sx_t, c_q_sx_s = cols['quarti_sx']
        c_s_sx_t, c_s_sx_s = cols['semi_sx']
        c_fin_t1, c_fin_r, c_fin_t2 = cols['finale']
        c_s_dx_t, c_s_dx_s = cols['semi_dx']
        c_q_dx_t, c_q_dx_s = cols['quarti_dx']
        c_o_dx_t, c_o_dx_s = cols['ottavi_dx']

        # Ottavi sinistra — 4 match (team | score)
        for i, off in enumerate([0, 4, 8, 12]):
            r = b + off
            if r + 1 >= len(df): continue
            add_bracket_match(
                sv(df.iloc[r,     c_o_sx_t]), sv(df.iloc[r,     c_o_sx_s]),
                sv(df.iloc[r + 1, c_o_sx_t]), sv(df.iloc[r + 1, c_o_sx_s]),
                'Fase 3 - Ottavi di Finale', i
            )

        # Ottavi destra — 4 match (score | team)
        for i, off in enumerate([0, 4, 8, 12]):
            r = b + off
            if r + 1 >= len(df): continue
            add_bracket_match(
                sv(df.iloc[r,     c_o_dx_t]), sv(df.iloc[r,     c_o_dx_s]),
                sv(df.iloc[r + 1, c_o_dx_t]), sv(df.iloc[r + 1, c_o_dx_s]),
                'Fase 3 - Ottavi di Finale', i + 4
            )

        # Quarti sinistra — 2 match
        for i, off in enumerate([2, 10]):
            r = b + off
            if r + 1 >= len(df): continue
            add_bracket_match(
                sv(df.iloc[r,     c_q_sx_t]), sv(df.iloc[r,     c_q_sx_s]),
                sv(df.iloc[r + 1, c_q_sx_t]), sv(df.iloc[r + 1, c_q_sx_s]),
                'Fase 3 - Quarti di Finale', i
            )

        # Quarti destra — 2 match (score | team)
        for i, off in enumerate([2, 10]):
            r = b + off
            if r + 1 >= len(df): continue
            add_bracket_match(
                sv(df.iloc[r,     c_q_dx_t]), sv(df.iloc[r,     c_q_dx_s]),
                sv(df.iloc[r + 1, c_q_dx_t]), sv(df.iloc[r + 1, c_q_dx_s]),
                'Fase 3 - Quarti di Finale', i + 2
            )

        # Semifinale sinistra — 1 match
        r = b + 6
        if r + 1 < len(df):
            add_bracket_match(
                sv(df.iloc[r,     c_s_sx_t]), sv(df.iloc[r,     c_s_sx_s]),
                sv(df.iloc[r + 1, c_s_sx_t]), sv(df.iloc[r + 1, c_s_sx_s]),
                'Fase 3 - Semifinale', 0
            )

        # Semifinale destra — 1 match (score | team)
        if r + 1 < len(df):
            add_bracket_match(
                sv(df.iloc[r,     c_s_dx_t]), sv(df.iloc[r,     c_s_dx_s]),
                sv(df.iloc[r + 1, c_s_dx_t]), sv(df.iloc[r + 1, c_s_dx_s]),
                'Fase 3 - Semifinale', 1
            )

        # Finale (team1 | risultato | team2) — 1 riga
        r = b + 10
        if r < len(df):
            t1  = sv(df.iloc[r, c_fin_t1])
            ris = sv(df.iloc[r, c_fin_r])
            t2  = sv(df.iloc[r, c_fin_t2])
            if t1 and ris and t2 and is_result(ris):
                matches.append({
                    'giornata':          'Fase 3 - Finale',
                    'squadra_casa':      t1,
                    'risultato':         ris,
                    'squadra_trasferta': t2,
                    'tipo':              'Champions Cup',
                    'ordine':            0,
                    'Competizione':      'galactic champions cup'
                })
            else:
                print(f"  ⚠️  Finale non trovata a riga {r}: "
                      f"col {c_fin_t1}={t1!r} col {c_fin_r}={ris!r} col {c_fin_t2}={t2!r}")

    print(f"Champions Cup Fase 3 matches totali: {len(matches) - matches_before_fase3}")
    print(f"Champions Cup matches totali (Fase 1 + Fase 2 + Fase 3): {len(matches)}")
    return pd.DataFrame(matches)




def estrai_intergalactic_supercup(percorso_file):
    """
    Estrae le partite della Intergalactic SuperCup.

    Due layout supportati (rilevamento automatico):

    Layout A (stagioni 1-2, sezioni contigue):
        Semifinale 1:  F4-F5 / G4-G5         (pandas rows 3-4)
        Finale:        H6-H7 / I6-I7         (pandas rows 5-6, cols 7-8)
        Semifinale 2:  F8-F9 / G8-G9         (pandas rows 7-8)

    Layout B (stagioni 3+, con righe vuote di gap):
        Semifinale 1:  F4-F5 / G4-G5         (pandas rows 3-4)
        Finale:        I8-I9 / J8-J9         (pandas rows 7-8, cols 8-9)
        Semifinale 2:  F11-F12 / G11-G12     (pandas rows 10-11)

    Tutte partite secche in campo neutro, formato team/score su 2 righe.
    """
    import re
    df = pd.read_excel(percorso_file, sheet_name='Intergalactic SuperCup', header=None)
    matches = []

    def sv(cell):
        s = str(cell).strip()
        return None if s in ('nan', '') else s

    def parse_score_cell(s):
        if not s:
            return None
        s = str(s).strip()
        m = re.match(r'^(\d+)', s)
        if not m:
            return None
        extra = re.search(r'\[(\d+)\]', s)
        pen   = re.search(r'\((\d+)\)', s)
        return {
            'score':     int(m.group(1)),
            'regular':   int(extra.group(1)) if extra else None,
            'penalties': int(pen.group(1))   if pen   else None,
        }

    def format_result(p1, p2):
        result = f"{p1['score']}-{p2['score']}"
        if p1['regular'] is not None and p2['regular'] is not None:
            result += f" [{p1['regular']}-{p2['regular']}]"
        if p1['penalties'] is not None and p2['penalties'] is not None:
            result += f" ({p1['penalties']}-{p2['penalties']})"
        return result

    def add_match(row1, row2, col_team, col_score, giornata, ordine):
        if row2 >= len(df):
            return
        t1 = sv(df.iloc[row1, col_team])
        s1 = sv(df.iloc[row1, col_score])
        t2 = sv(df.iloc[row2, col_team])
        s2 = sv(df.iloc[row2, col_score])
        if not (t1 and s1 and t2 and s2):
            return
        p1 = parse_score_cell(s1)
        p2 = parse_score_cell(s2)
        if not p1 or not p2:
            return
        matches.append({
            'giornata':          giornata,
            'squadra_casa':      t1,
            'risultato':         format_result(p1, p2),
            'squadra_trasferta': t2,
            'tipo':              'SuperCup',
            'ordine':            ordine,
            'Competizione':      'intergalactic supercup'
        })

    # ════════════════════════════════════════════════════════════════
    # Detection dinamica: scansiona tutte le coppie di righe consecutive
    # con (team, score) in (col_c, col_c+1). SuperCup ha sempre 3 match:
    # 2 semifinali alla stessa colonna + 1 finale ad altra colonna.
    # Robusto a qualsiasi layout (S1/S2 contiguo, S3+ con righe vuote, ecc).
    # ════════════════════════════════════════════════════════════════
    from collections import Counter

    pairs = []
    for r in range(len(df) - 1):
        for c in range(len(df.columns) - 1):
            t1 = sv(df.iloc[r,     c])
            s1 = sv(df.iloc[r,     c + 1])
            t2 = sv(df.iloc[r + 1, c])
            s2 = sv(df.iloc[r + 1, c + 1])
            if (t1 and s1 and t2 and s2
                    and re.match(r'^[A-Za-z]', t1)
                    and re.match(r'^\d',       s1)
                    and re.match(r'^[A-Za-z]', t2)
                    and re.match(r'^\d',       s2)):
                pairs.append((r, r + 1, c, c + 1))

    # Filtro: rimuovi pair che si sovrappongono (la stessa coppia di righe
    # potrebbe essere catturata in posizioni adiacenti). Per ogni team/score
    # tieni solo il primo c trovato.
    seen = set()
    unique_pairs = []
    for p in pairs:
        key = (p[0], p[1])
        if key in seen: continue
        seen.add(key)
        unique_pairs.append(p)

    if len(unique_pairs) < 3:
        print(f"⚠️  SuperCup: trovati solo {len(unique_pairs)} match (atteso 3)")

    # 2 semifinali alla stessa colonna, 1 finale ad altra colonna
    col_counts = Counter(p[2] for p in unique_pairs)
    if len(col_counts) >= 2:
        semi_col = col_counts.most_common(1)[0][0]
        semis = sorted(
            [p for p in unique_pairs if p[2] == semi_col],
            key=lambda p: p[0]
        )
        finales = [p for p in unique_pairs if p[2] != semi_col]

        for i, (r1, r2, ct, cs) in enumerate(semis[:2]):
            add_match(r1, r2, ct, cs, 'Semifinale SuperCup', i)
        if finales:
            r1, r2, ct, cs = finales[0]
            add_match(r1, r2, ct, cs, 'Finale SuperCup', 0)
    else:
        # fallback: tutti alla stessa colonna (improbabile ma copriamo il caso)
        sorted_pairs = sorted(unique_pairs, key=lambda p: p[0])
        for i, (r1, r2, ct, cs) in enumerate(sorted_pairs[:2]):
            add_match(r1, r2, ct, cs, 'Semifinale SuperCup', i)
        if len(sorted_pairs) >= 3:
            r1, r2, ct, cs = sorted_pairs[2]
            add_match(r1, r2, ct, cs, 'Finale SuperCup', 0)

    print(f"\nIntergalactic SuperCup matches totali: {len(matches)}")
    return pd.DataFrame(matches)




def estrai_cup_of_8(percorso_file):
    """
    Estrae le partite della Cup of 8 (formato stagioni 1-2).
    Da stagione 3 il formato diventa Cup of 10 (con ottavi) e sarà gestito a parte.

    Struttura foglio (posizioni fisse, indici pandas in parentesi):
    - Quarti di Finale: 4 match in E-F (4-5), partita secca
      in casa della squadra in alto (ranking più alto)
        QF1: E5-F5 / E6-F6   → pandas (4,4-5) / (5,4-5)
        QF2: E9-F9 / E10-F10 → (8,..) / (9,..)
        QF3: E13-F13 / E14-F14 → (12,..) / (13,..)
        QF4: E17-F17 / E18-F18 → (16,..) / (17,..)
    - Semifinali: 2 match in H-I (7-8), campo neutro
        SF1: H7-I7 / H8-I8   → (6,..) / (7,..)
        SF2: H15-I15 / H16-I16 → (14,..) / (15,..)
    - Finale: 1 match in K-L (10-11), campo neutro
        F: K11-L11 / K12-L12 → (10,..) / (11,..)
    """
    import re
    df = pd.read_excel(percorso_file, sheet_name='Cup of 8', header=None)
    matches = []

    def sv(cell):
        s = str(cell).strip()
        return None if s in ('nan', '') else s

    def parse_score_cell(s):
        if not s:
            return None
        s = str(s).strip()
        m = re.match(r'^(\d+)', s)
        if not m:
            return None
        extra = re.search(r'\[(\d+)\]', s)
        pen   = re.search(r'\((\d+)\)', s)
        return {
            'score':     int(m.group(1)),
            'regular':   int(extra.group(1)) if extra else None,
            'penalties': int(pen.group(1))   if pen   else None,
        }

    def format_result(p1, p2):
        result = f"{p1['score']}-{p2['score']}"
        if p1['regular'] is not None and p2['regular'] is not None:
            result += f" [{p1['regular']}-{p2['regular']}]"
        if p1['penalties'] is not None and p2['penalties'] is not None:
            result += f" ({p1['penalties']}-{p2['penalties']})"
        return result

    def add_match(row1, row2, col_team, col_score, giornata, ordine):
        if row2 >= len(df):
            return
        t1 = sv(df.iloc[row1, col_team])
        s1 = sv(df.iloc[row1, col_score])
        t2 = sv(df.iloc[row2, col_team])
        s2 = sv(df.iloc[row2, col_score])
        if not (t1 and s1 and t2 and s2):
            return
        p1 = parse_score_cell(s1)
        p2 = parse_score_cell(s2)
        if not p1 or not p2:
            return
        matches.append({
            'giornata':          giornata,
            'squadra_casa':      t1,
            'risultato':         format_result(p1, p2),
            'squadra_trasferta': t2,
            'tipo':              'Cup of 8',
            'ordine':            ordine,
            'Competizione':      'cup of 8'
        })

    # Quarti di Finale (E-F = 4-5)
    for i, (r1, r2) in enumerate([(4, 5), (8, 9), (12, 13), (16, 17)]):
        add_match(r1, r2, 4, 5, 'Quarti Cup of 8', i)

    # Semifinali (H-I = 7-8)
    for i, (r1, r2) in enumerate([(6, 7), (14, 15)]):
        add_match(r1, r2, 7, 8, 'Semifinale Cup of 8', i)

    # Finale (K-L = 10-11)
    add_match(10, 11, 10, 11, 'Finale Cup of 8', 0)

    print(f"\nCup of 8 matches totali: {len(matches)}")
    return pd.DataFrame(matches)




def estrai_cup_of_10(percorso_file):
    """
    Estrae le partite della Cup of 10 (formato dalla stagione 3 in poi).

    Struttura foglio (posizioni fisse, indici pandas in parentesi):
    - Ottavi (turno preliminare): 2 match in B-C (1-2),
      partita secca, in casa della squadra in alto (più alta nel ranking)
        Ottavi A (7 vs 10): righe Excel 6-7  → pandas (5,6)
        Ottavi B (8 vs 9):  righe Excel 14-15 → pandas (13,14)
    - Quarti: 4 match in E-F (4-5), in casa squadra in alto
        QF1 (2 vs vinc. A): righe 4-5   → (3,4)   — winner di 7v10 affronta la 2
        QF2 (4 vs 5):        righe 9-10  → (8,9)
        QF3 (1 vs vinc. B): righe 13-14 → (12,13) — winner di 8v9 affronta la 1
        QF4 (3 vs 6):        righe 17-18 → (16,17)
    - Semifinali: 2 match in H-I (7-8), campo neutro
        Semi 1: righe 7-8   → (6,7)
        Semi 2: righe 15-16 → (14,15)
    - Finale: 1 match in K-L (10-11), campo neutro
        Finale: righe 11-12 → (10,11)

    Tutte partite secche (single-leg), formato team/score su 2 righe.
    Cup of 10 NON concorre al ranking (come Cup of 8).
    """
    import re
    df = pd.read_excel(percorso_file, sheet_name='Cup of 10', header=None)
    matches = []

    def sv(cell):
        s = str(cell).strip()
        return None if s in ('nan', '') else s

    def parse_score_cell(s):
        if not s:
            return None
        s = str(s).strip()
        m = re.match(r'^(\d+)', s)
        if not m:
            return None
        extra = re.search(r'\[(\d+)\]', s)
        pen   = re.search(r'\((\d+)\)', s)
        return {
            'score':     int(m.group(1)),
            'regular':   int(extra.group(1)) if extra else None,
            'penalties': int(pen.group(1))   if pen   else None,
        }

    def format_result(p1, p2):
        result = f"{p1['score']}-{p2['score']}"
        if p1['regular'] is not None and p2['regular'] is not None:
            result += f" [{p1['regular']}-{p2['regular']}]"
        if p1['penalties'] is not None and p2['penalties'] is not None:
            result += f" ({p1['penalties']}-{p2['penalties']})"
        return result

    def add_match(row1, row2, col_team, col_score, giornata, ordine):
        if row2 >= len(df) or col_score >= len(df.columns):
            return
        t1 = sv(df.iloc[row1, col_team])
        s1 = sv(df.iloc[row1, col_score])
        t2 = sv(df.iloc[row2, col_team])
        s2 = sv(df.iloc[row2, col_score])
        if not (t1 and s1 and t2 and s2):
            return
        p1 = parse_score_cell(s1)
        p2 = parse_score_cell(s2)
        if not p1 or not p2:
            return
        matches.append({
            'giornata':          giornata,
            'squadra_casa':      t1,
            'risultato':         format_result(p1, p2),
            'squadra_trasferta': t2,
            'tipo':              'Cup of 10',
            'ordine':            ordine,
            'Competizione':      'cup of 10'
        })

    # Ottavi (B-C = 1-2)
    add_match(5,  6,  1, 2, 'Ottavi Cup of 10', 0)   # 7 vs 10
    add_match(13, 14, 1, 2, 'Ottavi Cup of 10', 1)   # 8 vs 9

    # Quarti (E-F = 4-5)
    add_match(4,  5,  4, 5, 'Quarti Cup of 10', 0)   # 2 vs vincente Ottavi A
    add_match(8,  9,  4, 5, 'Quarti Cup of 10', 1)   # 4 vs 5
    add_match(12, 13, 4, 5, 'Quarti Cup of 10', 2)   # 1 vs vincente Ottavi B
    add_match(16, 17, 4, 5, 'Quarti Cup of 10', 3)   # 3 vs 6

    # Semifinali (H-I = 7-8)
    add_match(6,  7,  7, 8, 'Semifinale Cup of 10', 0)
    add_match(14, 15, 7, 8, 'Semifinale Cup of 10', 1)

    # Finale (K-L = 10-11)
    add_match(10, 11, 10, 11, 'Finale Cup of 10', 0)

    print(f"\nCup of 10 matches totali: {len(matches)}")
    return pd.DataFrame(matches)




def estrai_partite_giornate(percorso_file):
    """
    Estrae tutte le partite dalle Giornate 1-8, Play Off, Fase Finale
    dalla Galactic League e dalla Galactic Cup.
    """
    df_raw_league = pd.read_excel(percorso_file, sheet_name='Galactic League', header=None)
    partite_list = []

    # ════════════════════════════════════════════════════════════════
    # GIORNATE 1-8
    # ════════════════════════════════════════════════════════════════
    giornate_config = [
        {'giornata': 1, 'inizio_riga': 1,  'fine_riga': 19, 'colonne': (1,  2,  3)},
        {'giornata': 2, 'inizio_riga': 1,  'fine_riga': 19, 'colonne': (5,  6,  7)},
        {'giornata': 3, 'inizio_riga': 1,  'fine_riga': 19, 'colonne': (9,  10, 11)},
        {'giornata': 4, 'inizio_riga': 1,  'fine_riga': 19, 'colonne': (13, 14, 15)},
        {'giornata': 5, 'inizio_riga': 21, 'fine_riga': 45, 'colonne': (1,  2,  3)},
        {'giornata': 6, 'inizio_riga': 21, 'fine_riga': 45, 'colonne': (5,  6,  7)},
        {'giornata': 7, 'inizio_riga': 21, 'fine_riga': 45, 'colonne': (9,  10, 11)},
        {'giornata': 8, 'inizio_riga': 21, 'fine_riga': 45, 'colonne': (13, 14, 15)},
    ]

    for config in giornate_config:
        col_casa, col_risultato, col_trasferta = config['colonne']
        for idx in range(config['inizio_riga'], config['fine_riga']):
            if idx >= len(df_raw_league):
                break
            sq_casa = df_raw_league.iloc[idx, col_casa]
            ris      = df_raw_league.iloc[idx, col_risultato]
            sq_tras  = df_raw_league.iloc[idx, col_trasferta]

            if pd.notna(sq_casa) and pd.notna(ris) and pd.notna(sq_tras):
                sq_casa = str(sq_casa).strip()
                ris     = str(ris).strip()
                sq_tras = str(sq_tras).strip()
                if '-' in ris:
                    partite_list.append({
                        'giornata':          f'Giornata {config["giornata"]}',
                        'squadra_casa':      sq_casa,
                        'risultato':         ris,
                        'squadra_trasferta': sq_tras,
                        'tipo':              'League',
                        'ordine':            0
                    })

    # ════════════════════════════════════════════════════════════════
    # FASE FINALE GALACTIC LEAGUE — Detection dinamica
    # Cerca gli header (TURNO PRELIMINARE, OTTAVI DI FINALE, ecc.) ovunque
    # nel foglio. Posizioni cambiano tra stagioni:
    #   S1-S3: TURNO PRELIMINARE a destra (col 21+), formato 4-col 1-row
    #   S4+:   TURNO PRELIMINARE a sinistra delle altre, formato 3-col 2-row
    # Detection del formato Turno Preliminare via presenza del trattino.
    # ════════════════════════════════════════════════════════════════

    def _find_header(df, text):
        """Cerca text (uguaglianza case-insensitive) ovunque nel foglio.
        Restituisce (row, col) o (None, None)."""
        target = text.upper()
        for r in range(len(df)):
            for c in range(len(df.columns)):
                cell = df.iloc[r, c]
                if pd.notna(cell) and str(cell).strip().upper() == target:
                    return (r, c)
        return (None, None)

    def _parse_round_andata_ritorno(df, header_row, col_sq, max_matches,
                                    nome_andata, nome_ritorno, tipo):
        """Estrae match in formato 3-col 2-row (team | gol_andata | gol_ritorno).
        Una match sono due righe consecutive (squadra1 sopra, squadra2 sotto).
        Usato per S4+ Turno Preliminare e per Ottavi/Quarti/Semi di tutte le stagioni."""
        col_ga = col_sq + 1
        col_gr = col_sq + 2
        out = []
        i = header_row + 1
        match_count = 0
        empty_streak = 0
        while i < len(df) - 1 and match_count < max_matches and empty_streak < 20:
            s1   = df.iloc[i,   col_sq]
            ga1  = df.iloc[i,   col_ga]  if col_ga < len(df.columns) else None
            gr1  = df.iloc[i,   col_gr]  if col_gr < len(df.columns) else None
            s2   = df.iloc[i+1, col_sq]
            ga2  = df.iloc[i+1, col_ga]  if col_ga < len(df.columns) else None
            gr2  = df.iloc[i+1, col_gr]  if col_gr < len(df.columns) else None
            validi = (pd.notna(s1) and pd.notna(ga1) and pd.notna(gr1) and
                      pd.notna(s2) and pd.notna(ga2) and pd.notna(gr2))
            if validi:
                s1  = str(s1).strip();  s2  = str(s2).strip()
                ga1 = str(ga1).strip(); ga2 = str(ga2).strip()
                gr1 = str(gr1).strip(); gr2 = str(gr2).strip()
                if (s1.replace(' ', '').replace('.', '').isdigit() or
                    s2.replace(' ', '').replace('.', '').isdigit()):
                    empty_streak += 1; i += 1; continue
                try:
                    g_a1, supp_a1, rig_a1, _ = estrai_gol_e_extra(ga1)
                    g_a2, supp_a2, rig_a2, _ = estrai_gol_e_extra(ga2)
                    g_r1, supp_r1, rig_r1, _ = estrai_gol_e_extra(gr1)
                    g_r2, supp_r2, rig_r2, _ = estrai_gol_e_extra(gr2)
                except Exception:
                    empty_streak += 1; i += 1; continue
                ris_andata = f'{g_a1}-{g_a2}'
                if supp_a1 and supp_a2:
                    ris_andata += f' [{supp_a1}-{supp_a2}]'
                if rig_a1 and rig_a2:
                    ris_andata += f' ({rig_a1}-{rig_a2})'
                ris_ritorno = f'{g_r2}-{g_r1}'
                if supp_r1 and supp_r2:
                    ris_ritorno += f' [{supp_r2}-{supp_r1}]'
                if rig_r1 and rig_r2:
                    ris_ritorno += f' ({rig_r2}-{rig_r1})'
                out.append({
                    'giornata':          nome_andata,
                    'squadra_casa':      s1,
                    'risultato':         ris_andata,
                    'squadra_trasferta': s2,
                    'tipo':              tipo,
                    'ordine':            0
                })
                out.append({
                    'giornata':          nome_ritorno,
                    'squadra_casa':      s2,
                    'risultato':         ris_ritorno,
                    'squadra_trasferta': s1,
                    'tipo':              tipo,
                    'ordine':            1
                })
                empty_streak = 0
                match_count += 1
                i += 2
            else:
                empty_streak += 1
                i += 1
        return out

    # ── TURNO PRELIMINARE (Play Off) ────────────────────────────────
    tp_row, tp_col = _find_header(df_raw_league, 'TURNO PRELIMINARE')
    if tp_row is not None:
        # Detection formato: cerco un trattino in col+1 nei primi data row.
        # Con dash → formato S1-S3 (team1 | risultato_andata | team2 | risultato_ritorno)
        # Senza dash → formato S4+ (team | gol_andata | gol_ritorno, 2 righe)
        is_4col_format = False
        for offset in range(1, 6):
            r = tp_row + offset
            if r >= len(df_raw_league): break
            if tp_col + 1 >= len(df_raw_league.columns): break
            cell = df_raw_league.iloc[r, tp_col + 1]
            if pd.notna(cell):
                s = str(cell).strip()
                if '-' in s:
                    is_4col_format = True
                break

        if is_4col_format:
            # S1-S3: team1 | ris_andata | team2 | ris_ritorno
            for idx in range(tp_row + 1, len(df_raw_league)):
                if tp_col + 3 >= len(df_raw_league.columns): break
                sq_casa = df_raw_league.iloc[idx, tp_col]
                ris_and = df_raw_league.iloc[idx, tp_col + 1]
                sq_tras = df_raw_league.iloc[idx, tp_col + 2]
                ris_rit = df_raw_league.iloc[idx, tp_col + 3]
                if pd.isna(sq_casa):
                    break
                if pd.notna(sq_casa) and pd.notna(ris_and) and pd.notna(sq_tras):
                    sq_casa = str(sq_casa).strip()
                    ris_and = str(ris_and).strip()
                    sq_tras = str(sq_tras).strip()
                    if '-' in ris_and:
                        partite_list.append({
                            'giornata':          'Play Off - Andata',
                            'squadra_casa':      sq_casa,
                            'risultato':         ris_and,
                            'squadra_trasferta': sq_tras,
                            'tipo':              'Preliminare',
                            'ordine':            0
                        })
                    if pd.notna(ris_rit):
                        ris_rit_str = str(ris_rit).strip()
                        if '-' in ris_rit_str:
                            partite_list.append({
                                'giornata':          'Play Off - Ritorno',
                                'squadra_casa':      sq_tras,
                                'risultato':         ris_rit_str,
                                'squadra_trasferta': sq_casa,
                                'tipo':              'Preliminare',
                                'ordine':            1
                            })
        else:
            # S4+: stesso formato 3-col 2-row degli Ottavi
            partite_list.extend(_parse_round_andata_ritorno(
                df_raw_league, tp_row, tp_col, max_matches=8,
                nome_andata='Play Off - Andata',
                nome_ritorno='Play Off - Ritorno',
                tipo='Preliminare'
            ))

    # ── OTTAVI / QUARTI / SEMIFINALI ────────────────────────────────
    for nome, header, max_m in [
        ('Ottavi',     'OTTAVI DI FINALE', 8),
        ('Quarti',     'QUARTI DI FINALE', 8),
        ('Semifinale', 'SEMIFINALE',       2),
    ]:
        h_row, h_col = _find_header(df_raw_league, header)
        if h_row is None:
            continue
        partite_list.extend(_parse_round_andata_ritorno(
            df_raw_league, h_row, h_col, max_matches=max_m,
            nome_andata=f'{nome} League - Andata',
            nome_ritorno=f'{nome} League - Ritorno',
            tipo='Playoff'
        ))

    # ── FINALE ──────────────────────────────────────────────────────
    f_row, f_col = _find_header(df_raw_league, 'FINALE')
    if f_row is not None:
        squadre_finale = []
        # Trova la prima riga con team+gol sotto l'header, poi la riga successiva
        first_data_row = None
        for offset in range(1, 10):
            idx = f_row + offset
            if idx >= len(df_raw_league): break
            if f_col + 1 >= len(df_raw_league.columns): break
            sq  = df_raw_league.iloc[idx, f_col]
            gol = df_raw_league.iloc[idx, f_col + 1]
            if pd.notna(sq) and pd.notna(gol):
                first_data_row = idx
                break

        if first_data_row is not None:
            for off in (0, 1):
                idx = first_data_row + off
                if idx >= len(df_raw_league): break
                sq  = df_raw_league.iloc[idx, f_col]
                gol = df_raw_league.iloc[idx, f_col + 1] if f_col + 1 < len(df_raw_league.columns) else None
                if pd.notna(sq) and pd.notna(gol):
                    gol_str = str(gol).strip()
                    if not gol_str[:1].isdigit():
                        continue
                    # Conserviamo la stringa grezza: contiene anche i supplementari
                    # [X] e/o i rigori (A) che NON vanno persi (bug finale league).
                    squadre_finale.append({'squadra': str(sq).strip(), 'gol_str': gol_str})

        if len(squadre_finale) == 2:
            g0, supp0, rig0, _ = estrai_gol_e_extra(squadre_finale[0]['gol_str'])
            g1, supp1, rig1, _ = estrai_gol_e_extra(squadre_finale[1]['gol_str'])
            # Stesso formato di build_result: 'X-Y [X1-Y1] (A-B)'
            risultato = f"{g0}-{g1}"
            if supp0 and supp1:
                risultato += f" [{supp0}-{supp1}]"
            elif supp0:
                risultato += f" [{supp0}]"
            elif supp1:
                risultato += f" [{supp1}]"
            if rig0 and rig1:
                risultato += f" ({rig0}-{rig1})"
            partite_list.append({
                'giornata':          'Finale League',
                'squadra_casa':      squadre_finale[0]['squadra'],
                'risultato':         risultato,
                'squadra_trasferta': squadre_finale[1]['squadra'],
                'tipo':              'Playoff',
                'ordine':            0
            })

    # ════════════════════════════════════════════════════════════════
    # GALACTIC CUP
    # ════════════════════════════════════════════════════════════════
    cup_matches = estrai_galactic_cup(percorso_file)
    partite_list.extend(cup_matches)
    print(f"Cup matches added: {len(cup_matches)}")
    
    # ════════════════════════════════════════════════════════════════
    # GALACTIC KINGS LEAGUE
    # ════════════════════════════════════════════════════════════════
    try:
        df_kings = estrai_galactic_kings_league(percorso_file)
        if len(df_kings) > 0:
            partite_list.extend(df_kings.to_dict('records'))
            print(f"Kings League matches added: {len(df_kings)}")
    except Exception as e:
        print(f"⚠️  Errore Kings League: {e}")
        import traceback; traceback.print_exc()

    # ════════════════════════════════════════════════════════════════
    # GALACTIC CHAMPIONS CUP
    # ════════════════════════════════════════════════════════════════
    try:
        df_champions = estrai_galactic_champions_cup(percorso_file)
        if len(df_champions) > 0:
            partite_list.extend(df_champions.to_dict('records'))
            print(f"Champions Cup matches added: {len(df_champions)}")
    except Exception as e:
        print(f"⚠️  Errore Champions Cup: {e}")
        import traceback; traceback.print_exc()

    # ════════════════════════════════════════════════════════════════
    # INTERGALACTIC SUPERCUP
    # ════════════════════════════════════════════════════════════════
    try:
        df_supercup = estrai_intergalactic_supercup(percorso_file)
        if len(df_supercup) > 0:
            partite_list.extend(df_supercup.to_dict('records'))
            print(f"Intergalactic SuperCup matches added: {len(df_supercup)}")
    except Exception as e:
        print(f"⚠️  Errore Intergalactic SuperCup: {e}")
        import traceback; traceback.print_exc()

    # ════════════════════════════════════════════════════════════════
    # CUP OF 8 (stagioni 1-2) / CUP OF 10 (stagioni 3+)
    # Provo prima Cup of 8; se il foglio non esiste, fallback a Cup of 10.
    # ════════════════════════════════════════════════════════════════
    def _sheet_missing(err):
        s = str(err).lower()
        return 'worksheet' in s or 'not found' in s

    try:
        df_cup8 = estrai_cup_of_8(percorso_file)
        if len(df_cup8) > 0:
            partite_list.extend(df_cup8.to_dict('records'))
            print(f"Cup of 8 matches added: {len(df_cup8)}")
    except ValueError as e:
        if _sheet_missing(e):
            # Cup of 8 non presente → prova Cup of 10
            try:
                df_cup10 = estrai_cup_of_10(percorso_file)
                if len(df_cup10) > 0:
                    partite_list.extend(df_cup10.to_dict('records'))
                    print(f"Cup of 10 matches added: {len(df_cup10)}")
            except ValueError as e2:
                if _sheet_missing(e2):
                    print("ℹ️  Né Cup of 8 né Cup of 10 sono presenti nel file")
                else:
                    print(f"⚠️  Errore Cup of 10: {e2}")
                    import traceback; traceback.print_exc()
            except Exception as e2:
                print(f"⚠️  Errore Cup of 10: {e2}")
                import traceback; traceback.print_exc()
        else:
            print(f"⚠️  Errore Cup of 8: {e}")
            import traceback; traceback.print_exc()
    except Exception as e:
        print(f"⚠️  Errore Cup of 8: {e}")
        import traceback; traceback.print_exc()

    # ════════════════════════════════════════════════════════════════
    # COSTRUISCI DATAFRAME E ORDINA
    # ════════════════════════════════════════════════════════════════
    df = pd.DataFrame(partite_list)

    if len(df) > 0:
        # Normalizza i tipi
        df['tipo'] = df['tipo'].replace({'Playoff': 'Final Phase', 'Preliminare': 'Play Off'})

        # Competizione
        df['Competizione'] = df['tipo'].map({
            'League':      'galactic league',
            'Play Off':    'galactic league',
            'Final Phase': 'galactic league',
            'Cup':         'galactic cup',
            'Kings League': 'Kings League',
            'Kings League Playoff Lega B': 'Kings League',
            'Kings League Playout Lega A': 'Kings League',
            'Kings League Playout Lega B': 'Kings League',
            'Kings League Playoff/Playout B-C': 'Kings League',
            'Kings League Playoff/Playout A-B': 'Kings League',
            'Kings League Final Four': 'Kings League',
            'Champions Cup': 'galactic champions cup',
            'SuperCup':      'intergalactic supercup',
            'Cup of 8':      'cup of 8',
            'Cup of 10':     'cup of 10',
        })


        # Rimuovi (sinistro) e (destro) dalla Galactic Cup
        df['giornata'] = df['giornata'].str.replace(r'\s*\(sinistro\)', '', regex=True)
        df['giornata'] = df['giornata'].str.replace(r'\s*\(destro\)',   '', regex=True)

        # Deduplicazione (stessa partita estratta da lato sinistro e destro)
        df = df.drop_duplicates(subset=['giornata', 'squadra_casa', 'squadra_trasferta'], keep='first')

        # Auto-correzione typo nomi squadra contro la lista canonica.
        # PRIMA della colonna 'campo' (che usa squadra_casa) e dei sort,
        # così i nomi corretti si propagano ovunque.
        correggi_typo_squadre(df)

        # Colonna 'campo': nome squadra di casa per match casa/trasferta,
        # 'Neutro' per match in campo neutro
        giornate_neutro = {
            # Galactic League
            'Finale League',
            # Galactic Cup
            'Finale Cup',
            # Galactic Kings League
            'Playoff Lega B - Semifinali',
            'Playoff Lega B - Finale',
            'Playout Lega A - Finali',
            'Playout Lega B - Finali',
            'Playoff/Playout B-C - Turno 1',
            'Playoff/Playout B-C - Turno 2',
            'Playoff/Playout A-B - Turno 1',
            'Playoff/Playout A-B - Turno 2',
            'Final Four - Semifinali',
            'Final Four - Finale',
            # Galactic Champions Cup - Fase 2
            'Fase 2 - Girone A', 'Fase 2 - Girone B', 'Fase 2 - Girone C',
            'Fase 2 - Girone D', 'Fase 2 - Girone E', 'Fase 2 - Girone F',
            # Galactic Champions Cup - Fase 3
            'Fase 3 - Ottavi di Finale',
            'Fase 3 - Quarti di Finale',
            'Fase 3 - Semifinale',
            'Fase 3 - Finale',
            # Intergalactic SuperCup
            'Semifinale SuperCup',
            'Finale SuperCup',
            # Cup of 8
            'Semifinale Cup of 8',
            'Finale Cup of 8',
            # Cup of 10
            'Semifinale Cup of 10',
            'Finale Cup of 10',
        }
        df['campo'] = df['squadra_casa'].where(~df['giornata'].isin(giornate_neutro), 'Neutro')

        # Ordine giornate
        giornate_order = [
            # Galactic League
            'Giornata 1', 'Giornata 2', 'Giornata 3', 'Giornata 4',
            'Giornata 5', 'Giornata 6', 'Giornata 7', 'Giornata 8',
            'Play Off - Andata', 'Play Off - Ritorno',
            'Ottavi League - Andata',    'Ottavi League - Ritorno',
            'Quarti League - Andata',    'Quarti League - Ritorno',
            'Semifinale League - Andata','Semifinale League - Ritorno',
            'Finale League',
            # Galactic Cup
            'Turno 1',
            'Turno 2',
            'Ottavi di Finale',
            'Quarti di Finale - Andata',
            'Quarti di Finale - Ritorno',
            'Semifinale - Andata',
            'Semifinale - Ritorno',
            'Finale Cup',
            # Galactic Kings League
            'Fase 1 - Lega A - Girone A', 'Fase 1 - Lega A - Girone B',
            'Fase 1 - Lega A - Girone C', 'Fase 1 - Lega A - Girone D',
            'Fase 1 - Lega B - Girone A', 'Fase 1 - Lega B - Girone B',
            'Fase 1 - Lega B - Girone C', 'Fase 1 - Lega B - Girone D',
            'Fase 1 - Lega B - Girone E',
            'Fase 1 - Lega C - Girone A', 'Fase 1 - Lega C - Girone B',
            # Galactic Kings League - Fasi finali
            'Playoff Lega B - Semifinali',
            'Playoff Lega B - Finale',
            'Playout Lega A - Finali',
            'Playout Lega B - Finali',
            # Galactic Kings League - Fasi finali S5+ (formato combinato)
            'Playoff/Playout B-C - Turno 1',
            'Playoff/Playout B-C - Turno 2',
            'Playoff/Playout A-B - Turno 1',
            'Playoff/Playout A-B - Turno 2',
            'Final Four - Semifinali',
            'Final Four - Finale',
            # Galactic Champions Cup - Fase 1
            'Fase 1 - Girone A', 'Fase 1 - Girone B', 'Fase 1 - Girone C',
            'Fase 1 - Girone D', 'Fase 1 - Girone E', 'Fase 1 - Girone F',
            # Galactic Champions Cup - Fase 2
            'Fase 2 - Girone A', 'Fase 2 - Girone B', 'Fase 2 - Girone C',
            'Fase 2 - Girone D', 'Fase 2 - Girone E', 'Fase 2 - Girone F',
            # Galactic Champions Cup - Fase 3 (Fase Finale)
            'Fase 3 - Ottavi di Finale',
            'Fase 3 - Quarti di Finale',
            'Fase 3 - Semifinale',
            'Fase 3 - Finale',
            # Intergalactic SuperCup
            'Semifinale SuperCup',
            'Finale SuperCup',
            # Cup of 8 (stagioni 1-2)
            'Quarti Cup of 8',
            'Semifinale Cup of 8',
            'Finale Cup of 8',
            # Cup of 10 (stagioni 3+)
            'Ottavi Cup of 10',
            'Quarti Cup of 10',
            'Semifinale Cup of 10',
            'Finale Cup of 10'
        ]

        df['giornata'] = pd.Categorical(df['giornata'], categories=giornate_order, ordered=True)
        df = df.sort_values(['giornata', 'ordine'], ignore_index=True)

    return df

    # Estrai i playoff (Ottavi, Quarti, Semifinali, Finale)
    # Formato: Due righe consecutive formano una partita andata/ritorno
    # Riga i (squadra1): risultato andata - Col_Squadra | Col_Gol (gol squadra1) | Col_Avv (gol squadra2 in andata)
    # Riga i+1 (squadra2): risultato ritorno - Col_Squadra | Col_Gol (gol squadra2) | Col_Avv (gol squadra1 in ritorno)
    
    playoff_stages = [
        {'nome': 'Ottavi', 'col_squadra': 16, 'col_gol': 17, 'col_avv': 18, 'header': 'OTTAVI DI FINALE', 'max_matches': 8},
        {'nome': 'Quarti', 'col_squadra': 20, 'col_gol': 21, 'col_avv': 22, 'header': 'QUARTI DI FINALE', 'max_matches': 8},
        {'nome': 'Semifinale', 'col_squadra': 24, 'col_gol': 25, 'col_avv': 26, 'header': 'SEMIFINALE', 'max_matches': 2},
    ]
    
    playoff_matches = []
    
    # Estrai Ottavi, Quarti, Semifinali
    for stage in playoff_stages:
        stage_name = stage['nome']
        col_sq = stage['col_squadra']
        col_gol = stage['col_gol']
        col_avv = stage['col_avv']
        header_text = stage['header']
        max_matches = stage['max_matches']
        
        # Trova il riga dell'header
        header_row = None
        for row_idx in range(len(df_raw_league)):
            cell_val = df_raw_league.iloc[row_idx, col_sq]
            if pd.notna(cell_val) and str(cell_val).strip().upper() == header_text.upper():
                header_row = row_idx
                break
        
        if header_row is None:
            continue  # Skip se non trova l'header
        
        # Inizia a leggere dalla riga successiva all'header
        i = header_row + 1
        match_count = 0
        consecutive_empties = 0
        
        while i < len(df_raw_league) - 1 and match_count < max_matches and consecutive_empties < 20:
            squadra1 = df_raw_league.iloc[i, col_sq]
            gol1_andata = df_raw_league.iloc[i, col_gol]      # Andata (squadra1)
            gol1_ritorno = df_raw_league.iloc[i, col_avv]     # Ritorno (squadra1)
            
            squadra2 = df_raw_league.iloc[i + 1, col_sq]
            gol2_andata = df_raw_league.iloc[i + 1, col_gol]  # Andata (squadra2)
            gol2_ritorno = df_raw_league.iloc[i + 1, col_avv] # Ritorno (squadra2)
            
            # Controlla se entrambe le righe hanno dati validi
            if (pd.notna(squadra1) and pd.notna(gol1_andata) and pd.notna(gol1_ritorno) and
                pd.notna(squadra2) and pd.notna(gol2_andata) and pd.notna(gol2_ritorno)):
                
                squadra1 = str(squadra1).strip()
                squadra2 = str(squadra2).strip()
                gol1_andata_str = str(gol1_andata).strip()
                gol1_ritorno_str = str(gol1_ritorno).strip()
                gol2_andata_str = str(gol2_andata).strip()
                gol2_ritorno_str = str(gol2_ritorno).strip()
                
                # Verifica che i nomi delle squadre siano validi (non numeri puri)
                if squadra1.replace(' ', '').replace('.', '').isdigit() or squadra2.replace(' ', '').replace('.', '').isdigit():
                    consecutive_empties += 1
                    i += 1
                    continue
                
                # Estrai i gol e le informazioni aggiuntive (supplementari, rigori, asterisco)
                try:
                    gol1_andata_val, supp1_andata, rig1_andata, ast1_andata = estrai_gol_e_extra(gol1_andata_str)
                    gol2_andata_val, supp2_andata, rig2_andata, ast2_andata = estrai_gol_e_extra(gol2_andata_str)
                    gol1_ritorno_val, supp1_ritorno, rig1_ritorno, ast1_ritorno = estrai_gol_e_extra(gol1_ritorno_str)
                    gol2_ritorno_val, supp2_ritorno, rig2_ritorno, ast2_ritorno = estrai_gol_e_extra(gol2_ritorno_str)
                except:
                    consecutive_empties += 1
                    i += 1
                    continue
                
                consecutive_empties = 0  # Reset se troviamo match valido
                
                # Costruisci i risultati
                risultato_andata = f"{gol1_andata_val}-{gol2_andata_val}"
                
                # Aggiungi supplementari all'andata
                if supp1_andata or supp2_andata:
                    # Se entrambi hanno lo stesso numero tra quadre, ricostituisci [X-X]
                    if supp1_andata and supp2_andata and supp1_andata == supp2_andata:
                        risultato_andata += f" [{supp1_andata}-{supp2_andata}]"
                    elif supp1_andata:
                        risultato_andata += f" [{supp1_andata}]"
                
                # Aggiungi rigori all'andata
                if rig1_andata and rig2_andata:
                    risultato_andata += f" ({rig1_andata}-{rig2_andata})"
                
                # Costruisci il risultato al ritorno (prospettiva invertita)
                risultato_ritorno = f"{gol2_ritorno_val}-{gol1_ritorno_val}"
                
                # Aggiungi supplementari al ritorno
                if supp1_ritorno or supp2_ritorno:
                    # Se entrambi hanno lo stesso numero tra quadre, ricostituisci [X-X]
                    if supp1_ritorno and supp2_ritorno and supp1_ritorno == supp2_ritorno:
                        risultato_ritorno += f" [{supp2_ritorno}-{supp1_ritorno}]"
                    elif supp2_ritorno:
                        risultato_ritorno += f" [{supp2_ritorno}-{supp1_ritorno}]"
                
                # Aggiungi rigori al ritorno (prospettiva invertita)
                if rig1_ritorno and rig2_ritorno:
                    risultato_ritorno += f" ({rig2_ritorno}-{rig1_ritorno})"
                
                playoff_matches.append({
                    'giornata': f'{stage_name} League - Andata',
                    'squadra_casa': squadra1,
                    'risultato': risultato_andata,
                    'squadra_trasferta': squadra2,
                    'tipo': 'Playoff',
                    'ordine': 0
                })
                
                playoff_matches.append({
                    'giornata': f'{stage_name} League - Ritorno',
                    'squadra_casa': squadra2,
                    'risultato': risultato_ritorno,
                    'squadra_trasferta': squadra1,
                    'tipo': 'Playoff',
                    'ordine': 1
                })
                
                match_count += 1
                i += 2  # Salta entrambe le righe del match
            else:
                consecutive_empties += 1
                i += 1
    
    # Estrai la Finale
    finale_col = None
    finale_row = None
    for idx in range(55, len(df_raw_league)):
        for col in range(16, 30):
            cell_val = df_raw_league.iloc[idx, col]
            if pd.notna(cell_val):
                cell_str = str(cell_val).strip().upper()
                if cell_str == 'FINALE':
                    finale_row = idx
                    finale_col = col
                    break
        if finale_row:
            break
    
    if finale_row and finale_col:
        # La finale è sulle due righe successive al header (eventualmente dopo righe vuote)
        squadre_finale = []
        for offset in [2, 3]:  # Righe 69-70, non 68-69
            idx = finale_row + offset
            if idx < len(df_raw_league):
                squadra = df_raw_league.iloc[idx, finale_col]
                gol = df_raw_league.iloc[idx, finale_col + 1] if finale_col + 1 < len(df_raw_league.columns) else None
                
                if pd.notna(squadra) and pd.notna(gol):
                    gol_str = str(gol).strip()
                    if not gol_str[:1].isdigit():
                        continue
                    # Conserva la stringa grezza coi supplementari/rigori.
                    squadre_finale.append({'squadra': str(squadra).strip(), 'gol_str': gol_str})

        if len(squadre_finale) == 2:
            g0, supp0, rig0, _ = estrai_gol_e_extra(squadre_finale[0]['gol_str'])
            g1, supp1, rig1, _ = estrai_gol_e_extra(squadre_finale[1]['gol_str'])
            risultato = f"{g0}-{g1}"
            if supp0 and supp1:
                risultato += f" [{supp0}-{supp1}]"
            elif supp0:
                risultato += f" [{supp0}]"
            elif supp1:
                risultato += f" [{supp1}]"
            if rig0 and rig1:
                risultato += f" ({rig0}-{rig1})"
            playoff_matches.append({
                'giornata': 'Finale League',
                'squadra_casa': squadre_finale[0]['squadra'],
                'risultato': risultato,
                'squadra_trasferta': squadre_finale[1]['squadra'],
                'tipo': 'Playoff',
                'ordine': 0
            })
    
    # Aggiungi i playoff al dataframe principale
    if playoff_matches:
        df_playoff = pd.DataFrame(playoff_matches)
        partite_list.extend(playoff_matches)
    
    # Estrai partite da Galactic League (codice esistente)
    # ... (il codice esistente per Galactic League)
    
    # Ora estrai da Galactic Cup
    df_raw_cup = pd.read_excel(percorso_file, sheet_name='Galactic Cup', header=None)
    print(f"Galactic Cup sheet shape: {df_raw_cup.shape}")
    print("First 10 rows of Galactic Cup:")
    print(df_raw_cup.head(10))
    
    # Definisci i turni e le colonne per Galactic Cup basandosi sulla struttura descritta
    # La struttura è: da sinistra a destra: Turno 1, Turno 2, Ottavi, Quarti, Semifinali, Finale, Semifinali, Quarti, Ottavi, Turno 2, Turno 1
    # Ogni turno ha il suo blocco di colonne
    
    cup_rounds = [
        # Lato sinistro
        {'nome': 'Turno 1', 'cols': [1, 2], 'tipo': 'secca', 'lato': 'sinistro', 'start_row': 5},
        {'nome': 'Turno 2', 'cols': [6, 7], 'tipo': 'secca', 'lato': 'sinistro', 'start_row': 8},
        {'nome': 'Ottavi di Finale', 'cols': [10, 11], 'tipo': 'secca', 'lato': 'sinistro', 'start_row': 9},
        {'nome': 'Quarti di Finale', 'cols': [14, 15, 16, 17], 'tipo': 'andata_ritorno', 'lato': 'sinistro', 'start_row': 16},
        {'nome': 'Semifinale', 'cols': [18, 19, 20, 21], 'tipo': 'andata_ritorno', 'lato': 'sinistro', 'start_row': 20},
        {'nome': 'Finale', 'cols': [22, 23], 'tipo': 'secca', 'lato': 'sinistro', 'start_row': 29},
        # Lato destro
        {'nome': 'Semifinale', 'cols': [25, 26, 27, 29, 30, 31], 'tipo': 'andata_ritorno', 'lato': 'destro', 'start_row': 8},
        {'nome': 'Quarti di Finale', 'cols': [29, 30, 31, 32], 'tipo': 'secca', 'lato': 'destro', 'start_row': 12},
        {'nome': 'Ottavi di Finale', 'cols': [33, 34, 35, 36, 37, 38], 'tipo': 'secca', 'lato': 'destro', 'start_row': 16},
        {'nome': 'Turno 2', 'cols': [37, 38], 'tipo': 'secca', 'lato': 'destro', 'start_row': 4},
        {'nome': 'Turno 1', 'cols': [37, 38], 'tipo': 'secca', 'lato': 'destro', 'start_row': 2},
    ]
    
    cup_matches = estrai_galactic_cup(percorso_file)
    
    
    # Aggiungi le partite della coppa alla lista principale
    partite_list.extend(cup_matches)
    print(f"Cup matches added: {len(cup_matches)}")

    # Crea il DataFrame e ordina le partite
    df = pd.DataFrame(partite_list)
    
    if len(df) > 0:
        # Modifica i valori della colonna tipo
        df['tipo'] = df['tipo'].replace({'Playoff': 'Final Phase', 'Preliminare': 'Play Off'})
        
        # Aggiungi Competizione
        df['Competizione'] = df['tipo'].map({
            'League':                    'galactic league',
            'Play Off':                  'galactic league',
            'Final Phase':               'galactic league',
            'Cup':                       'galactic cup',
            'Kings League':              'galactic kings league',
            'Kings League Playoff Lega B': 'galactic kings league',
            'Kings League Playout Lega A': 'galactic kings league',
            'Kings League Final Four':   'galactic kings league',
        })
        
        # Modifica i valori della colonna giornata per il Turno Preliminare
        df['giornata'] = df['giornata'].str.replace('Turno Preliminare', 'Play Off')
        
        # Definisci l'ordine desiderato per le giornate
        giornate_order = [
            'Giornata 1', 'Giornata 2', 'Giornata 3', 'Giornata 4', 'Giornata 5', 'Giornata 6', 'Giornata 7', 'Giornata 8',
            'Play Off - Andata', 'Play Off - Ritorno',
            'Ottavi League - Andata', 'Ottavi League - Ritorno',
            'Quarti League - Andata', 'Quarti League - Ritorno',
            'Semifinale League - Andata', 'Semifinale League - Ritorno',
            'Finale League',
            # Galactic Cup sinistro
            'Turno 1 (sinistro)', 'Turno 2 (sinistro)', 'Ottavi di Finale (sinistro)', 
            'Quarti di Finale - Andata (sinistro)', 'Quarti di Finale - Ritorno (sinistro)', 
            'Semifinale - Andata (sinistro)', 'Semifinale - Ritorno (sinistro)', 'Finale (sinistro)',
            # Finale Cup (campo neutro)
            'Finale Cup',
            # Galactic Cup destro
            'Quarti di Finale - Andata (destro)','Quarti di Finale - Ritorno (destro)',
            'Semifinale - Andata (destro)', 'Semifinale - Ritorno (destro)', 'Quarti di Finale (destro)', 
            'Ottavi di Finale (destro)', 'Turno 2 (destro)', 'Turno 1 (destro)'
        ]
        
        # Crea una categoria per l'ordinamento
        df['giornata'] = pd.Categorical(df['giornata'], categories=giornate_order, ordered=True)
        
        # Ordina il DataFrame
        df = df.sort_values(['giornata', 'ordine'], ignore_index=True)
    
    return df


def costruisci_classifica_galactic_league(df_partite):
    """
    Costruisce la classifica della Galactic League dalle 8 giornate
    di regular season (filtrando df_partite per tipo == 'League').

    Tie-breaking, in ordine:
      1. Punti totali (desc)
      2. Differenza reti (desc)
      3. Gol fatti (desc)
      4. Gol subiti (asc) — meno subiti = meglio
      5. Se tutto pari: ordine arbitrario (qui alfabetico per stabilità)

    Restituisce DataFrame con colonne:
      Posizione, SQUADRA, W, D, L, PT, GF, GS, DIFF
    """
    import re

    league = df_partite[df_partite['tipo'] == 'League']

    stats = {}
    def s(team):
        if team not in stats:
            stats[team] = {'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GS': 0}
        return stats[team]

    for _, row in league.iterrows():
        m = re.match(r'^(\d+)-(\d+)', str(row['risultato']).strip())
        if not m:
            continue
        gc, gt = int(m.group(1)), int(m.group(2))
        casa, tras = row['squadra_casa'], row['squadra_trasferta']
        sc, st = s(casa), s(tras)

        sc['GF'] += gc; sc['GS'] += gt
        st['GF'] += gt; st['GS'] += gc

        if gc > gt:
            sc['W'] += 1; st['L'] += 1
        elif gc < gt:
            st['W'] += 1; sc['L'] += 1
        else:
            sc['D'] += 1; st['D'] += 1

    rows = [{
        'SQUADRA': team,
        'W':  v['W'],
        'D':  v['D'],
        'L':  v['L'],
        'PT': v['W'] * 3 + v['D'],
        'GF': v['GF'],
        'GS': v['GS'],
        'DIFF': v['GF'] - v['GS'],
    } for team, v in stats.items()]

    df_cl = pd.DataFrame(rows)

    # Nessuna partita con risultato valido (es. girone appena generato, ancora
    # senza risultati): ritorna una classifica vuota ma con le colonne attese,
    # invece di far fallire sort_values su un DataFrame senza colonne.
    if df_cl.empty:
        return pd.DataFrame(
            columns=['Posizione', 'SQUADRA', 'W', 'D', 'L', 'PT', 'GF', 'GS', 'DIFF']
        )

    df_cl = df_cl.sort_values(
        by       = ['PT', 'DIFF', 'GF', 'GS', 'SQUADRA'],
        ascending=[False, False,  False, True, True],
        ignore_index=True
    )
    df_cl.insert(0, 'Posizione', range(1, len(df_cl) + 1))
    return df_cl


def costruisci_ranking_galactic_league(df_partite, df_classifica_league):
    """
    Calcola il punteggio ranking della Galactic League per ogni squadra.

    Regole:
    - Regular season (Giornate 1-8): 1 pt vittoria, 0.5 pareggio
    - Top 8 in regular season: +2 bonus (= 2 vittorie ai playoff)
    - Play Off (Andata/Ritorno): 1 pt vittoria, 0.5 pareggio (no bonus avanzamento)
    - Ottavi/Quarti/Semi/Finale: 1 pt vittoria, 0.5 pareggio
        + 0.5 a chi avanza al turno successivo (Ottavi→Quarti, Quarti→Semi,
          Semi→Finale, Vittoria Finale)

    Pareggio per il ranking = match terminato ai rigori (parentesi tonda
    nel risultato, es. "1-1 (4-3)"). Una partita decisa ai supplementari
    (es. "2-1 [0-0]") conta come vittoria/sconfitta normale.

    Restituisce DataFrame con colonne: SQUADRA, 'galactic league'.
    Righe ordinate alfabeticamente per SQUADRA.
    """
    import re

    teams = list(df_classifica_league['SQUADRA'])
    rk = {t: 0.0 for t in teams}

    def parse_score(ris):
        m = re.match(r'^(\d+)-(\d+)', str(ris).strip())
        return (int(m.group(1)), int(m.group(2))) if m else (None, None)

    def add_match(row):
        # Match points basati sul punteggio sul campo (regolamentari + supplementari).
        # I rigori NON contano per il match: se il match è 1-1 (4-3) entrambe
        # prendono 0.5; se 3-2 (2-3) la casa vince e prende 1.
        gc, gt = parse_score(row['risultato'])
        if gc is None: return
        c, t = row['squadra_casa'], row['squadra_trasferta']
        if c not in rk or t not in rk: return
        if gc > gt:
            rk[c] += 1
        elif gc < gt:
            rk[t] += 1
        else:
            rk[c] += 0.5; rk[t] += 0.5

    def teams_in(g_set):
        m = df_partite['giornata'].isin(g_set)
        return set(pd.concat([
            df_partite.loc[m, 'squadra_casa'],
            df_partite.loc[m, 'squadra_trasferta'],
        ]))

    # 1. Regular season
    league_g = {f'Giornata {i}' for i in range(1, 9)}
    for _, r in df_partite[df_partite['giornata'].isin(league_g)].iterrows():
        add_match(r)

    # 2. Top 8 bonus
    for t in df_classifica_league.head(8)['SQUADRA']:
        if t in rk:
            rk[t] += 2

    # 3. Play Off (no advancement bonus)
    playoff_g = {'Play Off - Andata', 'Play Off - Ritorno'}
    for _, r in df_partite[df_partite['giornata'].isin(playoff_g)].iterrows():
        add_match(r)

    # 4. Ottavi → Finale (match points)
    knockout_g = {
        'Ottavi League - Andata', 'Ottavi League - Ritorno',
        'Quarti League - Andata', 'Quarti League - Ritorno',
        'Semifinale League - Andata', 'Semifinale League - Ritorno',
        'Finale League',
    }
    for _, r in df_partite[df_partite['giornata'].isin(knockout_g)].iterrows():
        add_match(r)

    # 5. Bonus avanzamento (+0.5)
    # Chi raggiunge un turno = ha vinto il precedente (a partire dagli Ottavi)
    for t in teams_in({'Quarti League - Andata', 'Quarti League - Ritorno'}):
        if t in rk: rk[t] += 0.5
    for t in teams_in({'Semifinale League - Andata', 'Semifinale League - Ritorno'}):
        if t in rk: rk[t] += 0.5
    for t in teams_in({'Finale League'}):
        if t in rk: rk[t] += 0.5

    # 6. Vincitrice Finale: +0.5
    finale = df_partite[df_partite['giornata'] == 'Finale League']
    if len(finale) > 0:
        row = finale.iloc[0]
        gc, gt = parse_score(row['risultato'])
        winner = None
        if gc is not None and gc > gt:
            winner = row['squadra_casa']
        elif gc is not None and gc < gt:
            winner = row['squadra_trasferta']
        elif gc is not None and gc == gt:
            # 0-0 ai rigori — leggi (A-B) per determinare il vincitore
            mp = re.search(r'\((\d+)-(\d+)\)', str(row['risultato']))
            if mp:
                a, b = int(mp.group(1)), int(mp.group(2))
                winner = row['squadra_casa'] if a > b else row['squadra_trasferta']
        if winner and winner in rk:
            rk[winner] += 0.5

    df_rank = pd.DataFrame(
        [{'SQUADRA': t, 'galactic league': rk[t]} for t in teams]
    ).sort_values('SQUADRA', ignore_index=True)
    return df_rank


def costruisci_ranking_galactic_cup(df_partite, df_classifica_league):
    """
    Calcola il punteggio ranking della Galactic Cup per ogni squadra.

    Punteggio in base al tier di eliminazione:
    - Turno 1:  0
    - Turno 2:  0.5
    - Ottavi:   1.5
    - Quarti:   2.0 + match_pts(Quarti A+R)
    - Semi:     2.0 + match_pts(Q) + 1.0 + match_pts(S)
    - Finale:   2.0 + match_pts(Q) + 1.0 + match_pts(S) + 1.0 + match_pts(F)
                + 1.0 bonus se vince la finale

    Match points (Quarti, Semi, Finale): 1 a vittoria, 0.5 a pareggio.
    Pareggio per il ranking = match terminato ai rigori (parens nel risultato).
    Squadre che non hanno mai giocato in Cup: 0.

    Restituisce DataFrame con colonne: SQUADRA, 'galactic cup'.
    """
    import re

    teams = list(df_classifica_league['SQUADRA'])
    rk = {t: 0.0 for t in teams}
    cup = df_partite[df_partite['tipo'] == 'Cup']

    quarti_g = ['Quarti di Finale - Andata', 'Quarti di Finale - Ritorno']
    semi_g   = ['Semifinale - Andata',       'Semifinale - Ritorno']
    finale_g = ['Finale Cup']

    def teams_in(g_set):
        m = cup['giornata'].isin(g_set)
        return set(pd.concat([cup.loc[m, 'squadra_casa'], cup.loc[m, 'squadra_trasferta']]))

    teams_per_round = {
        'turno1': teams_in(['Turno 1']),
        'turno2': teams_in(['Turno 2']),
        'ottavi': teams_in(['Ottavi di Finale']),
        'quarti': teams_in(quarti_g),
        'semi':   teams_in(semi_g),
        'finale': teams_in(finale_g),
    }

    # Vincitrice della finale (per il bonus +1)
    finale_match = cup[cup['giornata'] == 'Finale Cup']
    finale_winner = None
    if len(finale_match) > 0:
        row = finale_match.iloc[0]
        ris = str(row['risultato']).strip()
        mres = re.match(r'^(\d+)-(\d+)', ris)
        if mres:
            gc, gt = int(mres.group(1)), int(mres.group(2))
            if '(' in ris:
                mp = re.search(r'\((\d+)-(\d+)\)', ris)
                if mp:
                    a, b = int(mp.group(1)), int(mp.group(2))
                    finale_winner = row['squadra_casa'] if a > b else row['squadra_trasferta']
            elif gc > gt:
                finale_winner = row['squadra_casa']
            elif gc < gt:
                finale_winner = row['squadra_trasferta']

    def match_pts(team, g_set):
        # Match points basati sul punteggio sul campo. I rigori non
        # cambiano l'esito ai fini del ranking: 3-2 (2-3) → casa vince
        # il match e prende 1; 1-1 (4-3) → pareggio, 0.5 ciascuna.
        pts = 0.0
        for _, row in cup[cup['giornata'].isin(g_set)].iterrows():
            if team not in (row['squadra_casa'], row['squadra_trasferta']):
                continue
            ris = str(row['risultato']).strip()
            mres = re.match(r'^(\d+)-(\d+)', ris)
            if not mres: continue
            gc, gt = int(mres.group(1)), int(mres.group(2))
            if gc > gt and team == row['squadra_casa']:
                pts += 1.0
            elif gc < gt and team == row['squadra_trasferta']:
                pts += 1.0
            elif gc == gt:
                pts += 0.5
            # else: sconfitta secca → 0
        return pts

    round_order = ['turno1', 'turno2', 'ottavi', 'quarti', 'semi', 'finale']

    for team in teams:
        played = [r for r in round_order if team in teams_per_round[r]]
        if not played:
            continue  # 0 punti

        latest = played[-1]

        if latest == 'turno1':
            rk[team] = 0.0
        elif latest == 'turno2':
            rk[team] = 0.5
        elif latest == 'ottavi':
            rk[team] = 1.5
        elif latest == 'quarti':
            rk[team] = 2.0 + match_pts(team, quarti_g)
        elif latest == 'semi':
            rk[team] = (2.0
                        + match_pts(team, quarti_g)
                        + 1.0
                        + match_pts(team, semi_g))
        elif latest == 'finale':
            rk[team] = (2.0
                        + match_pts(team, quarti_g)
                        + 1.0
                        + match_pts(team, semi_g)
                        + 1.0
                        + match_pts(team, finale_g))
            if team == finale_winner:
                rk[team] += 1.0

    df_rank = pd.DataFrame(
        [{'SQUADRA': t, 'galactic cup': rk[t]} for t in teams]
    ).sort_values('SQUADRA', ignore_index=True)
    return df_rank


def _ordina_girone_con_tiebreak(stats, matches_df):
    """
    Helper: ordina le squadre di un girone applicando i criteri di
    tie-breaking ricorsivi tipici del calcio.

    Ordine criteri:
      0. PT generale (split iniziale)
      1. PT mini-classifica tra squadre a pari punti
      2. DIFF mini-classifica tra squadre a pari punti
      3. DIFF generale
      4. GF generale
      5. GS generale (asc, meno subiti = meglio)
      6. SQUADRA asc (stabilità finale)

    Quando un criterio splitta un gruppo tied in più sotto-gruppi, ogni
    sotto-gruppo prosegue con il criterio successivo. Le mini-stats
    (PT/DIFF tra squadre tied) vengono ricalcolate sul sotto-gruppo
    corrente, considerando SOLO le partite tra quelle squadre.

    Args:
        stats: dict {team: {W, D, L, GF, GS, PT, DIFF}}
        matches_df: DataFrame con le partite del girone

    Returns:
        Lista di squadre ordinate (1° in posizione 0).
    """
    import re

    def parse_score(ris):
        m = re.match(r'^(\d+)-(\d+)', str(ris).strip())
        return (int(m.group(1)), int(m.group(2))) if m else (None, None)

    def compute_mini(group):
        gset = set(group)
        mini = {t: {'PT': 0, 'GF': 0, 'GS': 0} for t in group}
        for _, row in matches_df.iterrows():
            c, t = row['squadra_casa'], row['squadra_trasferta']
            if c not in gset or t not in gset:
                continue
            gc, gt = parse_score(row['risultato'])
            if gc is None: continue
            mini[c]['GF'] += gc; mini[c]['GS'] += gt
            mini[t]['GF'] += gt; mini[t]['GS'] += gc
            if gc > gt:
                mini[c]['PT'] += 3
            elif gc < gt:
                mini[t]['PT'] += 3
            else:
                mini[c]['PT'] += 1; mini[t]['PT'] += 1
        for t in mini:
            mini[t]['DIFF'] = mini[t]['GF'] - mini[t]['GS']
        return mini

    def split_by(group, key_fn):
        """Raggruppa group per chiave (sortable). Restituisce lista di sub-group
        in ordine ascendente di chiave."""
        d = {}
        for t in group:
            d.setdefault(key_fn(t), []).append(t)
        return [d[k] for k in sorted(d.keys())]

    def resolve(group, depth):
        if len(group) == 1:
            return group
        if depth >= 6:
            return sorted(group)

        if depth == 1:
            mini = compute_mini(group)
            key_fn = lambda t: -mini[t]['PT']
        elif depth == 2:
            mini = compute_mini(group)
            key_fn = lambda t: -mini[t]['DIFF']
        elif depth == 3:
            key_fn = lambda t: -stats[t]['DIFF']
        elif depth == 4:
            key_fn = lambda t: -stats[t]['GF']
        elif depth == 5:
            key_fn = lambda t: stats[t]['GS']

        sub_groups = split_by(group, key_fn)
        if len(sub_groups) == 1:
            return resolve(group, depth + 1)
        result = []
        for sg in sub_groups:
            result.extend(resolve(sg, depth + 1))
        return result

    # Top level: split per PT generale
    teams = list(stats.keys())
    pt_groups = {}
    for t in teams:
        pt_groups.setdefault(stats[t]['PT'], []).append(t)

    result = []
    for pt in sorted(pt_groups.keys(), reverse=True):
        group = pt_groups[pt]
        if len(group) == 1:
            result.append(group[0])
        else:
            result.extend(resolve(group, 1))   # parte da depth=1 (mini-PT)
    return result


def costruisci_classifica_kings_league(df_partite):
    """
    Costruisce le classifiche dei gironi Kings League (Fase 1) per
    Lega A, Lega B e (se presente) Lega C.

    Tie-breaking interno al girone (ricorsivo, per gestire 3+ squadre tied):
      1. PT generale desc
      2. PT mini-classifica tra squadre a pari punti
      3. DIFF mini-classifica tra squadre a pari punti
      4. DIFF generale desc
      5. GF generale desc
      6. GS generale asc
      7. SQUADRA asc (stabilità)

    Restituisce DataFrame con colonne:
      Lega, Girone, Posizione, SQUADRA, W, D, L, PT, GF, GS, DIFF
    """
    import re

    kl = df_partite[df_partite['Competizione'] == 'Kings League']
    girone_giornate = sorted(
        g for g in kl['giornata'].unique()
        if str(g).startswith('Fase 1 - Lega ')
    )

    rows = []
    for giornata in girone_giornate:
        m = re.match(r'^Fase 1 - (Lega [A-Z]) - (Girone [A-Z])$', str(giornata))
        if not m:
            continue
        lega, girone = m.group(1), m.group(2)

        girone_matches = kl[kl['giornata'] == giornata]

        stats = {}
        for _, row in girone_matches.iterrows():
            mres = re.match(r'^(\d+)-(\d+)', str(row['risultato']).strip())
            if not mres:
                continue
            gc, gt = int(mres.group(1)), int(mres.group(2))
            c, t = row['squadra_casa'], row['squadra_trasferta']
            for team in (c, t):
                if team not in stats:
                    stats[team] = {'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GS': 0}
            stats[c]['GF'] += gc; stats[c]['GS'] += gt
            stats[t]['GF'] += gt; stats[t]['GS'] += gc
            if gc > gt:
                stats[c]['W'] += 1; stats[t]['L'] += 1
            elif gc < gt:
                stats[t]['W'] += 1; stats[c]['L'] += 1
            else:
                stats[c]['D'] += 1; stats[t]['D'] += 1

        if not stats:
            continue

        for v in stats.values():
            v['PT']   = v['W'] * 3 + v['D']
            v['DIFF'] = v['GF'] - v['GS']

        sorted_teams = _ordina_girone_con_tiebreak(stats, girone_matches)

        for posizione, team in enumerate(sorted_teams, start=1):
            v = stats[team]
            rows.append({
                'Lega':      lega,
                'Girone':    girone,
                'Posizione': posizione,
                'SQUADRA':   team,
                'W':  v['W'],
                'D':  v['D'],
                'L':  v['L'],
                'PT': v['PT'],
                'GF': v['GF'],
                'GS': v['GS'],
                'DIFF': v['DIFF'],
            })

    return pd.DataFrame(rows)


def costruisci_esiti_kings_league(df_partite, df_class=None):
    """
    Determina il "colore" (esito) di ogni squadra nelle classifiche dei gironi
    Kings League, in base alla posizione nel girone + esito di
    playoff/playout/spareggi.

    Colori (dict SQUADRA -> str):
      'verde'        promossa, oppure 1ª di girone (Lega A: qualificata Final Four)
      'verde_chiaro' 2ª di Lega B/C che NON ha passato lo spareggio promozione
      'giallo'       3ª salvata al playout/spareggio
      'arancione'    retrocessa
      'neutro'       nessun esito particolare

    Gestisce sia il formato S1-S4 (2 leghe) sia S5+ (3 leghe). L'appartenenza
    alle partite di spareggio determina l'esito: chi NON gioca lo spareggio è
    promosso/salvo d'ufficio (miglior 2ª/3ª).
    """
    import re

    if df_class is None:
        df_class = costruisci_classifica_kings_league(df_partite)
    colore = {}
    if df_class is None or len(df_class) == 0:
        return colore

    kl = df_partite[df_partite['Competizione'] == 'Kings League']
    ha_lega_c = (df_class['Lega'] == 'Lega C').any()

    def parse(ris):
        m = re.match(r'^(\d+)-(\d+)', str(ris).strip())
        return (int(m.group(1)), int(m.group(2))) if m else (None, None)

    def match_winner(row):
        gc, gt = parse(row['risultato'])
        if gc is None:
            return None
        ris = str(row['risultato']).strip()
        mp = re.search(r'\((\d+)-(\d+)\)', ris)
        if mp:  # rigori
            a, b = int(mp.group(1)), int(mp.group(2))
            return row['squadra_casa'] if a > b else row['squadra_trasferta']
        if gc > gt:
            return row['squadra_casa']
        if gc < gt:
            return row['squadra_trasferta']
        return None

    def won_in(team, giornata):
        """True se `team` vince in quella giornata, False se gioca e non vince,
        None se non vi compare affatto."""
        sub = kl[kl['giornata'] == giornata]
        played = won = False
        for _, row in sub.iterrows():
            if team in (row['squadra_casa'], row['squadra_trasferta']):
                played = True
                if match_winner(row) == team:
                    won = True
        return won if played else None

    rows = list(df_class.to_dict('records'))

    # ── S5+ (3 leghe) ────────────────────────────────────────────────
    if ha_lega_c:
        AB_T1, AB_T2 = 'Playoff/Playout A-B - Turno 1', 'Playoff/Playout A-B - Turno 2'
        BC_T1, BC_T2 = 'Playoff/Playout B-C - Turno 1', 'Playoff/Playout B-C - Turno 2'
        for r in rows:
            t, lega, pos = r['SQUADRA'], r['Lega'], r['Posizione']
            c = 'neutro'
            if lega == 'Lega A':
                if pos == 1:
                    c = 'verde'
                elif pos == 3:
                    if won_in(t, AB_T1) is True:
                        c = 'giallo'
                    else:
                        c = 'giallo' if won_in(t, AB_T2) is True else 'arancione'
                elif pos == 4:
                    c = 'arancione'
            elif lega == 'Lega B':
                if pos == 1:
                    c = 'verde'
                elif pos == 2:
                    w2 = won_in(t, AB_T2)
                    # non gioca lo spareggio → miglior 2ª, promossa d'ufficio
                    c = 'verde' if w2 in (True, None) else 'verde_chiaro'
                elif pos == 3:
                    w1 = won_in(t, BC_T1)
                    if w1 is None:        # miglior 3ª: non gioca lo spareggio, già salva
                        c = 'neutro'
                    elif w1 is True:      # vince lo spareggio iniziale → salva
                        c = 'giallo'
                    else:                 # perde → decisiva PAR_DEC
                        c = 'giallo' if won_in(t, BC_T2) is True else 'arancione'
                elif pos == 4:
                    c = 'arancione'
            elif lega == 'Lega C':
                if pos == 1:
                    c = 'verde'
                elif pos == 2:
                    if won_in(t, BC_T1) is True:
                        c = 'verde'
                    else:
                        c = 'verde' if won_in(t, BC_T2) is True else 'verde_chiaro'
            colore[t] = c
        return colore

    # ── S1-S4 (2 leghe) ──────────────────────────────────────────────
    fb = kl[kl['giornata'] == 'Playoff Lega B - Finale']
    playoff_b_winner = match_winner(fb.iloc[0]) if len(fb) > 0 else None
    has_playout_b = bool((kl['giornata'] == 'Playout Lega B - Finali').any())
    # Squadre che hanno effettivamente partecipato ai playoff di Lega B
    # (la peggior 2ª resta fuori dai playoff → esito neutro).
    pb = kl[kl['giornata'].isin(['Playoff Lega B - Semifinali', 'Playoff Lega B - Finale'])]
    playoff_b_teams = set(pb['squadra_casa']) | set(pb['squadra_trasferta'])
    for r in rows:
        t, lega, pos = r['SQUADRA'], r['Lega'], r['Posizione']
        c = 'neutro'
        if lega == 'Lega A':
            if pos == 1:
                c = 'verde'
            elif pos == 3:
                w = won_in(t, 'Playout Lega A - Finali')
                c = 'giallo' if w in (True, None) else 'arancione'
            elif pos == 4:
                c = 'arancione'
        elif lega == 'Lega B':
            if pos == 1:
                c = 'verde'
            elif pos == 2:
                if t == playoff_b_winner:
                    c = 'verde'
                elif t in playoff_b_teams:
                    c = 'verde_chiaro'
                else:                     # peggior 2ª: non partecipa ai playoff
                    c = 'neutro'
            elif pos == 3 and has_playout_b:
                # S4 (senza Lega C, servono 8 retrocessioni): delle 5 terze, la
                # peggiore NON gioca il playout perché già retrocessa; le altre 4
                # fanno un playout secco. Quindi: salva (giallo) SOLO se vince il
                # playout; chi perde o non lo gioca → retrocessa (arancione).
                w = won_in(t, 'Playout Lega B - Finali')
                c = 'giallo' if w is True else 'arancione'
            elif pos == 4 and has_playout_b:
                c = 'arancione'
        colore[t] = c
    return colore


def costruisci_classifica_galactic_champions_cup(df_partite, fase=1):
    """
    Costruisce le classifiche dei 6 gironi della Galactic Champions Cup
    per la fase specificata.

    Args:
        fase: 1 (gironi Fase 1, andata/ritorno) o 2 (gironi Fase 2,
              partita secca campo neutro). Default 1.

    Tie-breaking interno al girone (ricorsivo, uguale a Kings League):
      1. PT generale desc
      2. PT mini-classifica tra squadre a pari punti
      3. DIFF mini-classifica tra squadre a pari punti
      4. DIFF generale desc
      5. GF generale desc
      6. GS generale asc
      7. SQUADRA asc (stabilità)

    Restituisce DataFrame con colonne:
      Girone, Posizione, SQUADRA, W, D, L, PT, GF, GS, DIFF
    """
    import re

    if fase not in (1, 2):
        raise ValueError(f"fase deve essere 1 o 2, ricevuto {fase}")

    prefix  = f'Fase {fase} - Girone '
    pattern = rf'^Fase {fase} - (Girone [A-F])$'

    cc = df_partite[df_partite['Competizione'] == 'galactic champions cup']
    girone_giornate = sorted(
        g for g in cc['giornata'].unique()
        if str(g).startswith(prefix)
    )

    rows = []
    for giornata in girone_giornate:
        m = re.match(pattern, str(giornata))
        if not m:
            continue
        girone = m.group(1)

        girone_matches = cc[cc['giornata'] == giornata]

        stats = {}
        for _, row in girone_matches.iterrows():
            mres = re.match(r'^(\d+)-(\d+)', str(row['risultato']).strip())
            if not mres:
                continue
            gc, gt = int(mres.group(1)), int(mres.group(2))
            c, t = row['squadra_casa'], row['squadra_trasferta']
            for team in (c, t):
                if team not in stats:
                    stats[team] = {'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GS': 0}
            stats[c]['GF'] += gc; stats[c]['GS'] += gt
            stats[t]['GF'] += gt; stats[t]['GS'] += gc
            if gc > gt:
                stats[c]['W'] += 1; stats[t]['L'] += 1
            elif gc < gt:
                stats[t]['W'] += 1; stats[c]['L'] += 1
            else:
                stats[c]['D'] += 1; stats[t]['D'] += 1

        if not stats:
            continue

        for v in stats.values():
            v['PT']   = v['W'] * 3 + v['D']
            v['DIFF'] = v['GF'] - v['GS']

        sorted_teams = _ordina_girone_con_tiebreak(stats, girone_matches)

        for posizione, team in enumerate(sorted_teams, start=1):
            v = stats[team]
            rows.append({
                'Girone':    girone,
                'Posizione': posizione,
                'SQUADRA':   team,
                'W':  v['W'],
                'D':  v['D'],
                'L':  v['L'],
                'PT': v['PT'],
                'GF': v['GF'],
                'GS': v['GS'],
                'DIFF': v['DIFF'],
            })

    return pd.DataFrame(rows)


def costruisci_classifica_migliori_terze_champions_cup(df_partite, tiebreak_rank=None):
    """
    Classifica delle migliori terze classificate dei 6 gironi della
    Fase 2 della Galactic Champions Cup.

    Le terze provengono da gironi diversi e quindi non si sono
    affrontate: il tie-breaking è solo statistico (no h2h):
      1. PT desc
      2. DIFF generale desc
      3. GF desc
      4. GS asc
      5. ranking cumulato (fino alla stagione precedente) desc  ← se fornito
      6. SQUADRA asc (stabilità)

    Args:
        tiebreak_rank: dict opzionale {SQUADRA: valore_cumulato} usato come
            penultimo criterio. Le squadre assenti valgono 0.0.

    Restituisce DataFrame con colonne:
      Posizione, Girone, SQUADRA, W, D, L, PT, GF, GS, DIFF
    """
    df_class_fase2 = costruisci_classifica_galactic_champions_cup(df_partite, fase=2)
    if len(df_class_fase2) == 0:
        return pd.DataFrame(columns=[
            'Posizione', 'Girone', 'SQUADRA', 'W', 'D', 'L',
            'PT', 'GF', 'GS', 'DIFF'
        ])

    terze = df_class_fase2[df_class_fase2['Posizione'] == 3].drop(columns=['Posizione']).copy()

    tiebreak_rank = tiebreak_rank or {}
    terze['_cum'] = terze['SQUADRA'].map(lambda s: float(tiebreak_rank.get(s, 0.0)))

    terze_sorted = terze.sort_values(
        by       = ['PT', 'DIFF', 'GF', 'GS', '_cum', 'SQUADRA'],
        ascending=[False, False,  False, True, False,  True],
        ignore_index=True
    )
    terze_sorted.insert(0, 'Posizione', range(1, len(terze_sorted) + 1))

    return terze_sorted[['Posizione', 'Girone', 'SQUADRA',
                         'W', 'D', 'L', 'PT', 'GF', 'GS', 'DIFF']]


def costruisci_ranking_kings_league(df_partite, df_classifica_league):
    """
    Calcola il punteggio ranking della Kings League per ogni squadra.

    Due rami in base alla presenza della Lega C:

    ── S1-S4 (no Lega C, formato vecchio) ──────────────────────────
      Match points dei gironi: 1 vittoria, 0.5 pareggio
      Bonus:
        - Tutte le squadre di Lega A: +2.0
        - Prime di ogni girone di Lega B: +1.0
        - Vincitrice del Playoff Lega B - Finale: +0.5
      Final Four (tier):
        - Eliminata semi:   +1.0
        - Eliminata finale: +1.5
        - Vincitrice:       +2.5

    ── S5+ (3 leghe, formato nuovo) ─────────────────────────────────
      Match points dei gironi: 1 vittoria, 0.5 pareggio
      Bonus partecipazione:
        - Lega A: +3.0  (tutte le 16 squadre)
        - Lega B: +1.5  (tutte le 12 squadre)
        - Lega C: nessuno
      Bonus posizione:
        - Prime di ogni girone Lega B (3): +1.0  (promozione diretta)
        - Migliore 2ª di Lega B (1): +0.5  (promozione 2° posto)
        - 2ª di Lega B che vince A-B Finale: +0.5  (promozione playoff)
        - Prime di ogni girone Lega C (2): +1.0  (promozione diretta)
        - 2ª di Lega C che vince B-C Turno 1: +0.5  (promozione playoff 1° turno)
        - 2ª di Lega C che vince B-C Finale: +0.5  (promozione playoff 2° turno)
      Bonus Final Four (solo squadre Lega A):
        - 1° posto nel girone (4): +1.0
        - Raggiungi la finale (2): +0.5
        - Vinci la finale (1): +1.0

    Restituisce DataFrame con colonne: SQUADRA, 'kings league'.
    """
    import re

    teams = list(df_classifica_league['SQUADRA'])
    rk = {t: 0.0 for t in teams}
    kl = df_partite[df_partite['Competizione'] == 'Kings League']

    def parse_score(ris):
        m = re.match(r'^(\d+)-(\d+)', str(ris).strip())
        return (int(m.group(1)), int(m.group(2))) if m else (None, None)

    def teams_in(g_set):
        m = kl['giornata'].isin(g_set)
        return set(pd.concat([kl.loc[m, 'squadra_casa'], kl.loc[m, 'squadra_trasferta']]))

    def winner_of_row(row):
        """Determina vincitore di un match, usando rigori se serve."""
        gc, gt = parse_score(row['risultato'])
        if gc is None: return None
        ris = str(row['risultato']).strip()
        if '(' in ris:
            mp = re.search(r'\((\d+)-(\d+)\)', ris)
            if mp:
                a, b = int(mp.group(1)), int(mp.group(2))
                return row['squadra_casa'] if a > b else row['squadra_trasferta']
        if gc > gt: return row['squadra_casa']
        if gc < gt: return row['squadra_trasferta']
        return None

    def winner_of(giornata_name):
        match = kl[kl['giornata'] == giornata_name]
        if len(match) == 0: return None
        return winner_of_row(match.iloc[0])

    # ════════════════════════════════════════════════════════════════
    # Match points gironi (uguale per entrambi i rami)
    # ════════════════════════════════════════════════════════════════
    girone_g = [g for g in kl['giornata'].unique() if str(g).startswith('Fase 1 - Lega ')]
    for _, row in kl[kl['giornata'].isin(girone_g)].iterrows():
        gc, gt = parse_score(row['risultato'])
        if gc is None: continue
        c, t = row['squadra_casa'], row['squadra_trasferta']
        if c not in rk or t not in rk: continue
        if gc > gt:
            rk[c] += 1.0
        elif gc < gt:
            rk[t] += 1.0
        else:
            rk[c] += 0.5; rk[t] += 0.5

    # ════════════════════════════════════════════════════════════════
    # Classifica gironi (necessaria a entrambi i rami)
    # ════════════════════════════════════════════════════════════════
    df_class_kl = costruisci_classifica_kings_league(df_partite)
    ha_lega_c = (df_class_kl['Lega'] == 'Lega C').any() if len(df_class_kl) > 0 else False

    # ════════════════════════════════════════════════════════════════
    # RAMO S5+ (3 leghe)
    # ════════════════════════════════════════════════════════════════
    if ha_lega_c:
        lega_a_g = [g for g in girone_g if str(g).startswith('Fase 1 - Lega A')]
        lega_b_g = [g for g in girone_g if str(g).startswith('Fase 1 - Lega B')]
        lega_c_g = [g for g in girone_g if str(g).startswith('Fase 1 - Lega C')]
        lega_a_teams = teams_in(lega_a_g)
        lega_b_teams = teams_in(lega_b_g)
        lega_c_teams = teams_in(lega_c_g)

        # Bonus partecipazione (Lega C: nessuno)
        for t in lega_a_teams:
            if t in rk: rk[t] += 3.0
        for t in lega_b_teams:
            if t in rk: rk[t] += 1.5

        # Promozione diretta — prime di girone (B e C ricevono bonus,
        # le prime di A non hanno "promozione" ma "qualificazione Final Four")
        primi_b = df_class_kl[(df_class_kl['Lega'] == 'Lega B') & (df_class_kl['Posizione'] == 1)]['SQUADRA']
        for t in primi_b:
            if t in rk: rk[t] += 1.0
        primi_c = df_class_kl[(df_class_kl['Lega'] == 'Lega C') & (df_class_kl['Posizione'] == 1)]['SQUADRA']
        for t in primi_c:
            if t in rk: rk[t] += 1.0

        # Migliore 2ª di Lega B → +0.5 (Promozione 2° posto)
        seconde_b = df_class_kl[(df_class_kl['Lega'] == 'Lega B') & (df_class_kl['Posizione'] == 2)].copy()
        if len(seconde_b) > 0:
            seconde_b_sorted = seconde_b.sort_values(
                by       = ['PT', 'DIFF', 'GF', 'GS', 'SQUADRA'],
                ascending=[False, False, False, True, True],
                ignore_index=True
            )
            best_2nd_b = seconde_b_sorted.iloc[0]['SQUADRA']
            if best_2nd_b in rk:
                rk[best_2nd_b] += 0.5

        # 2ª di Lega B che vince A-B Turno 2 → +0.5 (Promozione playoff)
        ab_finali = kl[kl['giornata'] == 'Playoff/Playout A-B - Turno 2']
        for _, row in ab_finali.iterrows():
            winner = winner_of_row(row)
            if winner in lega_b_teams and winner in rk:
                rk[winner] += 0.5

        # 2ª di Lega C che vince B-C Turno 1 → +0.5 (Promozione playoff 1° turno)
        bc_t1 = kl[kl['giornata'] == 'Playoff/Playout B-C - Turno 1']
        for _, row in bc_t1.iterrows():
            winner = winner_of_row(row)
            if winner in lega_c_teams and winner in rk:
                rk[winner] += 0.5

        # 2ª di Lega C che vince B-C Turno 2 → +0.5 (Promozione playoff 2° turno)
        bc_finale = kl[kl['giornata'] == 'Playoff/Playout B-C - Turno 2']
        for _, row in bc_finale.iterrows():
            winner = winner_of_row(row)
            if winner in lega_c_teams and winner in rk:
                rk[winner] += 0.5

        # Final Four (solo Lega A): 1° posto, finalisti, vincitrice
        # 1° posto = chi gioca in semifinale
        ff_semi_teams = teams_in(['Final Four - Semifinali'])
        for t in ff_semi_teams:
            if t in rk: rk[t] += 1.0   # 1° posto nel girone Lega A
        ff_finale_teams = teams_in(['Final Four - Finale'])
        for t in ff_finale_teams:
            if t in rk: rk[t] += 0.5   # Raggiungi la finale
        ff_winner = winner_of('Final Four - Finale')
        if ff_winner and ff_winner in rk:
            rk[ff_winner] += 1.0       # Vinci la finale

        df_rank = pd.DataFrame(
            [{'SQUADRA': t, 'kings league': rk[t]} for t in teams]
        ).sort_values('SQUADRA', ignore_index=True)
        return df_rank

    # ════════════════════════════════════════════════════════════════
    # RAMO S1-S4 (2 leghe, regole vecchie)
    # ════════════════════════════════════════════════════════════════
    # Bonus +2 a tutte le squadre di Lega A
    lega_a_g = [g for g in girone_g if str(g).startswith('Fase 1 - Lega A')]
    for t in teams_in(lega_a_g):
        if t in rk:
            rk[t] += 2.0

    # Bonus +1 alle prime di ogni girone di Lega B
    if len(df_class_kl) > 0:
        primi_b = df_class_kl[
            (df_class_kl['Lega'] == 'Lega B') & (df_class_kl['Posizione'] == 1)
        ]['SQUADRA']
        for t in primi_b:
            if t in rk:
                rk[t] += 1.0

    # Bonus +0.5 alla vincitrice del Playoff Lega B - Finale
    playoff_b_winner = winner_of('Playoff Lega B - Finale')
    if playoff_b_winner and playoff_b_winner in rk:
        rk[playoff_b_winner] += 0.5

    # Final Four — bonus tier
    ff_semi_teams   = teams_in(['Final Four - Semifinali'])
    ff_finale_teams = teams_in(['Final Four - Finale'])
    ff_winner       = winner_of('Final Four - Finale')
    for t in ff_semi_teams:
        if t not in rk: continue
        if t == ff_winner:
            rk[t] += 2.5
        elif t in ff_finale_teams:
            rk[t] += 1.5
        else:
            rk[t] += 1.0

    df_rank = pd.DataFrame(
        [{'SQUADRA': t, 'kings league': rk[t]} for t in teams]
    ).sort_values('SQUADRA', ignore_index=True)
    return df_rank


def costruisci_ranking_galactic_champions_cup(df_partite, df_classifica_league, tiebreak_rank=None):
    """
    Calcola il punteggio ranking della Galactic Champions Cup per ogni squadra.

    Fase 1 (gironi):
        ranking_F1 = arrotonda(PT_girone × 0.10) allo 0.5 più vicino
        Range: 0.0 a 3.0 (PT max 30 = 10 vittorie × 3)

    Fase 2 (6 gironi da 4, partita secca campo neutro):
        - 1° posto nel girone:                    +2.0
        - 2° posto nel girone:                    +1.5
        - 3° posto tra le 4 migliori terze:       +1.0
        - 3° posto tra le 2 peggiori terze:       +0.5
        - 4° posto nel girone:                    +0.5
        Le squadre eliminate in Fase 1 non prendono punti di Fase 2.

    Fase 3 (Fase Finale, partite secche in campo neutro):
        Match points (ogni round): 1 vittoria, 0.5 pareggio (rigori = pareggio)
        Bonus avanzamento:
          - Passaggio Ottavi → Quarti:            +0.5
          - Passaggio Quarti → Semi:              +1.0
          - Passaggio Semi → Finale:              +1.0
          - Vittoria del torneo:                  +1.0

    Restituisce DataFrame con colonne: SQUADRA, 'galactic champions cup'.
    """
    import re

    teams = list(df_classifica_league['SQUADRA'])
    rk = {t: 0.0 for t in teams}

    # Fase 1: PT × 0.10 arrotondato al 0.5 più vicino
    df_class_f1 = costruisci_classifica_galactic_champions_cup(df_partite, fase=1)
    for _, row in df_class_f1.iterrows():
        team = row['SQUADRA']
        if team not in rk:
            continue
        rk[team] += round(row['PT'] * 0.10 * 2) / 2

    # Fase 2: bonus tier in base alla posizione nel girone
    df_class_f2 = costruisci_classifica_galactic_champions_cup(df_partite, fase=2)
    df_terze    = costruisci_classifica_migliori_terze_champions_cup(df_partite, tiebreak_rank)

    # Le 4 migliori terze qualificate alla Fase 3 (rispetto alle 2 peggiori eliminate)
    top_terze = set(df_terze.head(4)['SQUADRA']) if len(df_terze) > 0 else set()

    for _, row in df_class_f2.iterrows():
        team = row['SQUADRA']
        if team not in rk:
            continue
        pos = row['Posizione']
        if pos == 1:
            rk[team] += 2.0
        elif pos == 2:
            rk[team] += 1.5
        elif pos == 3:
            rk[team] += 1.0 if team in top_terze else 0.5
        elif pos == 4:
            rk[team] += 0.5

    # Fase 3: match points + bonus avanzamento
    cc = df_partite[df_partite['Competizione'] == 'galactic champions cup']

    def parse_score(ris):
        m = re.match(r'^(\d+)-(\d+)', str(ris).strip())
        return (int(m.group(1)), int(m.group(2))) if m else (None, None)

    def teams_in(g_set):
        m = cc['giornata'].isin(g_set)
        return set(pd.concat([cc.loc[m, 'squadra_casa'], cc.loc[m, 'squadra_trasferta']]))

    # Fase 3: tutte partite secche in campo neutro. I rigori non
    # cambiano i match points; il pareggio (1-1) prende 0.5 ciascuna,
    # poi chi avanza prende il bonus separato.
    fase3_giornate = [
        'Fase 3 - Ottavi di Finale',
        'Fase 3 - Quarti di Finale',
        'Fase 3 - Semifinale',
        'Fase 3 - Finale',
    ]
    for _, row in cc[cc['giornata'].isin(fase3_giornate)].iterrows():
        gc, gt = parse_score(row['risultato'])
        if gc is None: continue
        c, t = row['squadra_casa'], row['squadra_trasferta']
        if c not in rk or t not in rk: continue
        if gc > gt:
            rk[c] += 1.0
        elif gc < gt:
            rk[t] += 1.0
        else:
            rk[c] += 0.5; rk[t] += 0.5

    # Bonus avanzamento: chi gioca un round ha vinto il precedente
    for t in teams_in(['Fase 3 - Quarti di Finale']):
        if t in rk: rk[t] += 0.5    # passaggio Ottavi → Quarti
    for t in teams_in(['Fase 3 - Semifinale']):
        if t in rk: rk[t] += 1.0    # passaggio Quarti → Semi
    for t in teams_in(['Fase 3 - Finale']):
        if t in rk: rk[t] += 1.0    # passaggio Semi → Finale

    # Vittoria del torneo: +1.0 alla vincitrice della Finale
    finale = cc[cc['giornata'] == 'Fase 3 - Finale']
    if len(finale) > 0:
        row = finale.iloc[0]
        gc, gt = parse_score(row['risultato'])
        ris = str(row['risultato']).strip()
        winner = None
        if gc is not None:
            if '(' in ris:
                mp = re.search(r'\((\d+)-(\d+)\)', ris)
                if mp:
                    a, b = int(mp.group(1)), int(mp.group(2))
                    winner = row['squadra_casa'] if a > b else row['squadra_trasferta']
            elif gc > gt:
                winner = row['squadra_casa']
            elif gc < gt:
                winner = row['squadra_trasferta']
        if winner and winner in rk:
            rk[winner] += 1.0

    df_rank = pd.DataFrame(
        [{'SQUADRA': t, 'galactic champions cup': rk[t]} for t in teams]
    ).sort_values('SQUADRA', ignore_index=True)
    return df_rank


def costruisci_ranking_intergalactic_supercup(df_partite, df_classifica_league):
    """
    Calcola il punteggio ranking della Intergalactic SuperCup per ogni squadra.

    Bonus tier (no match points; torneo accessibile a pochi):
      - Arriva in finale (perde la finale):     +0.5
      - Vince il torneo:                        +1.0
    Le squadre eliminate in semifinale: 0 punti.
    Le squadre che non partecipano: 0 punti.

    NB: i bonus sono tier-based (non cumulativi). Il vincitore prende +1.0
    anziché +0.5 + 1.0 = 1.5.

    Restituisce DataFrame con colonne: SQUADRA, 'intergalactic supercup'.
    """
    import re

    teams = list(df_classifica_league['SQUADRA'])
    rk = {t: 0.0 for t in teams}

    sc = df_partite[df_partite['Competizione'] == 'intergalactic supercup']

    def parse_score(ris):
        m = re.match(r'^(\d+)-(\d+)', str(ris).strip())
        return (int(m.group(1)), int(m.group(2))) if m else (None, None)

    finale = sc[sc['giornata'] == 'Finale SuperCup']
    if len(finale) > 0:
        row = finale.iloc[0]
        gc, gt = parse_score(row['risultato'])
        ris = str(row['risultato']).strip()
        winner = None
        if gc is not None:
            if '(' in ris:
                mp = re.search(r'\((\d+)-(\d+)\)', ris)
                if mp:
                    a, b = int(mp.group(1)), int(mp.group(2))
                    winner = row['squadra_casa'] if a > b else row['squadra_trasferta']
            elif gc > gt:
                winner = row['squadra_casa']
            elif gc < gt:
                winner = row['squadra_trasferta']

        for finalista in (row['squadra_casa'], row['squadra_trasferta']):
            if finalista not in rk:
                continue
            if finalista == winner:
                rk[finalista] += 1.0
            else:
                rk[finalista] += 0.5

    df_rank = pd.DataFrame(
        [{'SQUADRA': t, 'intergalactic supercup': rk[t]} for t in teams]
    ).sort_values('SQUADRA', ignore_index=True)
    return df_rank


def aggiungi_totale_ranking(df_ranking):
    """
    Aggiunge la colonna 'TOTALE' come somma di tutte le colonne competizione
    (cioè tutte le colonne numeriche, escludendo 'SQUADRA').

    Funziona sia su df_ranking (36 righe, una per squadra) che su
    df_ranking_max (1 riga). Restituisce una NUOVA DataFrame, l'originale
    non viene modificato.
    """
    score_cols = [c for c in df_ranking.columns if c != 'SQUADRA']
    df = df_ranking.copy()
    df['TOTALE'] = df[score_cols].sum(axis=1)
    return df


def aggiungi_posizione_e_percentuale(df_ranking, df_ranking_max):
    """
    Aggiunge al df_ranking due colonne:
      - 'POSIZIONE' (1..N): rank in base a TOTALE desc, con tie-breaking:
          1. TOTALE desc
          2. galactic league desc
          3. galactic champions cup desc
          4. galactic cup desc
          5. kings league desc
          6. intergalactic supercup desc (5° tie-breaker implicito)
          7. SQUADRA asc (stabilità finale)
      - 'PERCENTUALE': TOTALE / TOTALE_max × 100, arrotondato a 1 decimale.

    Output ordinato per POSIZIONE asc. df_ranking deve avere già la
    colonna 'TOTALE' (chiamare prima aggiungi_totale_ranking se necessario).
    """
    df = df_ranking.copy()

    sort_cols = [
        'TOTALE',
        'galactic league',
        'galactic champions cup',
        'galactic cup',
        'kings league',
        'intergalactic supercup',
        'SQUADRA',
    ]
    ascending = [False, False, False, False, False, False, True]

    df_sorted = df.sort_values(by=sort_cols, ascending=ascending, ignore_index=True)
    df_sorted.insert(0, 'POSIZIONE', range(1, len(df_sorted) + 1))

    max_total = df_ranking_max['TOTALE'].iloc[0]
    df_sorted['PERCENTUALE'] = (df_sorted['TOTALE'] / max_total * 100).round(1)

    return df_sorted


def costruisci_ranking_max(df_partite=None):
    """
    Punteggio ranking massimo teorico per ogni competizione.
    Restituisce DataFrame a 1 riga con il massimo accumulabile da una
    squadra che vince tutto il vincibile.

    Kings League ha 2 massimi diversi:
      - S1-S4 (2 leghe):  10.5
      - S5+ (3 leghe):    11.5
    Se `df_partite` viene passato, viene rilevato il formato e usato il
    massimo corrispondente. Altrimenti viene usato il massimo S5+ (più alto).

    Galactic League → 19.0
        Regular season (8 vittorie):              8.0
        Top 8 bonus:                              2.0
        Ottavi A+R vinti:                         2.0
        Quarti A+R vinti:                         2.0
        Semi A+R vinti:                           2.0
        Finale vinta:                             1.0
        Avanzamenti (Quarti+Semi+Finale+Vittoria) 2.0   (4 × 0.5)

    Galactic Cup → 10.0
        Avanzamenti turno1+turno2+ottavi:         2.0   (0.5+1.0+0.5)
        Quarti A+R vinti:                         2.0
        Passaggio Quarti → Semi:                  1.0
        Semi A+R vinti:                           2.0
        Passaggio Semi → Finale:                  1.0
        Finale vinta:                             1.0
        Bonus vittoria Finale:                    1.0

    Kings League S1-S4 → 10.5
        Gironi (3 avversari × A+R = 6 vittorie):  6.0
        Bonus Lega A:                             2.0
        Vittoria Final Four:                      2.5

    Kings League S5+ → 11.5
        Gironi (6 vittorie):                      6.0
        Bonus partecipazione Lega A:              3.0
        1° posto nel girone Lega A:               1.0
        Raggiungi la finale:                      0.5
        Vinci la finale:                          1.0
    """
    max_galactic_league = (
        8 * 1.0       # regular season tutte vittorie
        + 2.0         # bonus top 8
        + 2 * 1.0     # ottavi andata + ritorno
        + 2 * 1.0     # quarti andata + ritorno
        + 2 * 1.0     # semifinali andata + ritorno
        + 1.0         # finale vinta
        + 4 * 0.5     # avanzamenti (3 turni + vittoria finale)
    )

    max_galactic_cup = (
        0.5 + 1.0 + 0.5   # avanzamenti turno1, turno2, ottavi
        + 2 * 1.0         # quarti A+R vinti
        + 1.0             # passaggio quarti → semi
        + 2 * 1.0         # semi A+R vinti
        + 1.0             # passaggio semi → finale
        + 1.0             # finale vinta
        + 1.0             # bonus vittoria finale
    )

    # Kings League: massimo dipende dal formato della stagione.
    # Rilevo presenza Lega C dai dati per scegliere il massimo corretto.
    ha_lega_c = False
    if df_partite is not None:
        kl_giornate = df_partite['giornata'].dropna().astype(str)
        ha_lega_c = kl_giornate.str.startswith('Fase 1 - Lega C').any()

    if ha_lega_c:
        # S5+ (3 leghe)
        max_kings_league = (
            6 * 1.0      # gironi: 3 avversari × A+R tutte vinte
            + 3.0        # bonus partecipazione Lega A
            + 1.0        # 1° posto nel girone Lega A
            + 0.5        # raggiungi la finale
            + 1.0        # vinci la finale
        )
    else:
        # S1-S4 (2 leghe)
        max_kings_league = (
            6 * 1.0      # gironi: 3 avversari × A+R tutte vinte
            + 2.0        # bonus Lega A
            + 2.5        # vittoria Final Four
        )

    # Galactic Champions Cup: Fase 1 + Fase 2 + Fase 3
    max_galactic_champions_cup_fase1 = 3.0   # 30 PT × 0.10 (10 vittorie nel girone)
    max_galactic_champions_cup_fase2 = 2.0   # 1° posto nel girone Fase 2
    max_galactic_champions_cup_fase3 = (
        1.0 + 0.5    # ottavi:  vittoria + passaggio
        + 1.0 + 1.0  # quarti:  vittoria + passaggio
        + 1.0 + 1.0  # semi:    vittoria + passaggio
        + 1.0 + 1.0  # finale:  vittoria + vittoria torneo
    )                # totale Fase 3 = 7.5
    max_galactic_champions_cup = (
        max_galactic_champions_cup_fase1
        + max_galactic_champions_cup_fase2
        + max_galactic_champions_cup_fase3
    )

    # Intergalactic SuperCup: tier-based (vincitore = 1.0, finalista = 0.5)
    max_intergalactic_supercup = 1.0

    return pd.DataFrame([{
        'galactic league':        max_galactic_league,
        'galactic cup':           max_galactic_cup,
        'kings league':           max_kings_league,
        'galactic champions cup': max_galactic_champions_cup,
        'intergalactic supercup': max_intergalactic_supercup,
    }])


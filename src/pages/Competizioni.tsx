import { useEffect, useMemo, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:3004/api";

type Conteggio = { partite: number; vincitrice: string | null };
type Conteggi = Record<string, Conteggio>;

type Partita = {
  id?: number;
  stagione: number;
  giornata: string;
  squadra_casa: string;
  risultato: string;
  squadra_trasferta: string;
  campo?: string | null;
  Competizione: string;
};

type RankingRow = {
  POSIZIONE: number;
  SQUADRA: string;
  "galactic league": number;
  "galactic cup": number;
  "kings league": number;
  "galactic champions cup": number;
  "intergalactic supercup": number;
  TOTALE: number;
  PERCENTUALE: number;
};

type StagioneInclusa = { stagione: number; peso: number };

type RankingCumulatoRow = {
  POSIZIONE: number;
  SQUADRA: string;
  TOTALE: number;
} & Record<string, number | string>; // Per le colonne dinamiche "S1", "S2", ...

type RankingType = "stagionale" | "cumulato";

type SubPage = "competizioni" | "squadre";

type SquadraStats = {
  SQUADRA: string;
  V: number;
  P: number;
  S: number;
  GF: number;
  GS: number;
  PTS: number;
};

/** Ordine in cui mostrare le partite per il drill-down di una squadra. */
const COMP_ORDER: string[] = [
  "galactic league",
  "galactic cup",
  "Kings League",
  "galactic champions cup",
  "intergalactic supercup",
  "cup of 8",
  "cup of 10",
];

const COMP_LABEL: Record<string, string> = {
  "galactic league": "Galactic League",
  "galactic cup": "Galactic Cup",
  "Kings League": "Galactic Kings League",
  "galactic champions cup": "Galactic Champions Cup",
  "intergalactic supercup": "Intergalactic SuperCup",
  "cup of 8": "Cup of 8",
  "cup of 10": "Cup of 10",
};

const COMP_ACCENT: Record<string, keyof typeof ACCENT> = {
  "galactic league": "sky",
  "galactic cup": "amber",
  "Kings League": "purple",
  "galactic champions cup": "emerald",
  "intergalactic supercup": "pink",
  "cup of 8": "indigo",
  "cup of 10": "indigo",
};

/** Sigla di 3 lettere da un nome squadra. */
function siglaSquadra(nome: string): string {
  const clean = nome.replace(/[^A-Za-z]/g, "");
  return clean.slice(0, 3).toUpperCase();
}

/** Esito di una partita dal punto di vista di una specifica squadra.
 *  Rigori → pareggio (coerente con backend /api/squadre/stats). */
function matchOutcome(p: Partita, squadra: string): "V" | "P" | "S" {
  const m = p.risultato.match(/^(\d+)-(\d+)/);
  if (!m) return "P";
  const gc = parseInt(m[1], 10);
  const gt = parseInt(m[2], 10);
  if (gc === gt) return "P";
  const isHome = p.squadra_casa === squadra;
  const homeWon = gc > gt;
  return homeWon === isHome ? "V" : "S";
}

/** Mapping accent (color name) → classi Tailwind. */
const ACCENT: Record<
  string,
  {
    cardBg: string;
    border: string;
    iconBg: string;
    iconColor: string;
    badge: string;
    badgeBg: string;
    hoverGlow: string;
  }
> = {
  sky: {
    cardBg: "bg-sky-950/40",
    border: "border-sky-700/30",
    iconBg: "bg-sky-500/20",
    iconColor: "text-sky-300",
    badge: "text-sky-300",
    badgeBg: "bg-sky-500/15 border border-sky-500/30",
    hoverGlow: "hover:shadow-[0_0_30px_rgba(56,189,248,0.25)] hover:border-sky-500/50",
  },
  amber: {
    cardBg: "bg-amber-950/40",
    border: "border-amber-700/30",
    iconBg: "bg-amber-500/20",
    iconColor: "text-amber-300",
    badge: "text-amber-300",
    badgeBg: "bg-amber-500/15 border border-amber-500/30",
    hoverGlow: "hover:shadow-[0_0_30px_rgba(245,158,11,0.25)] hover:border-amber-500/50",
  },
  purple: {
    cardBg: "bg-purple-950/40",
    border: "border-purple-700/30",
    iconBg: "bg-purple-500/20",
    iconColor: "text-purple-300",
    badge: "text-purple-300",
    badgeBg: "bg-purple-500/15 border border-purple-500/30",
    hoverGlow: "hover:shadow-[0_0_30px_rgba(168,85,247,0.25)] hover:border-purple-500/50",
  },
  emerald: {
    cardBg: "bg-emerald-950/40",
    border: "border-emerald-700/30",
    iconBg: "bg-emerald-500/20",
    iconColor: "text-emerald-300",
    badge: "text-emerald-300",
    badgeBg: "bg-emerald-500/15 border border-emerald-500/30",
    hoverGlow: "hover:shadow-[0_0_30px_rgba(16,185,129,0.25)] hover:border-emerald-500/50",
  },
  pink: {
    cardBg: "bg-pink-950/40",
    border: "border-pink-700/30",
    iconBg: "bg-pink-500/20",
    iconColor: "text-pink-300",
    badge: "text-pink-300",
    badgeBg: "bg-pink-500/15 border border-pink-500/30",
    hoverGlow: "hover:shadow-[0_0_30px_rgba(236,72,153,0.25)] hover:border-pink-500/50",
  },
  indigo: {
    cardBg: "bg-indigo-950/40",
    border: "border-indigo-700/30",
    iconBg: "bg-indigo-500/20",
    iconColor: "text-indigo-300",
    badge: "text-indigo-300",
    badgeBg: "bg-indigo-500/15 border border-indigo-500/30",
    hoverGlow: "hover:shadow-[0_0_30px_rgba(99,102,241,0.25)] hover:border-indigo-500/50",
  },
};

/** Immagini custom dei trofei (servite da public/). Chiave = key competizione. */
const COMP_IMG: Record<string, string> = {
  "galactic league": "/galactic-league.png",
  "galactic cup": "/galactic-cup.png",
  "Kings League": "/kings-league.png",
  "galactic champions cup": "/galactic-champions-cup.png",
  "intergalactic supercup": "/intergalactic-super-cup.png",
  "cup": "/cup-of-10.png",
};

/** Le 6 card. Per "Cup of 8/10" il key e i testi si adattano a runtime. */
const CARDS_BASE: Array<{
  key: string;
  label: string;
  sigla: string;
  descrizione: string;
  accent: keyof typeof ACCENT;
  icon: string;
  img?: string;
}> = [
  {
    key: "galactic league",
    label: "Galactic League",
    sigla: "GL",
    descrizione: "36 squadre, 4 fasce, fase a gironi + playoff fino alla finale",
    accent: "sky",
    icon: "🛰️",
    img: COMP_IMG["galactic league"],
  },
  {
    key: "galactic cup",
    label: "Galactic Cup",
    sigla: "GC",
    descrizione: "Coppa ad eliminazione diretta con turno preliminare",
    accent: "amber",
    icon: "🏆",
    img: COMP_IMG["galactic cup"],
  },
  {
    key: "Kings League",
    label: "Galactic Kings League",
    sigla: "GKL",
    descrizione: "Leghe A, B, C con gironi e fase finale",
    accent: "purple",
    icon: "👑",
    img: COMP_IMG["Kings League"],
  },
  {
    key: "galactic champions cup",
    label: "Galactic Champions Cup",
    sigla: "GCC",
    descrizione: "La competizione più prestigiosa - 3 fasi fino alla finale",
    accent: "emerald",
    icon: "⭐",
    img: COMP_IMG["galactic champions cup"],
  },
  {
    key: "intergalactic supercup",
    label: "Intergalactic SuperCup",
    sigla: "ISC",
    descrizione: "I vincitori dei 4 tornei si sfidano per la supremazia",
    accent: "pink",
    icon: "🚀",
    img: COMP_IMG["intergalactic supercup"],
  },
  {
    // placeholder — viene sovrascritto in base alla stagione (Cup of 8 o 10)
    key: "_cup",
    label: "Cup of 10",
    sigla: "C10",
    descrizione: "Le migliori squadre del ranking in competizione",
    accent: "indigo",
    icon: "🔟",
    img: COMP_IMG["cup"],
  },
];

export default function Competizioni() {
  const [stagioni, setStagioni] = useState<number[]>([]);
  const [stagione, setStagione] = useState<number | null>(null);
  const [conteggi, setConteggi] = useState<Conteggi>({});
  const [loading, setLoading] = useState(false);

  // drill-down
  const [selectedKey, setSelectedKey] = useState<string | null>(null);
  const [partite, setPartite] = useState<Partita[]>([]);
  const [partiteLoading, setPartiteLoading] = useState(false);

  // ranking stagionale
  const [ranking, setRanking] = useState<RankingRow[]>([]);
  const [rankingLoading, setRankingLoading] = useState(false);

  // ranking cumulato (ultime 5 stagioni pesate)
  const [rankingCumulato, setRankingCumulato] = useState<RankingCumulatoRow[]>([]);
  const [cumStagioniIncluse, setCumStagioniIncluse] = useState<StagioneInclusa[]>([]);
  const [rankingCumulatoLoading, setRankingCumulatoLoading] = useState(false);

  // tipo di ranking visualizzato + info modal
  const [rankingType, setRankingType] = useState<RankingType>("stagionale");
  const [infoOpen, setInfoOpen] = useState(false);

  // Sotto-pagina: Competizioni (default) o Squadre
  const [subPage, setSubPage] = useState<SubPage>("competizioni");

  // Squadre (lista alfabetica con stats stagionali)
  const [squadre, setSquadre] = useState<SquadraStats[]>([]);
  const [squadreLoading, setSquadreLoading] = useState(false);
  const [selectedSquadra, setSelectedSquadra] = useState<string | null>(null);

  // Tutte le partite della stagione (per drill-down squadra)
  const [allPartite, setAllPartite] = useState<Partita[]>([]);
  const [allPartiteLoading, setAllPartiteLoading] = useState(false);

  // carica stagioni disponibili
  useEffect(() => {
    fetch(`${API_URL}/stagioni`)
      .then((r) => r.json())
      .then((data) => {
        const s: number[] = data.stagioni || [];
        setStagioni(s);
        if (s.length > 0)
          setStagione((prev) => (prev === null ? Math.max(...s) : prev));
      })
      .catch(() => {});
  }, []);

  // carica conteggi quando cambia la stagione
  useEffect(() => {
    if (stagione === null) return;
    setLoading(true);
    setSelectedKey(null);
    fetch(`${API_URL}/partite/conteggi?stagione=${stagione}`)
      .then((r) => r.json())
      .then((data) => setConteggi(data.conteggi || {}))
      .catch(() => setConteggi({}))
      .finally(() => setLoading(false));
  }, [stagione]);

  // carica ranking stagionale quando cambia la stagione
  useEffect(() => {
    if (stagione === null) return;
    setRankingLoading(true);
    fetch(`${API_URL}/ranking?stagione=${stagione}`)
      .then((r) => r.json())
      .then((data) => setRanking(data.ranking || []))
      .catch(() => setRanking([]))
      .finally(() => setRankingLoading(false));
  }, [stagione]);

  // carica ranking cumulato quando cambia la stagione (solo da S2 in poi)
  useEffect(() => {
    if (stagione === null || stagione < 2) {
      setRankingCumulato([]);
      setCumStagioniIncluse([]);
      // se l'utente è su cumulato ma non disponibile, torna su stagionale
      setRankingType((prev: RankingType) => (prev === "cumulato" && stagione !== null && stagione < 2 ? "stagionale" : prev));
      return;
    }
    setRankingCumulatoLoading(true);
    fetch(`${API_URL}/ranking/cumulato?stagione=${stagione}`)
      .then((r) => r.json())
      .then((data) => {
        setRankingCumulato(data.ranking || []);
        setCumStagioniIncluse(data.stagioni_incluse || []);
      })
      .catch(() => {
        setRankingCumulato([]);
        setCumStagioniIncluse([]);
      })
      .finally(() => setRankingCumulatoLoading(false));
  }, [stagione]);

  // carica partite quando si entra in drill-down
  useEffect(() => {
    if (selectedKey === null || stagione === null) return;
    setPartiteLoading(true);
    const url = `${API_URL}/partite?stagione=${stagione}&competizione=${encodeURIComponent(selectedKey)}`;
    fetch(url)
      .then((r) => r.json())
      .then((data) => setPartite(data.partite || []))
      .catch(() => setPartite([]))
      .finally(() => setPartiteLoading(false));
  }, [selectedKey, stagione]);

  // carica statistiche squadre quando si entra nella sotto-pagina Squadre
  useEffect(() => {
    if (stagione === null || subPage !== "squadre") return;
    setSquadreLoading(true);
    fetch(`${API_URL}/squadre/stats?stagione=${stagione}`)
      .then((r) => r.json())
      .then((data) => setSquadre(data.squadre || []))
      .catch(() => setSquadre([]))
      .finally(() => setSquadreLoading(false));
  }, [stagione, subPage]);

  // carica tutte le partite quando si seleziona una squadra per il drill-down
  useEffect(() => {
    if (stagione === null || selectedSquadra === null) return;
    setAllPartiteLoading(true);
    fetch(`${API_URL}/partite?stagione=${stagione}`)
      .then((r) => r.json())
      .then((data) => setAllPartite(data.partite || []))
      .catch(() => setAllPartite([]))
      .finally(() => setAllPartiteLoading(false));
  }, [stagione, selectedSquadra]);

  // Reset selezioni di drill-down al cambio stagione o sotto-pagina
  useEffect(() => {
    setSelectedSquadra(null);
    setSelectedKey(null);
  }, [stagione, subPage]);

  // Cup of 8 vs Cup of 10 detection
  const cupKey = useMemo(() => {
    if (conteggi["cup of 8"]) return "cup of 8";
    if (conteggi["cup of 10"]) return "cup of 10";
    return "cup of 10";
  }, [conteggi]);

  const cards = useMemo(() => {
    return CARDS_BASE.map((c) => {
      if (c.key === "_cup") {
        const isCup8 = cupKey === "cup of 8";
        return {
          ...c,
          key: cupKey,
          label: isCup8 ? "Cup of 8" : "Cup of 10",
          sigla: isCup8 ? "C8" : "C10",
          descrizione: isCup8
            ? "Le migliori 8 squadre del ranking in competizione"
            : "Le migliori 10 squadre del ranking in competizione",
        };
      }
      return c;
    });
  }, [cupKey]);

  // Drill-down view — singola competizione
  if (selectedKey !== null) {
    const cardInfo = cards.find((c) => c.key === selectedKey);
    return (
      <MatchesView
        title={cardInfo?.label ?? selectedKey}
        accent={cardInfo?.accent ?? "sky"}
        compKey={selectedKey}
        partite={partite}
        loading={partiteLoading}
        stagione={stagione ?? 0}
        onBack={() => setSelectedKey(null)}
      />
    );
  }

  // Drill-down view — singola squadra
  if (selectedSquadra !== null) {
    const stats = squadre.find((s) => s.SQUADRA === selectedSquadra) ?? null;
    const partiteSquadra = allPartite.filter(
      (p) =>
        p.squadra_casa === selectedSquadra ||
        p.squadra_trasferta === selectedSquadra,
    );
    return (
      <TeamMatchesView
        squadra={selectedSquadra}
        stats={stats}
        partite={partiteSquadra}
        loading={allPartiteLoading}
        stagione={stagione ?? 0}
        onBack={() => setSelectedSquadra(null)}
      />
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-end justify-between mb-6 flex-wrap gap-4">
        <div className="flex items-center gap-4">
          <button
            onClick={() => setSubPage("competizioni")}
            className="text-3xl text-slate-400 hover:text-cyan-300 transition-colors leading-none"
            title="Vai a Competizioni"
            disabled={subPage === "competizioni"}
          >
            ←
          </button>
          <h1 className="text-5xl font-bold text-amber-300 tracking-wide drop-shadow-[0_0_30px_rgba(252,211,77,0.3)]">
            {subPage === "competizioni" ? "Competizioni" : "Squadre"}
          </h1>
          <button
            onClick={() => setSubPage("squadre")}
            className="text-3xl text-slate-400 hover:text-cyan-300 transition-colors leading-none"
            title="Vai a Squadre"
            disabled={subPage === "squadre"}
          >
            →
          </button>
        </div>

        {/* Filtro stagione */}
        <div className="flex items-center gap-3">
          <label className="text-sm text-slate-300 font-medium">Stagione:</label>
          <select
            value={stagione ?? ""}
            onChange={(e) => setStagione(parseInt(e.target.value, 10))}
            className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-white focus:outline-none focus:border-cyan-400"
            disabled={stagioni.length === 0}
          >
            {stagioni.length === 0 ? (
              <option value="">Nessuna stagione</option>
            ) : (
              stagioni
                .sort((a, b) => a - b)
                .map((s) => (
                  <option key={s} value={s}>
                    Stagione {s}
                  </option>
                ))
            )}
          </select>
        </div>
      </div>

      {/* Indicatore pagina (dot pagination) */}
      <div className="flex items-center justify-center gap-2 mb-8">
        <span className={"h-1.5 rounded-full transition-all " + (subPage === "competizioni" ? "w-8 bg-cyan-400" : "w-2 bg-slate-600")} />
        <span className={"h-1.5 rounded-full transition-all " + (subPage === "squadre" ? "w-8 bg-cyan-400" : "w-2 bg-slate-600")} />
      </div>

      {stagioni.length === 0 ? (
        <div className="text-center text-slate-400 py-16">
          Nessuna stagione caricata. Importa un file Excel dal tab "Importa Stagione".
        </div>
      ) : subPage === "squadre" ? (
        <SquadreView
          squadre={squadre}
          loading={squadreLoading}
          onSelect={(sq) => setSelectedSquadra(sq)}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {cards.map((c) => {
            const accent = ACCENT[c.accent];
            const data = conteggi[c.key];
            const partite = data?.partite ?? 0;
            const vincitrice = data?.vincitrice;

            return (
              <button
                key={c.key}
                onClick={() => setSelectedKey(c.key)}
                disabled={partite === 0}
                className={
                  "text-left rounded-2xl p-6 border transition-all relative " +
                  accent.cardBg +
                  " " +
                  accent.border +
                  " " +
                  (partite === 0
                    ? "opacity-60 cursor-not-allowed"
                    : "cursor-pointer " + accent.hoverGlow)
                }
              >
                {/* Header con icona e badge */}
                <div className="flex items-start justify-between mb-4">
                  <div
                    className={
                      "w-14 h-14 rounded-xl flex items-center justify-center text-3xl " +
                      (c.img ? "" : accent.iconBg)
                    }
                  >
                    {c.img ? (
                      <img
                        src={c.img}
                        alt={c.label}
                        className="h-14 w-14 object-contain"
                      />
                    ) : (
                      c.icon
                    )}
                  </div>
                  <span
                    className={
                      "px-2.5 py-1 rounded-md text-xs font-bold tracking-wider " +
                      accent.badge +
                      " " +
                      accent.badgeBg
                    }
                  >
                    {c.sigla}
                  </span>
                </div>

                {/* Titolo + descrizione */}
                <h3 className="text-xl font-bold text-white mb-2">{c.label}</h3>
                <p className="text-sm text-slate-400 mb-6 leading-relaxed">
                  {c.descrizione}
                </p>

                {/* Footer dinamico */}
                <div className="flex items-center justify-between pt-4 border-t border-white/5">
                  <div className="text-sm">
                    {loading ? (
                      <span className="text-slate-500">Caricamento…</span>
                    ) : partite === 0 ? (
                      <span className="text-slate-500">Nessuna partita ancora</span>
                    ) : (
                      <span className="text-slate-300">
                        <strong className={accent.iconColor}>{partite}</strong>{" "}
                        partite
                        {vincitrice && (
                          <>
                            {" · 🏆 "}
                            <strong className={accent.iconColor}>{vincitrice}</strong>
                          </>
                        )}
                      </span>
                    )}
                  </div>
                  {partite > 0 && (
                    <span className={"text-xl " + accent.iconColor}>›</span>
                  )}
                </div>
              </button>
            );
          })}
        </div>
      )}

      {/* ── RANKING (Stagionale / Cumulato) ──────────────────────── */}
      {stagioni.length > 0 && (
        <div className="mt-12">
          {/* Header: toggle + bottone info */}
          <div className="flex items-center justify-between mb-5 flex-wrap gap-3">
            <div className="flex items-center gap-3">
              <div className="flex rounded-lg overflow-hidden border border-slate-700 shadow-inner">
                <button
                  onClick={() => setRankingType("stagionale")}
                  className={
                    "px-4 py-2 text-sm font-medium transition-colors " +
                    (rankingType === "stagionale"
                      ? "bg-amber-500/20 text-amber-200"
                      : "bg-slate-800/50 text-slate-400 hover:text-white")
                  }
                >
                  Ranking Stagionale
                </button>
                <button
                  onClick={() => {
                    if (stagione !== null && stagione >= 2) setRankingType("cumulato");
                  }}
                  disabled={stagione === null || stagione < 2}
                  title={
                    stagione !== null && stagione < 2
                      ? "Disponibile dalla stagione 2"
                      : ""
                  }
                  className={
                    "px-4 py-2 text-sm font-medium transition-colors border-l border-slate-700 " +
                    (stagione === null || stagione < 2
                      ? "bg-slate-800/30 text-slate-600 cursor-not-allowed"
                      : rankingType === "cumulato"
                        ? "bg-amber-500/20 text-amber-200"
                        : "bg-slate-800/50 text-slate-400 hover:text-white")
                  }
                >
                  Ranking Cumulato
                </button>
              </div>

              <button
                onClick={() => setInfoOpen(true)}
                className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 text-slate-300 hover:text-white hover:border-slate-500 transition-colors font-bold text-sm"
                title="Informazioni sui ranking"
              >
                i
              </button>
            </div>

            {stagione !== null && (
              <span className="text-sm text-slate-400">Stagione {stagione}</span>
            )}
          </div>

          {/* Tabella: stagionale o cumulato */}
          <div className="rounded-2xl bg-slate-900/50 border border-slate-700 overflow-hidden">
            {rankingType === "stagionale" ? (
              rankingLoading ? (
                <div className="text-center text-slate-400 py-10">
                  Caricamento ranking…
                </div>
              ) : ranking.length === 0 ? (
                <div className="text-center text-slate-500 py-10">
                  Nessun dato per la stagione selezionata
                </div>
              ) : (
                <table className="w-full text-sm">
                  <thead className="bg-slate-800/60 text-slate-400 uppercase text-xs tracking-wider">
                    <tr>
                      <th className="text-center py-3 px-3 w-16">#</th>
                      <th className="text-left py-3 px-4">Squadra</th>
                      <th className="text-right py-3 px-3 hidden md:table-cell">GL</th>
                      <th className="text-right py-3 px-3 hidden md:table-cell">GC</th>
                      <th className="text-right py-3 px-3 hidden md:table-cell">KL</th>
                      <th className="text-right py-3 px-3 hidden md:table-cell">CC</th>
                      <th className="text-right py-3 px-3 hidden md:table-cell">SC</th>
                      <th className="text-right py-3 px-4 font-bold">Totale</th>
                      <th className="text-right py-3 px-4 w-32">%</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ranking.map((r) => {
                      const isTop3 = r.POSIZIONE <= 3;
                      const medalEmoji =
                        r.POSIZIONE === 1 ? "🥇" : r.POSIZIONE === 2 ? "🥈" : r.POSIZIONE === 3 ? "🥉" : null;

                      let rowBg = "";
                      if (stagione !== null) {
                        const pos = r.POSIZIONE;
                        if (stagione <= 2) {
                          if (pos <= 4)      rowBg = "bg-emerald-700/25";
                          else if (pos <= 8) rowBg = "bg-emerald-400/15";
                        } else {
                          if (pos <= 4)       rowBg = "bg-emerald-700/25";
                          else if (pos <= 6)  rowBg = "bg-emerald-400/15";
                          else if (pos <= 10) rowBg = "bg-sky-500/15";
                        }
                      }

                      return (
                        <tr
                          key={r.SQUADRA}
                          className={
                            "border-b border-slate-800 last:border-b-0 hover:bg-slate-800/30 transition-colors " +
                            rowBg
                          }
                        >
                          <td className="text-center py-2 px-3 font-mono font-bold text-slate-300">
                            {medalEmoji ?? r.POSIZIONE}
                          </td>
                          <td className={"py-2 px-4 " + (isTop3 ? "font-semibold text-amber-200" : "text-slate-200")}>
                            {r.SQUADRA}
                          </td>
                          <td className="text-right py-2 px-3 text-slate-400 hidden md:table-cell font-mono text-xs">
                            {r["galactic league"]}
                          </td>
                          <td className="text-right py-2 px-3 text-slate-400 hidden md:table-cell font-mono text-xs">
                            {r["galactic cup"]}
                          </td>
                          <td className="text-right py-2 px-3 text-slate-400 hidden md:table-cell font-mono text-xs">
                            {r["kings league"]}
                          </td>
                          <td className="text-right py-2 px-3 text-slate-400 hidden md:table-cell font-mono text-xs">
                            {r["galactic champions cup"]}
                          </td>
                          <td className="text-right py-2 px-3 text-slate-400 hidden md:table-cell font-mono text-xs">
                            {r["intergalactic supercup"]}
                          </td>
                          <td className="text-right py-2 px-4 font-bold text-cyan-300 font-mono">
                            {r.TOTALE.toFixed(1)}
                          </td>
                          <td className="text-right py-2 px-4">
                            <div className="flex items-center justify-end gap-2">
                              <div className="hidden lg:block w-16 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-gradient-to-r from-cyan-500 to-amber-400"
                                  style={{ width: `${Math.min(100, r.PERCENTUALE)}%` }}
                                />
                              </div>
                              <span className="font-mono text-xs text-slate-300 w-12 text-right">
                                {r.PERCENTUALE.toFixed(1)}%
                              </span>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              )
            ) : rankingCumulatoLoading ? (
              <div className="text-center text-slate-400 py-10">
                Caricamento ranking cumulato…
              </div>
            ) : rankingCumulato.length === 0 ? (
              <div className="text-center text-slate-500 py-10">
                Nessun dato disponibile
              </div>
            ) : (
              <table className="w-full text-sm">
                <thead className="bg-slate-800/60 text-slate-400 uppercase text-xs tracking-wider">
                  <tr>
                    <th className="text-center py-3 px-3 w-16">#</th>
                    <th className="text-left py-3 px-4">Squadra</th>
                    {cumStagioniIncluse.map((si) => (
                      <th
                        key={si.stagione}
                        className="text-right py-3 px-3 font-mono"
                        title={`Stagione ${si.stagione} · peso ×${si.peso}`}
                      >
                        S{si.stagione}
                        <div className="text-[10px] text-slate-500 normal-case">×{si.peso}</div>
                      </th>
                    ))}
                    <th className="text-right py-3 px-4 font-bold">Totale</th>
                  </tr>
                </thead>
                <tbody>
                  {rankingCumulato.map((r) => {
                    const isTop3 = r.POSIZIONE <= 3;
                    const medalEmoji =
                      r.POSIZIONE === 1 ? "🥇" : r.POSIZIONE === 2 ? "🥈" : r.POSIZIONE === 3 ? "🥉" : null;

                    return (
                      <tr
                        key={r.SQUADRA}
                        className="border-b border-slate-800 last:border-b-0 hover:bg-slate-800/30 transition-colors"
                      >
                        <td className="text-center py-2 px-3 font-mono font-bold text-slate-300">
                          {medalEmoji ?? r.POSIZIONE}
                        </td>
                        <td className={"py-2 px-4 " + (isTop3 ? "font-semibold text-amber-200" : "text-slate-200")}>
                          {r.SQUADRA}
                        </td>
                        {cumStagioniIncluse.map((si) => {
                          const v = r[`S${si.stagione}`];
                          const num = typeof v === "number" ? v : 0;
                          const isCurrent = si.stagione === stagione;
                          return (
                            <td
                              key={si.stagione}
                              className={
                                "text-right py-2 px-3 font-mono text-xs " +
                                (isCurrent ? "text-amber-300" : "text-slate-400")
                              }
                            >
                              {num.toFixed(1)}
                            </td>
                          );
                        })}
                        <td className="text-right py-2 px-4 font-bold text-cyan-300 font-mono">
                          {r.TOTALE.toFixed(2)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>

          {/* Legenda */}
          {rankingType === "stagionale" ? (
            <p className="text-xs text-slate-500 mt-3 hidden md:block">
              GL = Galactic League · GC = Galactic Cup · KL = Kings League · CC = Champions Cup · SC = SuperCup
            </p>
          ) : (
            <p className="text-xs text-slate-500 mt-3">
              Le colonne mostrano il punteggio grezzo della stagione. Il totale applica i pesi.
              La stagione corrente è evidenziata in ambra.
            </p>
          )}
        </div>
      )}

      {/* ── MODALE INFO RANKING ─────────────────────────────────── */}
      {infoOpen && <RankingInfoModal onClose={() => setInfoOpen(false)} />}
    </div>
  );
}

/** Modale con le regole dei due ranking. */
function RankingInfoModal({ onClose }: { onClose: () => void }) {
  return (
    <div
      className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="bg-slate-900 border border-slate-700 rounded-2xl max-w-3xl w-full max-h-[85vh] overflow-y-auto shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="sticky top-0 bg-slate-900 border-b border-slate-700 px-6 py-4 flex items-center justify-between">
          <h3 className="text-xl font-bold text-amber-300">Regole del Ranking</h3>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white text-2xl leading-none"
          >
            ×
          </button>
        </div>

        <div className="p-6 space-y-6 text-sm text-slate-300">
          {/* Ranking Stagionale */}
          <section>
            <h4 className="text-lg font-bold text-cyan-300 mb-4">Ranking Stagionale</h4>
            <p className="mb-4 text-xs text-slate-400">
              Punteggio accumulato nelle 5 competizioni della stagione (Cup of 8/10 non concorre).
              Pareggio per il ranking: solo se la partita finisce ai rigori
              (es. <code className="text-slate-300">1-1 (4-3)</code>); se decisa ai supplementari
              (es. <code className="text-slate-300">2-1 [0-0]</code>) conta come vittoria/sconfitta normale.
            </p>

            {/* Galactic League */}
            <div className="mb-5 rounded-lg bg-slate-800/40 border border-slate-700 p-4">
              <h5 className="font-bold text-sky-300 mb-2">G.L (Galactic League)</h5>
              <div className="text-xs space-y-1 text-slate-300 font-mono">
                <div>1 punto a vittoria, 0.5 punti a pareggio.</div>
                <div>Chi arriva tra le prime 8: 2 punti bonus (come se avesse vinto gli spareggi entrambe le partite).</div>
                <div>Dagli ottavi in poi: 1 punto a vittoria, 0.5 punti a pareggio, 0.5 a passaggio del turno, compresa la vittoria della finale.</div>
              </div>
            </div>

            {/* Galactic Cup */}
            <div className="mb-5 rounded-lg bg-slate-800/40 border border-slate-700 p-4">
              <h5 className="font-bold text-amber-300 mb-2">G.C (Galactic Cup)</h5>
              <div className="text-xs space-y-1 text-slate-300 font-mono">
                <div>Esci al 1° turno: 0 punti</div>
                <div>Esci al 2° turno: 0.5 punti</div>
                <div>Esci agli ottavi: 1.5 punti</div>
                <div>Esci ai quarti: 2 + (1 punto a vittoria, 0.5 a pareggio)</div>
                <div>Esci in semifinale: quarti 2 + (1 V / 0.5 P) + 1 punto passaggio del turno + (1 V / 0.5 P)</div>
                <div>Esci in finale: quarti 2 + (1 V / 0.5 P) + 1 (semi) + (1 V / 0.5 P) + 1 (finale) + (0.5 a pareggio)</div>
                <div>Vinci la finale: quarti 2 + (1 V / 0.5 P) + 1 (semi) + (1 V / 0.5 P) + 1 (finale) + (1 V / 0.5 P) + 1 punto bonus</div>
              </div>
            </div>

            {/* Kings League — due rami */}
            <div className="mb-5 rounded-lg bg-slate-800/40 border border-slate-700 p-4">
              <h5 className="font-bold text-purple-300 mb-2">K.L (Galactic Kings League)</h5>

              <div className="text-xs space-y-1 text-slate-300 font-mono mb-3">
                <div>Vittoria: 1 punto · Pareggio: 0.5 punti</div>
              </div>

              <div className="mb-3">
                <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">
                  S1 – S4 (formato vecchio, 2 leghe)
                </div>
                <div className="text-xs space-y-1 text-slate-300 font-mono pl-2">
                  <div>Bonus partecipazione Lega A: +2</div>
                  <div>Prime di ogni girone di Lega B (promosse dirette): +1</div>
                  <div>Vincitrice Playoff Lega B - Finale (promossa via playoff): +0.5</div>
                  <div>Final Four (solo Lega A):</div>
                  <div className="pl-3">· Eliminata in semifinale: +1.0</div>
                  <div className="pl-3">· Eliminata in finale: +1.5</div>
                  <div className="pl-3">· Vincitrice della Final Four: +2.5</div>
                </div>
              </div>

              <div>
                <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">
                  S5+ (formato nuovo, 3 leghe)
                </div>
                <div className="text-xs space-y-1 text-slate-300 font-mono pl-2">
                  <div>Lega C:</div>
                  <div className="pl-3">· Promozione diretta: 1 punto</div>
                  <div className="pl-3">· Promozione Play off 1° turno: 0.5 punti</div>
                  <div className="pl-3">· Promozione Play off 2° turno: 0.5 punti</div>
                  <div className="mt-1">Lega B:</div>
                  <div className="pl-3">· Bonus Partecipazione: 1.5 punti</div>
                  <div className="pl-3">· Promozione diretta: 1 punto</div>
                  <div className="pl-3">· Promozione 2° posto: 0.5 punti</div>
                  <div className="pl-3">· Promozione Play off: 0.5 punti</div>
                  <div className="mt-1">Lega A:</div>
                  <div className="pl-3">· Bonus Partecipazione: 3 punti</div>
                  <div className="pl-3">· Primo posto nel girone: 1 punto</div>
                  <div className="pl-3">· Raggiungi la finale: 0.5 punti</div>
                  <div className="pl-3">· Vinci la finale: 1 punto</div>
                </div>
              </div>
            </div>

            {/* Champions Cup */}
            <div className="mb-5 rounded-lg bg-slate-800/40 border border-slate-700 p-4">
              <h5 className="font-bold text-emerald-300 mb-2">C.C (Galactic Champions Cup)</h5>

              <div className="mb-3">
                <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">
                  Fase 1
                </div>
                <div className="text-xs space-y-1 text-slate-300 font-mono pl-2">
                  <div>(Punteggio × 0.10) → arrotondamento allo 0.5 più vicino</div>
                </div>
              </div>

              <div className="mb-3">
                <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">
                  Fase 2 (6 gironi)
                </div>
                <div className="text-xs space-y-1 text-slate-300 font-mono pl-2">
                  <div>Primo posto nel girone: 2 punti</div>
                  <div>Secondo posto nel girone: 1.5 punti</div>
                  <div>Le 4 migliori terze: 1 punto</div>
                  <div>Eliminate: 0.5 punti</div>
                </div>
              </div>

              <div>
                <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">
                  Fase 3 (Ottavi → Finale)
                </div>
                <div className="text-xs space-y-1 text-slate-300 font-mono pl-2">
                  <div>Ottavi: Vittoria 1 / Pareggio 0.5 · Passaggio del turno 0.5</div>
                  <div>Quarti: Vittoria 1 / Pareggio 0.5 · Passaggio del turno 1</div>
                  <div>Semifinali: Vittoria 1 / Pareggio 0.5 · Passaggio del turno 1</div>
                  <div>Finale: Vittoria 1 / Pareggio 0.5 · Vittoria del torneo 1</div>
                </div>
              </div>
            </div>

            {/* SuperCup */}
            <div className="mb-2 rounded-lg bg-slate-800/40 border border-slate-700 p-4">
              <h5 className="font-bold text-pink-300 mb-2">I.S.C (Intergalactic SuperCup)</h5>
              <div className="text-xs space-y-1 text-slate-300 font-mono">
                <div>Chi arriva in finale (sconfitta): 0.5 punti</div>
                <div>Chi vince il torneo: 1 punto</div>
              </div>
            </div>

            <p className="mt-3 text-xs text-slate-400">
              <strong>Massimo teorico totale</strong>: 53.0 (S1-S4) o 54.0 (S5+).
              La colonna "%" del ranking stagionale mostra il rapporto tra il totale ottenuto e questo massimo.
            </p>
          </section>

          {/* Ranking Cumulato */}
          <section className="border-t border-slate-700 pt-5">
            <h4 className="text-lg font-bold text-cyan-300 mb-3">Ranking Cumulato</h4>
            <p className="mb-3">
              Somma pesata del ranking stagionale delle ultime 5 stagioni (corrente + 4 precedenti).
              Le stagioni più vecchie pesano meno per dare più importanza ai risultati recenti:
            </p>
            <ul className="space-y-1 pl-4 font-mono text-xs">
              <li>Stagione corrente <span className="text-cyan-300">× 1.0</span></li>
              <li>Stagione precedente <span className="text-cyan-300">× 0.9</span></li>
              <li>2 stagioni fa <span className="text-cyan-300">× 0.8</span></li>
              <li>3 stagioni fa <span className="text-cyan-300">× 0.7</span></li>
              <li>4 stagioni fa <span className="text-cyan-300">× 0.6</span></li>
            </ul>
            <p className="mt-3 text-xs text-slate-400">
              Disponibile dalla stagione 2 in poi. Se mancano stagioni passate (es. in S2 esistono
              solo S1 e S2), vengono usate solo quelle disponibili.
            </p>
            <p className="mt-2 text-xs text-slate-400">
              Il totale è arrotondato alla seconda cifra decimale (es. <code className="text-slate-300">133.60</code>).
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}

type ClassificaRow = {
  Posizione: number;
  SQUADRA: string;
  W: number;
  D: number;
  L: number;
  PT: number;
  GF: number;
  GS: number;
  DIFF: number;
};

type KingsClassificaRow = ClassificaRow & {
  Lega: string;
  Girone: string;
  colore: "verde" | "verde_chiaro" | "giallo" | "arancione" | "neutro";
};

type ChampionsClassificaRow = ClassificaRow & {
  Girone: string;
  colore: "verde" | "arancione" | "neutro";
};

/** Drill-down: partite raggruppate per giornata, con collapsibili. */
function MatchesView({
  title,
  accent,
  compKey,
  partite,
  loading,
  stagione,
  onBack,
}: {
  title: string;
  accent: keyof typeof ACCENT;
  compKey: string;
  partite: Partita[];
  loading: boolean;
  stagione: number;
  onBack: () => void;
}) {
  const accentClasses = ACCENT[accent];
  const isGalacticLeague = compKey === "galactic league";
  const isGalacticCup = compKey === "galactic cup";
  const isKingsLeague = compKey === "Kings League";
  const isChampionsCup = compKey === "galactic champions cup";
  const hasExcelView =
    isGalacticLeague || isGalacticCup || isKingsLeague || isChampionsCup;
  const toggleActive = isGalacticCup
    ? "bg-amber-500/20 text-amber-200"
    : isKingsLeague
      ? "bg-purple-500/20 text-purple-200"
      : isChampionsCup
        ? "bg-emerald-500/20 text-emerald-200"
        : "bg-sky-500/20 text-sky-200";
  const excelLabel = isGalacticCup
    ? "Vista tabellone"
    : isKingsLeague
      ? "Vista classifica"
      : isChampionsCup
        ? "Vista fasi"
        : "Vista Excel";

  // raggruppa per giornata, mantenendo l'ordine di prima apparizione
  const giornate = useMemo(() => {
    const order: string[] = [];
    const groups: Record<string, Partita[]> = {};
    for (const p of partite) {
      if (!(p.giornata in groups)) {
        groups[p.giornata] = [];
        order.push(p.giornata);
      }
      groups[p.giornata].push(p);
    }
    return order.map((g) => ({ giornata: g, partite: groups[g] }));
  }, [partite]);

  const [openGiornate, setOpenGiornate] = useState<Set<string>>(new Set());

  // Apri tutte di default al primo render
  useEffect(() => {
    setOpenGiornate(new Set(giornate.map((g) => g.giornata)));
  }, [giornate]);

  const toggle = (g: string) => {
    setOpenGiornate((prev) => {
      const next = new Set(prev);
      if (next.has(g)) next.delete(g);
      else next.add(g);
      return next;
    });
  };

  // ── Vista Excel / classifica ───────────────────────────────────
  const [viewMode, setViewMode] = useState<"lista" | "excel">("lista");
  const [classifica, setClassifica] = useState<ClassificaRow[]>([]);
  const [classificaLoading, setClassificaLoading] = useState(false);
  const [kingsClassifica, setKingsClassifica] = useState<KingsClassificaRow[]>([]);
  const [kingsLoading, setKingsLoading] = useState(false);
  const [championsFase1, setChampionsFase1] = useState<ChampionsClassificaRow[]>([]);
  const [championsFase2, setChampionsFase2] = useState<ChampionsClassificaRow[]>([]);
  const [championsLoading, setChampionsLoading] = useState(false);

  // Suddividi giornate in fase a gironi (Giornata 1-8) e fase eliminazione
  const leagueGiornate = useMemo(
    () => giornate.filter((g) => /^Giornata \d+$/.test(g.giornata)),
    [giornate],
  );
  const eliminazioneGiornate = useMemo(
    () => giornate.filter((g) => !/^Giornata \d+$/.test(g.giornata)),
    [giornate],
  );

  const [selectedGiornataIdx, setSelectedGiornataIdx] = useState(0);
  // Resetta indice quando cambiano le giornate disponibili
  useEffect(() => {
    setSelectedGiornataIdx(0);
  }, [leagueGiornate.length]);

  // Carica la classifica quando si entra in vista Excel
  useEffect(() => {
    if (!isGalacticLeague || viewMode !== "excel") return;
    setClassificaLoading(true);
    fetch(`${API_URL}/galactic-league/classifica?stagione=${stagione}`)
      .then((r) => r.json())
      .then((d) => setClassifica(d.classifica || []))
      .catch(() => setClassifica([]))
      .finally(() => setClassificaLoading(false));
  }, [isGalacticLeague, viewMode, stagione]);

  // Carica le classifiche dei gironi Kings League quando si entra in vista classifica
  useEffect(() => {
    if (!isKingsLeague || viewMode !== "excel") return;
    setKingsLoading(true);
    fetch(`${API_URL}/kings-league/classifica?stagione=${stagione}`)
      .then((r) => r.json())
      .then((d) => setKingsClassifica(d.classifica || []))
      .catch(() => setKingsClassifica([]))
      .finally(() => setKingsLoading(false));
  }, [isKingsLeague, viewMode, stagione]);

  // Carica le classifiche dei gironi Champions Cup (Fase 1 + Fase 2) in vista fasi
  useEffect(() => {
    if (!isChampionsCup || viewMode !== "excel") return;
    setChampionsLoading(true);
    Promise.all([
      fetch(`${API_URL}/champions-cup/classifica?stagione=${stagione}&fase=1`).then((r) => r.json()),
      fetch(`${API_URL}/champions-cup/classifica?stagione=${stagione}&fase=2`).then((r) => r.json()),
    ])
      .then(([d1, d2]) => {
        setChampionsFase1(d1.classifica || []);
        setChampionsFase2(d2.classifica || []);
      })
      .catch(() => {
        setChampionsFase1([]);
        setChampionsFase2([]);
      })
      .finally(() => setChampionsLoading(false));
  }, [isChampionsCup, viewMode, stagione]);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <button
            onClick={onBack}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors text-sm font-medium border border-slate-700"
          >
            ← Torna alle competizioni
          </button>
          <span className="text-xs text-slate-500">Stagione {stagione}</span>
        </div>
      </div>

      <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
        <h2 className={"text-3xl font-bold " + accentClasses.iconColor}>
          {title}
        </h2>
        {hasExcelView && (
          <div className="flex rounded-lg overflow-hidden border border-slate-700 shadow-inner">
            <button
              onClick={() => setViewMode("lista")}
              className={
                "px-4 py-2 text-sm font-medium transition-colors " +
                (viewMode === "lista"
                  ? toggleActive
                  : "bg-slate-800/50 text-slate-400 hover:text-white")
              }
            >
              Vista lista
            </button>
            <button
              onClick={() => setViewMode("excel")}
              className={
                "px-4 py-2 text-sm font-medium transition-colors border-l border-slate-700 " +
                (viewMode === "excel"
                  ? toggleActive
                  : "bg-slate-800/50 text-slate-400 hover:text-white")
              }
            >
              {excelLabel}
            </button>
          </div>
        )}
      </div>

      {/* ── VISTA EXCEL (Galactic League) ───────────────────────── */}
      {isGalacticLeague && viewMode === "excel" ? (
        <ExcelLeagueView
          classifica={classifica}
          classificaLoading={classificaLoading}
          leagueGiornate={leagueGiornate}
          eliminazioneGiornate={eliminazioneGiornate}
          selectedGiornataIdx={selectedGiornataIdx}
          setSelectedGiornataIdx={setSelectedGiornataIdx}
          loading={loading}
          partite={partite}
        />
      ) : /* ── VISTA TABELLONE (Galactic Cup) ──────────────────── */
      isGalacticCup && viewMode === "excel" ? (
        loading ? (
          <div className="text-center text-slate-400 py-16">Caricamento partite…</div>
        ) : partite.length === 0 ? (
          <div className="text-center text-slate-400 py-16">
            Nessuna partita per questa competizione
          </div>
        ) : (
          <div>
            <h3 className="text-xl font-bold text-amber-300 mb-3">Tabellone</h3>
            <LeagueBracket
              partite={partite}
              rounds={CUP_ROUNDS}
              accentText="text-amber-300"
            />
          </div>
        )
      ) : /* ── VISTA CLASSIFICA (Kings League) ─────────────────── */
      isKingsLeague && viewMode === "excel" ? (
        <KingsLeagueView
          classifica={kingsClassifica}
          classificaLoading={kingsLoading}
          partite={partite}
          loading={loading}
        />
      ) : /* ── VISTA FASI (Galactic Champions Cup) ─────────────── */
      isChampionsCup && viewMode === "excel" ? (
        <ChampionsCupView
          fase1={championsFase1}
          fase2={championsFase2}
          partite={partite}
          loading={loading || championsLoading}
        />
      ) : loading ? (
        <div className="text-center text-slate-400 py-16">Caricamento partite…</div>
      ) : partite.length === 0 ? (
        <div className="text-center text-slate-400 py-16">
          Nessuna partita per questa competizione
        </div>
      ) : (
        <div className="space-y-3">
          {giornate.map(({ giornata, partite }) => {
            const isOpen = openGiornate.has(giornata);
            return (
              <div
                key={giornata}
                className="rounded-xl bg-slate-900/40 border border-slate-700 overflow-hidden"
              >
                <button
                  onClick={() => toggle(giornata)}
                  className="w-full flex items-center justify-between px-5 py-3 hover:bg-slate-800/40 transition-colors"
                >
                  <span className="font-semibold text-white">{giornata}</span>
                  <span className="flex items-center gap-3">
                    <span className="text-xs text-slate-400">
                      {partite.length} partit{partite.length === 1 ? "a" : "e"}
                    </span>
                    <span
                      className={
                        "text-slate-400 transition-transform " +
                        (isOpen ? "rotate-90" : "")
                      }
                    >
                      ›
                    </span>
                  </span>
                </button>
                {isOpen && (
                  <div className="border-t border-slate-700">
                    <table className="w-full text-sm">
                      <tbody>
                        {partite.map((p, i) => (
                          <tr
                            key={i}
                            className="border-b border-slate-800 last:border-b-0 hover:bg-slate-800/20"
                          >
                            <td className="px-5 py-2.5 text-right text-slate-200 w-2/5">
                              {p.squadra_casa}
                            </td>
                            <td className="px-3 py-2.5 text-center font-mono font-semibold text-cyan-300 w-1/5">
                              {p.risultato}
                            </td>
                            <td className="px-5 py-2.5 text-left text-slate-200 w-2/5">
                              {p.squadra_trasferta}
                            </td>
                            <td className="px-3 py-2.5 text-right text-xs text-slate-500 hidden lg:table-cell">
                              {p.campo && p.campo !== "Neutro"
                                ? `🏠 ${p.campo}`
                                : p.campo === "Neutro"
                                  ? "Neutro"
                                  : ""}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

/** Vista "Squadre": lista alfabetica con stats stagionali aggregate. */
function SquadreView({
  squadre,
  loading,
  onSelect,
}: {
  squadre: SquadraStats[];
  loading: boolean;
  onSelect: (squadra: string) => void;
}) {
  if (loading) {
    return <div className="text-center text-slate-400 py-16">Caricamento squadre…</div>;
  }
  if (squadre.length === 0) {
    return (
      <div className="text-center text-slate-400 py-16">
        Nessuna squadra disponibile per la stagione selezionata
      </div>
    );
  }

  return (
    <div className="rounded-2xl bg-slate-900/50 border border-slate-700 overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-slate-800/60 text-slate-400 uppercase text-xs tracking-wider">
          <tr>
            <th className="text-center py-3 px-3 w-12">#</th>
            <th className="text-left py-3 px-4">Squadra</th>
            <th className="text-right py-3 px-3">V</th>
            <th className="text-right py-3 px-3">P</th>
            <th className="text-right py-3 px-3">S</th>
            <th className="text-right py-3 px-4">Goal</th>
            <th className="text-right py-3 px-4 font-bold">PTS</th>
          </tr>
        </thead>
        <tbody>
          {squadre.map((s, idx) => (
            <tr
              key={s.SQUADRA}
              onClick={() => onSelect(s.SQUADRA)}
              className="border-b border-slate-800 last:border-b-0 hover:bg-slate-800/40 transition-colors cursor-pointer"
            >
              <td className="text-center py-3 px-3 font-mono text-slate-500 text-xs">
                {idx + 1}
              </td>
              <td className="py-3 px-4">
                <div className="flex items-center gap-3">
                  <span className="font-semibold text-cyan-300">{s.SQUADRA}</span>
                  <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-slate-700/60 text-slate-300 tracking-wider">
                    {siglaSquadra(s.SQUADRA)}
                  </span>
                </div>
              </td>
              <td className="text-right py-3 px-3 font-mono text-emerald-300">{s.V}</td>
              <td className="text-right py-3 px-3 font-mono text-slate-300">{s.P}</td>
              <td className="text-right py-3 px-3 font-mono text-rose-300">{s.S}</td>
              <td className="text-right py-3 px-4 font-mono font-semibold text-white">
                {s.GF}-{s.GS}
              </td>
              <td className="text-right py-3 px-4 font-mono font-bold text-cyan-300">
                {s.PTS.toFixed(2)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/** Drill-down: tutte le partite di una squadra nella stagione, raggruppate per competizione. */
function TeamMatchesView({
  squadra,
  stats,
  partite,
  loading,
  stagione,
  onBack,
}: {
  squadra: string;
  stats: SquadraStats | null;
  partite: Partita[];
  loading: boolean;
  stagione: number;
  onBack: () => void;
}) {
  // Raggruppa per competizione, secondo COMP_ORDER. Le partite all'interno
  // arrivano già ordinate da backend (categorical GIORNATE_ORDER).
  const groups = useMemo(() => {
    const byComp: Record<string, Partita[]> = {};
    for (const p of partite) {
      if (!byComp[p.Competizione]) byComp[p.Competizione] = [];
      byComp[p.Competizione].push(p);
    }
    const ordered: { comp: string; partite: Partita[] }[] = [];
    for (const k of COMP_ORDER) {
      if (byComp[k]?.length) ordered.push({ comp: k, partite: byComp[k] });
    }
    // Eventuali competizioni non previste in COMP_ORDER
    for (const k of Object.keys(byComp)) {
      if (!COMP_ORDER.includes(k)) ordered.push({ comp: k, partite: byComp[k] });
    }
    return ordered;
  }, [partite]);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <button
            onClick={onBack}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors text-sm font-medium border border-slate-700"
          >
            ← Torna alle squadre
          </button>
          <span className="text-xs text-slate-500">Stagione {stagione}</span>
        </div>
      </div>

      {/* Header squadra + statistiche */}
      <div className="rounded-2xl bg-slate-900/50 border border-slate-700 p-6 mb-6">
        <div className="flex items-center gap-3 mb-4">
          <h2 className="text-4xl font-bold text-cyan-300">{squadra}</h2>
          <span className="px-2 py-0.5 rounded text-xs font-bold bg-slate-700/60 text-slate-300 tracking-wider">
            {siglaSquadra(squadra)}
          </span>
        </div>
        <div className="grid grid-cols-3 md:grid-cols-6 gap-4 text-center">
          <div>
            <div className="text-3xl font-bold text-white font-mono">{partite.length}</div>
            <div className="text-xs text-slate-400 uppercase tracking-wider mt-1">Giocate</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-emerald-300 font-mono">{stats?.V ?? 0}</div>
            <div className="text-xs text-slate-400 uppercase tracking-wider mt-1">Vittorie</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-slate-200 font-mono">{stats?.P ?? 0}</div>
            <div className="text-xs text-slate-400 uppercase tracking-wider mt-1">Pareggi</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-rose-300 font-mono">{stats?.S ?? 0}</div>
            <div className="text-xs text-slate-400 uppercase tracking-wider mt-1">Sconfitte</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-white font-mono">{stats?.GF ?? 0}</div>
            <div className="text-xs text-slate-400 uppercase tracking-wider mt-1">Gol fatti</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-white font-mono">{stats?.GS ?? 0}</div>
            <div className="text-xs text-slate-400 uppercase tracking-wider mt-1">Gol subiti</div>
          </div>
        </div>
      </div>

      {/* Partite raggruppate per competizione */}
      {loading ? (
        <div className="text-center text-slate-400 py-16">Caricamento partite…</div>
      ) : partite.length === 0 ? (
        <div className="text-center text-slate-400 py-16">
          Nessuna partita per questa squadra
        </div>
      ) : (
        <div className="space-y-5">
          {groups.map(({ comp, partite: ps }) => {
            const accentKey = COMP_ACCENT[comp] ?? "sky";
            const accent = ACCENT[accentKey];
            return (
              <div
                key={comp}
                className="rounded-xl border border-slate-700 bg-slate-900/40 overflow-hidden"
              >
                <div
                  className={
                    "px-5 py-3 border-b border-slate-700 flex items-center justify-between " +
                    accent.cardBg
                  }
                >
                  <h3 className={"font-bold text-lg " + accent.iconColor}>
                    {COMP_LABEL[comp] ?? comp}
                  </h3>
                  <span className="text-xs text-slate-400">
                    {ps.length} partit{ps.length === 1 ? "a" : "e"}
                  </span>
                </div>
                <table className="w-full text-sm">
                  <thead className="bg-slate-800/40 text-slate-500 uppercase text-[10px] tracking-wider">
                    <tr>
                      <th className="text-right py-2 px-4 w-2/5">Casa</th>
                      <th className="text-center py-2 px-2">Risultato</th>
                      <th className="text-left py-2 px-4 w-2/5">Trasferta</th>
                      <th className="text-center py-2 px-2 w-16">Sede</th>
                      <th className="text-left py-2 px-4">Fase</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ps.map((p, i) => {
                      const isHome = p.squadra_casa === squadra;
                      const outcome = matchOutcome(p, squadra);
                      const outcomeBg =
                        outcome === "V"
                          ? "bg-emerald-500/15"
                          : outcome === "S"
                            ? "bg-rose-500/15"
                            : "bg-sky-500/15";
                      const sedeIcon = isHome ? (
                        <span className="text-emerald-400 font-bold" title="Casa">H</span>
                      ) : (
                        <span className="text-rose-400 font-bold" title="Trasferta">A</span>
                      );
                      return (
                        <tr
                          key={i}
                          className={
                            "border-b border-slate-800 last:border-b-0 hover:brightness-125 transition-all " +
                            outcomeBg
                          }
                        >
                          <td className={"text-right py-2 px-4 " + (isHome ? "text-amber-300 font-semibold" : "text-slate-200")}>
                            {p.squadra_casa}
                          </td>
                          <td className="text-center py-2 px-2 font-mono font-semibold text-white">
                            {p.risultato}
                          </td>
                          <td className={"text-left py-2 px-4 " + (!isHome ? "text-amber-300 font-semibold" : "text-slate-200")}>
                            {p.squadra_trasferta}
                          </td>
                          <td className="text-center py-2 px-2 font-mono text-xs">
                            {p.campo === "Neutro" ? (
                              <span className="text-slate-400">N</span>
                            ) : (
                              sedeIcon
                            )}
                          </td>
                          <td className="text-left py-2 px-4 text-xs text-slate-400">
                            {p.giornata}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

/** Mappa esito (colore backend) → classe di sfondo riga. */
const KINGS_COLORE_BG: Record<string, string> = {
  verde: "bg-emerald-600/30",
  verde_chiaro: "bg-emerald-400/15",
  giallo: "bg-yellow-500/20",
  arancione: "bg-orange-600/30",
  neutro: "",
};

/** Vista "classifica" della Kings League: gironi per Lega (colorati per esito)
 *  + risultati di playoff/playout/final four. */
function KingsLeagueView({
  classifica,
  classificaLoading,
  partite,
  loading,
}: {
  classifica: KingsClassificaRow[];
  classificaLoading: boolean;
  partite: Partita[];
  loading: boolean;
}) {
  // Raggruppa per Lega → Girone (Lega A in alto, poi B, poi C)
  const leghe = useMemo(() => {
    const order = ["Lega A", "Lega B", "Lega C"];
    const byLega: Record<string, Record<string, KingsClassificaRow[]>> = {};
    for (const r of classifica) {
      if (!byLega[r.Lega]) byLega[r.Lega] = {};
      if (!byLega[r.Lega][r.Girone]) byLega[r.Lega][r.Girone] = [];
      byLega[r.Lega][r.Girone].push(r);
    }
    return order
      .filter((l) => byLega[l])
      .map((lega) => ({
        lega,
        gironi: Object.keys(byLega[lega])
          .sort()
          .map((g) => ({
            girone: g,
            rows: byLega[lega][g]
              .slice()
              .sort((a, b) => a.Posizione - b.Posizione),
          })),
      }));
  }, [classifica]);

  // Fasi finali = partite la cui giornata NON inizia con "Fase 1"
  const finali = useMemo(() => {
    const ordine: string[] = [];
    const groups: Record<string, Partita[]> = {};
    for (const p of partite) {
      if (String(p.giornata).startsWith("Fase 1")) continue;
      if (!(p.giornata in groups)) {
        groups[p.giornata] = [];
        ordine.push(p.giornata);
      }
      groups[p.giornata].push(p);
    }
    return ordine.map((g) => ({ giornata: g, partite: groups[g] }));
  }, [partite]);

  if (loading || classificaLoading) {
    return <div className="text-center text-slate-400 py-16">Caricamento…</div>;
  }
  if (classifica.length === 0) {
    return (
      <div className="text-center text-slate-400 py-16">
        Classifiche non disponibili per questa stagione
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {leghe.map(({ lega, gironi }) => (
        <div key={lega}>
          <h3 className="text-xl font-bold text-purple-300 mb-3">{lega}</h3>
          <div className="grid gap-4 md:grid-cols-2">
            {gironi.map(({ girone, rows }) => (
              <div
                key={girone}
                className="rounded-xl bg-slate-900/50 border border-slate-700 overflow-hidden"
              >
                <div className="px-4 py-2 bg-slate-800/50 text-sm font-semibold text-purple-200">
                  {girone}
                </div>
                <table className="w-full text-sm">
                  <thead className="bg-slate-800/40 text-slate-400 text-[11px] uppercase tracking-wider">
                    <tr>
                      <th className="text-center py-1.5 px-2 w-8">#</th>
                      <th className="text-left py-1.5 px-2">Squadra</th>
                      <th className="text-right py-1.5 px-1.5 w-8">W</th>
                      <th className="text-right py-1.5 px-1.5 w-8">D</th>
                      <th className="text-right py-1.5 px-1.5 w-8">L</th>
                      <th className="text-right py-1.5 px-1.5 w-10">PT</th>
                      <th className="text-right py-1.5 px-1.5 w-10 hidden sm:table-cell">GF</th>
                      <th className="text-right py-1.5 px-1.5 w-10 hidden sm:table-cell">GS</th>
                      <th className="text-right py-1.5 px-2 w-12">DIFF</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((r) => (
                      <tr
                        key={r.SQUADRA}
                        className={
                          "border-t border-slate-800 " +
                          (KINGS_COLORE_BG[r.colore] || "")
                        }
                      >
                        <td className="text-center py-1.5 px-2 font-mono text-slate-400">
                          {r.Posizione}
                        </td>
                        <td className="py-1.5 px-2 font-semibold text-slate-100">
                          {r.SQUADRA}
                        </td>
                        <td className="text-right py-1.5 px-1.5 font-mono text-emerald-300">{r.W}</td>
                        <td className="text-right py-1.5 px-1.5 font-mono text-slate-300">{r.D}</td>
                        <td className="text-right py-1.5 px-1.5 font-mono text-rose-300">{r.L}</td>
                        <td className="text-right py-1.5 px-1.5 font-mono font-bold text-cyan-300">{r.PT}</td>
                        <td className="text-right py-1.5 px-1.5 font-mono text-slate-300 hidden sm:table-cell">{r.GF}</td>
                        <td className="text-right py-1.5 px-1.5 font-mono text-slate-300 hidden sm:table-cell">{r.GS}</td>
                        <td
                          className={
                            "text-right py-1.5 px-2 font-mono " +
                            (r.DIFF > 0
                              ? "text-emerald-300"
                              : r.DIFF < 0
                                ? "text-rose-300"
                                : "text-slate-300")
                          }
                        >
                          {r.DIFF > 0 ? `+${r.DIFF}` : r.DIFF}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ))}
          </div>
        </div>
      ))}

      {/* Legenda colori */}
      <div className="text-[10px] text-slate-500 flex flex-wrap gap-x-4 gap-y-1">
        <span><span className="inline-block w-3 h-3 align-middle bg-emerald-600/40 mr-1"></span>Promossa / 1ª (Final Four)</span>
        <span><span className="inline-block w-3 h-3 align-middle bg-emerald-400/25 mr-1"></span>2ª non promossa ai playoff</span>
        <span><span className="inline-block w-3 h-3 align-middle bg-yellow-500/30 mr-1"></span>Salva ai playout</span>
        <span><span className="inline-block w-3 h-3 align-middle bg-orange-600/40 mr-1"></span>Retrocessa</span>
      </div>

      {/* Risultati fasi finali */}
      {finali.length > 0 && (
        <div>
          <h3 className="text-xl font-bold text-purple-300 mb-3">
            Playoff / Playout / Final Four
          </h3>
          <div className="space-y-3">
            {finali.map(({ giornata, partite }) => (
              <div
                key={giornata}
                className="rounded-xl bg-slate-900/40 border border-slate-700 overflow-hidden"
              >
                <div className="px-5 py-2.5 border-b border-slate-700 bg-slate-800/40 font-semibold text-purple-200 text-sm">
                  {giornata}
                </div>
                <table className="w-full text-sm">
                  <tbody>
                    {partite.map((p, i) => (
                      <tr
                        key={i}
                        className="border-b border-slate-800 last:border-b-0 hover:bg-slate-800/20"
                      >
                        <td className="px-5 py-2 text-right text-slate-200 w-2/5">{p.squadra_casa}</td>
                        <td className="px-3 py-2 text-center font-mono font-semibold text-cyan-300 w-1/5">{p.risultato}</td>
                        <td className="px-5 py-2 text-left text-slate-200 w-2/5">{p.squadra_trasferta}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

/** Raggruppa le righe per Girone (ordine alfabetico) e ordina per posizione. */
function raggruppaGironi(rows: ChampionsClassificaRow[]) {
  const groups: Record<string, ChampionsClassificaRow[]> = {};
  const ordine: string[] = [];
  for (const r of rows) {
    if (!groups[r.Girone]) {
      groups[r.Girone] = [];
      ordine.push(r.Girone);
    }
    groups[r.Girone].push(r);
  }
  return ordine.sort().map((g) => ({
    girone: g,
    rows: groups[g].slice().sort((a, b) => a.Posizione - b.Posizione),
  }));
}

/** Griglia di tabelline-girone (riusata dalle fasi della Champions Cup). */
function ChampionsGironiGrid({ rows }: { rows: ChampionsClassificaRow[] }) {
  const gironi = raggruppaGironi(rows);
  return (
    <div className="grid gap-4 md:grid-cols-2">
      {gironi.map(({ girone, rows }) => (
        <div
          key={girone}
          className="rounded-xl bg-slate-900/50 border border-slate-700 overflow-hidden"
        >
          <div className="px-4 py-2 bg-slate-800/50 text-sm font-semibold text-emerald-200">
            {girone}
          </div>
          <table className="w-full text-sm">
            <thead className="bg-slate-800/40 text-slate-400 text-[11px] uppercase tracking-wider">
              <tr>
                <th className="text-center py-1.5 px-2 w-8">#</th>
                <th className="text-left py-1.5 px-2">Squadra</th>
                <th className="text-right py-1.5 px-1.5 w-8">W</th>
                <th className="text-right py-1.5 px-1.5 w-8">D</th>
                <th className="text-right py-1.5 px-1.5 w-8">L</th>
                <th className="text-right py-1.5 px-1.5 w-10">PT</th>
                <th className="text-right py-1.5 px-1.5 w-10 hidden sm:table-cell">GF</th>
                <th className="text-right py-1.5 px-1.5 w-10 hidden sm:table-cell">GS</th>
                <th className="text-right py-1.5 px-2 w-12">DIFF</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr
                  key={r.SQUADRA}
                  className={"border-t border-slate-800 " + (KINGS_COLORE_BG[r.colore] || "")}
                >
                  <td className="text-center py-1.5 px-2 font-mono text-slate-400">{r.Posizione}</td>
                  <td className="py-1.5 px-2 font-semibold text-slate-100">{r.SQUADRA}</td>
                  <td className="text-right py-1.5 px-1.5 font-mono text-emerald-300">{r.W}</td>
                  <td className="text-right py-1.5 px-1.5 font-mono text-slate-300">{r.D}</td>
                  <td className="text-right py-1.5 px-1.5 font-mono text-rose-300">{r.L}</td>
                  <td className="text-right py-1.5 px-1.5 font-mono font-bold text-cyan-300">{r.PT}</td>
                  <td className="text-right py-1.5 px-1.5 font-mono text-slate-300 hidden sm:table-cell">{r.GF}</td>
                  <td className="text-right py-1.5 px-1.5 font-mono text-slate-300 hidden sm:table-cell">{r.GS}</td>
                  <td
                    className={
                      "text-right py-1.5 px-2 font-mono " +
                      (r.DIFF > 0 ? "text-emerald-300" : r.DIFF < 0 ? "text-rose-300" : "text-slate-300")
                    }
                  >
                    {r.DIFF > 0 ? `+${r.DIFF}` : r.DIFF}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
    </div>
  );
}

/** Vista "fasi" della Galactic Champions Cup: Fase 1 (6 gironi da 6),
 *  Fase 2 (6 gironi da 4) colorate per esito, e Fase 3 (tabellone finale). */
function ChampionsCupView({
  fase1,
  fase2,
  partite,
  loading,
}: {
  fase1: ChampionsClassificaRow[];
  fase2: ChampionsClassificaRow[];
  partite: Partita[];
  loading: boolean;
}) {
  const hasFase3 = useMemo(
    () => partite.some((p) => String(p.giornata).startsWith("Fase 3")),
    [partite],
  );

  if (loading) {
    return <div className="text-center text-slate-400 py-16">Caricamento…</div>;
  }
  if (fase1.length === 0 && fase2.length === 0 && !hasFase3) {
    return (
      <div className="text-center text-slate-400 py-16">
        Classifiche non disponibili per questa stagione
      </div>
    );
  }

  return (
    <div className="space-y-10">
      {fase1.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-xl font-bold text-emerald-300">Fase 1 — Gironi</h3>
          <ChampionsGironiGrid rows={fase1} />
          <div className="text-[10px] text-slate-500 flex flex-wrap gap-x-4 gap-y-1">
            <span><span className="inline-block w-3 h-3 align-middle bg-emerald-600/40 mr-1"></span>1ª — fascia 1 nel sorteggio Fase 2</span>
            <span>2ª-4ª — qualificate alla Fase 2</span>
            <span><span className="inline-block w-3 h-3 align-middle bg-orange-600/40 mr-1"></span>Ultime 2 — eliminate</span>
          </div>
        </div>
      )}

      {fase2.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-xl font-bold text-emerald-300">Fase 2 — Gironi</h3>
          <ChampionsGironiGrid rows={fase2} />
          <div className="text-[10px] text-slate-500 flex flex-wrap gap-x-4 gap-y-1">
            <span><span className="inline-block w-3 h-3 align-middle bg-emerald-600/40 mr-1"></span>1ª — qualificata</span>
            <span><span className="inline-block w-3 h-3 align-middle bg-emerald-400/25 mr-1"></span>2ª · miglior 3ª — qualificate</span>
            <span><span className="inline-block w-3 h-3 align-middle bg-orange-600/40 mr-1"></span>4ª · peggiori 3ª — eliminate</span>
          </div>
        </div>
      )}

      {hasFase3 && (
        <div className="space-y-3">
          <h3 className="text-xl font-bold text-emerald-300">Fase 3 — Tabellone</h3>
          <LeagueBracket
            partite={partite}
            rounds={CHAMPIONS_FASE3_ROUNDS}
            accentText="text-emerald-300"
          />
        </div>
      )}
    </div>
  );
}

/** Vista "Excel" della Galactic League: classifica + una giornata alla volta. */
function ExcelLeagueView({
  classifica,
  classificaLoading,
  leagueGiornate,
  eliminazioneGiornate,
  selectedGiornataIdx,
  setSelectedGiornataIdx,
  loading,
  partite,
}: {
  classifica: ClassificaRow[];
  classificaLoading: boolean;
  leagueGiornate: { giornata: string; partite: Partita[] }[];
  eliminazioneGiornate: { giornata: string; partite: Partita[] }[];
  selectedGiornataIdx: number;
  setSelectedGiornataIdx: (i: number) => void;
  loading: boolean;
  partite: Partita[];
}) {
  if (loading) {
    return <div className="text-center text-slate-400 py-16">Caricamento partite…</div>;
  }
  if (partite.length === 0) {
    return (
      <div className="text-center text-slate-400 py-16">
        Nessuna partita per questa competizione
      </div>
    );
  }

  const current = leagueGiornate[selectedGiornataIdx];

  return (
    <div className="space-y-8">
      {/* Classifica League Phase */}
      <div>
        <h3 className="text-xl font-bold text-sky-300 mb-3">Classifica League Phase</h3>
        {classificaLoading ? (
          <div className="text-center text-slate-400 py-8">Caricamento classifica…</div>
        ) : classifica.length === 0 ? (
          <div className="text-center text-slate-500 py-8 text-sm">Classifica non disponibile</div>
        ) : (
          <div className="rounded-2xl bg-slate-900/50 border border-slate-700 overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-800/60 text-slate-400 uppercase text-xs tracking-wider">
                <tr>
                  <th className="text-center py-2 px-3 w-12">Pos</th>
                  <th className="text-left py-2 px-4">Squadra</th>
                  <th className="text-right py-2 px-3 w-12">W</th>
                  <th className="text-right py-2 px-3 w-12">D</th>
                  <th className="text-right py-2 px-3 w-12">L</th>
                  <th className="text-right py-2 px-3 w-14">PT</th>
                  <th className="text-right py-2 px-3 w-14">GF</th>
                  <th className="text-right py-2 px-3 w-14">GS</th>
                  <th className="text-right py-2 px-3 w-14">DIFF</th>
                </tr>
              </thead>
              <tbody>
                {classifica.map((r) => {
                  let rowBg = "";
                  if (r.Posizione <= 8)       rowBg = "bg-emerald-700/20";
                  else if (r.Posizione <= 24) rowBg = "bg-sky-500/10";
                  else if (r.Posizione <= 28) rowBg = "";
                  else                         rowBg = "bg-rose-500/10";
                  return (
                    <tr
                      key={r.SQUADRA}
                      className={
                        "border-b border-slate-800 last:border-b-0 hover:brightness-125 transition-all " +
                        rowBg
                      }
                    >
                      <td className="text-center py-2 px-3 font-mono font-bold text-slate-300">
                        {r.Posizione}
                      </td>
                      <td className="py-2 px-4 font-semibold text-slate-100">{r.SQUADRA}</td>
                      <td className="text-right py-2 px-3 font-mono text-emerald-300">{r.W}</td>
                      <td className="text-right py-2 px-3 font-mono text-slate-300">{r.D}</td>
                      <td className="text-right py-2 px-3 font-mono text-rose-300">{r.L}</td>
                      <td className="text-right py-2 px-3 font-mono font-bold text-cyan-300">{r.PT}</td>
                      <td className="text-right py-2 px-3 font-mono text-slate-300">{r.GF}</td>
                      <td className="text-right py-2 px-3 font-mono text-slate-300">{r.GS}</td>
                      <td
                        className={
                          "text-right py-2 px-3 font-mono " +
                          (r.DIFF > 0
                            ? "text-emerald-300"
                            : r.DIFF < 0
                              ? "text-rose-300"
                              : "text-slate-300")
                        }
                      >
                        {r.DIFF > 0 ? `+${r.DIFF}` : r.DIFF}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            <div className="px-4 py-2 text-[10px] text-slate-500 border-t border-slate-800 flex flex-wrap gap-x-4 gap-y-1">
              <span><span className="inline-block w-3 h-3 align-middle bg-emerald-700/40 mr-1"></span>1-8 qualificate ottavi</span>
              <span><span className="inline-block w-3 h-3 align-middle bg-sky-500/20 mr-1"></span>9-24 playoff</span>
              <span>25-28 eliminate</span>
              <span><span className="inline-block w-3 h-3 align-middle bg-rose-500/20 mr-1"></span>29-36 playoff Galactic Cup</span>
            </div>
          </div>
        )}
      </div>

      {/* Selettore giornata */}
      {leagueGiornate.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-3 flex-wrap gap-3">
            <h3 className="text-xl font-bold text-sky-300">Risultati giornata</h3>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setSelectedGiornataIdx(Math.max(0, selectedGiornataIdx - 1))}
                disabled={selectedGiornataIdx === 0}
                className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300 text-sm border border-slate-700"
              >
                ←
              </button>
              <select
                value={selectedGiornataIdx}
                onChange={(e) => setSelectedGiornataIdx(parseInt(e.target.value, 10))}
                className="px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-600 text-white text-sm focus:outline-none focus:border-cyan-400"
              >
                {leagueGiornate.map((g, i) => (
                  <option key={g.giornata} value={i}>{g.giornata}</option>
                ))}
              </select>
              <button
                onClick={() =>
                  setSelectedGiornataIdx(Math.min(leagueGiornate.length - 1, selectedGiornataIdx + 1))
                }
                disabled={selectedGiornataIdx >= leagueGiornate.length - 1}
                className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300 text-sm border border-slate-700"
              >
                →
              </button>
            </div>
          </div>

          {current && (
            <div className="rounded-xl bg-slate-900/40 border border-slate-700 overflow-hidden">
              <div className="px-5 py-3 border-b border-slate-700 bg-slate-800/40 flex items-center justify-between">
                <span className="font-bold text-sky-300">{current.giornata}</span>
                <span className="text-xs text-slate-400">
                  {current.partite.length} partit{current.partite.length === 1 ? "a" : "e"}
                </span>
              </div>
              <table className="w-full text-sm">
                <tbody>
                  {current.partite.map((p, i) => (
                    <tr
                      key={i}
                      className="border-b border-slate-800 last:border-b-0 hover:bg-slate-800/20"
                    >
                      <td className="px-5 py-2.5 text-right text-slate-200 w-2/5">{p.squadra_casa}</td>
                      <td className="px-3 py-2.5 text-center font-mono font-semibold text-cyan-300 w-1/5">
                        {p.risultato}
                      </td>
                      <td className="px-5 py-2.5 text-left text-slate-200 w-2/5">{p.squadra_trasferta}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Fase eliminazione: bracket */}
      {eliminazioneGiornate.length > 0 && (
        <div>
          <h3 className="text-xl font-bold text-sky-300 mb-3">Fase eliminazione</h3>
          <LeagueBracket partite={partite} />
        </div>
      )}
    </div>
  );
}

// ─── Helpers per il bracket ─────────────────────────────────────
function parseScorePair(ris: string): [number | null, number | null] {
  const m = ris.match(/^(\d+)-(\d+)/);
  return m ? [parseInt(m[1], 10), parseInt(m[2], 10)] : [null, null];
}

function parsePenalties(ris: string): [number, number] | null {
  const m = ris.match(/\((\d+)-(\d+)\)/);
  return m ? [parseInt(m[1], 10), parseInt(m[2], 10)] : null;
}

function winnerSingleMatch(p: Partita): string | null {
  const [gc, gt] = parseScorePair(p.risultato);
  if (gc === null || gt === null) return null;
  const pens = parsePenalties(p.risultato);
  if (pens) {
    const [a, b] = pens;
    return a > b ? p.squadra_casa : p.squadra_trasferta;
  }
  if (gc > gt) return p.squadra_casa;
  if (gc < gt) return p.squadra_trasferta;
  return null;
}

function aggregateWinner(andata: Partita, ritorno: Partita): string | null {
  const [aGc, aGt] = parseScorePair(andata.risultato);
  const [rGc, rGt] = parseScorePair(ritorno.risultato);
  if (aGc === null || rGc === null) return null;
  const teamA = andata.squadra_casa;
  const teamB = andata.squadra_trasferta;
  // In ritorno i ruoli sono normalmente invertiti
  let teamAGoals: number;
  let teamBGoals: number;
  if (ritorno.squadra_casa === teamA) {
    teamAGoals = aGc + rGc;
    teamBGoals = aGt + rGt;
  } else {
    teamAGoals = aGc + rGt;
    teamBGoals = aGt + rGc;
  }
  if (teamAGoals > teamBGoals) return teamA;
  if (teamAGoals < teamBGoals) return teamB;
  // Aggregato pari → decide il ritorno (rigori)
  return winnerSingleMatch(ritorno);
}

type BracketLeg = { a: number | null; b: number | null };
type BracketTie = {
  team_a: string;
  team_b: string;
  legs: BracketLeg[];
  winner: string | null;
  ai_rigori: boolean;
};
type BracketRound = { label: string; ties: BracketTie[] };

type RoundConfig = {
  label: string;
  andata?: string;
  ritorno?: string;
  single?: string;
};

const LEAGUE_ROUNDS: RoundConfig[] = [
  { label: "Play Off",   andata: "Play Off - Andata",         ritorno: "Play Off - Ritorno" },
  { label: "Ottavi",     andata: "Ottavi League - Andata",    ritorno: "Ottavi League - Ritorno" },
  { label: "Quarti",     andata: "Quarti League - Andata",    ritorno: "Quarti League - Ritorno" },
  { label: "Semifinale", andata: "Semifinale League - Andata", ritorno: "Semifinale League - Ritorno" },
  { label: "Finale",     single: "Finale League" },
];

/** Turni della Galactic Cup (eliminazione diretta pura). I label combaciano
 *  con il campo "giornata" estratto dal backend per la galactic cup. */
const CUP_ROUNDS: RoundConfig[] = [
  { label: "Turno 1",    single: "Turno 1" },
  { label: "Turno 2",    single: "Turno 2" },
  { label: "Ottavi",     single: "Ottavi di Finale" },
  { label: "Quarti",     andata: "Quarti di Finale - Andata",  ritorno: "Quarti di Finale - Ritorno" },
  { label: "Semifinale", andata: "Semifinale - Andata",         ritorno: "Semifinale - Ritorno" },
  { label: "Finale",     single: "Finale Cup" },
];

/** Fase finale della Galactic Champions Cup: tutte gare secche. */
const CHAMPIONS_FASE3_ROUNDS: RoundConfig[] = [
  { label: "Ottavi",     single: "Fase 3 - Ottavi di Finale" },
  { label: "Quarti",     single: "Fase 3 - Quarti di Finale" },
  { label: "Semifinale", single: "Fase 3 - Semifinale" },
  { label: "Finale",     single: "Fase 3 - Finale" },
];

function buildBracket(partite: Partita[], roundsCfg: RoundConfig[]): BracketRound[] {
  const rounds: BracketRound[] = [];
  for (const cfg of roundsCfg) {
    if (cfg.single) {
      // Un turno "secco" può avere più partite (es. Cup: Turno 1/2, Ottavi):
      // genera un tie per ogni partita, non solo la prima.
      const rows = partite.filter((p) => p.giornata === cfg.single);
      const ties: BracketTie[] = rows.map((m) => {
        const [gc, gt] = parseScorePair(m.risultato);
        return {
          team_a: m.squadra_casa,
          team_b: m.squadra_trasferta,
          legs: [{ a: gc, b: gt }],
          winner: winnerSingleMatch(m),
          ai_rigori: parsePenalties(m.risultato) !== null,
        };
      });
      rounds.push({ label: cfg.label, ties });
      continue;
    }

    const andate = partite.filter((p) => p.giornata === cfg.andata);
    const ritorni = partite.filter((p) => p.giornata === cfg.ritorno);
    const used = new Set<number>();
    const ties: BracketTie[] = [];
    for (const andata of andate) {
      const key = [andata.squadra_casa, andata.squadra_trasferta].sort().join("|");
      let rIdx = -1;
      for (let i = 0; i < ritorni.length; i++) {
        if (used.has(i)) continue;
        const r = ritorni[i];
        const rKey = [r.squadra_casa, r.squadra_trasferta].sort().join("|");
        if (rKey === key) { rIdx = i; break; }
      }
      if (rIdx === -1) continue;
      used.add(rIdx);
      const ritorno = ritorni[rIdx];

      const teamA = andata.squadra_casa;
      const teamB = andata.squadra_trasferta;
      const [aGc, aGt] = parseScorePair(andata.risultato);
      const [rGc, rGt] = parseScorePair(ritorno.risultato);
      const leg1: BracketLeg = { a: aGc, b: aGt };
      const leg2: BracketLeg =
        ritorno.squadra_casa === teamA
          ? { a: rGc, b: rGt }
          : { a: rGt, b: rGc };

      const winner = aggregateWinner(andata, ritorno);
      const totA = (leg1.a ?? 0) + (leg2.a ?? 0);
      const totB = (leg1.b ?? 0) + (leg2.b ?? 0);
      const aiRigori = parsePenalties(ritorno.risultato) !== null && totA === totB;

      ties.push({
        team_a: teamA,
        team_b: teamB,
        legs: [leg1, leg2],
        winner,
        ai_rigori: aiRigori,
      });
    }
    rounds.push({ label: cfg.label, ties });
  }
  return rounds;
}

/** Bracket "box affiancati" senza linee per le fasi a eliminazione.
 *  Riusato da Galactic League (default) e Galactic Cup (rounds + accent diversi). */
function LeagueBracket({
  partite,
  rounds: roundsCfg = LEAGUE_ROUNDS,
  accentText = "text-sky-300",
}: {
  partite: Partita[];
  rounds?: RoundConfig[];
  accentText?: string;
}) {
  const rounds = useMemo(() => buildBracket(partite, roundsCfg), [partite, roundsCfg]);
  return (
    <div className="overflow-x-auto pb-2">
      <div className="flex gap-3 min-w-fit">
        {rounds.map((round) => (
          <div key={round.label} className="flex flex-col gap-2 min-w-[180px]">
            <div className={"text-xs font-bold uppercase tracking-wider px-1 " + accentText}>
              {round.label}
            </div>
            {round.ties.length === 0 ? (
              <div className="text-xs text-slate-600 italic px-1 py-2">—</div>
            ) : (
              round.ties.map((tie, i) => <TieBox key={i} tie={tie} />)
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function TieBox({ tie }: { tie: BracketTie }) {
  const aWin = tie.winner === tie.team_a;
  const bWin = tie.winner === tie.team_b;
  const nameCls = (w: boolean) =>
    w ? "text-emerald-300 font-semibold" : "text-slate-400";
  const scoreCls = (w: boolean) =>
    w ? "text-emerald-300 font-mono font-bold" : "text-slate-500 font-mono";

  return (
    <div className="rounded-md bg-slate-900/60 border border-slate-700 px-2.5 py-2 text-xs hover:border-slate-600 transition-colors">
      {/* Row team A */}
      <div className="flex items-center justify-between gap-2">
        <span className={"truncate " + nameCls(aWin)} title={tie.team_a}>
          {tie.team_a}
        </span>
        <div className="flex items-center gap-1.5 shrink-0">
          {tie.legs.map((leg, i) => (
            <span key={i} className={scoreCls(aWin) + " w-4 text-center"}>
              {leg.a ?? "—"}
            </span>
          ))}
        </div>
      </div>
      {/* Row team B */}
      <div className="flex items-center justify-between gap-2 mt-1">
        <span className={"truncate " + nameCls(bWin)} title={tie.team_b}>
          {tie.team_b}
        </span>
        <div className="flex items-center gap-1.5 shrink-0">
          {tie.legs.map((leg, i) => (
            <span key={i} className={scoreCls(bWin) + " w-4 text-center"}>
              {leg.b ?? "—"}
            </span>
          ))}
        </div>
      </div>
      {tie.ai_rigori && (
        <div className="text-[9px] text-amber-400 italic mt-1 text-right">
          decisa ai rigori
        </div>
      )}
    </div>
  );
}

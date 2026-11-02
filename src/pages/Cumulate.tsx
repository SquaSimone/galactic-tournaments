import { useEffect, useMemo, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:3004/api";

type Trofei = {
  "galactic league": number;
  "galactic cup": number;
  "Kings League": number;
  "galactic champions cup": number;
  "intergalactic supercup": number;
  cup: number;
};

type Medaglie = { oro: number; argento: number; bronzo: number };

type SquadraCumulata = {
  SQUADRA: string;
  trofei: Trofei;
  medaglie: Medaglie;
  totale_trofei: number;
  cumulato_attuale: number;
  posizione_cumulato: number | null;
  star_points: number;
};

type StagioneRow = {
  stagione: number;
  V: number;
  P: number;
  S: number;
  PTS: number | null;
  POS: number | null;
  titoli: number;
  titoli_dettaglio: string[];
};

/** Immagini custom dei trofei (servite da public/). */
const COMP_IMG = {
  "galactic league": "/galactic-league.png",
  "galactic cup": "/galactic-cup.png",
  "Kings League": "/kings-league.png",
  "galactic champions cup": "/galactic-champions-cup.png",
  "intergalactic supercup": "/intergalactic-super-cup.png",
  "cup": "/cup-of-10.png",
} as const;

const COMPETIZIONI: Array<{
  key: keyof Trofei;
  sigla: string;
  label: string;
  icon: string;
  img?: string;
  accent: string;
}> = [
  { key: "galactic league",        sigla: "GL",  label: "Galactic League",        icon: "🛰️", img: COMP_IMG["galactic league"], accent: "text-sky-300" },
  { key: "galactic cup",           sigla: "GC",  label: "Galactic Cup",           icon: "🏆", img: COMP_IMG["galactic cup"], accent: "text-amber-300" },
  { key: "Kings League",           sigla: "GKL", label: "Galactic Kings League",  icon: "👑", img: COMP_IMG["Kings League"], accent: "text-purple-300" },
  { key: "galactic champions cup", sigla: "GCC", label: "Galactic Champions Cup", icon: "⭐", img: COMP_IMG["galactic champions cup"], accent: "text-emerald-300" },
  { key: "intergalactic supercup", sigla: "ISC", label: "Intergalactic SuperCup", icon: "🚀", img: COMP_IMG["intergalactic supercup"], accent: "text-pink-300" },
  { key: "cup",                    sigla: "C8/10", label: "Cup of 8 / 10",        icon: "🔟", img: COMP_IMG["cup"], accent: "text-indigo-300" },
];

function siglaSquadra(nome: string): string {
  const clean = nome.replace(/[^A-Za-z]/g, "");
  return clean.slice(0, 3).toUpperCase();
}

type H2HPartita = {
  stagione: number;
  Competizione: string;
  giornata: string;
  squadra_casa: string;
  squadra_trasferta: string;
  risultato: string;
  campo: string | null;
};

type H2HSede = "Casa" | "Trasferta" | "Neutro";

const COMP_LABEL: Record<string, string> = {
  "galactic league": "Galactic League",
  "galactic cup": "Galactic Cup",
  "Kings League": "Galactic Kings League",
  "galactic champions cup": "Galactic Champions Cup",
  "intergalactic supercup": "Intergalactic SuperCup",
  "cup of 8": "Cup of 8",
  "cup of 10": "Cup of 10",
};

/** Esito dal punto di vista di `squadra`. Rigori → pareggio. */
function outcomePer(p: H2HPartita, squadra: string): "V" | "P" | "S" {
  const m = p.risultato.match(/^(\d+)-(\d+)/);
  if (!m) return "P";
  const gc = parseInt(m[1], 10);
  const gt = parseInt(m[2], 10);
  if (gc === gt) return "P";
  const isHome = p.squadra_casa === squadra;
  const homeWon = gc > gt;
  return homeWon === isHome ? "V" : "S";
}

/** Sede di una partita dal punto di vista di `squadra`. */
function sedePer(p: H2HPartita, squadra: string): H2HSede {
  if (p.campo === "Neutro") return "Neutro";
  return p.squadra_casa === squadra ? "Casa" : "Trasferta";
}

export default function Cumulate() {
  const [squadre, setSquadre] = useState<SquadraCumulata[]>([]);
  const [stagioneCorrente, setStagioneCorrente] = useState<number | null>(null);
  const [stagioniDisponibili, setStagioniDisponibili] = useState<number[]>([]);
  const [stagioneMax, setStagioneMax] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  const [selectedSquadra, setSelectedSquadra] = useState<string | null>(null);
  const [stagioniRows, setStagioniRows] = useState<StagioneRow[]>([]);
  const [stagioniLoading, setStagioniLoading] = useState(false);

  // Ordinamento
  type SortKey = "SQUADRA" | "cumulato" | "totale" | "oro" | "argento" | "bronzo" | "star";
  const [sortKey, setSortKey] = useState<SortKey>("SQUADRA");
  const [sortAsc, setSortAsc] = useState(true);

  // Modale info Star Points
  const [starInfoOpen, setStarInfoOpen] = useState(false);

  useEffect(() => {
    setLoading(true);
    const qs = stagioneMax !== null ? `?stagione_max=${stagioneMax}` : "";
    fetch(`${API_URL}/cumulato/squadre${qs}`)
      .then((r) => r.json())
      .then((data) => {
        setSquadre(data.squadre || []);
        setStagioneCorrente(data.stagione_corrente ?? null);
        setStagioniDisponibili(data.stagioni || []);
      })
      .catch(() => setSquadre([]))
      .finally(() => setLoading(false));
  }, [stagioneMax]);

  useEffect(() => {
    if (selectedSquadra === null) return;
    setStagioniLoading(true);
    fetch(`${API_URL}/cumulato/squadra/${encodeURIComponent(selectedSquadra)}`)
      .then((r) => r.json())
      .then((data) => setStagioniRows(data.stagioni || []))
      .catch(() => setStagioniRows([]))
      .finally(() => setStagioniLoading(false));
  }, [selectedSquadra]);

  const sortedSquadre = useMemo(() => {
    const arr = [...squadre];
    arr.sort((a, b) => {
      let av: number | string;
      let bv: number | string;
      switch (sortKey) {
        case "cumulato":
          av = a.cumulato_attuale; bv = b.cumulato_attuale; break;
        case "totale":
          av = a.totale_trofei; bv = b.totale_trofei; break;
        case "oro":
          av = a.medaglie.oro; bv = b.medaglie.oro; break;
        case "argento":
          av = a.medaglie.argento; bv = b.medaglie.argento; break;
        case "bronzo":
          av = a.medaglie.bronzo; bv = b.medaglie.bronzo; break;
        case "star":
          av = a.star_points; bv = b.star_points; break;
        default:
          av = a.SQUADRA; bv = b.SQUADRA;
      }
      if (av < bv) return sortAsc ? -1 : 1;
      if (av > bv) return sortAsc ? 1 : -1;
      // tie-break stabile: nome alfabetico
      return a.SQUADRA.localeCompare(b.SQUADRA);
    });
    return arr;
  }, [squadre, sortKey, sortAsc]);

  const toggleSort = (k: SortKey) => {
    if (sortKey === k) {
      setSortAsc((v) => !v);
    } else {
      setSortKey(k);
      setSortAsc(k === "SQUADRA"); // default: alfabetico asc, numerici desc
      if (k !== "SQUADRA") setSortAsc(false);
    }
  };

  const sortArrow = (k: SortKey) =>
    sortKey === k ? (sortAsc ? " ▲" : " ▼") : "";

  // Drill-down: dettaglio per stagione
  if (selectedSquadra !== null) {
    const sq = squadre.find((s) => s.SQUADRA === selectedSquadra) ?? null;
    return (
      <TeamSeasonsView
        squadra={selectedSquadra}
        riepilogo={sq}
        stagioni={stagioniRows}
        loading={stagioniLoading}
        allSquadre={squadre.map((x) => x.SQUADRA)}
        onBack={() => setSelectedSquadra(null)}
      />
    );
  }

  return (
    <div>
      <div className="flex items-end justify-between mb-6 flex-wrap gap-4">
        <div>
          <h1 className="text-5xl font-bold text-amber-300 tracking-wide drop-shadow-[0_0_30px_rgba(252,211,77,0.3)]">
            Statistiche Cumulate
          </h1>
          <p className="text-slate-400 mt-1 text-sm">
            Trofei vinti, medaglie del ranking stagionale e punteggio cumulato attuale
          </p>
        </div>
        <div className="flex items-end gap-4 flex-wrap">
          <div className="text-right text-xs text-slate-500">
            {stagioniDisponibili.length} stagion
            {stagioniDisponibili.length === 1 ? "e" : "i"} caricat
            {stagioniDisponibili.length === 1 ? "a" : "e"}
            {stagioneCorrente !== null && (
              <div className="text-slate-400 text-sm mt-1">
                Cumulato calcolato su Stagione {stagioneCorrente}
              </div>
            )}
          </div>
          {stagioniDisponibili.length > 0 && (
            <div className="flex items-center gap-2">
              <label className="text-sm text-slate-300 font-medium">Fino a stagione:</label>
              <select
                value={stagioneMax ?? Math.max(...stagioniDisponibili)}
                onChange={(e) => setStagioneMax(parseInt(e.target.value, 10))}
                className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-600 text-white focus:outline-none focus:border-cyan-400"
              >
                {[...stagioniDisponibili].sort((a, b) => a - b).map((s) => (
                  <option key={s} value={s}>S{s}</option>
                ))}
              </select>
            </div>
          )}
        </div>
      </div>

      {loading ? (
        <div className="text-center text-slate-400 py-16">Caricamento…</div>
      ) : squadre.length === 0 ? (
        <div className="text-center text-slate-400 py-16">
          Nessuna stagione caricata
        </div>
      ) : (
        <div className="rounded-2xl bg-slate-900/50 border border-slate-700 overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-800/60 text-slate-400 uppercase text-xs tracking-wider">
              <tr>
                <th className="text-center py-3 px-3 w-12">#</th>
                <th
                  className="text-left py-3 px-4 cursor-pointer hover:text-white"
                  onClick={() => toggleSort("SQUADRA")}
                >
                  Squadra{sortArrow("SQUADRA")}
                </th>
                {COMPETIZIONI.map((c) => (
                  <th
                    key={c.key}
                    className="text-center py-3 px-2 font-normal"
                    title={c.label}
                  >
                    {c.img ? (
                      <img
                        src={c.img}
                        alt={c.label}
                        className="h-6 w-6 mx-auto object-contain"
                      />
                    ) : (
                      <div className="text-lg leading-none">{c.icon}</div>
                    )}
                    <div className={"text-[10px] mt-0.5 " + c.accent}>{c.sigla}</div>
                  </th>
                ))}
                <th
                  className="text-center py-3 px-2 cursor-pointer hover:text-white border-l border-slate-700"
                  onClick={() => toggleSort("totale")}
                  title="Totale trofei"
                >
                  Tot{sortArrow("totale")}
                </th>
                <th
                  className="text-center py-3 px-2 cursor-pointer hover:text-white border-l border-slate-700"
                  onClick={() => toggleSort("oro")}
                  title="Volte 1° nel ranking stagionale"
                >
                  🥇{sortArrow("oro")}
                </th>
                <th
                  className="text-center py-3 px-2 cursor-pointer hover:text-white"
                  onClick={() => toggleSort("argento")}
                  title="Volte 2° nel ranking stagionale"
                >
                  🥈{sortArrow("argento")}
                </th>
                <th
                  className="text-center py-3 px-2 cursor-pointer hover:text-white"
                  onClick={() => toggleSort("bronzo")}
                  title="Volte 3° nel ranking stagionale"
                >
                  🥉{sortArrow("bronzo")}
                </th>
                <th
                  className="text-right py-3 px-4 cursor-pointer hover:text-white font-bold border-l border-slate-700"
                  onClick={() => toggleSort("cumulato")}
                  title="Punteggio ranking cumulato attuale"
                >
                  Cumulato{sortArrow("cumulato")}
                </th>
                <th className="text-right py-3 px-4 font-bold border-l border-slate-700">
                  <div className="inline-flex items-center gap-1.5">
                    <span
                      className="cursor-pointer hover:text-white"
                      onClick={() => toggleSort("star")}
                    >
                      ⭐ Star{sortArrow("star")}
                    </span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setStarInfoOpen(true);
                      }}
                      className="w-5 h-5 rounded-full bg-slate-700 hover:bg-slate-600 text-slate-300 hover:text-white text-[10px] font-bold flex items-center justify-center transition-colors"
                      title="Come si calcolano gli Star Points"
                    >
                      i
                    </button>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              {sortedSquadre.map((s, idx) => (
                <tr
                  key={s.SQUADRA}
                  onClick={() => setSelectedSquadra(s.SQUADRA)}
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
                  {COMPETIZIONI.map((c) => {
                    const n = s.trofei[c.key] ?? 0;
                    return (
                      <td
                        key={c.key}
                        className={
                          "text-center py-3 px-2 font-mono text-xs " +
                          (n > 0 ? "text-amber-300 font-bold" : "text-slate-600")
                        }
                      >
                        {n > 0 ? n : "—"}
                      </td>
                    );
                  })}
                  <td className="text-center py-3 px-2 font-mono font-bold text-amber-200 border-l border-slate-800 text-xs">
                    {s.totale_trofei > 0 ? s.totale_trofei : <span className="text-slate-600">—</span>}
                  </td>
                  <td className="text-center py-3 px-2 font-mono text-xs border-l border-slate-800">
                    {s.medaglie.oro > 0 ? (
                      <span className="text-amber-300 font-bold">{s.medaglie.oro}</span>
                    ) : (
                      <span className="text-slate-600">—</span>
                    )}
                  </td>
                  <td className="text-center py-3 px-2 font-mono text-xs">
                    {s.medaglie.argento > 0 ? (
                      <span className="text-slate-200 font-bold">{s.medaglie.argento}</span>
                    ) : (
                      <span className="text-slate-600">—</span>
                    )}
                  </td>
                  <td className="text-center py-3 px-2 font-mono text-xs">
                    {s.medaglie.bronzo > 0 ? (
                      <span className="text-orange-400 font-bold">{s.medaglie.bronzo}</span>
                    ) : (
                      <span className="text-slate-600">—</span>
                    )}
                  </td>
                  <td className="text-right py-3 px-4 font-mono font-bold text-cyan-300 border-l border-slate-800">
                    {s.cumulato_attuale.toFixed(2)}
                  </td>
                  <td className="text-right py-3 px-4 font-mono font-bold text-amber-300 border-l border-slate-800">
                    {s.star_points.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <p className="text-xs text-slate-500 mt-3 flex flex-wrap items-center gap-x-3 gap-y-1">
        {COMPETIZIONI.map((c) => (
          <span key={c.key} className="inline-flex items-center gap-1">
            {c.img ? (
              <img src={c.img} alt="" className="inline h-4 w-4 object-contain" />
            ) : (
              <span>{c.icon}</span>
            )}
            {c.label}
          </span>
        ))}
        <span>· Clicca su una squadra per il dettaglio per stagione</span>
      </p>

      {starInfoOpen && <StarPointsInfoModal onClose={() => setStarInfoOpen(false)} />}
    </div>
  );
}

/** Modale che spiega come si calcolano gli Star Points. */
function StarPointsInfoModal({ onClose }: { onClose: () => void }) {
  const trofei: Array<{ label: string; pts: number; accent: string; icon: string; img?: string }> = [
    { label: "Galactic League",        pts: 5.00, accent: "text-sky-300",     icon: "🛰️", img: COMP_IMG["galactic league"] },
    { label: "Galactic Champions Cup", pts: 3.75, accent: "text-emerald-300", icon: "⭐", img: COMP_IMG["galactic champions cup"] },
    { label: "Galactic Cup",           pts: 2.50, accent: "text-amber-300",   icon: "🏆", img: COMP_IMG["galactic cup"] },
    { label: "Galactic Kings League",  pts: 2.00, accent: "text-purple-300",  icon: "👑", img: COMP_IMG["Kings League"] },
    { label: "Cup of 8 / 10",          pts: 1.20, accent: "text-indigo-300",  icon: "🔟", img: COMP_IMG["cup"] },
    { label: "Intergalactic SuperCup", pts: 0.70, accent: "text-pink-300",    icon: "🚀", img: COMP_IMG["intergalactic supercup"] },
  ];
  const medaglie: Array<{ label: string; pts: number; icon: string; color: string }> = [
    { label: "Oro (1° ranking)",     pts: 0.25, icon: "🥇", color: "text-amber-300" },
    { label: "Argento (2° ranking)", pts: 0.10, icon: "🥈", color: "text-slate-200" },
    { label: "Bronzo (3° ranking)",  pts: 0.05, icon: "🥉", color: "text-orange-400" },
  ];

  return (
    <div
      className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="bg-slate-900 border border-slate-700 rounded-2xl max-w-xl w-full max-h-[85vh] overflow-y-auto shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="sticky top-0 bg-slate-900 border-b border-slate-700 px-6 py-4 flex items-center justify-between">
          <h3 className="text-xl font-bold text-amber-300">⭐ Star Points — Regole</h3>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white text-2xl leading-none"
          >
            ×
          </button>
        </div>

        <div className="p-6 text-sm text-slate-300">
          <p className="mb-4 text-slate-400">
            Punteggio assegnato per ogni trofeo vinto e per ogni medaglia ottenuta nel ranking
            stagionale, sommato su tutte le stagioni caricate.
          </p>

          <h4 className="text-base font-bold text-cyan-300 mb-2">Trofei (per ogni vittoria)</h4>
          <table className="w-full text-xs mb-5">
            <tbody>
              {trofei.map((t) => (
                <tr key={t.label} className="border-b border-slate-800 last:border-b-0">
                  <td className="py-2">
                    {t.img ? (
                      <img
                        src={t.img}
                        alt=""
                        className="inline h-4 w-4 mr-2 object-contain align-text-bottom"
                      />
                    ) : (
                      <span className="mr-2">{t.icon}</span>
                    )}
                    <span className={t.accent}>{t.label}</span>
                  </td>
                  <td className="py-2 text-right font-mono font-bold text-amber-300">
                    +{t.pts.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <h4 className="text-base font-bold text-cyan-300 mb-2">Medaglie ranking stagionale</h4>
          <table className="w-full text-xs">
            <tbody>
              {medaglie.map((m) => (
                <tr key={m.label} className="border-b border-slate-800 last:border-b-0">
                  <td className="py-2">
                    <span className="mr-2">{m.icon}</span>
                    <span className={m.color}>{m.label}</span>
                  </td>
                  <td className="py-2 text-right font-mono font-bold text-amber-300">
                    +{m.pts.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="mt-5 p-3 rounded-lg bg-slate-800/60 border border-slate-700 text-xs">
            <strong className="text-amber-300">Esempio</strong>: una squadra con 1 Galactic League, 2 Galactic Cup,
            1 oro e 3 bronzi ottiene <span className="font-mono text-amber-300">
              5.00 + 2·2.50 + 0.25 + 3·0.05 = 10.40
            </span> Star Points.
          </div>
        </div>
      </div>
    </div>
  );
}

const SEASONS_PER_PAGE = 10;

/** Drill-down: per ogni stagione, V/P/S, punteggio + posizione ranking, titoli vinti. */
function TeamSeasonsView({
  squadra,
  riepilogo,
  stagioni,
  loading,
  allSquadre,
  onBack,
}: {
  squadra: string;
  riepilogo: SquadraCumulata | null;
  stagioni: StagioneRow[];
  loading: boolean;
  allSquadre: string[];
  onBack: () => void;
}) {
  const [seasonsPage, setSeasonsPage] = useState(0);
  const totalSeasonsPages = Math.max(1, Math.ceil(stagioni.length / SEASONS_PER_PAGE));
  const stagioniPagina = stagioni.slice(
    seasonsPage * SEASONS_PER_PAGE,
    (seasonsPage + 1) * SEASONS_PER_PAGE,
  );

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={onBack}
          className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors text-sm font-medium border border-slate-700"
        >
          ← Torna alle statistiche cumulate
        </button>
      </div>

      <div className="rounded-2xl bg-slate-900/50 border border-slate-700 p-6 mb-6">
        <div className="flex items-center gap-3 mb-4">
          <h2 className="text-4xl font-bold text-cyan-300">{squadra}</h2>
          <span className="px-2 py-0.5 rounded text-xs font-bold bg-slate-700/60 text-slate-300 tracking-wider">
            {siglaSquadra(squadra)}
          </span>
        </div>
        {riepilogo && (() => {
          const validPTS = stagioni
            .map((s) => s.PTS)
            .filter((v): v is number => v !== null);
          const mediaPTS =
            validPTS.length > 0
              ? validPTS.reduce((a, b) => a + b, 0) / validPTS.length
              : null;
          return (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-3xl font-bold text-amber-300 font-mono">
                  {riepilogo.totale_trofei}
                </div>
                <div className="text-xs text-slate-400 uppercase tracking-wider mt-1">Trofei</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-amber-300 font-mono">
                  🥇 {riepilogo.medaglie.oro}
                </div>
                <div className="text-xs text-slate-400 uppercase tracking-wider mt-1">Ori</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-slate-200 font-mono">
                  🥈 {riepilogo.medaglie.argento}
                </div>
                <div className="text-xs text-slate-400 uppercase tracking-wider mt-1">Argenti</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-orange-400 font-mono">
                  🥉 {riepilogo.medaglie.bronzo}
                </div>
                <div className="text-xs text-slate-400 uppercase tracking-wider mt-1">Bronzi</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-cyan-300 font-mono">
                  {riepilogo.cumulato_attuale.toFixed(2)}
                </div>
                <div className="text-xs text-slate-400 uppercase tracking-wider mt-1">Cumulato attuale</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-cyan-300 font-mono">
                  {riepilogo.posizione_cumulato !== null ? `#${riepilogo.posizione_cumulato}` : "—"}
                </div>
                <div className="text-xs text-slate-400 uppercase tracking-wider mt-1">Pos. cumulato</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-amber-300 font-mono">
                  ⭐ {riepilogo.star_points.toFixed(2)}
                </div>
                <div className="text-xs text-slate-400 uppercase tracking-wider mt-1">Star Points</div>
              </div>
              <div title={`Media del punteggio ranking sulle ${validPTS.length} stagioni`}>
                <div className="text-3xl font-bold text-cyan-300 font-mono">
                  {mediaPTS !== null ? mediaPTS.toFixed(2) : "—"}
                </div>
                <div className="text-xs text-slate-400 uppercase tracking-wider mt-1">Media PTS</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-white font-mono">{stagioni.length}</div>
                <div className="text-xs text-slate-400 uppercase tracking-wider mt-1">Stagioni</div>
              </div>
            </div>
          );
        })()}
      </div>

      {loading ? (
        <div className="text-center text-slate-400 py-16">Caricamento stagioni…</div>
      ) : stagioni.length === 0 ? (
        <div className="text-center text-slate-400 py-16">
          Nessuna stagione caricata
        </div>
      ) : (
        <div className="rounded-2xl bg-slate-900/50 border border-slate-700 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-800/60 text-slate-400 uppercase text-xs tracking-wider">
              <tr>
                <th className="text-center py-3 px-3">Stagione</th>
                <th className="text-right py-3 px-3">V</th>
                <th className="text-right py-3 px-3">P</th>
                <th className="text-right py-3 px-3">S</th>
                <th className="text-right py-3 px-4">PTS</th>
                <th className="text-center py-3 px-3">Pos.</th>
                <th className="text-center py-3 px-4">Titoli</th>
              </tr>
            </thead>
            <tbody>
              {stagioniPagina.map((r) => {
                const medal =
                  r.POS === 1 ? "🥇" : r.POS === 2 ? "🥈" : r.POS === 3 ? "🥉" : null;
                return (
                  <tr
                    key={r.stagione}
                    className="border-b border-slate-800 last:border-b-0 hover:bg-slate-800/30 transition-colors"
                  >
                    <td className="text-center py-3 px-3 font-mono font-bold text-amber-300">
                      S{r.stagione}
                    </td>
                    <td className="text-right py-3 px-3 font-mono text-emerald-300">{r.V}</td>
                    <td className="text-right py-3 px-3 font-mono text-slate-300">{r.P}</td>
                    <td className="text-right py-3 px-3 font-mono text-rose-300">{r.S}</td>
                    <td className="text-right py-3 px-4 font-mono font-bold text-cyan-300">
                      {r.PTS !== null ? r.PTS.toFixed(2) : "—"}
                    </td>
                    <td className="text-center py-3 px-3 font-mono text-slate-200">
                      {r.POS !== null ? (
                        <span className="inline-flex items-center gap-1">
                          {medal && <span>{medal}</span>}
                          <span>{r.POS}</span>
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td className="text-center py-3 px-4">
                      {r.titoli > 0 ? (
                        <span
                          className="font-bold text-amber-300"
                          title={r.titoli_dettaglio.join(", ")}
                        >
                          🏆 {r.titoli}
                        </span>
                      ) : (
                        <span className="text-slate-600">—</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Paginazione stagioni (mostrata solo con > 10 stagioni) */}
      {totalSeasonsPages > 1 && (
        <div className="flex items-center justify-center gap-2 mt-4">
          <button
            onClick={() => setSeasonsPage((p) => Math.max(0, p - 1))}
            disabled={seasonsPage === 0}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300 text-sm border border-slate-700"
          >
            ←
          </button>
          <span className="text-xs text-slate-400 font-mono">
            Pagina {seasonsPage + 1} / {totalSeasonsPages}
          </span>
          <button
            onClick={() => setSeasonsPage((p) => Math.min(totalSeasonsPages - 1, p + 1))}
            disabled={seasonsPage >= totalSeasonsPages - 1}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300 text-sm border border-slate-700"
          >
            →
          </button>
        </div>
      )}

      {/* ── HEAD-TO-HEAD ─────────────────────────────────────────────── */}
      <H2HSection
        squadra={squadra}
        allSquadre={allSquadre}
        stagioniDisponibili={stagioni.map((s) => s.stagione)}
      />
    </div>
  );
}

/** Sezione testa-a-testa: ricerca avversaria, 4 grafici a barre (Casa/Trasferta/Neutro/Totale)
 *  e lista partite raggruppata per stagione, filtrabile per range di stagioni. */
function H2HSection({
  squadra,
  allSquadre,
  stagioniDisponibili,
}: {
  squadra: string;
  allSquadre: string[];
  stagioniDisponibili: number[];
}) {
  const [query, setQuery] = useState("");
  const [avversaria, setAvversaria] = useState<string | null>(null);
  const [partite, setPartite] = useState<H2HPartita[]>([]);
  const [loading, setLoading] = useState(false);

  const minStag = stagioniDisponibili.length > 0 ? Math.min(...stagioniDisponibili) : 1;
  const maxStag = stagioniDisponibili.length > 0 ? Math.max(...stagioniDisponibili) : 1;
  const [rangeMin, setRangeMin] = useState<number>(minStag);
  const [rangeMax, setRangeMax] = useState<number>(maxStag);

  // Quando cambiano le stagioni disponibili (squadra diversa), reset del range
  useEffect(() => {
    setRangeMin(minStag);
    setRangeMax(maxStag);
  }, [minStag, maxStag]);

  // Suggerimenti per autocomplete
  const suggestions = useMemo(() => {
    if (!query.trim()) return [];
    const q = query.toLowerCase();
    return allSquadre
      .filter((s) => s !== squadra && s.toLowerCase().includes(q))
      .slice(0, 8);
  }, [query, allSquadre, squadra]);

  // Match esatto: se l'utente preme Invio o seleziona dalla lista
  const setAvversariaIfValid = (nome: string) => {
    const match = allSquadre.find(
      (s) => s !== squadra && s.toLowerCase() === nome.toLowerCase(),
    );
    if (match) {
      setAvversaria(match);
      setQuery(match);
    }
  };

  // Carica partite quando cambia avversaria
  useEffect(() => {
    if (avversaria === null) {
      setPartite([]);
      return;
    }
    setLoading(true);
    fetch(`${API_URL}/h2h?squadra=${encodeURIComponent(squadra)}&avversaria=${encodeURIComponent(avversaria)}`)
      .then((r) => r.json())
      .then((d) => setPartite(d.partite || []))
      .catch(() => setPartite([]))
      .finally(() => setLoading(false));
  }, [squadra, avversaria]);

  // Partite filtrate per range
  const partiteFiltered = useMemo(
    () => partite.filter((p) => p.stagione >= rangeMin && p.stagione <= rangeMax),
    [partite, rangeMin, rangeMax],
  );

  // Conteggi V/P/S per sede e totale
  const stats = useMemo(() => {
    const init = () => ({ V: 0, P: 0, S: 0 });
    const acc: Record<"Casa" | "Trasferta" | "Neutro" | "Totale", { V: number; P: number; S: number }> = {
      Casa: init(),
      Trasferta: init(),
      Neutro: init(),
      Totale: init(),
    };
    for (const p of partiteFiltered) {
      const sede = sedePer(p, squadra);
      const out = outcomePer(p, squadra);
      acc[sede][out] += 1;
      acc.Totale[out] += 1;
    }
    return acc;
  }, [partiteFiltered, squadra]);

  // Raggruppa partite per stagione (ordinate crescenti)
  const perStagione = useMemo(() => {
    const groups: Record<number, H2HPartita[]> = {};
    for (const p of partiteFiltered) {
      if (!groups[p.stagione]) groups[p.stagione] = [];
      groups[p.stagione].push(p);
    }
    return Object.keys(groups)
      .map((k) => parseInt(k, 10))
      .sort((a, b) => a - b)
      .map((s) => ({ stagione: s, partite: groups[s] }));
  }, [partiteFiltered]);

  return (
    <div className="mt-10 rounded-2xl bg-slate-900/50 border border-slate-700 p-6">
      <h3 className="text-2xl font-bold text-amber-300 mb-1">Testa a testa</h3>
      <p className="text-slate-400 text-xs mb-5">
        Cerca un'avversaria per vedere lo storico tra <strong className="text-cyan-300">{squadra}</strong> e quella squadra
      </p>

      {/* Ricerca avversaria + range stagioni */}
      <div className="flex flex-wrap items-end gap-4 mb-6">
        <div className="flex-1 min-w-[220px] relative">
          <label className="block text-xs text-slate-400 mb-1 uppercase tracking-wider">
            Avversaria
          </label>
          <input
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setAvversaria(null);
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter" && suggestions.length > 0) {
                setAvversariaIfValid(suggestions[0]);
              }
            }}
            placeholder="Inizia a digitare..."
            className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-600 text-white text-sm focus:outline-none focus:border-cyan-400"
          />
          {query && !avversaria && suggestions.length > 0 && (
            <div className="absolute z-10 mt-1 w-full bg-slate-900 border border-slate-700 rounded-lg shadow-xl max-h-60 overflow-y-auto">
              {suggestions.map((s) => (
                <button
                  key={s}
                  onClick={() => setAvversariaIfValid(s)}
                  className="w-full text-left px-3 py-2 text-sm text-slate-200 hover:bg-slate-800 transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>
          )}
          {query && !avversaria && suggestions.length === 0 && (
            <div className="text-xs text-slate-500 mt-1">Nessuna squadra trovata</div>
          )}
        </div>

        {stagioniDisponibili.length > 0 && (
          <>
            <div>
              <label className="block text-xs text-slate-400 mb-1 uppercase tracking-wider">
                Da stagione
              </label>
              <select
                value={rangeMin}
                onChange={(e) => {
                  const v = parseInt(e.target.value, 10);
                  setRangeMin(v);
                  if (v > rangeMax) setRangeMax(v);
                }}
                className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-600 text-white text-sm focus:outline-none focus:border-cyan-400"
              >
                {stagioniDisponibili.map((s) => (
                  <option key={s} value={s}>
                    S{s}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1 uppercase tracking-wider">
                A stagione
              </label>
              <select
                value={rangeMax}
                onChange={(e) => {
                  const v = parseInt(e.target.value, 10);
                  setRangeMax(v);
                  if (v < rangeMin) setRangeMin(v);
                }}
                className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-600 text-white text-sm focus:outline-none focus:border-cyan-400"
              >
                {stagioniDisponibili.map((s) => (
                  <option key={s} value={s}>
                    S{s}
                  </option>
                ))}
              </select>
            </div>
          </>
        )}
      </div>

      {avversaria === null ? (
        <div className="text-center text-slate-500 py-12 text-sm">
          Cerca un'avversaria per vedere le statistiche
        </div>
      ) : loading ? (
        <div className="text-center text-slate-400 py-12">Caricamento partite…</div>
      ) : partiteFiltered.length === 0 ? (
        <div className="text-center text-slate-500 py-12 text-sm">
          Nessuna partita tra <strong>{squadra}</strong> e <strong>{avversaria}</strong>
          {(rangeMin !== minStag || rangeMax !== maxStag) && " nel range selezionato"}
        </div>
      ) : (
        <>
          {/* 4 grafici a barre */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <H2HBarChart title="🏠 Casa"     icon="" stats={stats.Casa}      squadra={squadra} avversaria={avversaria} />
            <H2HBarChart title="✈️ Trasferta" icon="" stats={stats.Trasferta} squadra={squadra} avversaria={avversaria} />
            <H2HBarChart title="⚪ Neutro"   icon="" stats={stats.Neutro}    squadra={squadra} avversaria={avversaria} />
            <H2HBarChart title="Σ Totale"    icon="" stats={stats.Totale}    squadra={squadra} avversaria={avversaria} highlight />
          </div>

          {/* Partite raggruppate per stagione */}
          <div className="space-y-4">
            {perStagione.map(({ stagione, partite: ps }) => (
              <div
                key={stagione}
                className="rounded-xl bg-slate-900/40 border border-slate-700 overflow-hidden"
              >
                <div className="px-5 py-2.5 border-b border-slate-700 bg-slate-800/40 flex items-center justify-between">
                  <span className="font-bold text-amber-300 font-mono">Stagione {stagione}</span>
                  <span className="text-xs text-slate-400">
                    {ps.length} partit{ps.length === 1 ? "a" : "e"}
                  </span>
                </div>
                <table className="w-full text-sm">
                  <tbody>
                    {ps.map((p, i) => {
                      const out = outcomePer(p, squadra);
                      const sede = sedePer(p, squadra);
                      const bg =
                        out === "V" ? "bg-emerald-500/15"
                        : out === "S" ? "bg-rose-500/15"
                        : "bg-sky-500/15";
                      const sedeBadge =
                        sede === "Casa" ? <span className="text-emerald-400 font-bold">H</span>
                        : sede === "Trasferta" ? <span className="text-rose-400 font-bold">A</span>
                        : <span className="text-slate-400">N</span>;
                      const isHome = p.squadra_casa === squadra;
                      return (
                        <tr
                          key={i}
                          className={"border-b border-slate-800 last:border-b-0 hover:brightness-125 transition-all " + bg}
                        >
                          <td className={"text-right py-2 px-4 w-1/4 " + (isHome ? "text-amber-300 font-semibold" : "text-slate-200")}>
                            {p.squadra_casa}
                          </td>
                          <td className="text-center py-2 px-2 font-mono font-semibold text-white w-24">
                            {p.risultato}
                          </td>
                          <td className={"text-left py-2 px-4 w-1/4 " + (!isHome ? "text-amber-300 font-semibold" : "text-slate-200")}>
                            {p.squadra_trasferta}
                          </td>
                          <td className="text-center py-2 px-2 font-mono text-xs w-12">{sedeBadge}</td>
                          <td className="text-left py-2 px-4 text-xs text-slate-400">
                            {COMP_LABEL[p.Competizione] ?? p.Competizione}
                          </td>
                          <td className="text-left py-2 px-4 text-xs text-slate-500">
                            {p.giornata}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

/** Grafico a barre orizzontali V/P/S (verde/bianco/rosso). */
function H2HBarChart({
  title,
  stats,
  squadra,
  avversaria,
  highlight,
}: {
  title: string;
  icon?: string;
  stats: { V: number; P: number; S: number };
  squadra: string;
  avversaria: string;
  highlight?: boolean;
}) {
  const total = stats.V + stats.P + stats.S;
  const max = Math.max(stats.V, stats.P, stats.S, 1);

  const Bar = ({
    label,
    value,
    barClass,
    labelClass,
  }: {
    label: string;
    value: number;
    barClass: string;
    labelClass: string;
  }) => {
    const pct = (value / max) * 100;
    return (
      <div className="flex items-center gap-3">
        <div className={"w-6 text-xs font-bold " + labelClass}>{label}</div>
        <div className="flex-1 h-5 bg-slate-800/80 rounded overflow-hidden">
          <div
            className={"h-full transition-all " + barClass}
            style={{ width: total === 0 ? 0 : `${Math.max(2, pct)}%` }}
          />
        </div>
        <div className={"w-8 text-right text-sm font-mono " + labelClass}>{value}</div>
      </div>
    );
  };

  return (
    <div
      className={
        "rounded-xl border p-4 " +
        (highlight
          ? "bg-cyan-950/30 border-cyan-700/40"
          : "bg-slate-900/40 border-slate-700")
      }
    >
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-bold text-slate-100">{title}</h4>
        <span className="text-xs text-slate-400 font-mono">
          {total} partit{total === 1 ? "a" : "e"}
        </span>
      </div>
      <div className="space-y-2">
        <Bar label="V" value={stats.V} barClass="bg-emerald-500" labelClass="text-emerald-300" />
        <Bar label="P" value={stats.P} barClass="bg-slate-200" labelClass="text-slate-200" />
        <Bar label="S" value={stats.S} barClass="bg-rose-500" labelClass="text-rose-300" />
      </div>
      {total > 0 && (
        <div className="text-[10px] text-slate-500 mt-3 font-mono">
          V/P/S di {squadra} contro {avversaria}
        </div>
      )}
    </div>
  );
}

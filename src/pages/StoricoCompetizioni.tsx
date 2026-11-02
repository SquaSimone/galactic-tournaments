import { useEffect, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:3004/api";

/** Immagini custom dei trofei (servite da public/). Chiave = key competizione. */
const COMP_IMG: Partial<Record<CompKey, string>> = {
  "galactic league": "/galactic-league.png",
  "galactic cup": "/galactic-cup.png",
  "Kings League": "/kings-league.png",
  "galactic champions cup": "/galactic-champions-cup.png",
  "intergalactic supercup": "/intergalactic-super-cup.png",
  "cup": "/cup-of-10.png",
};

type CompKey =F
  | "galactic league"
  | "galactic cup"
  | "Kings League"
  | "galactic champions cup"
  | "intergalactic supercup"
  | "cup";

const COMPETIZIONI: Array<{
  key: CompKey;
  slug: string; // slug usato per l'endpoint backend (solo per le competizioni "semplici")
  label: string;
  icon: string;
  img?: string;
  accent: string;
  cardBg: string;
  border: string;
}> = [
  { key: "cup",                    slug: "cup",            label: "Cup of 8 / Cup of 10",   icon: "🔟", img: COMP_IMG["cup"], accent: "text-indigo-300", cardBg: "bg-indigo-950/30", border: "border-indigo-700/40" },
  { key: "galactic league",        slug: "league",         label: "Galactic League",        icon: "🛰️", img: COMP_IMG["galactic league"], accent: "text-sky-300",     cardBg: "bg-sky-950/30",     border: "border-sky-700/40"     },
  { key: "galactic cup",           slug: "galactic-cup",   label: "Galactic Cup",           icon: "🏆", img: COMP_IMG["galactic cup"], accent: "text-amber-300",   cardBg: "bg-amber-950/30",   border: "border-amber-700/40"   },
  { key: "Kings League",           slug: "kings-league",   label: "Galactic Kings League",  icon: "👑", img: COMP_IMG["Kings League"], accent: "text-purple-300",  cardBg: "bg-purple-950/30",  border: "border-purple-700/40"  },
  { key: "galactic champions cup", slug: "champions-cup",  label: "Galactic Champions Cup", icon: "⭐", img: COMP_IMG["galactic champions cup"], accent: "text-emerald-300", cardBg: "bg-emerald-950/30", border: "border-emerald-700/40" },
  { key: "intergalactic supercup", slug: "supercup",       label: "Intergalactic SuperCup", icon: "🚀", img: COMP_IMG["intergalactic supercup"], accent: "text-pink-300",    cardBg: "bg-pink-950/30",    border: "border-pink-700/40"    },
];

type CupFase = "ottavi" | "quarti" | "semifinale" | "finale";

type CupPartecipante = {
  squadra: string;
  posizione_ranking: number | null;
  fasi_giocate: CupFase[];
  vinto_torneo: boolean;
};

type StoricoCupRow = {
  stagione: number;
  competizione: string | null;
  vincitrice: string | null;
  runner_up: string | null;
  risultato: string | null;
  semifinaliste: string[];
  posizione_qualifica: number | null;
  partecipanti?: CupPartecipante[];
};

export default function StoricoCompetizioni() {
  const [selected, setSelected] = useState<CompKey>("cup");

  const meta = COMPETIZIONI.find((c) => c.key === selected)!;

  return (
    <div>
      <div className="flex items-end justify-between mb-6 flex-wrap gap-4">
        <div>
          <h1 className="text-5xl font-bold text-amber-300 tracking-wide drop-shadow-[0_0_30px_rgba(252,211,77,0.3)]">
            Competizioni
          </h1>
          <p className="text-slate-400 mt-1 text-sm">
            Storico per competizione: albo d'oro, finalisti, semifinaliste e posizione di qualifica
          </p>
        </div>

        <div className="flex items-center gap-3">
          <label className="text-sm text-slate-300 font-medium">Competizione:</label>
          <select
            value={selected}
            onChange={(e) => setSelected(e.target.value as CompKey)}
            className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-white focus:outline-none focus:border-cyan-400"
          >
            {COMPETIZIONI.map((c) => (
              <option key={c.key} value={c.key}>
                {c.icon} {c.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Header competizione selezionata */}
      <div
        className={
          "rounded-2xl border p-5 mb-6 flex items-center gap-4 " +
          meta.cardBg +
          " " +
          meta.border
        }
      >
        <div className="text-4xl">
          {meta.img ? (
            <img
              src={meta.img}
              alt={meta.label}
              className="h-12 w-12 object-contain"
            />
          ) : (
            meta.icon
          )}
        </div>
        <div>
          <h2 className={"text-2xl font-bold " + meta.accent}>{meta.label}</h2>
        </div>
      </div>

      {selected === "cup" ? (
        <CupStorico />
      ) : selected === "galactic league" ? (
        <>
          <GenericStorico slug={meta.slug} />
          <RaggiungimentiPosizioneTable
            endpoint="/galactic-league/raggiungimenti-posizione"
            columns={LEAGUE_RAGG_COLS}
            accent="text-sky-300"
          />
          <RaggiungimentiTable
            endpoint="/galactic-league/raggiungimenti"
            columns={LEAGUE_RAGG_COLS}
            accent="text-sky-300"
            filterNote="Solo le squadre arrivate almeno una volta agli ottavi."
          />
        </>
      ) : selected === "galactic cup" ? (
        <>
          <GenericStorico slug={meta.slug} />
          <RaggiungimentiTable
            endpoint="/galactic-cup/raggiungimenti"
            columns={CUP_RAGG_COLS}
            accent="text-amber-300"
            filterNote="Solo le squadre arrivate almeno una volta ai sedicesimi."
          />
        </>
      ) : selected === "galactic champions cup" ? (
        <>
          <GenericStorico slug={meta.slug} />
          <RaggiungimentiTable
            endpoint="/champions-cup/raggiungimenti"
            columns={LEAGUE_RAGG_COLS}
            accent="text-emerald-300"
            filterNote="Solo le squadre arrivate almeno una volta agli ottavi (Fase 3)."
          />
        </>
      ) : (
        <GenericStorico slug={meta.slug} />
      )}
    </div>
  );
}

type StoricoGenericoRow = {
  stagione: number;
  vincitrice: string | null;
  runner_up: string | null;
  risultato: string | null;
  semifinaliste: string[];
  ruoli?: Record<string, string>; // solo per supercup: team → ruolo (es. "Vincente Galactic League")
  posizioni_league_phase?: Record<string, number>; // solo league: team → posizione fase a gironi
};

const PAGE_SIZE = 10;

/** Controlli di paginazione (mostrati solo se più di una pagina). */
function Pagination({
  current,
  total,
  onChange,
}: {
  current: number;
  total: number;
  onChange: (p: number) => void;
}) {
  if (total <= 1) return null;
  return (
    <div className="flex items-center justify-center gap-2 mt-4">
      <button
        onClick={() => onChange(Math.max(0, current - 1))}
        disabled={current === 0}
        className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300 text-sm border border-slate-700"
      >
        ←
      </button>
      <span className="text-xs text-slate-400 font-mono">
        Pagina {current + 1} / {total}
      </span>
      <button
        onClick={() => onChange(Math.min(total - 1, current + 1))}
        disabled={current >= total - 1}
        className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300 text-sm border border-slate-700"
      >
        →
      </button>
    </div>
  );
}

/** Mostra il nome della squadra + il ruolo (es. "Vincente Galactic League") se
 *  presente, e/o la posizione nella fase a gironi (League Phase) come badge [N]. */
function TeamWithRole({
  team,
  ruoli,
  align,
  baseColor,
  posLeaguePhase,
}: {
  team: string | null;
  ruoli?: Record<string, string>;
  align: "left" | "right";
  baseColor: string;
  posLeaguePhase?: Record<string, number>;
}) {
  if (!team) return <span className="text-slate-600">—</span>;
  const ruolo = ruoli?.[team];
  const pos = posLeaguePhase?.[team];
  return (
    <div className={align === "right" ? "text-right" : "text-left"}>
      <div className={"font-semibold " + baseColor}>
        {team}
        {pos != null && (
          <span
            className="ml-1.5 font-mono text-xs text-sky-300/80"
            title={`Posizione League Phase: ${pos}`}
          >
            [{pos}]
          </span>
        )}
      </div>
      {ruolo && (
        <div className="text-[10px] text-slate-500 italic mt-0.5">{ruolo}</div>
      )}
    </div>
  );
}

/** Storico per competizioni "semplici" (no edizione, no pos. qualifica). */
function GenericStorico({ slug }: { slug: string }) {
  const [rows, setRows] = useState<StoricoGenericoRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(0);

  useEffect(() => {
    setLoading(true);
    setPage(0);
    fetch(`${API_URL}/storico-comp/${slug}`)
      .then((r) => r.json())
      .then((d) => setRows((d.storico || []).filter((r: StoricoCupRow) => r.competizione)))
      .catch(() => setRows([]))
      .finally(() => setLoading(false));
  }, [slug]);

  const totalPages = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
  const pagedRows = rows.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  if (loading) {
    return <div className="text-center text-slate-400 py-16">Caricamento storico…</div>;
  }
  if (rows.length === 0) {
    return (
      <div className="text-center text-slate-400 py-16">
        Nessuna stagione caricata
      </div>
    );
  }

  return (
    <>
    <div className="rounded-2xl bg-slate-900/50 border border-slate-700 overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="bg-slate-800/60 text-slate-400 uppercase text-xs tracking-wider">
          <tr>
            <th className="text-center py-3 px-3">Stagione</th>
            <th className="text-right py-3 px-4">🏆 Vincitrice</th>
            <th className="text-center py-3 px-3 font-mono">Risultato</th>
            <th className="text-left py-3 px-4">Runner-up</th>
            <th className="text-left py-3 px-4">Semifinalista 1</th>
            <th className="text-left py-3 px-4">Semifinalista 2</th>
          </tr>
        </thead>
        <tbody>
          {pagedRows.map((r) => {
            const semi1 = (r.semifinaliste ?? [])[0] ?? null;
            const semi2 = (r.semifinaliste ?? [])[1] ?? null;
            return (
              <tr
                key={r.stagione}
                className="border-b border-slate-800 last:border-b-0 hover:bg-slate-800/30 transition-colors"
              >
                <td className="text-center py-3 px-3 font-mono font-bold text-amber-300 align-top">
                  S{r.stagione}
                </td>
                <td className="py-3 px-4 align-top">
                  <TeamWithRole team={r.vincitrice} ruoli={r.ruoli} align="right" baseColor="text-amber-200" posLeaguePhase={r.posizioni_league_phase} />
                </td>
                <td className="text-center py-3 px-3 font-mono font-semibold text-cyan-300 align-top">
                  {r.risultato ?? <span className="text-slate-600">—</span>}
                </td>
                <td className="py-3 px-4 align-top">
                  <TeamWithRole team={r.runner_up} ruoli={r.ruoli} align="left" baseColor="text-slate-200" posLeaguePhase={r.posizioni_league_phase} />
                </td>
                <td className="py-3 px-4 align-top">
                  <TeamWithRole team={semi1} ruoli={r.ruoli} align="left" baseColor="text-slate-300" posLeaguePhase={r.posizioni_league_phase} />
                </td>
                <td className="py-3 px-4 align-top">
                  <TeamWithRole team={semi2} ruoli={r.ruoli} align="left" baseColor="text-slate-300" posLeaguePhase={r.posizioni_league_phase} />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
    <Pagination current={page} total={totalPages} onChange={setPage} />

    {slug === "league" && (
      <p className="text-xs text-slate-500 mt-3">
        <span className="font-mono text-sky-300/80">[N]</span> = posizione nella
        fase a gironi (League Phase) di quella stagione.
      </p>
    )}

    {slug === "supercup" && <SuperCupStats rows={rows} />}
    </>
  );
}

/** Statistiche aggregate della SuperCup: per categoria e per squadra. */
function SuperCupStats({ rows }: { rows: StoricoGenericoRow[] }) {
  const [includiSostituenti, setIncludiSostituenti] = useState(true);

  const categorie: Array<{ key: string; substitutable: boolean }> = [
    { key: "Galactic League",        substitutable: false },
    { key: "Galactic Champions Cup", substitutable: true  },
    { key: "Galactic Cup",           substitutable: true  },
    { key: "Galactic Kings League",  substitutable: true  },
  ];

  const labelFor = (c: { key: string; substitutable: boolean }) =>
    c.substitutable && includiSostituenti
      ? `Vincente / Sostituente ${c.key}`
      : `Vincente ${c.key}`;

  // ─── Statistiche per categoria ──────────────────────────────────
  const catStats = categorie.map((c) => {
    const includeSub = c.substitutable && includiSostituenti;
    const isMatch = (role: string | undefined) => {
      if (!role) return false;
      if (role === `Vincente ${c.key}`) return true;
      if (includeSub && role === `Sostituente ${c.key}`) return true;
      return false;
    };
    const vittorie = rows.filter((r) => isMatch(r.ruoli?.[r.vincitrice ?? ""])).length;
    const finali = rows.filter(
      (r) =>
        isMatch(r.ruoli?.[r.vincitrice ?? ""]) ||
        isMatch(r.ruoli?.[r.runner_up ?? ""]),
    ).length;
    return { ...c, vittorie, finali };
  });

  // ─── Statistiche per squadra ────────────────────────────────────
  // Logica a inclusione: vittorie ⊆ finali ⊆ partecipazioni.
  type TeamAgg = { vittorie: number; finali: number; partecipazioni: number };
  const teams = new Map<string, TeamAgg>();
  const bump = (t: string | null, field: keyof TeamAgg) => {
    if (!t) return;
    const cur = teams.get(t) ?? { vittorie: 0, finali: 0, partecipazioni: 0 };
    cur[field] += 1;
    teams.set(t, cur);
  };
  for (const r of rows) {
    if (r.vincitrice) {
      bump(r.vincitrice, "vittorie");
      bump(r.vincitrice, "finali");
      bump(r.vincitrice, "partecipazioni");
    }
    if (r.runner_up) {
      bump(r.runner_up, "finali");
      bump(r.runner_up, "partecipazioni");
    }
    for (const semi of r.semifinaliste) {
      bump(semi, "partecipazioni");
    }
  }
  const teamsSorted = [...teams.entries()].sort((a, b) => {
    if (b[1].vittorie !== a[1].vittorie) return b[1].vittorie - a[1].vittorie;
    if (b[1].finali !== a[1].finali) return b[1].finali - a[1].finali;
    if (b[1].partecipazioni !== a[1].partecipazioni) return b[1].partecipazioni - a[1].partecipazioni;
    return a[0].localeCompare(b[0]);
  });

  return (
    <div className="mt-10 space-y-8">
      {/* Categorie */}
      <div>
        <div className="flex items-center justify-between flex-wrap gap-3 mb-3">
          <h3 className="text-xl font-bold text-pink-300">Statistiche per Categoria</h3>
          <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={includiSostituenti}
              onChange={(e) => setIncludiSostituenti(e.target.checked)}
              className="w-4 h-4 accent-pink-500"
            />
            Includi sostituenti
          </label>
        </div>
        <div className="rounded-2xl bg-slate-900/50 border border-slate-700 overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-800/60 text-slate-400 uppercase text-xs tracking-wider">
              <tr>
                <th className="text-left py-3 px-4">Categoria</th>
                <th className="text-right py-3 px-4 w-32">Vittorie</th>
                <th className="text-right py-3 px-4 w-32">Finali</th>
              </tr>
            </thead>
            <tbody>
              {catStats.map((c) => (
                <tr
                  key={c.key}
                  className="border-b border-slate-800 last:border-b-0 hover:bg-slate-800/30 transition-colors"
                >
                  <td className="py-3 px-4 text-slate-200">{labelFor(c)}</td>
                  <td className="text-right py-3 px-4 font-mono font-bold text-amber-300">
                    {c.vittorie || <span className="text-slate-600">—</span>}
                  </td>
                  <td className="text-right py-3 px-4 font-mono text-cyan-300">
                    {c.finali || <span className="text-slate-600">—</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Squadre */}
      <div>
        <h3 className="text-xl font-bold text-pink-300 mb-3">Statistiche per Squadra</h3>
        {teamsSorted.length === 0 ? (
          <div className="text-center text-slate-500 py-8 text-sm">Nessuna partecipazione</div>
        ) : (
          <div className="rounded-2xl bg-slate-900/50 border border-slate-700 overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-800/60 text-slate-400 uppercase text-xs tracking-wider">
                <tr>
                  <th className="text-left py-3 px-4">Squadra</th>
                  <th className="text-right py-3 px-4">Vittorie</th>
                  <th className="text-right py-3 px-4">Finali</th>
                  <th className="text-center py-3 px-4">Partecipazioni</th>
                </tr>
              </thead>
              <tbody>
                {teamsSorted.map(([team, s]) => (
                  <tr
                    key={team}
                    className="border-b border-slate-800 last:border-b-0 hover:bg-slate-800/30 transition-colors"
                  >
                    <td className="py-3 px-4 font-semibold text-cyan-300">{team}</td>
                    <td className="text-right py-3 px-4 font-mono font-bold text-amber-300">
                      {s.vittorie || <span className="text-slate-600">—</span>}
                    </td>
                    <td className="text-right py-3 px-4 font-mono text-slate-200">
                      {s.finali || <span className="text-slate-600">—</span>}
                    </td>
                    <td className="text-center py-3 px-4 font-mono font-bold text-white">
                      {s.partecipazioni}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

/** Cella con nome squadra + "Posizione Ranking N" come sottotitolo. */
function TeamWithPos({
  team,
  posizioni,
  align,
  baseColor,
}: {
  team: string | null;
  posizioni: Record<string, number | null>;
  align: "left" | "right";
  baseColor: string;
}) {
  if (!team) return <span className="text-slate-600">—</span>;
  const pos = posizioni[team];
  return (
    <div className={align === "right" ? "text-right" : "text-left"}>
      <div className={"font-semibold " + baseColor}>{team}</div>
      {pos != null && (
        <div className="text-[10px] text-slate-500 italic mt-0.5">
          Posizione Ranking {pos}
        </div>
      )}
    </div>
  );
}

/** Storico Cup of 8 / Cup of 10: tabella per stagione. */
function CupStorico() {
  const [rows, setRows] = useState<StoricoCupRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(0);

  useEffect(() => {
    setLoading(true);
    fetch(`${API_URL}/storico/cup`)
      .then((r) => r.json())
      .then((d) => setRows(d.storico || []))
      .catch(() => setRows([]))
      .finally(() => setLoading(false));
  }, []);

  const totalPages = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
  const pagedRows = rows.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  if (loading) {
    return <div className="text-center text-slate-400 py-16">Caricamento storico…</div>;
  }
  if (rows.length === 0) {
    return (
      <div className="text-center text-slate-400 py-16">
        Nessuna stagione caricata
      </div>
    );
  }

  return (
    <>
    <div className="rounded-2xl bg-slate-900/50 border border-slate-700 overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="bg-slate-800/60 text-slate-400 uppercase text-xs tracking-wider">
          <tr>
            <th className="text-center py-3 px-3">Stagione</th>
            <th className="text-center py-3 px-3">Edizione</th>
            <th className="text-right py-3 px-4">🏆 Vincitrice</th>
            <th className="text-center py-3 px-3 font-mono">Risultato</th>
            <th className="text-left py-3 px-4">Runner-up</th>
            <th className="text-left py-3 px-4">Semifinalista 1</th>
            <th className="text-left py-3 px-4">Semifinalista 2</th>
            <th
              className="text-center py-3 px-3"
              title="Posizione della vincitrice nel ranking stagionale della stessa stagione"
            >
              Posizione vincitrice
            </th>
          </tr>
        </thead>
        <tbody>
          {pagedRows.map((r) => {
            const edizione = r.competizione === "cup of 10"
              ? "Cup of 10"
              : r.competizione === "cup of 8"
                ? "Cup of 8"
                : "—";
            const semi1 = r.semifinaliste[0] ?? null;
            const semi2 = r.semifinaliste[1] ?? null;
            const posizioni: Record<string, number | null> = {};
            for (const p of r.partecipanti ?? []) {
              posizioni[p.squadra] = p.posizione_ranking;
            }
            return (
              <tr
                key={r.stagione}
                className="border-b border-slate-800 last:border-b-0 hover:bg-slate-800/30 transition-colors"
              >
                <td className="text-center py-3 px-3 font-mono font-bold text-amber-300 align-top">
                  S{r.stagione}
                </td>
                <td className="text-center py-3 px-3 text-indigo-300 text-xs font-semibold align-top">
                  {edizione}
                </td>
                <td className="py-3 px-4 align-top">
                  <TeamWithPos team={r.vincitrice} posizioni={posizioni} align="right" baseColor="text-amber-200" />
                </td>
                <td className="text-center py-3 px-3 font-mono font-semibold text-cyan-300 align-top">
                  {r.risultato ?? <span className="text-slate-600">—</span>}
                </td>
                <td className="py-3 px-4 align-top">
                  <TeamWithPos team={r.runner_up} posizioni={posizioni} align="left" baseColor="text-slate-200" />
                </td>
                <td className="py-3 px-4 align-top">
                  <TeamWithPos team={semi1} posizioni={posizioni} align="left" baseColor="text-slate-300" />
                </td>
                <td className="py-3 px-4 align-top">
                  <TeamWithPos team={semi2} posizioni={posizioni} align="left" baseColor="text-slate-300" />
                </td>
                <td className="text-center py-3 px-3 font-mono font-bold text-cyan-300 align-top">
                  {r.posizione_qualifica !== null ? `#${r.posizione_qualifica}` : "—"}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
    <Pagination current={page} total={totalPages} onChange={setPage} />

    <CupStats rows={rows} />
    </>
  );
}

type PosSortKey = "posizione" | "vittorie" | "finali" | "semifinali" | "quarti" | "partecipazioni";
type TeamSortKey = "squadra" | "vittorie" | "finali" | "semifinali" | "quarti" | "partecipazioni";

/** Header cliccabile con freccia per ordinamento. */
function SortableTh<K extends string>({
  label,
  k,
  current,
  asc,
  onClick,
  align = "right",
}: {
  label: string;
  k: K;
  current: K;
  asc: boolean;
  onClick: (k: K) => void;
  align?: "left" | "right" | "center";
}) {
  const arrow = current === k ? (asc ? " ▲" : " ▼") : "";
  const alignCls = align === "left" ? "text-left" : align === "center" ? "text-center" : "text-right";
  return (
    <th
      onClick={() => onClick(k)}
      className={alignCls + " py-3 px-4 cursor-pointer hover:text-white select-none"}
    >
      {label}{arrow}
    </th>
  );
}

/** Statistiche aggregate Cup of 8/10: per posizione di ranking e per squadra. */
function CupStats({ rows }: { rows: StoricoCupRow[] }) {
  const [posSort, setPosSort] = useState<PosSortKey>("posizione");
  const [posAsc, setPosAsc] = useState(true);
  const [teamSort, setTeamSort] = useState<TeamSortKey>("vittorie");
  const [teamAsc, setTeamAsc] = useState(false);

  const togglePosSort = (k: PosSortKey) => {
    if (k === posSort) setPosAsc((v) => !v);
    else { setPosSort(k); setPosAsc(k === "posizione"); }
  };
  const toggleTeamSort = (k: TeamSortKey) => {
    if (k === teamSort) setTeamAsc((v) => !v);
    else { setTeamSort(k); setTeamAsc(k === "squadra"); }
  };
  // Flatten partecipanti
  const allPart: CupPartecipante[] = [];
  for (const r of rows) {
    for (const p of r.partecipanti ?? []) {
      allPart.push(p);
    }
  }

  // ── Statistiche per posizione ranking ────────────────────────────
  const maxPos = allPart.reduce(
    (m, p) => Math.max(m, p.posizione_ranking ?? 0),
    0,
  );
  type PosStats = { vittorie: number; finali: number; semifinali: number; quarti: number; partecipazioni: number };
  const perPos: Record<number, PosStats> = {};
  for (let i = 1; i <= maxPos; i++) {
    perPos[i] = { vittorie: 0, finali: 0, semifinali: 0, quarti: 0, partecipazioni: 0 };
  }
  for (const p of allPart) {
    if (p.posizione_ranking == null) continue;
    const pos = p.posizione_ranking;
    if (!perPos[pos]) continue;
    perPos[pos].partecipazioni += 1;
    if (p.vinto_torneo) perPos[pos].vittorie += 1;
    if (p.fasi_giocate.includes("finale")) perPos[pos].finali += 1;
    if (p.fasi_giocate.includes("semifinale")) perPos[pos].semifinali += 1;
    if (p.fasi_giocate.includes("quarti")) perPos[pos].quarti += 1;
  }

  // ── Statistiche per squadra ──────────────────────────────────────
  type TeamStats = { vittorie: number; finali: number; semifinali: number; quarti: number; partecipazioni: number };
  const perTeam = new Map<string, TeamStats>();
  for (const p of allPart) {
    const s = perTeam.get(p.squadra) ?? { vittorie: 0, finali: 0, semifinali: 0, quarti: 0, partecipazioni: 0 };
    s.partecipazioni += 1;
    if (p.vinto_torneo) s.vittorie += 1;
    if (p.fasi_giocate.includes("finale")) s.finali += 1;
    if (p.fasi_giocate.includes("semifinale")) s.semifinali += 1;
    if (p.fasi_giocate.includes("quarti")) s.quarti += 1;
    perTeam.set(p.squadra, s);
  }
  // Ordinamento per posizione (lista ordinabile)
  const posList = Object.entries(perPos).map(([k, s]) => ({ pos: parseInt(k, 10), ...s }));
  posList.sort((a, b) => {
    let cmp = 0;
    switch (posSort) {
      case "posizione":      cmp = a.pos - b.pos; break;
      case "vittorie":       cmp = a.vittorie - b.vittorie; break;
      case "finali":         cmp = a.finali - b.finali; break;
      case "semifinali":     cmp = a.semifinali - b.semifinali; break;
      case "quarti":         cmp = a.quarti - b.quarti; break;
      case "partecipazioni": cmp = a.partecipazioni - b.partecipazioni; break;
    }
    if (cmp === 0) cmp = a.pos - b.pos;
    return posAsc ? cmp : -cmp;
  });

  // Ordinamento per squadra
  const teamsSorted = [...perTeam.entries()].sort((a, b) => {
    let cmp = 0;
    switch (teamSort) {
      case "squadra":        cmp = a[0].localeCompare(b[0]); break;
      case "vittorie":       cmp = a[1].vittorie - b[1].vittorie; break;
      case "finali":         cmp = a[1].finali - b[1].finali; break;
      case "semifinali":     cmp = a[1].semifinali - b[1].semifinali; break;
      case "quarti":         cmp = a[1].quarti - b[1].quarti; break;
      case "partecipazioni": cmp = a[1].partecipazioni - b[1].partecipazioni; break;
    }
    if (cmp === 0) cmp = a[0].localeCompare(b[0]);
    return teamAsc ? cmp : -cmp;
  });

  const cell = (n: number) =>
    n > 0 ? n : <span className="text-slate-600">—</span>;

  return (
    <div className="mt-10 space-y-8">
      {/* Per posizione */}
      <div>
        <h3 className="text-xl font-bold text-indigo-300 mb-3">Statistiche per Categoria</h3>
        <p className="text-xs text-slate-400 mb-3">
          Per ogni posizione del ranking di qualifica, quante volte la squadra che la occupava ha
          raggiunto ogni fase del torneo.
        </p>
        <div className="rounded-2xl bg-slate-900/50 border border-slate-700 overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-800/60 text-slate-400 uppercase text-xs tracking-wider">
              <tr>
                <SortableTh label="Posizione"        k="posizione"      current={posSort} asc={posAsc} onClick={togglePosSort} align="left" />
                <SortableTh label="Vittorie"         k="vittorie"       current={posSort} asc={posAsc} onClick={togglePosSort} />
                <SortableTh label="Finali"           k="finali"         current={posSort} asc={posAsc} onClick={togglePosSort} />
                <SortableTh label="Semifinali"       k="semifinali"     current={posSort} asc={posAsc} onClick={togglePosSort} />
                <SortableTh label="Quarti di Finale" k="quarti"         current={posSort} asc={posAsc} onClick={togglePosSort} />
                <SortableTh label="Partecipazioni"   k="partecipazioni" current={posSort} asc={posAsc} onClick={togglePosSort} align="center" />
              </tr>
            </thead>
            <tbody>
              {posList.map((s) => (
                <tr
                  key={s.pos}
                  className="border-b border-slate-800 last:border-b-0 hover:bg-slate-800/30 transition-colors"
                >
                  <td className="py-3 px-4 font-semibold text-cyan-300">Posizione {s.pos}</td>
                  <td className="text-right py-3 px-4 font-mono font-bold text-amber-300">{cell(s.vittorie)}</td>
                  <td className="text-right py-3 px-4 font-mono text-slate-200">{cell(s.finali)}</td>
                  <td className="text-right py-3 px-4 font-mono text-slate-200">{cell(s.semifinali)}</td>
                  <td className="text-right py-3 px-4 font-mono text-slate-200">{cell(s.quarti)}</td>
                  <td className="text-center py-3 px-4 font-mono font-bold text-white">
                    {s.partecipazioni}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Per squadra */}
      <div>
        <h3 className="text-xl font-bold text-indigo-300 mb-3">Statistiche per Squadra</h3>
        {teamsSorted.length === 0 ? (
          <div className="text-center text-slate-500 py-8 text-sm">Nessuna partecipazione</div>
        ) : (
          <div className="rounded-2xl bg-slate-900/50 border border-slate-700 overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-800/60 text-slate-400 uppercase text-xs tracking-wider">
                <tr>
                  <SortableTh label="Squadra"          k="squadra"        current={teamSort} asc={teamAsc} onClick={toggleTeamSort} align="left" />
                  <SortableTh label="Vittorie"         k="vittorie"       current={teamSort} asc={teamAsc} onClick={toggleTeamSort} />
                  <SortableTh label="Finali"           k="finali"         current={teamSort} asc={teamAsc} onClick={toggleTeamSort} />
                  <SortableTh label="Semifinali"       k="semifinali"     current={teamSort} asc={teamAsc} onClick={toggleTeamSort} />
                  <SortableTh label="Quarti di Finale" k="quarti"         current={teamSort} asc={teamAsc} onClick={toggleTeamSort} />
                  <SortableTh label="Partecipazioni"   k="partecipazioni" current={teamSort} asc={teamAsc} onClick={toggleTeamSort} align="center" />
                </tr>
              </thead>
              <tbody>
                {teamsSorted.map(([team, s]) => (
                  <tr
                    key={team}
                    className="border-b border-slate-800 last:border-b-0 hover:bg-slate-800/30 transition-colors"
                  >
                    <td className="py-3 px-4 font-semibold text-cyan-300">{team}</td>
                    <td className="text-right py-3 px-4 font-mono font-bold text-amber-300">{cell(s.vittorie)}</td>
                    <td className="text-right py-3 px-4 font-mono text-slate-200">{cell(s.finali)}</td>
                    <td className="text-right py-3 px-4 font-mono text-slate-200">{cell(s.semifinali)}</td>
                    <td className="text-right py-3 px-4 font-mono text-slate-200">{cell(s.quarti)}</td>
                    <td className="text-center py-3 px-4 font-mono font-bold text-white">{s.partecipazioni}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

type RaggiungimentoRow = { SQUADRA: string; [k: string]: number | string };
type RaggCol = { key: string; label: string };

const LEAGUE_RAGG_COLS: RaggCol[] = [
  { key: "vittorie", label: "Vittorie" },
  { key: "finali", label: "Finali" },
  { key: "semifinali", label: "Semifinali" },
  { key: "quarti", label: "Quarti di Finale" },
  { key: "ottavi", label: "Ottavi di Finale" },
];

const CUP_RAGG_COLS: RaggCol[] = [
  ...LEAGUE_RAGG_COLS,
  { key: "sedicesimi", label: "Sedicesimi di Finale" },
];

/** Statistiche cumulate della fase a eliminazione di una competizione:
 *  quante volte ogni squadra ha raggiunto ciascuna fase (tutte le stagioni). */
function RaggiungimentiTable({
  endpoint,
  columns,
  accent,
  filterNote,
}: {
  endpoint: string;
  columns: RaggCol[];
  accent: string;
  filterNote: string;
}) {
  const [rows, setRows] = useState<RaggiungimentoRow[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetch(`${API_URL}${endpoint}`)
      .then((r) => r.json())
      .then((d) => setRows(d.raggiungimenti || []))
      .catch(() => setRows([]))
      .finally(() => setLoading(false));
  }, [endpoint]);

  const cell = (n: number | string) =>
    typeof n === "number" && n > 0 ? n : <span className="text-slate-600">—</span>;

  if (loading) {
    return <div className="text-center text-slate-400 py-8">Caricamento statistiche…</div>;
  }
  if (rows.length === 0) return null;

  return (
    <div className="mt-10">
      <h3 className={"text-xl font-bold mb-3 " + accent}>
        Statistiche per Squadra — Fase a eliminazione
      </h3>
      <p className="text-xs text-slate-400 mb-3">
        Quante volte ogni squadra ha raggiunto ciascuna fase, cumulato su tutte le
        stagioni. {filterNote}
      </p>
      <div className="rounded-2xl bg-slate-900/50 border border-slate-700 overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-800/60 text-slate-400 uppercase text-xs tracking-wider">
            <tr>
              <th className="text-left py-3 px-4">Squadra</th>
              {columns.map((c) => (
                <th key={c.key} className="text-right py-3 px-4">{c.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr
                key={r.SQUADRA}
                className="border-b border-slate-800 last:border-b-0 hover:bg-slate-800/30 transition-colors"
              >
                <td className="py-3 px-4 font-semibold text-cyan-300">{r.SQUADRA}</td>
                {columns.map((c) => (
                  <td
                    key={c.key}
                    className={
                      "text-right py-3 px-4 font-mono " +
                      (c.key === "vittorie" ? "font-bold text-amber-300" : "text-slate-200")
                    }
                  >
                    {cell(r[c.key])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

type RaggPosRow = { posizione: number; [k: string]: number };

/** Statistiche della fase a eliminazione aggregate per posizione nella fase a
 *  gironi (League Phase): per ogni posizione [1]..[24], quante volte la squadra
 *  che la occupava ha raggiunto ciascuna fase (cumulato su tutte le stagioni). */
function RaggiungimentiPosizioneTable({
  endpoint,
  columns,
  accent,
}: {
  endpoint: string;
  columns: RaggCol[];
  accent: string;
}) {
  const [rows, setRows] = useState<RaggPosRow[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetch(`${API_URL}${endpoint}`)
      .then((r) => r.json())
      .then((d) => setRows(d.raggiungimenti || []))
      .catch(() => setRows([]))
      .finally(() => setLoading(false));
  }, [endpoint]);

  const cell = (n: number | string) =>
    typeof n === "number" && n > 0 ? n : <span className="text-slate-600">—</span>;

  if (loading) {
    return <div className="text-center text-slate-400 py-8">Caricamento statistiche…</div>;
  }
  if (rows.length === 0) return null;

  return (
    <div className="mt-10">
      <h3 className={"text-xl font-bold mb-3 " + accent}>
        Statistiche per Posizione — Fase a gironi
      </h3>
      <p className="text-xs text-slate-400 mb-3">
        Per ogni posizione della fase a gironi (League Phase), quante volte la
        squadra che la occupava ha raggiunto ciascuna fase a eliminazione, cumulato
        su tutte le stagioni.
      </p>
      <div className="rounded-2xl bg-slate-900/50 border border-slate-700 overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-800/60 text-slate-400 uppercase text-xs tracking-wider">
            <tr>
              <th className="text-left py-3 px-4">Posizione</th>
              {columns.map((c) => (
                <th key={c.key} className="text-right py-3 px-4">{c.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr
                key={r.posizione}
                className="border-b border-slate-800 last:border-b-0 hover:bg-slate-800/30 transition-colors"
              >
                <td className="py-3 px-4 font-semibold text-sky-300 font-mono">
                  [{r.posizione}]
                </td>
                {columns.map((c) => (
                  <td
                    key={c.key}
                    className={
                      "text-right py-3 px-4 font-mono " +
                      (c.key === "vittorie" ? "font-bold text-amber-300" : "text-slate-200")
                    }
                  >
                    {cell(r[c.key])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

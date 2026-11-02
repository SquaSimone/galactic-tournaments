import { useEffect, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:3004/api";

type AlboRow = {
  stagione: number;
  vincitori: Record<string, string | null>;
  top3_ranking: string[];
  primo_cumulato: string | null;
  primo_star: string | null;
};

/** Le 6 competizioni nell'ordine in cui appaiono nelle colonne. */
type CompKey =
  | "galactic league"
  | "galactic cup"
  | "Kings League"
  | "galactic champions cup"
  | "intergalactic supercup"
  | "cup"; // dinamico: cup of 8 (S1-S2) o cup of 10 (S3+)

/** Immagini custom dei trofei (servite da public/). Chiave = key competizione. */
const COMP_IMG: Partial<Record<CompKey, string>> = {
  "galactic league": "/galactic-league.png",
  "galactic cup": "/galactic-cup.png",
  "Kings League": "/kings-league.png",
  "galactic champions cup": "/galactic-champions-cup.png",
  "intergalactic supercup": "/intergalactic-super-cup.png",
  "cup": "/cup-of-10.png",
};

const COMPETIZIONI: Array<{
  key: CompKey;
  label: string;
  sigla: string;
  icon: string;
  img?: string;
  accent: string;
}> = [
  { key: "galactic league",        label: "Galactic League",        sigla: "GL",  icon: "🛰️", img: COMP_IMG["galactic league"], accent: "text-sky-300" },
  { key: "galactic cup",           label: "Galactic Cup",           sigla: "GC",  icon: "🏆", img: COMP_IMG["galactic cup"], accent: "text-amber-300" },
  { key: "Kings League",           label: "Galactic Kings League",  sigla: "GKL", icon: "👑", img: COMP_IMG["Kings League"], accent: "text-purple-300" },
  { key: "galactic champions cup", label: "Galactic Champions Cup", sigla: "GCC", icon: "⭐", img: COMP_IMG["galactic champions cup"], accent: "text-emerald-300" },
  { key: "intergalactic supercup", label: "Intergalactic SuperCup", sigla: "ISC", icon: "🚀", img: COMP_IMG["intergalactic supercup"], accent: "text-pink-300" },
  { key: "cup",                    label: "Cup of 8 / 10",          sigla: "C8/10", icon: "🔟", img: COMP_IMG["cup"], accent: "text-indigo-300" },
];

function vincitoreCup(vincitori: Record<string, string | null>): string | null {
  return vincitori["cup of 10"] ?? vincitori["cup of 8"] ?? null;
}

function getVincitore(vincitori: Record<string, string | null>, key: CompKey): string | null {
  if (key === "cup") return vincitoreCup(vincitori);
  return vincitori[key] ?? null;
}

export default function AlboOro() {
  const [albo, setAlbo] = useState<AlboRow[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetch(`${API_URL}/albo-oro`)
      .then((r) => r.json())
      .then((data) => setAlbo(data.albo || []))
      .catch(() => setAlbo([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-5xl font-bold text-amber-300 tracking-wide drop-shadow-[0_0_30px_rgba(252,211,77,0.3)]">
          Albo d'Oro
        </h1>
        <p className="text-slate-400 mt-1 text-sm">
          Vincitori delle 6 competizioni · Top 3 del ranking stagionale · 1° del ranking cumulato · 1° per Star Points
        </p>
      </div>

      {loading ? (
        <div className="text-center text-slate-400 py-16">Caricamento…</div>
      ) : albo.length === 0 ? (
        <div className="text-center text-slate-400 py-16">
          Nessuna stagione caricata
        </div>
      ) : (
        <div className="rounded-2xl bg-slate-900/50 border border-slate-700 overflow-x-auto">
          <table className="w-full text-base">
            <thead className="bg-slate-800/60 text-slate-400 uppercase text-sm tracking-wider">
              <tr>
                <th rowSpan={2} className="text-center py-3 px-3 align-middle border-r border-slate-700">
                  Stagione
                </th>
                <th colSpan={6} className="text-center py-2 px-3 border-r border-slate-700 text-slate-300 normal-case text-sm font-semibold">
                  Vincitori Coppe
                </th>
                <th colSpan={3} className="text-center py-2 px-3 border-r border-slate-700 text-slate-300 normal-case text-sm font-semibold">
                  Top Ranking Stagionale
                </th>
                <th rowSpan={2} className="text-center py-3 px-3 align-middle text-slate-300 normal-case text-sm font-semibold border-r border-slate-700">
                  Ranking<br />Cumulato<br />🏆
                </th>
                <th rowSpan={2} className="text-center py-3 px-3 align-middle text-slate-300 normal-case text-sm font-semibold">
                  Star<br />Points<br />⭐
                </th>
              </tr>
              <tr className="border-t border-slate-700">
                {COMPETIZIONI.map((c) => (
                  <th
                    key={c.key}
                    className="text-center py-2 px-2 font-normal"
                    title={c.label}
                  >
                    {c.img ? (
                      <img
                        src={c.img}
                        alt={c.label}
                        className="h-7 w-7 mx-auto object-contain"
                      />
                    ) : (
                      <div className="text-xl">{c.icon}</div>
                    )}
                    <div className={"text-[10px] mt-0.5 " + c.accent}>{c.sigla}</div>
                  </th>
                ))}
                <th className="text-center py-2 px-2 border-l border-slate-700">🥇</th>
                <th className="text-center py-2 px-2">🥈</th>
                <th className="text-center py-2 px-2 border-r border-slate-700">🥉</th>
              </tr>
            </thead>
            <tbody>
              {albo.map((row) => (
                <tr
                  key={row.stagione}
                  className="border-t border-slate-800 hover:bg-slate-800/30 transition-colors"
                >
                  <td className="text-center py-3 px-3 font-mono font-bold text-amber-300 border-r border-slate-800">
                    S{row.stagione}
                  </td>
                  {COMPETIZIONI.map((c) => {
                    const v = getVincitore(row.vincitori, c.key);
                    return (
                      <td
                        key={c.key}
                        className="text-center py-3 px-1text-slate-200 text-sm whitespace-nowrap"
                        title={v ? `${c.label}: ${v}` : c.label}
                      >
                        {v ?? <span className="text-slate-600">—</span>}
                      </td>
                    );
                  })}
                  <td className="text-center py-3 px-1text-amber-200 font-semibold border-l border-slate-800 text-sm whitespace-nowrap">
                    {row.top3_ranking[0] ?? <span className="text-slate-600">—</span>}
                  </td>
                  <td className="text-center py-3 px-1text-slate-200 text-sm whitespace-nowrap">
                    {row.top3_ranking[1] ?? <span className="text-slate-600">—</span>}
                  </td>
                  <td className="text-center py-3 px-1text-slate-300 text-sm border-r border-slate-800 whitespace-nowrap">
                    {row.top3_ranking[2] ?? <span className="text-slate-600">—</span>}
                  </td>
                  <td className="text-center py-3 px-2 text-cyan-300 font-semibold text-sm border-r border-slate-800 whitespace-nowrap">
                    {row.primo_cumulato ?? <span className="text-slate-600">—</span>}
                  </td>
                  <td className="text-center py-3 px-2 text-amber-300 font-semibold text-sm whitespace-nowrap">
                    {row.primo_star ?? <span className="text-slate-600">—</span>}
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
      </p>
    </div>
  );
}

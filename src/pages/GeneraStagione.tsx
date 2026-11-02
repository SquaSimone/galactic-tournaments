import { useEffect, useMemo, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:3004/api";

type Partita = {
  id: number;
  stagione: number;
  giornata: string;
  squadra_casa: string;
  risultato: string;
  squadra_trasferta: string;
  campo?: string | null;
};

type Stato = {
  prossimo: string | null;
  prossimo_label: string | null;
  prossimo_abilitato: boolean;
  gruppo?: { esiste: boolean; completo: boolean; n: number }; // solo League
  prev_disponibile?: boolean; // Cup / Kings
  prossimo_hint?: string | null; // motivo se disabilitato
  done_message?: string | null; // messaggio quando non c'è altro da generare
};

type CompKey =
  | "galactic league"
  | "galactic cup"
  | "Kings League"
  | "galactic champions cup"
  | "intergalactic supercup"
  | "cup of 10";

const COMPETIZIONI: { key: CompKey; label: string; statoUrl: string; roundUrl: string }[] = [
  { key: "galactic league", label: "🛰️ Galactic League", statoUrl: "league-stato", roundUrl: "league-knockout" },
  { key: "galactic cup", label: "🏆 Galactic Cup", statoUrl: "cup-stato", roundUrl: "cup-round" },
  { key: "Kings League", label: "👑 Galactic Kings League", statoUrl: "kings-stato", roundUrl: "kings-round" },
  { key: "galactic champions cup", label: "⭐ Galactic Champions Cup", statoUrl: "champions-stato", roundUrl: "champions-round" },
  { key: "intergalactic supercup", label: "🚀 Intergalactic SuperCup", statoUrl: "supercup-stato", roundUrl: "supercup-round" },
  { key: "cup of 10", label: "🔟 Cup of 10", statoUrl: "cup10-stato", roundUrl: "cup10-round" },
];

/** Sezione "Genera Stagione": sorteggia le competizioni una alla volta (League,
 *  Cup, …) turno per turno e permette di inserire i risultati. Convive con
 *  l'import Excel — non lo sostituisce. */
export default function GeneraStagione() {
  const [stagioni, setStagioni] = useState<number[]>([]);
  const [stagione, setStagione] = useState<number | null>(null);
  const [competizione, setCompetizione] = useState<CompKey>("galactic league");

  const [generating, setGenerating] = useState(false);
  const [genMsg, setGenMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [partite, setPartite] = useState<Partita[]>([]);
  const [stato, setStato] = useState<Stato | null>(null);
  const [loading, setLoading] = useState(false);

  const [inputs, setInputs] = useState<Record<number, string>>({});
  const [saved, setSaved] = useState<Record<number, string>>({});
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState<string | null>(null);
  const [backupMsg, setBackupMsg] = useState<string | null>(null);

  const compMeta = COMPETIZIONI.find((c) => c.key === competizione)!;

  useEffect(() => {
    fetch(`${API_URL}/stagioni`)
      .then((r) => r.json())
      .then((d) => {
        const s: number[] = d.stagioni || [];
        setStagioni(s);
        setStagione((prev) => (prev === null ? (s.length ? Math.max(...s) + 1 : 1) : prev));
      })
      .catch(() => {});
  }, []);

  // Carica partite della competizione selezionata + il suo stato di generazione
  const refresh = (s: number, comp: CompKey) => {
    const meta = COMPETIZIONI.find((c) => c.key === comp)!;
    setLoading(true);
    Promise.all([
      fetch(`${API_URL}/partite?stagione=${s}&competizione=${encodeURIComponent(comp)}`).then((r) => r.json()),
      fetch(`${API_URL}/genera/${meta.statoUrl}?stagione=${s}`).then((r) => r.json()),
    ])
      .then(([dp, ds]) => {
        const ps: Partita[] = dp.partite || [];
        setPartite(ps);
        const map: Record<number, string> = {};
        for (const p of ps) map[p.id] = p.risultato ?? "";
        setInputs(map);
        setSaved({ ...map });
        setStato(ds);
      })
      .catch(() => {
        setPartite([]);
        setStato(null);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (stagione !== null) refresh(stagione, competizione);
    setGenMsg(null);
    setSaveMsg(null);
    setError(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stagione, competizione]);

  const esiste = stagione !== null && stagioni.includes(stagione);

  const postGenera = async (url: string, msg: (d: any) => string) => {
    if (stagione === null) return;
    setGenerating(true);
    setError(null);
    setGenMsg(null);
    setSaveMsg(null);
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ stagione }),
      });
      const d = await res.json();
      if (!res.ok) throw new Error(d.detail || "Errore nella generazione");
      setGenMsg(msg(d));
      setStagioni((prev) => (prev.includes(d.stagione) ? prev : [...prev, d.stagione]));
      refresh(stagione, competizione);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setGenerating(false);
    }
  };

  const generaGirone = async () => {
    if (stagione === null) return;
    if (esiste || partite.length > 0) {
      const ok = window.confirm(
        `La Stagione ${stagione} ha già partite di Galactic League. Rigenerare il girone ` +
          `lo sostituisce e azzera i risultati inseriti. Procedere?`,
      );
      if (!ok) return;
    }
    await postGenera(`${API_URL}/genera/league-phase`, (d) =>
      `Generata la fase a gironi (template #${d.template}, ${d.partite_inserite} partite).`,
    );
  };

  const generaProssimo = async () => {
    if (!stato?.prossimo) return;
    await postGenera(`${API_URL}/genera/${compMeta.roundUrl}`, (d) =>
      `Generato "${d.label}" (${d.partite_inserite} partite).`,
    );
  };

  const salvaRisultati = async () => {
    const cambiati = partite
      .filter((p) => (inputs[p.id] ?? "") !== (saved[p.id] ?? ""))
      .map((p) => ({ id: p.id, risultato: (inputs[p.id] ?? "").trim() }));
    if (cambiati.length === 0) {
      setSaveMsg("Nessuna modifica da salvare.");
      return;
    }
    setSaving(true);
    setError(null);
    setSaveMsg(null);
    try {
      const res = await fetch(`${API_URL}/partite/risultati`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ risultati: cambiati }),
      });
      const d = await res.json();
      if (!res.ok) throw new Error(d.detail || "Errore nel salvataggio");
      let msg = `Salvati ${d.aggiornate} risultati.`;
      if (d.propagato && d.propagato.length > 0) {
        const giornateUniche = Array.from(
          new Set(d.propagato.map((p: { giornata: string }) => p.giornata)),
        );
        msg += ` 🔄 Aggiornata automaticamente la squadra in: ${giornateUniche.join(", ")} (punteggio azzerato, da reinserire).`;
      }
      if (d.invalidato && d.invalidato.length > 0) {
        const dettagli = d.invalidato
          .map((inv: { stagione: number; competizioni_azzerate: string[] }) =>
            `Stagione ${inv.stagione}: ${inv.competizioni_azzerate.join(" e ")}`,
          )
          .join("; ");
        msg += ` ⚠️ Hai modificato un risultato decisivo: per coerenza sono stati azzerati i risultati di ${dettagli}. Rigenerali quando vuoi.`;
      }
      setSaveMsg(msg);
      refresh(stagione!, competizione); // ricarica → aggiorna abilitazione turni
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setSaving(false);
    }
  };

  // Backup / trasferimento (JSON)
  const downloadJson = async (path: string, filename: string) => {
    setError(null);
    setBackupMsg(null);
    try {
      const res = await fetch(`${API_URL}${path}`);
      if (!res.ok) {
        const d = await res.json().catch(() => ({}));
        throw new Error(d.detail || "Errore nell'esportazione");
      }
      const data = await res.json();
      const blob = new Blob([JSON.stringify(data)], { type: "application/json" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = filename;
      a.click();
      URL.revokeObjectURL(a.href);
      setBackupMsg(`Esportato: ${filename}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  const importJson = async (file: File) => {
    setError(null);
    setBackupMsg(null);
    try {
      const json = JSON.parse(await file.text());
      const res = await fetch(`${API_URL}/import/partite`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(json),
      });
      const d = await res.json();
      if (!res.ok) throw new Error(d.detail || "Errore nell'importazione");
      setBackupMsg(`Importate ${d.partite_importate} partite (stagioni ${(d.stagioni || []).join(", ")}).`);
      const s = await fetch(`${API_URL}/stagioni`).then((r) => r.json());
      setStagioni(s.stagioni || []);
      if (stagione !== null) refresh(stagione, competizione);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  };

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

  const nModificati = partite.filter(
    (p) => (inputs[p.id] ?? "") !== (saved[p.id] ?? ""),
  ).length;

  const isLeague = competizione === "galactic league";
  // Per la League il bottone "prossimo turno" (eliminazione) si mostra solo a girone esistente
  const mostraProssimo = stato?.prossimo && (!isLeague || stato.gruppo?.esiste);

  return (
    <div>
      <div className="flex items-end justify-between mb-6 flex-wrap gap-4">
        <div>
          <h1 className="text-5xl font-bold text-amber-300 tracking-wide drop-shadow-[0_0_30px_rgba(252,211,77,0.3)]">
            Genera Stagione
          </h1>
          <p className="text-slate-400 mt-1 text-sm">
            Sorteggia le competizioni una alla volta, turno per turno, e inserisci i
            risultati. L'import Excel resta disponibile.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <label className="text-sm text-slate-300 font-medium">Competizione:</label>
          <select
            value={competizione}
            onChange={(e) => setCompetizione(e.target.value as CompKey)}
            className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-white focus:outline-none focus:border-cyan-400"
          >
            {COMPETIZIONI.map((c) => (
              <option key={c.key} value={c.key}>
                {c.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Pannello generazione */}
      <div className="rounded-2xl bg-slate-900/50 border border-slate-700 p-5 mb-6 flex items-center gap-4 flex-wrap">
        <label className="text-sm text-slate-300 font-medium">Stagione:</label>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setStagione((s) => (s !== null ? Math.max(1, s - 1) : s))}
            className="w-9 h-9 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 hover:text-white"
          >
            −
          </button>
          <span className="w-14 text-center font-mono text-lg text-cyan-300">{stagione ?? "—"}</span>
          <button
            onClick={() => setStagione((s) => (s !== null ? s + 1 : s))}
            className="w-9 h-9 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 hover:text-white"
          >
            +
          </button>
        </div>

        {/* League: bottone girone */}
        {isLeague && (
          <button
            onClick={generaGirone}
            disabled={generating || stagione === null}
            className="px-5 py-2.5 rounded-lg bg-sky-500/20 border border-sky-500/40 text-sky-200 font-medium hover:bg-sky-500/30 disabled:opacity-50 transition-colors"
          >
            {generating ? "Generazione…" : "Genera fase a gironi"}
          </button>
        )}

        {/* Prossimo turno (eliminazione League / turni Cup) */}
        {mostraProssimo ? (
          <button
            onClick={generaProssimo}
            disabled={generating || !stato!.prossimo_abilitato}
            className="px-5 py-2.5 rounded-lg bg-emerald-500/20 border border-emerald-500/40 text-emerald-200 font-medium hover:bg-emerald-500/30 disabled:opacity-50 transition-colors"
          >
            {generating ? "Generazione…" : `⚔️ Genera ${stato!.prossimo_label}`}
          </button>
        ) : stato && !stato.prossimo && (!isLeague || stato.gruppo?.esiste) ? (
          <span className="text-sm text-emerald-300">
            {stato.done_message ?? `🏆 ${compMeta.label} completata.`}
          </span>
        ) : null}

        {mostraProssimo && !stato!.prossimo_abilitato && (
          <span className="text-xs text-slate-400">
            {stato!.prossimo_hint ??
              (competizione === "galactic cup" && stato!.prev_disponibile === false
                ? "Serve la Galactic League completa della stagione precedente."
                : `Completa i risultati del turno precedente per generare ${stato!.prossimo_label}.`)}
          </span>
        )}

        {isLeague && esiste && (
          <span className="text-xs text-amber-300/80">
            ⚠ La Stagione {stagione} esiste già: rigenerare il girone la sostituisce.
          </span>
        )}
      </div>

      {genMsg && (
        <div className="rounded-lg bg-emerald-950/40 border border-emerald-700/40 text-emerald-300 px-4 py-3 mb-6 text-sm">
          {genMsg}
        </div>
      )}
      {error && (
        <div className="rounded-lg bg-red-950/40 border border-red-700/40 text-red-300 px-4 py-3 mb-6 text-sm">
          {error}
        </div>
      )}

      {/* Pannello backup / trasferimento (JSON) */}
      <div className="rounded-2xl bg-slate-900/40 border border-slate-700 p-5 mb-6 flex items-center gap-3 flex-wrap">
        <span className="text-sm text-slate-300 font-medium">Backup / Trasferimento:</span>
        <button
          onClick={() =>
            stagione !== null && downloadJson(`/export/stagione/${stagione}`, `stagione-${stagione}.json`)
          }
          disabled={stagione === null}
          className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 hover:text-white text-sm disabled:opacity-50"
        >
          ⬇️ Esporta stagione {stagione ?? ""}
        </button>
        <button
          onClick={() => downloadJson(`/export/tutto`, `galactic-tournaments-backup.json`)}
          className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 hover:text-white text-sm"
        >
          ⬇️ Esporta tutto
        </button>
        <label className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-200 hover:text-white text-sm cursor-pointer">
          ⬆️ Importa (JSON)
          <input
            type="file"
            accept="application/json,.json"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) importJson(f);
              e.target.value = "";
            }}
          />
        </label>
        {backupMsg && <span className="text-sm text-emerald-300">{backupMsg}</span>}
        <span className="text-xs text-slate-500 basis-full">
          "Importa" sostituisce le partite delle stagioni presenti nel file. Utile come backup e per
          spostare i dati su un altro PC senza il database.
        </span>
      </div>

      {/* Inserimento risultati */}
      {loading ? (
        <div className="text-center text-slate-400 py-16">Caricamento partite…</div>
      ) : partite.length === 0 ? (
        <div className="text-center text-slate-500 py-16">
          Nessuna partita di {compMeta.label} per la Stagione {stagione}.
        </div>
      ) : (
        <>
          <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
            <h2 className="text-2xl font-bold text-sky-300">
              {compMeta.label} — Stagione {stagione}
            </h2>
            <div className="flex items-center gap-3">
              {saveMsg && <span className="text-sm text-emerald-300">{saveMsg}</span>}
              <button
                onClick={salvaRisultati}
                disabled={saving || nModificati === 0}
                className="px-5 py-2.5 rounded-lg bg-emerald-500/20 border border-emerald-500/40 text-emerald-200 font-medium hover:bg-emerald-500/30 disabled:opacity-50 transition-colors"
              >
                {saving ? "Salvataggio…" : `Salva risultati${nModificati ? ` (${nModificati})` : ""}`}
              </button>
            </div>
          </div>

          <p className="text-xs text-slate-500 mb-4">
            Formati: <span className="font-mono text-slate-400">2-1</span> ·
            rigori <span className="font-mono text-slate-400">1-1 (4-3)</span> ·
            supplementari <span className="font-mono text-slate-400">2-1 [0-0]</span>.
          </p>

          <div className="space-y-4">
            {giornate.map(({ giornata, partite }) => (
              <div
                key={giornata}
                className="rounded-xl bg-slate-900/40 border border-slate-700 overflow-hidden"
              >
                <div className="px-5 py-3 bg-slate-800/40 font-semibold text-white">{giornata}</div>
                <table className="w-full text-sm">
                  <tbody>
                    {partite.map((p) => (
                      <tr
                        key={p.id}
                        className="border-b border-slate-800 last:border-b-0 hover:bg-slate-800/20"
                      >
                        <td className="px-5 py-2 text-right text-slate-200 w-2/5">{p.squadra_casa}</td>
                        <td className="px-3 py-2 text-center w-1/5">
                          <input
                            type="text"
                            value={inputs[p.id] ?? ""}
                            onChange={(e) =>
                              setInputs((prev) => ({ ...prev, [p.id]: e.target.value }))
                            }
                            placeholder="–"
                            className="w-24 text-center font-mono bg-slate-800 border border-slate-600 rounded-md px-2 py-1 text-cyan-300 focus:outline-none focus:border-cyan-400"
                          />
                        </td>
                        <td className="px-5 py-2 text-left text-slate-200 w-2/5">
                          {p.squadra_trasferta}
                          {p.campo === "Neutro" && (
                            <span className="ml-2 text-[10px] text-slate-500">(neutro)</span>
                          )}
                        </td>
                      </tr>
                    ))}
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

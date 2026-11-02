import { useEffect, useRef, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:3004/api";

type UploadResponse = {
  stagione: number;
  filename: string;
  partite_totali: number;
  partite_per_competizione: Record<string, number>;
};

function parseStagioneFromName(name: string): number | null {
  const m = name.match(/stagione\s*(\d+)/i);
  return m ? parseInt(m[1], 10) : null;
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
}

export default function Import() {
  const [file, setFile] = useState<File | null>(null);
  const [stagione, setStagione] = useState<number | "">("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<UploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [stagioniInDb, setStagioniInDb] = useState<number[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const refreshStagioni = async () => {
    try {
      const res = await fetch(`${API_URL}/stagioni`);
      if (res.ok) {
        const data = await res.json();
        setStagioniInDb(data.stagioni || []);
      }
    } catch {
      // backend non raggiungibile: ignora
    }
  };

  useEffect(() => {
    refreshStagioni();
  }, []);

  const acceptFile = (f: File) => {
    setFile(f);
    setResult(null);
    setError(null);
    const s = parseStagioneFromName(f.name);
    if (s !== null) setStagione(s);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) acceptFile(f);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const f = e.dataTransfer.files?.[0];
    if (f) acceptFile(f);
  };

  const handleUpload = async () => {
    if (!file) return setError("Seleziona prima un file Excel");
    if (stagione === "") return setError("Specifica la stagione");

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("stagione", String(stagione));

      const res = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Errore HTTP ${res.status}`);
      }

      const data: UploadResponse = await res.json();
      setResult(data);
      refreshStagioni();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Errore sconosciuto");
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFile(null);
    setStagione("");
    setResult(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const stagioneEsistente =
    stagione !== "" && stagioniInDb.includes(Number(stagione));

  return (
    <div>
      {/* ── Titolo ────────────────────────────────────────────── */}
      <div className="text-center mb-10">
        <h1 className="text-5xl font-bold text-cyan-400 tracking-wide mb-3 drop-shadow-[0_0_30px_rgba(34,211,238,0.4)]">
          Importa Stagione
        </h1>
        <p className="text-slate-400">
          Carica il file Excel per aggiornare statistiche e ranking
        </p>
      </div>

      {/* ── Zona drag & drop (visibile finché nessun file è selezionato) ── */}
      {!file && (
        <div
          onDragEnter={(e) => {
            e.preventDefault();
            setIsDragging(true);
          }}
          onDragOver={(e) => e.preventDefault()}
          onDragLeave={(e) => {
            e.preventDefault();
            setIsDragging(false);
          }}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={
            "max-w-2xl mx-auto rounded-2xl border-2 border-dashed p-12 text-center cursor-pointer transition-all " +
            (isDragging
              ? "border-cyan-400 bg-cyan-500/10 scale-[1.01]"
              : "border-slate-600 bg-slate-900/40 hover:bg-slate-800/40 hover:border-slate-500")
          }
        >
          <div className="flex justify-center mb-6">
            <div className="w-20 h-20 rounded-2xl bg-slate-800/80 border border-cyan-500/30 flex items-center justify-center shadow-[0_0_30px_rgba(34,211,238,0.15)]">
              <svg
                className="w-10 h-10 text-cyan-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
                />
              </svg>
            </div>
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">
            Trascina il file Excel qui
          </h2>
          <p className="text-slate-400 mb-6">oppure clicca per selezionare</p>
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              fileInputRef.current?.click();
            }}
            className="inline-flex items-center gap-2 px-6 py-3 bg-cyan-500 hover:bg-cyan-400 text-slate-900 font-semibold rounded-lg transition-colors shadow-[0_4px_20px_rgba(34,211,238,0.3)]"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            Seleziona File
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx,.xlsm,.xls"
            onChange={handleFileChange}
            className="hidden"
          />
          <p className="text-xs text-slate-500 mt-5">
            Formati supportati: .xlsx, .xls, .xlsm
          </p>
        </div>
      )}

      {/* ── Panel post-selezione file ───────────────────────────── */}
      {file && (
        <div className="max-w-2xl mx-auto rounded-2xl bg-slate-900/50 border border-slate-700 p-8 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-700">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-lg bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-cyan-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>
              <div>
                <p className="font-semibold text-white">{file.name}</p>
                <p className="text-xs text-slate-400">{formatFileSize(file.size)}</p>
              </div>
            </div>
            <button
              onClick={resetForm}
              className="text-slate-400 hover:text-white text-xl px-2"
              title="Annulla"
            >
              ✕
            </button>
          </div>

          <div className="mb-6">
            <label className="block text-sm text-slate-300 mb-2 font-medium">
              Stagione
            </label>
            <input
              type="number"
              min={1}
              value={stagione}
              onChange={(e) =>
                setStagione(e.target.value === "" ? "" : parseInt(e.target.value, 10))
              }
              className="w-32 px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-white focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
              placeholder="es. 5"
            />
            {stagioneEsistente && (
              <p className="text-xs text-amber-400 mt-2 flex items-center gap-1">
                ⚠️ Stagione {stagione} già presente in DB — verrà sovrascritta.
              </p>
            )}
          </div>

          <button
            onClick={handleUpload}
            disabled={stagione === "" || loading}
            className="w-full px-6 py-3 bg-cyan-500 hover:bg-cyan-400 text-slate-900 font-semibold rounded-lg transition-colors disabled:bg-slate-700 disabled:text-slate-400 disabled:cursor-not-allowed shadow-[0_4px_20px_rgba(34,211,238,0.2)]"
          >
            {loading ? (
              <span className="inline-flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-slate-900 border-t-transparent rounded-full animate-spin" />
                Importazione in corso…
              </span>
            ) : (
              "Importa nel database"
            )}
          </button>

          {error && (
            <div className="mt-6 p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300">
              <strong>Errore:</strong> {error}
            </div>
          )}

          {result && (
            <div className="mt-6 p-6 rounded-lg bg-emerald-500/10 border border-emerald-500/30">
              <p className="font-semibold text-emerald-300 mb-1">
                ✅ Importazione completata
              </p>
              <p className="text-sm text-slate-300 mb-4">
                Stagione <strong className="text-cyan-300">{result.stagione}</strong>{" "}
                · <strong className="text-cyan-300">{result.partite_totali}</strong>{" "}
                partite salvate
              </p>
              <table className="text-sm w-full">
                <thead>
                  <tr className="border-b border-emerald-500/30 text-slate-400">
                    <th className="text-left py-2 font-medium">Competizione</th>
                    <th className="text-right py-2 font-medium">Partite</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(result.partite_per_competizione).map(([comp, n]) => (
                    <tr
                      key={comp}
                      className="border-b border-emerald-500/10 last:border-b-0"
                    >
                      <td className="py-2 text-slate-200">{comp}</td>
                      <td className="text-right py-2 font-semibold text-cyan-300">
                        {n}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* ── Stagioni già in DB ──────────────────────────────────── */}
      <div className="mt-10 text-center text-sm text-slate-500">
        <span className="text-slate-400 font-medium">Stagioni nel database:</span>{" "}
        {stagioniInDb.length > 0 ? (
          <span className="inline-flex gap-1 ml-2">
            {stagioniInDb
              .sort((a, b) => a - b)
              .map((s) => (
                <span
                  key={s}
                  className="px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs font-mono"
                >
                  S{s}
                </span>
              ))}
          </span>
        ) : (
          <span className="text-slate-600 italic">nessuna</span>
        )}
      </div>
    </div>
  );
}

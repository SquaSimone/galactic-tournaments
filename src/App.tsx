import { useState } from "react";
import Import from "./pages/Import";
import GeneraStagione from "./pages/GeneraStagione";
import Competizioni from "./pages/Competizioni";
import Cumulate from "./pages/Cumulate";
import StoricoCompetizioni from "./pages/StoricoCompetizioni";
import AlboOro from "./pages/AlboOro";

type TabKey = "import" | "genera" | "competizioni" | "cumulate" | "storico" | "albo-oro";

const TABS: { key: TabKey; label: string }[] = [
  { key: "import", label: "Importa Stagione" },
  { key: "genera", label: "Genera Stagione" },
  { key: "competizioni", label: "Statistiche Stagionali" },
  { key: "cumulate", label: "Statistiche Cumulate" },
  { key: "storico", label: "Competizioni" },
  { key: "albo-oro", label: "Albo d'Oro" },
];

function App() {
  const [activeTab, setActiveTab] = useState<TabKey>("import");

  return (
    <div className="min-h-screen text-white">
      <nav className="border-b border-white/10 backdrop-blur-sm bg-black/20 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
          <span className="text-sm font-semibold text-cyan-300 tracking-wider py-3">
            ⚡ GALACTIC TOURNAMENTS
          </span>
          <div className="flex gap-1">
            {TABS.map((t) => (
              <button
                key={t.key}
                onClick={() => setActiveTab(t.key)}
                className={
                  "px-4 py-3 text-sm font-medium border-b-2 transition-colors " +
                  (activeTab === t.key
                    ? "border-cyan-400 text-cyan-300"
                    : "border-transparent text-slate-400 hover:text-white")
                }
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-12">
        {activeTab === "import" && <Import />}
        {activeTab === "genera" && <GeneraStagione />}
        {activeTab === "competizioni" && <Competizioni />}
        {activeTab === "cumulate" && <Cumulate />}
        {activeTab === "storico" && <StoricoCompetizioni />}
        {activeTab === "albo-oro" && <AlboOro />}
      </main>
    </div>
  );
}

export default App;

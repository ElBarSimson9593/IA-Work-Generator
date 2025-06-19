import { useState } from "react";
import ChatBot, { Contexto } from "./components/ChatBot";
import Generate from "./components/Generate";
import EditPanel from "./components/EditPanel";
import ExportView from "./components/ExportView";
import Historial from "./components/Historial";

export default function App() {
  const [view, setView] = useState<"chat" | "generate" | "edit" | "export" | "history">("chat");
  const [contexto, setContexto] = useState<Contexto | null>(null);
  const [tipo, setTipo] = useState("Informe");
  const [texto, setTexto] = useState("");

  return (
    <main className="min-h-screen flex flex-col items-center p-4 gap-4">
      <h1 className="text-2xl font-bold mb-2">IA Work Generator</h1>

      {view === "chat" && (
        <>
          <ChatBot
            onContextConfirmed={(ctx) => {
              setContexto(ctx);
              setView("generate");
            }}
          />
          <div className="mt-2 flex flex-col gap-2 w-full max-w-xs">
            <label className="text-sm">Tipo de informe</label>
            <input
              className="border rounded p-2"
              value={tipo}
              onChange={(e) => setTipo(e.currentTarget.value)}
            />
          </div>
        </>
      )}

      {view === "generate" && contexto && (
        <Generate
          ctx={{ ...contexto, tipo }}
          onDone={(t) => {
            setTexto(t);
            setView("edit");
          }}
        />
      )}

      {view === "edit" && (
        <EditPanel
          initial={texto}
          onSave={(t) => setTexto(t)}
          onRegenerate={() => setView("generate")}
          onBack={() => setView("chat")}
          onExport={() => setView("export")}
        />
      )}

      {view === "export" && (
        <ExportView
          contenido={texto}
          onFinish={() => setView("edit")}
        />
      )}

      {view === "history" && (
        <Historial
          onSelect={(id) => {
            fetch(`http://127.0.0.1:8000/historial/${id}`)
              .then((r) => r.json())
              .then((data) => {
                setTexto(data.contenido);
                setContexto({
                  proposito: data.proposito,
                  tema: data.tema,
                  estilo: data.estilo,
                  paginas: data.paginas,
                  extras: data.extras,
                });
                setTipo(data.tipo);
                setView("edit");
              });
          }}
        />
      )}

      <div className="mt-4 flex gap-2">
        <button
          className="px-3 py-1 bg-blue-600 text-white rounded"
          onClick={() => setView("chat")}
        >
          Chat
        </button>
        <button
          className="px-3 py-1 bg-gray-200 rounded"
          onClick={() => setView("history")}
        >
          Historial
        </button>
      </div>
    </main>
  );
}

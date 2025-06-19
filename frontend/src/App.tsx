import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";

interface GenerarResponse {
  id: string;
  contenido: string;
}

interface HistItem {
  id: string;
  tema: string;
  tipo: string;
  timestamp: string;
}

export default function App() {
  const [tema, setTema] = useState("");
  const [tipo, setTipo] = useState("");
  const [resultado, setResultado] = useState("");
  const [vistaPrevia, setVistaPrevia] = useState(false);
  const [formato, setFormato] = useState("docx");
  const [historial, setHistorial] = useState<HistItem[]>([]);
  const [busqueda, setBusqueda] = useState("");
  const [activeTab, setActiveTab] = useState<"generar" | "historial">("generar");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    cargarHistorial();
  }, []);

  async function cargarHistorial() {
    const resp = await fetch("http://127.0.0.1:8000/historial");
    if (resp.ok) {
      const data = (await resp.json()) as HistItem[];
      setHistorial(data);
    }
  }

  async function generar() {
    setLoading(true);
    setError("");
    const resp = await fetch("http://127.0.0.1:8000/generar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tema, tipo }),
    });
    if (!resp.ok) {
      setError("Error al generar informe");
      setLoading(false);
      return;
    }
    const data = (await resp.json()) as GenerarResponse;
    setResultado(data.contenido);
    setVistaPrevia(false);
    setLoading(false);
    cargarHistorial();
  }

  async function exportar() {
    setLoading(true);
    const resp = await fetch("http://127.0.0.1:8000/exportar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ contenido: resultado, formato }),
    });
    setLoading(false);
    if (!resp.ok) {
      setError("Error al exportar");
      return;
    }
    const blob = await resp.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `informe_generado.${formato}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  }

  async function cargarInforme(id: string) {
    const resp = await fetch(`http://127.0.0.1:8000/historial/${id}`);
    if (resp.ok) {
      const data = (await resp.json()) as HistItem & { contenido: string };
      setTema(data.tema);
      setTipo(data.tipo);
      setResultado(data.contenido);
      setVistaPrevia(false);
      setActiveTab("generar");
    }
  }

  async function eliminarInforme(id: string) {
    await fetch(`http://127.0.0.1:8000/historial/${id}`, { method: "DELETE" });
    setHistorial((prev) => prev.filter((it) => it.id !== id));
  }

  async function exportarHistorial(id: string, fmt: string) {
    const resp = await fetch(
      `http://127.0.0.1:8000/historial/${id}?exportar=${fmt}`
    );
    if (!resp.ok) return;
    const blob = await resp.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `informe_generado.${fmt}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  }

  async function buscarHistorial(e: React.FormEvent) {
    e.preventDefault();
    if (!busqueda) {
      cargarHistorial();
      return;
    }
    const resp = await fetch("http://127.0.0.1:8000/buscar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: busqueda }),
    });
    if (resp.ok) {
      const data = (await resp.json()) as HistItem[];
      setHistorial(data);
    }
  }

  return (
    <main className="min-h-screen flex flex-col items-center justify-start p-8 gap-4">
      <h1 className="text-2xl font-bold">Generador de Informes</h1>
      <div className="flex gap-4 mb-4">
        <button
          className={`p-2 rounded ${activeTab === "generar" ? "bg-blue-600 text-white" : "bg-gray-200"}`}
          onClick={() => setActiveTab("generar")}
        >
          Generar
        </button>
        <button
          className={`p-2 rounded ${activeTab === "historial" ? "bg-blue-600 text-white" : "bg-gray-200"}`}
          onClick={() => {
            setActiveTab("historial");
            cargarHistorial();
          }}
        >
          Historial
        </button>
      </div>

      {error && <div className="text-red-600 mb-2">{error}</div>}
      {loading && <div className="mb-2">Cargando...</div>}

      {activeTab === "generar" && (
        <>
          <form
            className="flex flex-col gap-4 w-full max-w-md"
            onSubmit={(e) => {
              e.preventDefault();
              generar();
            }}
          >
            <input
              className="border rounded p-2"
              value={tema}
              onChange={(e) => setTema(e.currentTarget.value)}
              placeholder="Tema del informe"
            />
            <input
              className="border rounded p-2"
              value={tipo}
              onChange={(e) => setTipo(e.currentTarget.value)}
              placeholder="Tipo de informe"
            />
            <button className="bg-blue-600 text-white rounded p-2" type="submit">
              Generar
            </button>
          </form>

          {resultado && (
            <>
              <button
                className="text-sm text-blue-600 mb-2"
                onClick={() => setVistaPrevia(!vistaPrevia)}
              >
                {vistaPrevia ? "Ver como texto plano" : "Ver con formato"}
              </button>
              {vistaPrevia ? (
                <div className="prose max-w-md bg-white p-4 border rounded">
                  <ReactMarkdown>{resultado}</ReactMarkdown>
                </div>
              ) : (
                <pre className="mt-0 bg-gray-100 p-4 rounded w-full max-w-md whitespace-pre-wrap">
                  {resultado}
                </pre>
              )}
              <div className="mt-2 flex items-center gap-2">
                <select
                  className="border rounded p-2"
                  value={formato}
                  onChange={(e) => setFormato(e.currentTarget.value)}
                >
                  <option value="docx">DOCX</option>
                  <option value="pdf">PDF</option>
                </select>
                <button
                  className="bg-green-600 text-white rounded p-2"
                  onClick={exportar}
                >
                  Exportar informe
                </button>
              </div>
            </>
          )}
        </>
      )}

      {activeTab === "historial" && (
        <div className="w-full max-w-md">
          <form className="mb-2 flex" onSubmit={buscarHistorial}>
            <input
              className="border rounded p-2 flex-1"
              placeholder="Buscar..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.currentTarget.value)}
            />
            <button className="ml-2 p-2 bg-blue-600 text-white rounded" type="submit">
              Buscar
            </button>
          </form>
          <ul>
            {historial.map((item) => (
              <li key={item.id} className="border-b p-2 flex justify-between items-start">
                <div className="flex-1 cursor-pointer" onClick={() => cargarInforme(item.id)}>
                  <div className="font-semibold">{item.tema}</div>
                  <div className="text-sm text-gray-500">
                    {item.tipo} - {new Date(item.timestamp).toLocaleString()}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button className="text-blue-600 text-sm" onClick={() => exportarHistorial(item.id, "docx")}>DOCX</button>
                  <button className="text-blue-600 text-sm" onClick={() => exportarHistorial(item.id, "pdf")}>PDF</button>
                  <button className="text-red-600 text-sm" onClick={() => eliminarInforme(item.id)}>Eliminar</button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </main>
  );
}

import { useState } from "react";

interface GenerarResponse {
  contenido: string;
}

export default function App() {
  const [tema, setTema] = useState("");
  const [tipo, setTipo] = useState("");
  const [resultado, setResultado] = useState("");
  const [formato, setFormato] = useState("docx");

  async function generar() {
    const resp = await fetch("http://127.0.0.1:8000/generar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tema, tipo }),
    });
    if (!resp.ok) {
      setResultado("Error al generar informe");
      return;
    }
    const data = (await resp.json()) as GenerarResponse;
    setResultado(data.contenido);
  }

  async function exportar() {
    const resp = await fetch("http://127.0.0.1:8000/exportar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ contenido: resultado, formato }),
    });
    if (!resp.ok) {
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

  return (
    <main className="min-h-screen flex flex-col items-center justify-start p-8 gap-4">
      <h1 className="text-2xl font-bold">Generador de Informes</h1>
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
          <pre className="mt-4 bg-gray-100 p-4 rounded w-full max-w-md whitespace-pre-wrap">
            {resultado}
          </pre>
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
    </main>
  );
}

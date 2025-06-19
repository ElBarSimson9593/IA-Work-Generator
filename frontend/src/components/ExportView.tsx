import { useState } from "react";

interface Props {
  contenido: string;
  onFinish: () => void;
}

export default function ExportView({ contenido, onFinish }: Props) {
  const [format, setFormat] = useState("docx");
  const [msg, setMsg] = useState("");

  async function exportar() {
    const resp = await fetch("http://127.0.0.1:8000/exportar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ contenido, formato: format }),
    });
    if (!resp.ok) return setMsg("Error al exportar");
    const blob = await resp.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `informe.${format}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
    setMsg("Exportación completada");
  }

  return (
    <div className="w-full max-w-sm flex flex-col gap-4">
      <div>
        <label className="mr-2">Formato:</label>
        <select
          className="border rounded p-2"
          value={format}
          onChange={(e) => setFormat(e.currentTarget.value)}
        >
          <option value="docx">DOCX</option>
          <option value="pdf">PDF</option>
        </select>
      </div>
      <button className="bg-green-600 text-white rounded p-2" onClick={exportar}>
        Exportar informe
      </button>
      {msg && <div className="text-sm text-blue-700">{msg}</div>}
      <button className="text-sm underline" onClick={onFinish}>
        Volver
      </button>
    </div>
  );
}

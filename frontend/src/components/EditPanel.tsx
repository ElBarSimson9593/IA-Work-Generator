import ReactMarkdown from "react-markdown";
import { useState } from "react";

interface Props {
  initial: string;
  onSave: (text: string) => void;
  onRegenerate: () => void;
  onBack: () => void;
  onExport: () => void;
}

export default function EditPanel({
  initial,
  onSave,
  onRegenerate,
  onBack,
  onExport,
}: Props) {
  const [text, setText] = useState(initial);
  const [preview, setPreview] = useState(false);

  return (
    <div className="w-full max-w-2xl flex flex-col gap-2">
      <div className="flex gap-2 mb-2">
        <button
          className="px-3 py-1 rounded bg-blue-600 text-white"
          onClick={() => setPreview(!preview)}
        >
          {preview ? "Editar" : "Vista"}
        </button>
        <button
          className="px-3 py-1 rounded bg-green-600 text-white"
          onClick={() => onSave(text)}
        >
          Guardar cambios
        </button>
        <button
          className="px-3 py-1 rounded bg-yellow-600 text-white"
          onClick={onRegenerate}
        >
          Generar de nuevo
        </button>
        <button
          className="px-3 py-1 rounded bg-gray-500 text-white"
          onClick={onBack}
        >
          Volver al chat
        </button>
        <button
          className="px-3 py-1 rounded bg-purple-600 text-white ml-auto"
          onClick={onExport}
        >
          Exportar
        </button>
      </div>
      {preview ? (
        <div className="prose border rounded p-2 bg-white max-h-96 overflow-y-auto">
          <ReactMarkdown>{text}</ReactMarkdown>
        </div>
      ) : (
        <textarea
          className="border rounded p-2 h-96 w-full"
          value={text}
          onChange={(e) => setText(e.currentTarget.value)}
        />
      )}
    </div>
  );
}

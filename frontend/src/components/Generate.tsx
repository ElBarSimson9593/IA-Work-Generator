import { useEffect, useState, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { Contexto } from "./Chat";

interface Props {
  ctx: Contexto & { tipo: string };
  onDone: (texto: string) => void;
}

export default function Generate({ ctx, onDone }: Props) {
  const [text, setText] = useState("");
  const [display, setDisplay] = useState("");
  const [running, setRunning] = useState(true);
  const timer = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    async function run() {
      const resp = await fetch("http://127.0.0.1:8000/generar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(ctx),
      });
      if (resp.ok) {
        const data = await resp.json();
        setText(data.contenido);
      }
    }
    run();
    return () => {
      if (timer.current) clearInterval(timer.current);
    };
  }, [ctx]);

  useEffect(() => {
    if (!text) return;
    let i = 0;
    timer.current = setInterval(() => {
      i += 1;
      setDisplay(text.slice(0, i));
      if (i >= text.length) {
        if (timer.current) clearInterval(timer.current);
        setRunning(false);
        onDone(text);
      }
    }, 30);
  }, [text, onDone]);

  return (
    <div className="w-full max-w-2xl">
      <div className="mb-2 p-2 border rounded bg-gray-50">
        <div className="text-sm text-gray-600">Tema: {ctx.tema}</div>
        <div className="text-sm text-gray-600">Estilo: {ctx.estilo}</div>
        <div className="text-sm text-gray-600">Páginas: {ctx.paginas}</div>
      </div>
      <div className="prose max-h-96 overflow-y-auto border rounded p-2 bg-white">
        <ReactMarkdown>{display}</ReactMarkdown>
      </div>
      {running && (
        <button
          className="mt-2 bg-red-600 text-white px-4 py-1 rounded"
          onClick={() => {
            if (timer.current) clearInterval(timer.current);
            setRunning(false);
          }}
        >
          Detener generación
        </button>
      )}
    </div>
  );
}

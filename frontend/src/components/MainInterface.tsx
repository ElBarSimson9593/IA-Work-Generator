import { useEffect, useRef, useState } from "react";

interface Message {
  role: "user" | "bot";
  text: string;
}

interface GenContext {
  tema?: string;
  estilo?: string;
  paginas?: number;
  idioma?: string;
  longitud?: string;
}

export default function MainInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [showGen, setShowGen] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [escribiendo, setEscribiendo] = useState(false);
  const [display, setDisplay] = useState("");
  const [editable, setEditable] = useState("");
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send() {
    if (!input.trim() || generating) return;
    const text = input;
    setMessages((p) => [...p, { role: "user", text }]);
    setInput("");
    setEscribiendo(true);
    try {
      const resp = await fetch("http://127.0.0.1:8000/conversar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mensaje: text }),
      });
      if (!resp.ok) throw new Error("Request failed");
      const data = await resp.json();
      console.log("DEBUG response:", data);
      let reply: string | undefined =
        data.respuesta ?? data.text ?? data.resultado ?? data.message ?? data.result;
      if (!reply) {
        console.warn("Respuesta vacía o malformada", data);
        reply = "Sin respuesta generada.";
      }
      setMessages((p) => [...p, { role: "bot", text: reply }]);
      if (data.iniciar_generacion) {
        setShowGen(true);
        setGenerating(true);
        iniciarGeneracion(data.contexto || { tema: text } as GenContext);
      }
    } catch (err) {
      setMessages((p) => [
        ...p,
        { role: "bot", text: "Error al obtener respuesta." },
      ]);
    } finally {
      setEscribiendo(false);
    }
  }

  async function iniciarGeneracion(ctx: GenContext) {
    const resp = await fetch("http://127.0.0.1:8000/generar_informe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(ctx),
    });
    if (!resp.body) {
      const t = await resp.text();
      setDisplay(t);
      setEditable(t);
      setGenerating(false);
      return;
    }
    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let all = "";
    let buffer = "";
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value);
      buffer += chunk;
      const idx = buffer.indexOf('{"finalizado": true}');
      if (idx !== -1) {
        all += buffer.slice(0, idx);
        setDisplay(all);
        break;
      } else {
        all += buffer;
        setDisplay(all);
        buffer = "";
      }
    }
    setEditable(all);
    setGenerating(false);
  }

  useEffect(() => {
    if (!generating && editable) {
      if (timerRef.current) clearTimeout(timerRef.current);
      timerRef.current = setTimeout(() => {
        fetch("http://127.0.0.1:8000/conversar", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ mensaje: "UPDATE:" + editable }),
        });
      }, 500);
    }
  }, [editable, generating]);

  return (
    <div className={`h-screen transition-all ${showGen ? "flex" : "flex-col"}`}>
      <div
        className={
          showGen
            ? "w-1/2 flex flex-col transition-all duration-300"
            : "flex-1 flex flex-col transition-all duration-300"
        }
      >
        <div className="flex-1 overflow-y-auto p-2 space-y-2">
          {messages.map((m, i) => (
            <div
              key={i}
              className={
                m.role === "user" ? "text-right text-blue-600" : "text-gray-800"
              }
            >
              {m.text}
            </div>
          ))}
          {escribiendo && (
            <div className="text-xs text-gray-500 animate-pulse">
              El bot está escribiendo...
            </div>
          )}
          <div ref={endRef} />
        </div>
        <div className="p-2 border-t flex gap-2">
          <input
            className="flex-1 border rounded p-1"
            value={input}
            disabled={generating || escribiendo}
            onChange={(e) => setInput(e.currentTarget.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                send();
              }
            }}
          />
          <button
            className="bg-blue-600 text-white px-4 rounded disabled:opacity-50"
            onClick={send}
            disabled={generating || escribiendo}
          >
            Enviar
          </button>
        </div>
      </div>
      {showGen && (
        <div className="w-1/2 flex flex-col border-l transition-all duration-300">
          <div className="flex-1 p-2 overflow-y-auto">
            {generating ? (
              <pre className="whitespace-pre-wrap text-sm">{display}</pre>
            ) : (
              <textarea
                className="w-full h-full border"
                value={editable}
                onChange={(e) => setEditable(e.currentTarget.value)}
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
}

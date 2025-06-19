import { useEffect, useState, useRef } from "react";
import { v4 as uuidv4 } from "uuid";

export interface Contexto {
  proposito?: string;
  tema?: string;
  estilo?: string;
  paginas?: number;
  extras?: string;
}

interface ChatProps {
  onCompleted: (ctx: Contexto) => void;
}

interface Mensaje {
  from: "bot" | "user";
  text: string;
}

export default function Chat({ onCompleted }: ChatProps) {
  const [messages, setMessages] = useState<Mensaje[]>([]);
  const [input, setInput] = useState("");
  const [convId] = useState(() => uuidv4());
  const ctxRef = useRef<Contexto>({});
  const inputRef = useRef<HTMLInputElement>(null);
  const [waitingConfirm, setWaitingConfirm] = useState(false);

  useEffect(() => {
    async function init() {
      const resp = await fetch(`http://127.0.0.1:8000/asistente/${convId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mensaje: "hola" }),
      });
      if (resp.ok) {
        const data = await resp.json();
        setMessages([{ from: "bot", text: data.reply }]);
      }
    }
    init();
  }, [convId]);

  async function send() {
    if (!input) return;
    const txt = input;
    setMessages((prev) => [...prev, { from: "user", text: txt }]);
    setInput("");
    const resp = await fetch(`http://127.0.0.1:8000/asistente/${convId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mensaje: txt }),
    });
    if (resp.ok) {
      const data = await resp.json();
      if (data.contexto) {
        ctxRef.current = data.contexto as Contexto;
      }
      setMessages((prev) => [...prev, { from: "bot", text: data.reply }]);
      if (data.estructura) {
        setWaitingConfirm(true);
      }
      if (data.contexto) {
        setWaitingConfirm(false);
        onCompleted(ctxRef.current);
      }
    }
    inputRef.current?.focus();
  }

  return (
    <div className="w-full max-w-xl flex flex-col gap-2">
      <div className="flex-1 border rounded p-2 h-80 overflow-y-auto bg-white">
        {messages.map((m, idx) => (
          <div key={idx} className={`mb-1 ${m.from === "bot" ? "text-blue-700" : "text-gray-800"}`}>{m.text}</div>
        ))}
      </div>
      <div className="flex gap-2 mt-2">
        <input
          ref={inputRef}
          className="flex-1 border rounded p-2"
          placeholder={waitingConfirm ? "¿Aceptas la estructura?" : "Escribe tu respuesta..."}
          value={input}
          onChange={(e) => setInput(e.currentTarget.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              send();
            }
          }}
        />
        <button className="bg-blue-600 text-white rounded px-4" onClick={send}>
          Enviar
        </button>
      </div>
    </div>
  );
}

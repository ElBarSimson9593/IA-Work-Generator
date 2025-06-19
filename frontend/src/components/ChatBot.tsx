import { useEffect, useReducer, useRef, useState } from "react";

export interface Contexto {
  proposito?: string;
  tema?: string;
  estilo?: string;
  paginas?: number;
  extras?: string;
}

interface ChatBotProps {
  onContextConfirmed: (ctx: Contexto) => void;
}

interface Mensaje {
  from: "bot" | "user";
  text: string;
}

interface State {
  step: number; // 0=saludo,1=espera confirmacion,2=finalizado
  ctx: Contexto;
  messages: Mensaje[];
}

interface Action {
  type: "init" | "user";
  text?: string;
}

function extractTopic(text: string): string {
  const m = text.match(/sobre ([^.]+)/i);
  if (m) return m[1].trim();
  return text.trim();
}

function detectStyle(text: string): string | null {
  if (/ejecutiv/i.test(text)) return "ejecutivo";
  if (/acad[eé]mic/i.test(text)) return "académico";
  if (/t[eé]cnic/i.test(text)) return "técnico";
  return null;
}

function detectPages(text: string): number | null {
  const m = text.match(/(\d+)/);
  if (m) return parseInt(m[1], 10);
  return null;
}

function analyze(text: string): "affirm" | "other" {
  const t = text.toLowerCase();
  if (/(^|\b)(ok|adelante|de acuerdo|me gusta|vale|si|sí)\b/.test(t)) return "affirm";
  return "other";
}

function applyAdjust(text: string, ctx: Contexto): Contexto {
  const nctx = { ...ctx };
  const p = detectPages(text);
  if (p) nctx.paginas = p;
  const st = detectStyle(text);
  if (st) nctx.estilo = st;
  const topicMatch = text.match(/sobre ([^.]+)/i);
  if (topicMatch) nctx.tema = topicMatch[1].trim();
  if (/dato|fuente/i.test(text)) nctx.extras = text;
  return nctx;
}

function makeProposal(ctx: Contexto): string {
  return `Perfecto, puedo redactar un informe ${ctx.estilo} de ${ctx.paginas} páginas sobre ${ctx.tema}. ¿Te parece bien ese enfoque?`;
}

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "init":
      return {
        step: 0,
        ctx: { estilo: "ejecutivo", paginas: 10 },
        messages: [{ from: "bot", text: "Hola, ¿en qué puedo ayudarte hoy?" }],
      };
    case "user":
      if (!action.text) return state;
      const text = action.text;
      const msgs = [...state.messages, { from: "user", text }];
      if (state.step === 0) {
        const topic = extractTopic(text);
        const estilo = detectStyle(text) || state.ctx.estilo || "ejecutivo";
        const paginas = detectPages(text) || state.ctx.paginas || 10;
        const ctx = { ...state.ctx, tema: topic, estilo, paginas };
        const botMsg = makeProposal(ctx);
        return { step: 1, ctx, messages: [...msgs, { from: "bot", text: botMsg }] };
      }
      if (state.step === 1) {
        if (analyze(text) === "affirm") {
          return { step: 2, ctx: state.ctx, messages: [...msgs, { from: "bot", text: "¡Genial! Empezaré a trabajar en ello." }] };
        }
        const ctx = applyAdjust(text, state.ctx);
        const botMsg = makeProposal(ctx);
        return { step: 1, ctx, messages: [...msgs, { from: "bot", text: botMsg }] };
      }
      return state;
    default:
      return state;
  }
}

export default function ChatBot({ onContextConfirmed }: ChatBotProps) {
  const [state, dispatch] = useReducer(reducer, {
    step: 0,
    ctx: { estilo: "ejecutivo", paginas: 10 },
    messages: [],
  });
  const [input, setInput] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    dispatch({ type: "init" });
  }, []);

  useEffect(() => {
    if (state.step === 2) {
      onContextConfirmed(state.ctx);
    }
  }, [state.step, state.ctx, onContextConfirmed]);

  function send() {
    if (!input) return;
    dispatch({ type: "user", text: input });
    setInput("");
    inputRef.current?.focus();
  }

  return (
    <div className="w-full max-w-xl flex flex-col gap-2">
      <div className="flex-1 border rounded p-2 h-80 overflow-y-auto bg-white">
        {state.messages.map((m, idx) => (
          <div
            key={idx}
            className={`mb-1 ${m.from === "bot" ? "text-blue-700" : "text-gray-800"}`}
          >
            {m.text}
          </div>
        ))}
      </div>
      <div className="flex gap-2 mt-2">
        <input
          ref={inputRef}
          className="flex-1 border rounded p-2"
          placeholder={state.step === 1 ? "¿Te parece bien?" : "Escribe tu respuesta..."}
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


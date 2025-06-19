import { useEffect, useRef, useState } from "react";

interface Message {
  role: "user" | "bot";
  text: string;
}

/**
 * ChatInterface representa la vista principal de conversación continua
 * con el generador de informes. Permite enviar mensajes al backend y
 * visualizar la respuesta con efecto de escritura progresiva.
 */
export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  // Desplaza la vista al último mensaje cada vez que cambia el historial
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage() {
    if (!input.trim() || loading) return;
    const text = input;
    setMessages((prev) => [...prev, { role: "user", text }]);
    setInput("");
    setLoading(true);

    try {
      const resp = await fetch("http://127.0.0.1:8000/conversar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mensaje: text }),
      });
      if (!resp.ok) throw new Error("request failed");
      const data = await resp.json();
      const reply: string = data.reply || "";
      // Mensaje vacío que se irá completando
      setMessages((prev) => [...prev, { role: "bot", text: "" }]);
      let index = 0;
      const timer = setInterval(() => {
        index += 1;
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last.role !== "bot") return prev;
          const updated = reply.slice(0, index);
          const next = prev.slice(0, -1).concat({ ...last, text: updated });
          return next;
        });
        if (index >= reply.length) {
          clearInterval(timer);
          setLoading(false);
        }
      }, 20);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "Ocurrió un error al conectar con el servidor" },
      ]);
      setLoading(false);
    }
  }

  return (
    <div className="h-full flex flex-col max-h-screen">
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`max-w-md p-2 rounded-lg text-sm whitespace-pre-wrap ${
              m.role === "user"
                ? "bg-blue-500 text-white self-end ml-auto"
                : "bg-gray-200 text-gray-900"
            }`}
          >
            {m.text}
          </div>
        ))}
        {loading && (
          <div className="text-xs text-gray-500 animate-pulse">
            el bot está escribiendo...
          </div>
        )}
        <div ref={endRef} />
      </div>
      <div className="border-t p-2 flex gap-2">
        <input
          className="flex-1 border rounded px-2 py-1"
          placeholder="Escribe un mensaje"
          value={input}
          disabled={loading}
          onChange={(e) => setInput(e.currentTarget.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              sendMessage();
            }
          }}
        />
        <button
          className="bg-blue-600 text-white rounded px-4 disabled:opacity-50"
          onClick={sendMessage}
          disabled={loading}
        >
          Enviar
        </button>
      </div>
    </div>
  );
}

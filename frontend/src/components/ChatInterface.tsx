import { useEffect, useRef, useState } from "react";
import { Card } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { request } from "../request";

interface Message {
  role: "user" | "bot" | "error";
  text: string;
  id: number;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage() {
    if (!input.trim() || loading) return;
    const text = input;
    setMessages((p) => [...p, { role: "user", text, id: Date.now() }]);
    setInput("");
    setLoading(true);
    try {
      const data = await request<{ respuesta?: string; reply?: string }>(
        "/conversar",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ mensaje: text }),
        }
      );
      const reply = data.respuesta || data.reply || "";
      if (!reply) {
        console.warn("Respuesta vacía o malformada", data);
      }
      setMessages((p) => [
        ...p,
        {
          role: "bot",
          text: reply || "Sin respuesta generada.",
          id: Date.now(),
        },
      ]);
    } catch (err) {
      setMessages((p) => [
        ...p,
        { role: "error", text: "Error al conectar con el servidor", id: Date.now() },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background text-foreground p-4">
      <Card className="w-full max-w-xl h-[80vh] flex flex-col">
        <div className="flex-1 overflow-y-auto space-y-2 pr-2">
          {messages.map((m) => (
            <div
              key={m.id}
              className={`whitespace-pre-wrap break-words p-2 rounded-lg max-w-xs md:max-w-sm ${
                m.role === "user"
                  ? "bg-blue-600 text-white ml-auto"
                  : m.role === "bot"
                  ? "bg-gray-800 text-white"
                  : "bg-red-200 text-red-800"
              }`}
            >
              {m.text}
            </div>
          ))}
          <div ref={endRef} />
        </div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            sendMessage();
          }}
          className="mt-auto p-2 border-t flex gap-2"
        >
          <Input
            className="flex-1"
            placeholder="Escribe un mensaje"
            value={input}
            onChange={(e) => setInput(e.currentTarget.value)}
            disabled={loading}
          />
          <Button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white flex items-center gap-2 disabled:opacity-50"
          >
            {loading && (
              <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            )}
            <span>Enviar</span>
          </Button>
        </form>
      </Card>
    </div>
  );
}

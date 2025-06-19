import { useState } from "react";
import { Textarea } from "./ui/textarea";
import { Button } from "./ui/button";
import { Card } from "./ui/card";

interface Props {
  onContextConfirmed: () => void;
}

export default function ContextAssistant({ onContextConfirmed }: Props) {
  const [messages, setMessages] = useState<string[]>([]);
  const [input, setInput] = useState("");
  const [confirmed, setConfirmed] = useState(false);

  // Avanza al siguiente paso cuando el usuario aprueba el contexto
  function goToNextStep() {
    onContextConfirmed();
  }

  function send() {
    if (!input) return;
    const userText = input;
    setMessages((m) => [...m, `Tú: ${userText}`]);
    setInput("");

    // TODO: conectar con backend para obtener respuesta
    if (!confirmed) {
      const botProposal = "Propuesta de estructura generada. Responde \"ok\" para continuar.";
      setMessages((m) => [...m, botProposal]);
      if (/^(ok|adelante|de acuerdo|si|sí)$/i.test(userText.trim())) {
        setConfirmed(true);
        goToNextStep();
      }
    } else {
      // Additional conversation if needed
    }
  }

  return (
    <Card>
      <div className="flex flex-col gap-4">
        <div className="h-64 overflow-y-auto space-y-2">
          {messages.map((m, i) => (
            <div key={i} className="text-sm">
              {m}
            </div>
          ))}
        </div>
        <Textarea
          placeholder="Escribe aquí..."
          value={input}
          onChange={(e) => setInput(e.currentTarget.value)}
        />
        <Button onClick={send} className="self-end">
          Enviar
        </Button>
      </div>
    </Card>
  );
}

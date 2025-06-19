import { useState } from "react";
import { Tabs } from "./ui/tabs";
import { Textarea } from "./ui/textarea";
import { Button } from "./ui/button";
import { Card } from "./ui/card";

interface Props {
  onEditConfirmed: () => void;
}

export default function InteractiveEditor({ onEditConfirmed }: Props) {
  const [sections, setSections] = useState([
    { label: "Introducción", text: "" },
    { label: "Desarrollo", text: "" },
    { label: "Conclusión", text: "" },
  ]);

  const tabs = sections.map((s, idx) => ({
    label: s.label,
    content: (
      <Textarea
        value={s.text}
        onChange={(e) => {
          const t = e.currentTarget.value;
          setSections((prev) => {
            const copy = [...prev];
            copy[idx] = { ...copy[idx], text: t };
            return copy;
          });
        }}
      />
    ),
  }));

  function save() {
    // TODO: guardar en backend
  }

  function regenerate() {
    // TODO: llamar a backend para regenerar
  }

  // Se ejecuta cuando el usuario decide exportar
  function goToNextStep() {
    onEditConfirmed();
  }

  return (
    <Card>
      <div className="space-y-4">
        <Tabs tabs={tabs} />
        <div className="flex gap-2 justify-end">
          <Button onClick={regenerate}>Regenerar</Button>
          <Button onClick={save}>Guardar</Button>
          <Button onClick={goToNextStep}>Ir a exportar</Button>
        </div>
      </div>
    </Card>
  );
}

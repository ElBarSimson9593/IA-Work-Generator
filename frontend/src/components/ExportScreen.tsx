import { useState } from "react";
import { Card } from "./ui/card";
import { Select } from "./ui/select";
import { Button } from "./ui/button";
import { AlertDialog } from "./ui/alert-dialog";

interface Props {
  onExported: () => void;
}

export default function ExportScreen({ onExported }: Props) {
  const [format, setFormat] = useState("docx");
  const [success, setSuccess] = useState(false);

  // Avanza al finalizar la exportación
  function goToNextStep() {
    onExported();
  }

  function exportar() {
    // TODO: llamar backend
    setSuccess(true);
  }

  return (
    <Card>
      <div className="space-y-4">
        <div>
          <label className="mr-2">Formato:</label>
          <Select value={format} onChange={(e) => setFormat(e.currentTarget.value)}>
            <option value="docx">DOCX</option>
            <option value="pdf">PDF</option>
          </Select>
        </div>
        <Button onClick={exportar}>Exportar informe</Button>
        {success && (
          <AlertDialog open onClose={() => { setSuccess(false); goToNextStep(); }}>
            <p>Exportación exitosa</p>
          </AlertDialog>
        )}
      </div>
    </Card>
  );
}

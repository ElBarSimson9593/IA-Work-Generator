import { useEffect, useState } from "react";
import { Select } from "./ui/select";
import { request } from "../request";

export default function Settings() {
  const [lang, setLang] = useState("es");
  const [msg, setMsg] = useState("");

  useEffect(() => {
    const stored = localStorage.getItem("idioma");
    if (stored) setLang(stored);
  }, []);

  async function change(value: string) {
    setLang(value);
    localStorage.setItem("idioma", value);
    try {
      await request("/config/idioma", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ idioma: value }),
      });
      setMsg(value === "es" ? "Idioma cambiado a Español" : "Language switched to English");
    } catch {
      setMsg("Error");
    }
  }

  return (
    <div className="p-4 space-y-4">
      <div>
        <label className="block mb-1 font-medium">Idioma</label>
        <Select value={lang} onChange={(e) => change(e.currentTarget.value)}>
          <option value="es">Español</option>
          <option value="en">English</option>
        </Select>
      </div>
      {msg && <div className="text-sm text-green-600">{msg}</div>}
    </div>
  );
}

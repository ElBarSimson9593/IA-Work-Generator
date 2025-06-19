import { useEffect, useState } from "react";

interface HistItem {
  id: string;
  tema: string;
  tipo: string;
  timestamp: string;
}

interface Props {
  onSelect: (id: string) => void;
}

export default function Historial({ onSelect }: Props) {
  const [items, setItems] = useState<HistItem[]>([]);
  const [query, setQuery] = useState("");

  useEffect(() => {
    cargar();
  }, []);

  async function cargar() {
    const resp = await fetch("http://127.0.0.1:8000/historial");
    if (resp.ok) setItems(await resp.json());
  }

  async function buscar(e: React.FormEvent) {
    e.preventDefault();
    if (!query) return cargar();
    const resp = await fetch("http://127.0.0.1:8000/buscar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    if (resp.ok) setItems(await resp.json());
  }

  async function eliminar(id: string) {
    await fetch(`http://127.0.0.1:8000/historial/${id}`, { method: "DELETE" });
    setItems((prev) => prev.filter((i) => i.id !== id));
  }

  return (
    <div className="w-full max-w-md">
      <form className="flex mb-2" onSubmit={buscar}>
        <input
          className="flex-1 border rounded p-2"
          placeholder="Buscar..."
          value={query}
          onChange={(e) => setQuery(e.currentTarget.value)}
        />
        <button className="ml-2 bg-blue-600 text-white px-4 rounded" type="submit">
          Buscar
        </button>
      </form>
      <ul>
        {items.map((it) => (
          <li key={it.id} className="border-b p-2 flex justify-between">
            <div className="flex-1 cursor-pointer" onClick={() => onSelect(it.id)}>
              <div className="font-semibold">{it.tema}</div>
              <div className="text-sm text-gray-500">
                {it.tipo} - {new Date(it.timestamp).toLocaleString()}
              </div>
            </div>
            <button className="text-red-600 text-sm" onClick={() => eliminar(it.id)}>
              Eliminar
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

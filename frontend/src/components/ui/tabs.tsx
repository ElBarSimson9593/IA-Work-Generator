import { ReactNode, useState } from "react";

interface Tab {
  label: string;
  content: ReactNode;
}

interface TabsProps {
  tabs: Tab[];
}

export function Tabs({ tabs }: TabsProps) {
  const [active, setActive] = useState(0);
  return (
    <div>
      <div className="flex gap-2 mb-4">
        {tabs.map((t, i) => (
          <button
            key={i}
            className={`px-4 py-2 rounded-2xl shadow-md ${
              i === active ? "bg-gray-200" : "bg-white"
            }`}
            onClick={() => setActive(i)}
          >
            {t.label}
          </button>
        ))}
      </div>
      <div>{tabs[active]?.content}</div>
    </div>
  );
}

import { ReactNode, useState } from "react";

interface DropdownProps {
  label: ReactNode;
  items: { label: string; onSelect: () => void }[];
}

export function Dropdown({ label, items }: DropdownProps) {
  const [open, setOpen] = useState(false);
  return (
    <div className="relative inline-block" onBlur={() => setOpen(false)} tabIndex={0}>
      <div onClick={() => setOpen((o) => !o)}>{label}</div>
      {open && (
        <div className="absolute mt-2 bg-white shadow-md rounded-2xl p-2">
          {items.map((item, i) => (
            <div
              key={i}
              className="px-4 py-2 hover:bg-gray-100 rounded-2xl cursor-pointer"
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => {
                setOpen(false);
                item.onSelect();
              }}
            >
              {item.label}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

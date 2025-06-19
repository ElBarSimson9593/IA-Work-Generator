import { SelectHTMLAttributes } from "react";

export function Select({ className = '', ...props }: SelectHTMLAttributes<HTMLSelectElement>) {
  return <select className={`rounded-2xl p-2 shadow-md border ${className}`} {...props} />;
}

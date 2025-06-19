import { HTMLAttributes } from "react";

export function Card({ className = '', ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={`rounded-2xl p-4 shadow-md bg-white ${className}`} {...props} />;
}

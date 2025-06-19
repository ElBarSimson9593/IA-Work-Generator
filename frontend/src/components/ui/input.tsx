import { InputHTMLAttributes } from "react";

export function Input({ className = '', ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={`rounded-2xl border p-2 shadow-sm bg-background text-foreground ${className}`}
      {...props}
    />
  );
}

import { ButtonHTMLAttributes } from "react";

export function Button({ className = '', ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={`rounded-2xl px-4 py-2 shadow-md ${className}`}
      {...props}
    />
  );
}

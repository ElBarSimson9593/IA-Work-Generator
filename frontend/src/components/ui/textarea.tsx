import { TextareaHTMLAttributes } from "react";

export function Textarea({ className = '', ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      className={`rounded-2xl p-4 shadow-md border w-full ${className}`}
      {...props}
    />
  );
}

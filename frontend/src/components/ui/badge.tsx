import { HTMLAttributes } from "react";

export function Badge({ className = '', ...props }: HTMLAttributes<HTMLSpanElement>) {
  return (
    <span className={`px-2 py-1 rounded-2xl text-xs shadow-md ${className}`} {...props} />
  );
}

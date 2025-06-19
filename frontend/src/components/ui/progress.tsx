import { HTMLAttributes } from "react";

interface ProgressProps extends HTMLAttributes<HTMLDivElement> {
  value: number;
}

export function Progress({ value, className = '', ...props }: ProgressProps) {
  return (
    <div className={`w-full bg-gray-200 rounded-2xl h-4 ${className}`} {...props}>
      <div
        className="bg-gray-500 h-4 rounded-2xl"
        style={{ width: `${value}%` }}
      />
    </div>
  );
}

import { HTMLAttributes } from "react";

export function Table({ className = '', ...props }: HTMLAttributes<HTMLTableElement>) {
  return <table className={`min-w-full border rounded-2xl shadow-md ${className}`} {...props} />;
}

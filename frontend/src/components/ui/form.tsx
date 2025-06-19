import { FormHTMLAttributes } from "react";

export function Form({ className = '', ...props }: FormHTMLAttributes<HTMLFormElement>) {
  return <form className={`space-y-4 ${className}`} {...props} />;
}

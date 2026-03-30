import type { ReactNode } from "react";

export function FieldLabel({
  htmlFor,
  children,
}: {
  htmlFor: string;
  children: ReactNode;
}) {
  return (
    <label htmlFor={htmlFor} className="text-sm font-medium text-slate-900">
      {children}
    </label>
  );
}


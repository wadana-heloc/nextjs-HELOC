import type { ReactNode } from "react";

export function HelpText({ children }: { children: ReactNode }) {
  return <p className="mt-1 text-xs text-slate-600">{children}</p>;
}


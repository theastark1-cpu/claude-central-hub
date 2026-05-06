import type { ReactNode } from "react";

interface Props {
  eyebrow: string;
  title: string;
  subtitle?: string;
  right?: ReactNode;
  children: ReactNode;
}

export const Section = ({ eyebrow, title, subtitle, right, children }: Props) => (
  <section className="px-6 lg:px-10 py-8 border-t border-border">
    <header className="flex items-end justify-between mb-6">
      <div>
        <div className="text-[10px] uppercase tracking-[0.24em] text-accent/80 mb-2">
          {eyebrow}
        </div>
        <h2 className="text-2xl font-semibold tracking-tight">{title}</h2>
        {subtitle ? <p className="text-sm text-muted mt-1 max-w-2xl">{subtitle}</p> : null}
      </div>
      {right ? <div>{right}</div> : null}
    </header>
    {children}
  </section>
);

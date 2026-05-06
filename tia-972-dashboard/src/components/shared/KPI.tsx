interface Props {
  label: string;
  value: string;
  hint?: string;
  tone?: "neutral" | "profit" | "loss" | "accent";
}
const toneCls: Record<NonNullable<Props["tone"]>, string> = {
  neutral: "text-fg",
  profit: "text-profit",
  loss: "text-loss",
  accent: "text-accent",
};
export const KPI = ({ label, value, hint, tone = "neutral" }: Props) => (
  <div className="flex flex-col gap-1">
    <div className="text-[10px] uppercase tracking-[0.18em] text-muted">{label}</div>
    <div className={`mono text-2xl font-semibold leading-none ${toneCls[tone]}`}>{value}</div>
    {hint ? <div className="text-[11px] text-muted">{hint}</div> : null}
  </div>
);

export const fmtPct = (v: number | null | undefined, digits = 2): string => {
  if (v == null || Number.isNaN(v)) return "—";
  const sign = v > 0 ? "+" : "";
  return `${sign}${v.toFixed(digits)}%`;
};

export const fmtPctNoSign = (v: number | null | undefined, digits = 2): string => {
  if (v == null || Number.isNaN(v)) return "—";
  return `${v.toFixed(digits)}%`;
};

export const fmtPips = (v: number | null | undefined): string => {
  if (v == null || Number.isNaN(v)) return "—";
  return v.toFixed(1);
};

export const fmtNum = (v: number | null | undefined, digits = 0): string => {
  if (v == null || Number.isNaN(v)) return "—";
  return v.toLocaleString(undefined, { minimumFractionDigits: digits, maximumFractionDigits: digits });
};

export const prettySymbol = (sym: string) => sym.replace(/X$/, "").replace(/^(...)/, "$1/");

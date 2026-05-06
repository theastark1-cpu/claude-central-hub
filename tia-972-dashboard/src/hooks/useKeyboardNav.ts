import { useEffect } from "react";
import { useDashboard } from "@/store/dashboard";
import type { StrategyData } from "@/types";

export const useKeyboardNav = (data: StrategyData | null) => {
  const { selectedPair, setSelectedPair, toggleView } = useDashboard();
  useEffect(() => {
    if (!data) return;
    const handler = (e: KeyboardEvent) => {
      const symbols = data.pairs.map((p) => p.symbol);
      const idx = symbols.indexOf(selectedPair);
      if (e.key === "ArrowRight" || e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedPair(symbols[(idx + 1) % symbols.length]);
      } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedPair(symbols[(idx - 1 + symbols.length) % symbols.length]);
      } else if (e.key === " ") {
        e.preventDefault();
        toggleView();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [data, selectedPair, setSelectedPair, toggleView]);
};

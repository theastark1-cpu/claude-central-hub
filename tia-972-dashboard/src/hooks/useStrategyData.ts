import { useEffect, useState } from "react";
import type { StrategyData } from "@/types";

export const useStrategyData = () => {
  const [data, setData] = useState<StrategyData | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}data/strategy.json`)
      .then((r) => {
        if (!r.ok) throw new Error(`strategy.json ${r.status}`);
        return r.json();
      })
      .then((d: StrategyData) => setData(d))
      .catch((e) => setError(String(e)));
  }, []);
  return { data, error };
};

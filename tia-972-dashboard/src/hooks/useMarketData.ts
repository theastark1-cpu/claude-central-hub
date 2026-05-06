import { useEffect, useState } from "react";
import type { MarketData } from "@/types";

const cache: Record<string, MarketData> = {};

export const useMarketData = (symbol: string | null) => {
  const [data, setData] = useState<MarketData | null>(symbol ? cache[symbol] ?? null : null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!symbol) return;
    if (cache[symbol]) {
      setData(cache[symbol]);
      return;
    }
    setLoading(true);
    fetch(`/data/market/${symbol}.json`)
      .then((r) => r.json())
      .then((d: MarketData) => {
        cache[symbol] = d;
        setData(d);
      })
      .finally(() => setLoading(false));
  }, [symbol]);

  return { data, loading };
};

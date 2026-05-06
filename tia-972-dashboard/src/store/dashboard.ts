import { create } from "zustand";
import type { ViewMode } from "@/types";

interface ReplayState {
  pair: string;
  year: number;
}

interface DashboardState {
  selectedPair: string;
  selectedYear: number;
  viewMode: ViewMode;
  replay: ReplayState | null;
  setSelectedPair: (s: string) => void;
  setSelectedYear: (y: number) => void;
  toggleView: () => void;
  setView: (v: ViewMode) => void;
  triggerReplay: (pair: string, year: number) => void;
  clearReplay: () => void;
}

export const useDashboard = create<DashboardState>((set) => ({
  selectedPair: "EURUSDX",
  selectedYear: 2024,
  viewMode: "strategy",
  replay: null,
  setSelectedPair: (s) => set({ selectedPair: s }),
  setSelectedYear: (y) => set({ selectedYear: y }),
  toggleView: () =>
    set((st) => ({ viewMode: st.viewMode === "strategy" ? "market" : "strategy" })),
  setView: (v) => set({ viewMode: v }),
  triggerReplay: (pair, year) => set({ replay: { pair, year }, selectedPair: pair, selectedYear: year }),
  clearReplay: () => set({ replay: null }),
}));

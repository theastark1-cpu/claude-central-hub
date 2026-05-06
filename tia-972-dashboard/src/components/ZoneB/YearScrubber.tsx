import { useDashboard } from "@/store/dashboard";

const YEARS = [2020, 2021, 2022, 2023, 2024, 2025];

export const YearScrubber = () => {
  const { selectedYear, setSelectedYear } = useDashboard();
  return (
    <div className="flex flex-col gap-2 w-full">
      <input
        type="range"
        min={2020}
        max={2025}
        step={1}
        value={selectedYear}
        onChange={(e) => setSelectedYear(parseInt(e.target.value, 10))}
        className="w-full accent-accent"
      />
      <div className="flex justify-between mono text-[10px] text-muted">
        {YEARS.map((y) => (
          <button
            key={y}
            onClick={() => setSelectedYear(y)}
            className={`px-1.5 py-0.5 rounded ${selectedYear === y ? "text-accent bg-accent/10" : "hover:text-fg"}`}
          >
            {y}
          </button>
        ))}
      </div>
    </div>
  );
};

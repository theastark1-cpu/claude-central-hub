/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      colors: {
        base: "#0a0a0f",
        panel: "#12121a",
        panel2: "#16161f",
        fg: "#e8e9ee",
        muted: "#576574",
        border: "rgba(255,255,255,0.08)",
        profit: "#00d084",
        loss: "#ff4757",
        accent: "#feca57",
        gridline: "rgba(255,255,255,0.10)",
      },
      backgroundImage: {
        base: "radial-gradient(ellipse at top, #12121a 0%, #0a0a0f 70%)",
      },
      boxShadow: {
        card: "0 1px 0 rgba(255,255,255,0.04) inset, 0 8px 30px rgba(0,0,0,0.4)",
        glow: "0 0 0 1px rgba(254,202,87,0.4), 0 0 40px rgba(254,202,87,0.15)",
      },
    },
  },
  plugins: [],
};

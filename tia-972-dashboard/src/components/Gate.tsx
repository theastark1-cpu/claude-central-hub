import { useEffect, useRef, useState } from "react";

const PW_HASH = "687d4a28291ace6fe39dd464374c4098dfb84f8b1edf9b7c828e73319597bfbb";
const STORAGE_KEY = "tia972_auth";

const sha256 = async (s: string): Promise<string> => {
  const buf = new TextEncoder().encode(s);
  const digest = await crypto.subtle.digest("SHA-256", buf);
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
};

export const Gate = ({ children }: { children: React.ReactNode }) => {
  const [unlocked, setUnlocked] = useState<boolean>(
    () => typeof sessionStorage !== "undefined" && sessionStorage.getItem(STORAGE_KEY) === "1",
  );
  const [error, setError] = useState(false);
  const [busy, setBusy] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!unlocked) inputRef.current?.focus();
  }, [unlocked]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputRef.current) return;
    setBusy(true);
    const hash = await sha256(inputRef.current.value);
    setBusy(false);
    if (hash === PW_HASH) {
      sessionStorage.setItem(STORAGE_KEY, "1");
      setUnlocked(true);
    } else {
      setError(true);
      inputRef.current.value = "";
      inputRef.current.focus();
      setTimeout(() => setError(false), 1800);
    }
  };

  if (unlocked) return <>{children}</>;

  return (
    <div className="min-h-screen flex items-center justify-center px-6">
      <div className="w-full max-w-sm">
        <div className="text-[10px] uppercase tracking-[0.32em] text-muted mono mb-3">
          Restricted · Walk-Forward Validation
        </div>
        <h1 className="text-3xl font-semibold tracking-tight mb-1">
          <span className="mono text-accent">TIA-9.72</span>
        </h1>
        <p className="text-sm text-muted mb-8">
          Enter passphrase to view the analytics terminal.
        </p>
        <form onSubmit={submit} className="flex flex-col gap-3">
          <input
            ref={inputRef}
            type="password"
            autoComplete="off"
            spellCheck={false}
            placeholder="passphrase"
            className={`mono w-full bg-panel border rounded-lg px-4 py-3 text-base tracking-wider focus:outline-none transition-colors ${
              error ? "border-loss" : "border-border focus:border-accent"
            }`}
          />
          <button
            type="submit"
            disabled={busy}
            className="mono uppercase tracking-[0.18em] text-xs bg-accent text-base hover:bg-accent/90 disabled:opacity-50 px-4 py-3 rounded-lg font-semibold transition-colors"
          >
            {busy ? "Verifying…" : "Unlock"}
          </button>
          {error && (
            <div className="mono text-xs text-loss text-center mt-1">
              Incorrect passphrase.
            </div>
          )}
        </form>
        <div className="mt-10 text-[10px] mono text-muted/60 text-center">
          Session stored locally · clears on tab close
        </div>
      </div>
    </div>
  );
};

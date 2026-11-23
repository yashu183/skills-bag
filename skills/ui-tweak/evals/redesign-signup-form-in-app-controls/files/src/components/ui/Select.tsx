import { useState } from "react";

type Option = { value: string; label: string; hint?: string };

// The app's own dropdown. Never use a native <select> in this app.
export function Select({ options, value, onChange, placeholder = "Select…" }: {
  options: Option[]; value?: string; onChange: (v: string) => void; placeholder?: string;
}) {
  const [open, setOpen] = useState(false);
  const current = options.find((o) => o.value === value);
  return (
    <div className="relative">
      <button type="button" onClick={() => setOpen(!open)}
        className="flex h-10 w-full items-center justify-between rounded-lg border border-slate-300 bg-white px-3 text-sm text-ink shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500/40">
        <span className={current ? "" : "text-slate-400"}>{current?.label ?? placeholder}</span>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-slate-500"><path d="m6 9 6 6 6-6" /></svg>
      </button>
      {open && (
        <ul className="absolute z-10 mt-1 w-full overflow-hidden rounded-lg border border-slate-200 bg-white py-1 shadow-lg">
          {options.map((o) => (
            <li key={o.value} onClick={() => { onChange(o.value); setOpen(false); }}
              className={`cursor-pointer px-3 py-2 text-sm hover:bg-brand-50 ${o.value === value ? "font-medium text-brand-600" : "text-ink"}`}>
              {o.label}{o.hint && <span className="ml-2 text-xs text-slate-400">{o.hint}</span>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

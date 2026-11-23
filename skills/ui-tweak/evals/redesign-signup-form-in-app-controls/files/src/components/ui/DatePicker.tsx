import { useState } from "react";

// The app's own calendar popover. Never use <input type="date"> in this app.
export function DatePicker({ value, onChange }: { value?: Date; onChange: (d: Date) => void }) {
  const [open, setOpen] = useState(false);
  const [month, setMonth] = useState(value ?? new Date());
  const days = new Date(month.getFullYear(), month.getMonth() + 1, 0).getDate();
  return (
    <div className="relative">
      <button type="button" onClick={() => setOpen(!open)}
        className="flex h-10 w-full items-center gap-2 rounded-lg border border-slate-300 bg-white px-3 text-sm text-ink shadow-sm">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-slate-500"><rect x="3" y="4" width="18" height="18" rx="2" /><path d="M16 2v4M8 2v4M3 10h18" /></svg>
        {value ? value.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" }) : <span className="text-slate-400">Pick a date</span>}
      </button>
      {open && (
        <div className="absolute z-10 mt-1 w-72 rounded-card border border-slate-200 bg-white p-3 shadow-lg">
          <div className="mb-2 flex items-center justify-between text-sm font-medium text-ink">
            <button onClick={() => setMonth(new Date(month.getFullYear(), month.getMonth() - 1))} className="rounded-md px-2 hover:bg-slate-100">‹</button>
            {month.toLocaleDateString("en-GB", { month: "long", year: "numeric" })}
            <button onClick={() => setMonth(new Date(month.getFullYear(), month.getMonth() + 1))} className="rounded-md px-2 hover:bg-slate-100">›</button>
          </div>
          <div className="grid grid-cols-7 gap-1 text-center text-sm">
            {Array.from({ length: days }, (_, i) => i + 1).map((d) => (
              <button key={d} onClick={() => { onChange(new Date(month.getFullYear(), month.getMonth(), d)); setOpen(false); }}
                className={`h-8 rounded-md hover:bg-brand-50 ${value?.getDate() === d ? "bg-brand-500 text-white hover:bg-brand-600" : "text-ink"}`}>{d}</button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

import { useState } from "react";
import { Select } from "./components/ui/Select";
import { DatePicker } from "./components/ui/DatePicker";

const plans = [
  { value: "starter", label: "Starter", hint: "$9/mo" },
  { value: "team", label: "Team", hint: "$29/mo" },
  { value: "scale", label: "Scale", hint: "$99/mo" },
];

export default function SignupForm() {
  const [plan, setPlan] = useState<string>();
  const [start, setStart] = useState<Date>();
  return (
    <form className="mx-auto max-w-md space-y-4 p-8">
      <h2 className="text-xl font-semibold text-ink">Start your free trial</h2>
      <label className="block text-sm text-slate-600">Work email
        <input className="mt-1 h-10 w-full rounded-lg border border-slate-300 px-3 text-sm" placeholder="you@company.com" />
      </label>
      <label className="block text-sm text-slate-600">Company name
        <input className="mt-1 h-10 w-full rounded-lg border border-slate-300 px-3 text-sm" />
      </label>
      <div className="text-sm text-slate-600">Plan<div className="mt-1"><Select options={plans} value={plan} onChange={setPlan} /></div></div>
      <div className="text-sm text-slate-600">Trial start date<div className="mt-1"><DatePicker value={start} onChange={setStart} /></div></div>
      <button className="h-10 w-full rounded-md bg-brand-500 text-sm font-medium text-white hover:bg-brand-600">Create account</button>
    </form>
  );
}

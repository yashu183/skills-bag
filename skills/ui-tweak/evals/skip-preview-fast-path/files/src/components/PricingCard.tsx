type Props = { name: string; price: number; features: string[]; popular?: boolean };

export function PricingCard({ name, price, features, popular }: Props) {
  return (
    <div className="relative rounded-card border border-slate-200 bg-white p-6 shadow-sm">
      {popular && (
        <span className="absolute -top-3 right-4 rounded-full bg-brand-500 px-3 py-1 text-xs font-semibold text-white">
          Popular
        </span>
      )}
      <h3 className="text-lg font-semibold text-ink">{name}</h3>
      <p className="mt-2 text-3xl font-bold text-ink">
        ${price}<span className="text-sm font-normal text-slate-500">/mo</span>
      </p>
      <ul className="mt-4 space-y-2 text-sm text-slate-600">
        {features.map((f) => (
          <li key={f}>✓ {f}</li>
        ))}
      </ul>
      <button className="mt-6 rounded-md bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600">
        Get started
      </button>
    </div>
  );
}

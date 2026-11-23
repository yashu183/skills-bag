import { PricingCard } from "./components/PricingCard";

export default function Pricing() {
  return (
    <section className="mx-auto grid max-w-5xl gap-6 px-4 py-16 md:grid-cols-3">
      <PricingCard name="Starter" price={9} features={["1 project", "Email support"]} />
      <PricingCard name="Team" price={29} features={["10 projects", "Priority support", "SSO"]} popular />
      <PricingCard name="Scale" price={99} features={["Unlimited projects", "Dedicated CSM", "SSO", "Audit log"]} />
    </section>
  );
}

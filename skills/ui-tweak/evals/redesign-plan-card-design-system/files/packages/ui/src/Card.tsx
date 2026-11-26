import "./card.css";

export function Card({ children }: { children: React.ReactNode }) {
  return <section className="acme-card">{children}</section>;
}

import { Button, Card } from "@acme/ui";

export function PlanCard() {
  return (
    <Card>
      <h2 style={{ fontSize: "var(--text-lg)", margin: 0 }}>Pro plan</h2>
      <p style={{ color: "var(--color-text-muted)" }}>$24 per month, billed yearly</p>
      <p>Unlimited projects, 50 GB storage, priority support.</p>
      <Button variant="primary">Upgrade</Button>
      <Button variant="primary">Compare plans</Button>
    </Card>
  );
}

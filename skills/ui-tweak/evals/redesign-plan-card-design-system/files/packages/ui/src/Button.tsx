import "./button.css";

type Props = { variant?: "primary" | "secondary" | "ghost"; size?: "sm" | "md"; children: React.ReactNode };

export function Button({ variant = "primary", size = "md", children }: Props) {
  return <button className={`acme-btn acme-btn--${variant} acme-btn--${size}`}>{children}</button>;
}

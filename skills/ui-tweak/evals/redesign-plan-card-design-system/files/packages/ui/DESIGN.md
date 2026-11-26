# Acme UI

Rules:
- One primary Button per view. Secondary actions use `variant="secondary"` or `variant="ghost"`.
- Spacing comes from the --space-* scale only. No one-off margins.
- Group related content in a Card. Cards use --radius-lg; nothing else in the app uses a larger radius.
- --color-accent is for highlights (badges, the selected state), never for body text.
- Body text is --text-md (16px); --text-sm (14px) is for secondary text only.

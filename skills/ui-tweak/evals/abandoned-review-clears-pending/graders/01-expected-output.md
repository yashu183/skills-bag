---
type: llm
focus: trace
weight: 1
---

Score this as a test of the ui-tweak skill's "review ends without approval" rule. The prompt invokes /ui-tweak, which loads the skill's instructions straight into the prompt, so the trace has no Skill tool call; don't require one. What shows the skill was followed is the behavior below: deleting `.ui-tweak/pending` is something only the skill asks for, and an agent without the skill leaves it in place.

All of these must hold:
1. .ui-tweak/pending no longer exists at the end. It is deleted before src/Pricing.tsx is edited.
2. .ui-tweak/pricing-cta/v1.html still exists, and no new .ui-tweak/**/*.html is created.
3. src/components/PricingCard.tsx is unchanged (the dropped restyle is not implemented).
4. In src/Pricing.tsx the Team card's price is 35 and the Scale card's features include "API access". Nothing else changes.
5. The agent tells the user, in its reply, that the mock review is closed and the mock files are kept.

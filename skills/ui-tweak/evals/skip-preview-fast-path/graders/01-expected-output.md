---
type: llm
focus: trace
weight: 1
---

Score this as a test of the ui-tweak skill's fast path, not of editing in general. A correct source edit alone is not enough. The prompt invokes /ui-tweak, which loads the skill's instructions straight into the prompt, so the trace has no Skill tool call; don't require one. What shows the skill was followed is the behavior below: deleting `.ui-tweak/pending` is something only the skill asks for, and an agent without the skill leaves it in place.

All of these must hold:
1. No new mock is built: no .ui-tweak/pricing-cta/v2.html and no other new .ui-tweak/**/*.html. The existing .ui-tweak/pricing-cta/v1.html is still there.
2. The leftover review flag .ui-tweak/pending is deleted, and the deletion happens before src/components/PricingCard.tsx is edited. (Only the skill's instructions ask for this; an agent without the skill leaves it in place.)
3. In src/components/PricingCard.tsx the Get started button's rounded-md is replaced by rounded-full and w-full is added. Nothing else in the file or in src/ changes.
4. The repo's own .gitignore is not created or modified.

# Quran House — Change Policy

This file controls how implementation changes are introduced while working with GPT, Spark, and other agents.

## Rules

1. Do not expand scope silently.
2. Do not change established architecture without explaining why first.
3. Do not add a dependency without stating its purpose and trade-offs.
4. Do not replace working behavior merely for stylistic preference.
5. Changes affecting multiple components must be reported before implementation when practical.
6. Existing working behavior must be regression-checked after meaningful changes.
7. Never claim a feature is complete without evidence.
8. Keep secrets, API keys, tokens, and private credentials out of source and project memory.
9. Prefer the smallest change that satisfies the current milestone.
10. If implementation evidence contradicts a planning document, update the planning document rather than pretending the old plan is still accurate.

## Agent Rule

Agents may implement bounded tasks. They must not independently redefine the product, introduce major architectural scope, or turn a local task into a broad refactor without explicit agreement.

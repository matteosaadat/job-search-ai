---
atom_id: atom_contracts_003
domain: contracts
group: scoring_model
confidence: high
sources:
  - chunk_id: chunk_20260529_directChat
    date: 2026-05-29
created: 2026-05-29
last_updated: 2026-05-29
---

Employment type preference and schedule preference are independent dimensions that multiply: final score = type_multiplier × schedule_multiplier × 100. Results: contract 3d/wk = 100, contract 5d/wk = 80, employed 3d/wk = 80, employed 5d/wk = 64. When days/week are not stated, infer from contract type: full-time → 5 days, part-time/fractional → 3 days, contract → 5 days (conservative default).

# Broad 1-1 discovery sweep: failures remain open

All 37 selectable identities now have at least one controller-only 1-1 attempt
in each mode: 74 identity/mode pairs. This is attempt coverage, not a passing
roster matrix. Across the explicitly recorded OE and injury-fix hashes, 36 pairs
have a clean discovery and 28 have an independent exact input/trace replay.
Earlier-hash clears do not certify the final ROM.

The complete receipts, policies, inputs, traces, screenshots and failed runs
are retained at
`C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-full-routes-of`.
`coverage-v1.json` lists every identity/mode, each attempt's exact ROM hash and
its distinction between discovery and replay. Fixed MM/Proto receipts live in
the separately named `2026-10-24-proto-hurt-of/fix-v8` evidence directory.

The runner extends only the existing ND profile/name tables to cover the legacy
characters. Its legacy graphics observer follows the real logical CHR map or
an explicit physical page, then compares matching actual DMA player parts.
It does not assume that Mario uses Samus's pose pointer or that Samus uses an
expanded direct page. The initial incompatible harness failures are retained
in `original-pilot-v1`; they are not labeled game defects.

The common discovery controller is not a skilled universal player. Deaths,
timeouts and ledge stalls require inspecting the actual scene before changing
the game. No collision, jumping or enemy rule has been weakened to make a
failed controller pass. The failed runs are useful starting points for the
remaining character-specific navigation and terrain/ability investigation.

Two genuine faults were separated from those route failures: the Little Mac
HUD-boundary sideways jump, now repaired in OE, and the MM/Proto recovery page
swap, addressed by the injury-page candidate. Their native reproductions and
strict passing bounds remain separate from the full roster gate.

Next work remains:

- Investigate the 38 identity/mode pairs without a clean discovery, using
  existing character-specific policies and source moves before changing physics.
- Finish independent replays and inspect the complete relevant scenes; sampled
  overviews alone are not exhaustive frame-by-frame human review.
- Investigate partial bodies, sprite overload, major lag, block publication,
  ability gaps and source audio rather than treating a level clear as fidelity.
- Extract and exercise every applicable item, weapon, form and special attack
  for every identity, with real emergence/pickup/use and damage/expiry evidence.
- Complete the oversized MMC3 integration and rerun the required final matrix
  on both completed mapper builds.

Later OG investigation reproduced Sophia's apparent Easy timeout as a real
audio-NMI stack overflow, repaired the deep inventory predicate, and produced
fresh exact guarded Easy/Hard Sophia1-1replays. Its first raw movement failure
was a positively traced temporary projectile block origin rather than a drawn
tank teleport. See `inventory-stack-repair-2026-10-24.md` for exact-hash evidence
and the preserved failed fixtures. Earlier mixed-hash coverage totals do not
become an OG full-roster pass.

The full goal remains active and incomplete. The player guide and published
ROMs have not been relabeled as final by these partial results.

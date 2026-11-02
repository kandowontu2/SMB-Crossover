# Arthur actual weapon-tail admission

Private candidate: `build/arthur-side-clamp-1101-v8/weapon-tail-candidate.nes`,
SHA-256 `d8a87050beefefe96869ebd4d188beeb52733241cd2c0fa64392a55ec8ebca05`.
Its base is the delivered Arthur-maturity/Excitebike counterpart379590:
`37959000690d3f9fe596823fc0910e86b9fc977448779360d523751764248b0c`.
This note is source/CPU qualification; native targeted combat and current
full1-1 remain pending when the packet is prepared.

The real first-enemy negative is retained at
`build/arthur-side-clamp-1101-v8/weapon-ingress/capture/`. It ran1200 physical
frames/700play frames with real menu input and the existing first-enemy stop
near world247. Source lances were active at expected ground screenY190.
347 original lance updates occurred, but no `NrWeapons`, `HuWeapons`,
`ArHostShotContacts`, source shot-contact or native enemy-hit ingress occurred.
The7 original MarkShotHit calls alone are not evidence of enemy hits; the
source also marks shots at terrain. No outcome or shot coordinates were seeded.

Current actual ROM instructions establish the missing route:

1. `ProcFireball_Bubble`, physical0:ADC7..ADD6, forwards to
   `NrObjectWeaponTail`, physical124:AD58.
2. That caller invokes `HuWeaponTail`, physical79:B820, whose public entry
   selects policy34. It then continues with genuine native air bubbles.
3. Arthur policy34 was the default Noop at70:BE2A. The separate public
   `HuWeapons` policy4 already targeted the working Arthur contact worker,
   but normal Main does not use that public entry.

`arthur_weapon_tail_1102_v15.s` changes only Arthur's policy34 target to the
existing policy4 transport at70:BD92. This reaches the unchanged
`ArHostShotContacts`26:BE68, original `ArNativeShotContact`63:DD1A and genuine
native `HandleEnemyFBallCol`126:9A8F. The original air-bubble continuation
remains in place. Starting source weapon64 is the lance; dagger66 is a later
source upgrade. No original source attack, collision rectangle or controller
behavior is changed.

Exact two-byte delta: file580983 `$2A->$92`, file580984 `$BE->$BD`.
The three-byte owning table slot is70:BD66..BD69. No new PRG, CHR, RAM,
veneer, helper or stage grant is needed. Every Excitebike/shared-dispatch byte
and every foreign character's ROM byte is unchanged.

`check_arthur_weapon_tail_1102_v15.py` assembles the table entry, qualifies it
in memory, and emits a candidate only after these checks pass:

- 152 foreign actual `ProcFireball_Bubble` cases preserve complete application
 RAM, WRAM/cache, palette/PPU, mapper, AXYP and live stack.
- 140 cases preserve all35 other Arthur public policy entries.
- 32 genuine source-B shot-spawn/motion cases traverse the actual
 `ProcFireball_Bubble`/tail/contact/native consumer route, across both facings
 and pages. Goombas/Koopas are defeated, Buzzy remains fireproof, and original
 Bowser HP drops5→4. Enemy placements are isolated legal CPU fixtures; shot
 positions and contact results are not seeded.
- 32 IRQ/lag-NMI cuts preserve live stack, SMC, mappings and all private cache
 bytes except the exact predicted original physical-clock mailbox advance at
 DFD0..DFD2. The source clock is required to advance during a Main interruption.

The changed owner path matches an independent in-memory copy of the existing
policy4 transport at the former policy34 transport address. The receipt is
`weapon-tail-CPU.json`; all source, code and base-ROM bindings are recorded.
The natural-B narrow diagnostic predating the repair is
`audit_arthur_weapon_contact_1102_v14.py` / `weapon-contact-CPU.json`.

The native successor retains the exact first-enemy controls and requires a
genuine native enemy hit with no life loss. It adds read-only actual tail
ingress counters; source-contact return carry is observed at the source-bound
caller returnBED4 with matching SP. Shot first/last/range X/Y and active-frame
counts are aggregated, with at most160 detail rows and four PNGs.

```powershell
python tools/audit/run_bounded_build_v1.py --output build/arthur-side-clamp-1101-v8/weapon-tail-native --resume --timeout 180 -- python -B build/arthur-side-clamp-1101-v8/weapon-tail-native/run.py
```

Root owns Mesen, delivery, cleanup and the full-stage controller. Original
full1-1 negatives remain retained; all four pipes and three gaps have been
crossed without helpers, but that is not a current complete stage-clear claim.

## Native delivery

The exact candidate and actual Downloads pass real source-lance/native enemy defeat. The unchanged full1-1 controller now reaches active1-2 in5950physicalframes, lives2to2, allfourpipes/allthreegaps, nohelpers and no sourceinjury. Downloads was replaced without backup; patch guards pass. All other weapons/powerups and full-roster checks remain open.

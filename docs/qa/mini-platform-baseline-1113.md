# Mini Mario: current shared-platform regression baseline

Current Downloads has since advanced to f88. A fresh actual f88 run exactly
reproduces the5279-frame/3495-Main result and the one missed update described
below. Lua b5c66789, receipt42974aad. The private14ae contact candidate also
clears1-1 but records four misses; it remains private. See
`mini-platform-descending-1113.md` for exact hashes and the paired comparison.
The original7ef measurements below remain scoped to their own ROM.

The actual Downloads ROM remains
`7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc`.
No ROM change or delivery is made by this check. This is the baseline for the
proposed DK Jr shared-platform repair, which remains private.

`replay_mini_platform_regression_1113.py` reads the retained final-roster
controller, SHA256
`d20ec6a9c7481b902a5b45033e1a2e4448df4555ba31d4e0981d1a371e920677`.
It authenticates every retained native/loaded hook against current bytes and
rebinds the complete Mini carrier digest. Ordinary inputs, original-source
movement, collision/body/DMA assertions, native end-sequence observations and
the passive native lift-constructor observer remain. Old CSV/JSON writers,
screenshots and instruction/audio profilers are removed. This is not a new
acoustic qualification.

## Actual native result

The final diagnostic controller is
`67e3166de50a065c509e428bb3b8748353416f9ba5b56b3c8a4deae6191b231b`.
Native receipt:
`00247b613fc8abbbbf3f0ad4587bd77fc5fd104a1cac0b97d0718924c9c95503`.
The complete route passes in5,279 physical frames, with3,495 completed Main
and source updates, both lives, all four pipe/three pit obstacles, no wall-jump
restarts, the actual flag/castle transition, and active underground1-2.
The endpoint is X40/Y51 during ordinary entry falling; it does not claim25
grounded1-2 updates.

| Consecutive eligible original1-1 window | Observed |
| --- | ---: |
| Physical frames / completed Main / source updates |3493 /3493 /3493 |
| Frames with input polls |3493 |
| Native skipped-NMI delta |1 |
| Frames with no completed Main/source update |1 |
| Maximum source updates in a physical frame |2 |

The bounded exception observer locates the single missed completion at
frame2838, playerX1585/Y176, PC90BC/SP243, source/Main2182. The next physical
frame completes two updates at X1586 and increments skipped-NMI by1.
This is already present in the public baseline before the DK proposal. It
must not be reported as zero lag or attributed to a future candidate. The
historical c10 zero-lag receipt remains scoped to its own ROM.

All three existing native helpers are born before entering the viewport:

| Stage | Initial left / center | Initial top | Collision width | Actual birth relative X | Boarding / departure physical frames |
| --- | --- | ---: | ---: | ---: | --- |
|1-1 |560 /576 |192 |32 |262 |1290 /1374 |
|1-1 |688 /704 |192 |32 |263 |1769 /1867 |
|1-1 |864 /880 |192 |32 |263 |2210 /2302 |

These are unchanged locations in the helper inventory. The replay observes
real carrying and departure for all three. No helper is constructed by Lua.

## Retained harness diagnostics

The first stdout adaptation accidentally omitted the passive lift-birth
observer on which the unchanged boarding assertion depends. Lua262ed6e3,
receipt71574944, stops at X490 after365/365 eligible updates with zero skipped
NMIs. This is an observer omission, not a game or platform failure.

Restoring that observer leaves inputs and assertions unchanged. Lua86191a0a
passes the complete route, receipt
`668af61d90c7e2ad56d99d68bf46b5fcd1332e101ccce3bbadb78f99b095fdaf`,
and measures the same single missed/catch-up pair. The separate
`--require-zero-lag` postcheck correctly exits1, so that command is not a
zero-lag acceptance. Adding the bounded exception details produces the final
passing diagnostic above. No runtime state or outcome is repaired.

Every run uses the existing bounded `build/metal-flower-native-1112` two-file
root and the root-owned single Mesen queue. The private DK candidate file
stays e73; only the root controller is replaced. Captures and generated
receipt files:0. Nightly auto-patch guard is clear before and after.

The later `contact_candidate=True` factory option accepts only the strict
private composer PIN, reverses it through e73 to exact public7ef, and requires
the Mini carrier to stay byte-identical. The public Lua remains67e3166d.
An in-memory compile on the gap-only privatea3452808 yields Lua9e7040f4;
this is syntax/binding qualification, not a native candidate run. Root has
not staged that ROM. `--contact-candidate` requires root to stage it first.

GitHub releases are now intentionally empty at the user's request. This
verification does not authorize recreating Current or uploading a patch.

## Current12397 actual Downloads regression

Root session20901 reran the retained route on the actual installed
`12397b1c2557834f6a2b7e23c9915d5dc40c6cabff7a6ee844c1adebf6564c52`.
Exact Lua is
`b98e5798b0dfa7b1aca5d89670d8507b0f0bcf9971f148495a2fccf6c594dc38`;
receipt is
`d2b3e4a6acb8dd4b56f4195b3a92b9cf478ffe45a8993cacd8f21e3fe9331fd4`.
It passes5279 physical /3495 Main and source updates,190693 checks, both lives,
all four pipes, three pits and three native helper boardings/departures.
The endpoint remains active entry falling at40/51 in1-2, not25 grounded updates.

The eligible window is exactly3493 physical/Main/source/input-polled frames.
The same missed completion occurs at2838,1585/176, PC90BC/SP243; frame2839
completes two updates and increments skipped-NMI once. This matches the
preceding public baselines and private optimized769afe comparison; it is
not a zero-lag claim. The six SMB2 post-background operand fixes introduce
no measured regression in this route.

All three helpers retain the table above, including offscreen births at
relative262/263/263, initial top192, left560/688/864 and center576/704/880.
Actual board/depart frames are1290/1374,1769/1867 and2210/2302.
No helper, physics or ROM byte changes. The existing two-file metal component
keeps its private769afe candidate; only its controller slot now contains
Mini b98e5798. The actual launch uses Downloads, not that private candidate.
Output and capture files are zero; pre/post nightly sidecar/hash guards pass.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/metal-flower-native-1112 --resume --max-files 2 --timeout 360 -- python -B tools/audit/replay_mini_platform_regression_1113.py
```

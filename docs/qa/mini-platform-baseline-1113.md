# Mini Mario: current shared-platform regression baseline

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

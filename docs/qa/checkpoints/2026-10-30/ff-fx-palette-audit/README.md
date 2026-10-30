Read-only FF FX palette recommendation, exact source cart c1aeff70d438788c1abbe542186c59ac10c5a7bac0f60fd53b0718b44d3d0a79.

The smallest source-faithful next candidate is one borrowed P1, preserving the original effect pattern bytes and remapping effect/sword palette-role2 to P1. Choose one complete color family per displayed epoch, drawing every admitted object of that family. Include an unchanged native-world P1 epoch only when a genuine visible world consumer conflicts. This is a design recommendation, not an implemented or qualified palette scheduler.

| Family | Exact visible NES codes | Legal overlap |
| --- | --- | --- |
| Fire | 16,26,30 | Other Fires; one Bolt or Ice |
| Ice / White light | 12,21,30 | Black Mage Fire; White staff body |
| Bolt | 18,28,30 | Black Mage Fire |
| Fighter / Thief sword | 0C,1C,2C | No legal spell pool for these fixed classes |

All three colors of each family are actually opaque in the source CHR. White's staff is P0 body art, not a separate sword palette. Black has no melee sword. Heal has no projectile. Source CPU inputs demonstrate Fire+Bolt and Fire+Ice at ticks79..85, White light+staff at ticks32..48, and two Fires+Bolt or Ice at ticks94..96 after genuine ground-A cast cancellation. Fixtures provide declared flat-floor contact between updates; these are not campaign replays. Class changes are not allowed during these witnesses.

Non-Fire lifetime controls execute every reachable75ms clock phase: Bolt23..27 logical updates, Ice/White19..23. The next preparation requires30 updates even after cast cancellation, so two non-Fire spells cannot naturally coexist. The original FfEffectPalettePointer's Ice/Bolt rejection is consistent with that timing, rather than evidence that Fire and another spell cannot coexist.

A single P1 can show all matching Fire slots together. With no world conflict it needs one epoch for ordinary single-family scenes and two alternating epochs for Fire+Ice/Bolt. With a visible P1 world consumer, the corresponding cycles need two or three epochs. Suppress whole competing objects and continue all source updates, damage and allocation. Palette fairness cannot repair existing OAM or eight-sprite saturation.

World P1 is not spare: actual unchanged native renderer calls prove green Koopa, Piranha, Bowser and1UP use P1. Fireflower contains both P0 and P1 parts, so hiding just final P1 OAM records would leave half a flower. World P2 is the mushroom/red-enemy/coin/platform/fireball palette [16,30,27], proven through the native queue and actual mushroom/red-Koopa OAM. Preserve it. P3 remains area-dependent: water[0F,30,10], ground[0F,36,17], underground[0C,3C,1C], castle[00,30,10]. Optional FF ink uses index1; its source black0F is exact in water/ground, not underground/castle. Palette slot0 is transparent and cannot supply opaque black. Do not silently call00 or0C black.

Exact lossless masks are color-feasible without relying on red P0:

- Fire16/30 can use existing world P2 indices1/2; Fire26 uses P1 index1.
- Concurrent Ice12/21 can use P1 indices2/3 and white30 uses P2 index2: P1=[26,12,21].
- Concurrent Bolt18/28 can use P1 indices2/3 and white30 uses P2 index2: P1=[26,18,28].
- P0 remains unchanged, including source-class and guest transformation/star phases. Blue Black Mage P0=[28,18,21] supplies some colors in its ordinary phase, but those donors disappear during guest color phases; it is not an unconditional donor.

Every tested opaque source pixel and transparent hole survives the mask model with exactly the same raw NES color. The direct split adds many parts. Full-object coalescing searches all1288x16 grid phases, so the following are improved measurements rather than assuming the direct split is optimal:

| Source frame | Original parts | Coalesced parts at lowest line pressure | Lowest sprites/line | Minimum distinct mask pairs across grids |
| --- | ---: | ---: | ---: | ---: |
| Fire144 | 8 | 10 | 8 | 10 |
| Ice149 | 26 | 34 | 11 | 34 |
| Bolt152 | 35 | 47 | 5 | 35 |
| Bolt154 | 53 | 76 | 6 | 27 |

Ice149 exceeds eight sprites even alone in all these regular-grid candidates. Ice149 and Bolt152 exceed the current one1KB/32-pair object window. Bolt154 has a71-part alternative at seven sprites/line, still above software64 before body/world. A new atlas/window/partial-render producer and fairness policy would be necessary. These measurements do not prove that every conceivable irregular mask layout is impossible. No new pages or windows are assumed. The model changes OAM part geometry, so source/world priority equivalence would also require executable tests.

For optional ink in underground/castle, a donor-color table separately assesses exact P0/P2/P3 availability. Mixed Fire+Ice/Bolt plus black may require four missing P1 colors during some guest phases; one P1 has only three opaque entries. Castle sword plus black likewise lacks a simultaneous exact donor in ordinary body phases. Keep this explicit rather than recoloring or turning opaque pixels transparent. Outlines-off remains the source's optional-ink policy for FF; Arthur's intrinsic ink is a different owner.

Before implementing the minimal scheduler, resolve these real integration obligations:

1. Queue the chosen P1 packet together with matching OAM for the same genuine normal-NMI display epoch. Main/lag/catch-up counts alone are not a display clock. Restore the true area or Bowser P1 on world epochs and on exit.
2. Identify complete admitted native object groups, not merely P1 attribute bytes; mixed fireflower is an actual counterexample.
3. Preserve the P0 player body while gating embedded Fighter/Thief sword color parts. Their optional ink shares body descriptors, so simple attribute filtering does not establish complete sword-object suppression.
4. Keep whole-object/family time fairness separate from source update/attack and independent OAM overload fairness. Share a color epoch across all same-color Fire slots to minimize flicker.

Evidence:

- build/ff-fx-palette-audit-v2/audit.json:632 actual iterator cases,1328 actual chunks, all27 non-Fire lifetime phase cases, legal action traces, exact source palettes/CHR.
- build/ff-fx-mask-feasibility-v2/audit.json:exact pixel masks,1792 coalesced full-object grid models, five native palette queue cases, eight actual native OAM object cases, scheduler design constraints.
- controls.json:additional actual two-Fire+non-Fire witnesses,17 exact source-closure matches, donor-color feasibility cross-product and all input hashes.
- Negative-v1 fixtures are retained. One stationary triple-Fire input had its first Fire correctly culled; the successful left-edge witness is a separate declared fixture. The other negative demonstrates c1aeff's already-known incomplete selected22 world-palette donor route; the positive original-world proof uses genuine native Mario routing. Root's later body/world palette packet is a separate successor.

No source cart, frozen/root FF file, shared menu, native process, ROM install, RAM or CHR lease was changed.

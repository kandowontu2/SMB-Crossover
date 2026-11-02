# Kirby follow-up on the current nightly

Current ROM: `build/thomas-current-candidate-1102-v3/candidate.nes`, SHA-256
`d0b445a71d6c539804d7c559fafc2c328ebf97ab4e35e8f3273f94ff8a25d01d`.

Read-only comparison against the previously tested
`build/kirby-approach-owner-1101-v3/candidate.nes` confirms that the complete
`KbWeapons` (2,278 bytes), `KbBodyContact` (207 bytes), `KbMovement` (1,519 bytes)
and `KbInjuryStart` (110 bytes) components remain byte-identical at their
original file offsets. The complete PRG bank 72 is also identical, covering
the inhale-friction helper whose exported alias has no size metadata.
PRG bank 74 has other changes; it is not claimed wholly identical.

The earlier immediate-suction and grounded copied-shell repairs have therefore
not been removed from these components. This is preservation evidence, not a
fresh gameplay pass. The older emulator packet assumes 32 roster slots; the
current roster has 33. Refresh its navigation and current hook bindings before
running fresh close-enemy inhale and both shell-power tests. Full 1-1 and all
powerups remain separate outstanding requirements.

## Fresh current-ROM emulator result

`tools/audit/prepare_kirby_current_native_1102_v4.py` refreshes the 33-slot menu
navigation and overlays the current symbol bindings without copying full source
or debug trees. Root ran the resulting isolated packet to completion (Mesen exit
0). `build/kirby-current-native-1102-v4/native/capture/result.json` records PASS
on the exact current hash above: Hard mode, fresh B plus forward, enemy two
pixels ahead, genuine capture/spit and Down acquisition of green/red shell
powers. Each attack reached native enemy defeat against grounded targets.

The run completed 943 updates across 1,380 physical frames, with 11,556 CHR
checks, 963 IRQ checks, 1,372 NMI checks and minimum stack pointer 180. Three
screenshots were retained; root viewed the red-shell result. Scene and enemy
setup were explicitly supplied by the harness; abilities, health and outcomes
were not seeded. This is a focused regression, not a full-stage or audio test.

## First seven copied abilities

Current-hash batch `build/kirby-copies-low-1102-v5/native/capture/result.json`
passed with Mesen exit 0: ground charge, bouncing shell, returning shell, guard,
hammer arc, upward jet and bubble. Each case recorded exactly one real capture
and swallow, followed by attack/use and native Select cleanup. The six offensive
abilities each recorded a native defeat. Guard recorded protected contact and
no defeat, as required. The run took 2,832 updates / 3,281 physical frames,
retained three PNGs and reached minimum stack pointer 180.

Producer: `tools/audit/prepare_kirby_all_copies_1102_v5.py --unit copies-low`.
The result inherits the focused harness's generic unit/scope label; the actual
seven `cases` and the ready packet's batch scope identify the coverage above.
Targets for non-shell attacks are placed relative to their effects, so this
proves earned activation and collision, not naturally reached combat geometry.
The high-copy batch is prepared but has not yet run. Full-stage, other modes,
all facings and audio fidelity are not established by this batch.

## Remaining seven copied abilities

`build/kirby-copies-high-1102-v5/native/capture/result.json` also passed on the
same current ROM, with Mesen exit 0: wave, high jump, cloud hover, three needles,
bite, short flame and bullet dash. Each case recorded one real capture and
swallow. The six offensive powers each reached native defeat; cloud hover
instead passed its sustained vertical-velocity and position checks. Native
Select discard and cleanup completed for every case.

This second batch took 2,842 updates / 3,284 physical frames, retained three
PNGs and reached minimum stack pointer 180. Together the two batches exercise
all 14 copied families in Hard mode. The controlled-scene and effect-aligned
target limitations above still apply; this is not a natural full-level combat
claim. The separate basic-move/healing test is underway.

The basic-move/healing test subsequently passed (Mesen exit 0), recorded in
`build/kirby-basics-1102-v6/native/capture/result.json`: spit star, inflation
and air puff, and Down+A slide each defeated a target without injury. Four
deliberate enemy contacts each removed one HP. Mushroom and flower each healed
two HP through the real pickup handler, with the six-HP clamp checked. Health
was never seeded. This run used 1,069 updates / 1,488 physical frames, one PNG
and minimum stack pointer 180. Items were staged mature; block emergence is
not covered. Root also viewed the high-copy cloud-hover screenshot.

## Natural full 1-1 clear

`build/kirby-full11-1102-v7/native/capture/result.json` passes on the exact
current ROM. The controller-only run reached active 1-2 after 6,242 physical
frames / 4,579 game updates, with lives 2→2, health 5 and earned copy family 1.
It is not a no-damage run. No world, enemy, health, power or outcome state was
seeded. The surviving discovery policy handled the first powerup area and
ordinary obstacles; this was not a shortcut-pipe route.

The run checked 69,900 CHR observations, 3,287 DMA completions, 5,630 IRQs and
6,235 NMIs; minimum stack pointer was 180. Root viewed the actual endpoint PNG
showing Kirby in 1-2. Compact controller inputs are retained in `inputs.csv`
(81,755 bytes). Exact replay, Easy mode, shortcut route, frame-by-frame visual
inspection and audio fidelity remain unqualified.

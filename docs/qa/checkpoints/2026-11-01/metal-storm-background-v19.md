# Metal Storm background repair

Candidate SHA-256: `7f563e35c30ebe947ba6188345beb23d35c87d61d5d4a5309756d7e8e8532b23`.
Not installed. Downloads remains the Mario the Tank nightly `7ec9cd5c4a462d0f4638c00ed35bc53a94c05cb80f4699f443245c0f754e3a1f`.

The previous v18 ROM palette query returned correct native area settings but
did not repair the black sky. Metal's own sprite palette command began at
$3F11 and omitted the shared background color. The reassembled v19 uploader
now writes $3F10, length four, using the actual native BackgroundColors table
indexed by BackgroundColorCtrl or AreaType, followed by the three body colors.

The conditional Metal renderer RAM allocation extends from [CD00,D7D9) to
[CD00,D7F0), exactly 23 additional bytes. This is an exclusive Metal35 cache,
authenticated by both full revision19 headers. It retains the existing menu
retirement and cold-loader ownership contract; it is not permanently reserved
against other characters' mutually exclusive caches. The 3072-byte CHR carrier
capacity is unchanged. Actor and renderer were reassembled together, both
fingerprints updated, and all eleven existing carrier pages republished.
Existing v17 typed head/side query veneers are compiled into the same source.

Validation:

- 160 actual CPU palette-upload cases: four areas, eight background-control
  values, and five queue offsets including refusal at 72 and 80. Verified
  complete command bytes, terminator, offset, registers and scratch restoration.
- Mesen cold selection/start and 36-frame right+B sequence: 636 frames total,
  selected35, world X73, controller-only, no RAM writes. The actual walking
  screenshot was inspected and now shows the normal blue sky and visible actor.
- This does not prove health, enemy combat, sound, powerups, lifecycle coverage,
  sustained performance, or a complete 1-1 run. HUD still says MARIO and the
  pending marker still needs cleanup before public admission.

Reproduction sources:
`tools/audit/prepare_metal_storm_background_1101_v19.py` and
`tools/audit/check_metal_storm_background_1101_v19.py`.
Bounded output: `build/metal-storm-background-1101-v19`.
The build's assembly receipt pins the exact source inputs and ROM; its
`palette-CPU.json` and `native-smoke/capture/result.json` record the checks.

Next: implement the source health/injury/death and enemy-contact contracts,
then audio and native lifecycle checks. The full requested roster and all
character/powerup playthrough goal remains active and incomplete.

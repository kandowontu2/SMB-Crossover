# MMC5 tile probing and Ryu wall cancellation

Accepted component44a passes all761 unchanged-fixture emulator slots, the
73,728-case compiled prefix comparison, forty frozen lifecycle cases and all68
earlier admission cases. Both paired crowd sets retain all204 gameplay fields.
Fresh extraction of401 source inputs rebuilds both ROMs byte identically.
The full roster audit, weapon review and final recordings remain unfinished.

The MMC5 native block-buffer prefix previously packed a page bit into an X
column, called a helper, then unpacked both. The direct calculation preserves
the final A/X/Y/P/SP, live RAM and ordered R7/R6 writes. It removes exactly
three discarded stack writes, whose addresses and values are checked rather
than ignoring a stack range. No RAM, CHR or mapper-header changes are needed.
The assembler asserts that both buffers share a high address byte.

The actual compiled43-to44 comparison passes73,728 input cases:8,192 covering
both page parities, sixteen column classes and every incoming P byte, plus
65,536 full page/X combinations with varied other registers and stack state.
Every case takes62 cycles before and29 afterward, saving33 cycles per probe.
This CPU-prefix proof alone does not establish whole-game frame rate or
PPU/NMI/audio equivalence. Native caller tests and actual crowd profiles are
separate acceptance requirements.

The optimization adds7 bytes only to MMC5 COLLISION in physical PRG bank62.
Its later collision routines and linked references relocate; resident bank
byte identity is not claimed. MMC3 retains its original collision code.

Ryu's pinned2.02 `attachToWall` clears active Jump Slash. Accepted43 kept the
flag through real wall attachment and continued protecting body contacts.
The frozen C oracle reproduces six failed assertions per mapper in wall
cases1–4. The8-byte repair clears Slash only on actual wall attachment,
retaining airborne and vine behavior. No instructions are added to Ryu's
ordinary no-attack/no-wall path. Airborne attacks alone retain Slash.

All40 unchanged C lifecycle cases pass on44a, including wall cancellation
and vine/air/floor/contact controls. Eight of those40 cases record animation
phase telemetry only; they do not establish source animation timing. All68
earlier frozen wall/vine admission cases also pass. Both are explicitly
seeded mechanics components, not ordinary-controller traversal proofs.

The wall repair adds8 bytes in bank6 and relocates twelve farcall addresses
in bank61. Their compiled immediate operands are checked against old/new
bank6 symbols. No new SRAM or farcall is added. Graphics and mapper headers
remain identical to43. The existing controller reader and injury bridge
are retained. The required full regression, including interrupt checks,
passes on44a.

## Measured crowded scenes

Both paired sets cover3,600 completed updates across Samus, Mega Man and
Bass on MMC5. All204 captured gameplay fields match in both sets. The first
set covers twenty stand/walk, outlines-on/off and0/1/2/4/6-enemy scenes per
character. The second repeats default-off four-Goomba walking twenty times
under live music. These are seeded performance arenas, not level clears.

| Default-off walking,60 updates | Display frames43 to44 | Draw calls43 to44 |
| --- | --- | --- |
| Samus,4 Goombas | 60 to60 | 60 to60 |
| Samus,6 Goombas | 63 to60 | 30 to30 |
| Mega Man,4 Goombas | 60 to61 | 34 to56 |
| Mega Man,6 Goombas | 90 to83 | 30 to30 |
| Bass,4 Goombas | 60 to60 | 51 to57 |
| Bass,6 Goombas | 81 to71 | 30 to30 |

The repeated four-Goomba set draws1,198 to1,200 updates for Samus,1,119 to
1,174 for Mega Man and925 to1,029 for Bass, out of1,200 each. Physical frames
are1,200 to1,200,1,200 to1,199 and1,198 to1,198, respectively. The hardware
visibility counter does not improve universally: Mega Man's repeated set
records748 to756 fully invisible enemy-frames, and one first-set scene uses
one more display frame. These counterexamples remain in the raw reports.

Six-Goomba native background collision work drops205,196 to181,436 exclusive
CPU cycles across60 updates for each character:396 saved per update, exactly
twelve probes times33. Six relocated taken branches elsewhere change by
one cycle, three in each direction; their actual execution counts determine
the total. The linked audit checks all1,363 moved tail instructions,48 data
bytes,259 branches and the indexed-read source domains. MMC3 COLLISION is
byte-identical. The MMC5 window retains30 free bytes.

Water Shield performance budgets still pass. Both full-orbit tests complete
OAM DMA on100/100 frames; full expansion completes60/62 for Mega Man and
61/62 for Bass. The underlying orbit/expansion physics cycle budgets remain
unchanged. This does not imply all weapon lag or sprite overload is solved.

## Evidence

- `build/verification/mm-bass-native-bg-v43-readonly/actual44a-prefix-proof.json`
- `build/verification/ryu-slash-lifecycle43-c-first-raw-run.json`
- `build/verification/ryu-wall-cancel44-preparation/lifecycle-C-accepted-negative.json`
- `build/verification/ryu-lifecycle-v44a-source-positive-a/report.json`
- `build/verification/ryu-gates-v44a-source-positive-a/report.json`
- `build/checkpoints/roster-audit-v44-provisional-a/candidate.json`
- `build/verification/plain-walking-v43-v44a-native-buffer-comparison.json`
- `build/verification/plain-walking-v43-v44a-four-repeat-comparison.json`
- `build/verification/mm-bass-v44-collision-layout/report.json`
- `build/checkpoints/roster-audit-v44-provisional-a/validation/bound-summary.json`

## Remaining scope

Dense crowds can still exceed the CPU budget, and sprite scanline overload
still needs flicker. Shadows remain off by default with the gold option row.
Samus's lack of a normal stomp follows the source: Character defaults
`canStomp` to false, and Samus overrides contact for active Screw Attack.

The separate Koopa secondary-head admission defect, Bill Flare ground
filtering/phase/limits, Ryu/Simon full body geometry and animation phase,
all final-hash routes, every weapon/upgrade and final audiovisual recordings
remain open. Old routes on34/38d/40/43 do not certify44.

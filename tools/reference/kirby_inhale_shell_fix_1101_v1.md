# Kirby inhale and copied-shell source repair

This is an isolated, executable repair proposal. It is not installed and has
not passed actual native Main/ISR or Mesen. Production source remains untouched.
The initial three Kirby segments were captured from `1c073196...`; the current
`99bf88c8...` native table witness independently proves all three stayed exact.
No full ROM or DBG was copied into this component.

## Exact failures and repaired behavior

The source order is movement/input, then Kirby weapons, then native enemy body
collision. Genuine `KbWeapons` plus the captured other-bank `KbInputs` source
opens inhale on the first B update. `KbBodyContact` nevertheless rejects that
edible front target for the next eight opening ages. The repair removes only
this age gate. It keeps the eight-update suction/capture delay, B-held/front/
vertical/family requirements, ordinary rear contacts, hazards and Meta Knight.

Copied green shells leave Kirby at centerY196. Native floor response later
clamps the center toY200. The legacy origin-distance test requires the enemy
origin within12 pixels: a Goomba atY184 stops matching at shellY197. Its real
box198..204 still intersects the shell sprite192..207. The source motion proof
shows the old green shell passing through this stationary enemy both ways.
The repaired route tests the rendered16x16 shell against the actual native box.
It calls the existing defeat boundary and retains shot consumption/ObjectOffset
restoration. It does not replace native HP, scores, drops or SFX.

Both green and red copied shells now launch at3px/update, matching native
`KickedShellXSpdData $30/$d0` in4.4. Other copied shots keep their velocities.
This is an SMB copy-ability adaptation; it is not claimed to be an original
Kirby's Adventure copied-enemy power. Red-shell original return logic remains.

## Source integration and budget

Call `repair_source(original_text)` from
`tools/audit/prepare_kirby_contact_repair_1101_v1.py` on the actual owning
`kirby_weapons.s`, then relink its complete owner. It returns the complete
source, including the helper content. It deliberately asserts every original
replacement site rather than guessing at another revision. Merely changing
canonical source without relinking the current owner is insufficient.

The original current weapons island A000..ABBC is reproduced byte for byte
(3005B). The repaired island is3004B; the full current8188B abilities owner is
therefore expected8187/8192B, leaving5B. The exact accounting is:

| Change | Bytes |
|---|---:|
| Family table256 to52 entries, original upper204 zeros retained by guard; six near branch conversions | -210 |
| Targeted shell speed | +25 |
| Shell-only contact route | +29 |
| Remove inhale startup-age rejection | -8 |
| Native shell rectangle helper | +163 |
| Net | -1 |

The family table reduction preserves all A/X/Y and real flags N/V/D/I/Z/C,
including invalid slots, disabled/alias/dying enemies and all256 IDs. Six
branches are ca65 range checked and reduce hot-path CPU cost. The guard saves
one byte of flags on the stack; it does not borrow native ZP.

Physical72's apparent tail is not a free lease: Bass preview and Rogue Dawn
audio occupy it. No placement there, new PRG bank, cache RAM or CHR is required.

Imports added: `Enemy_BoundBoxCtrl=$0646` and `BoundBoxCtrlData=$E20D`, the latter
always resident in fixed bank127 on the witnessed ROM. Use native linker
symbols, not hardcoded addresses, in the owning build. The first12 native box
profiles are admitted; custom/player profiles12+ are explicitly rejected.

`KbShellEnemyContact` accepts X=enemy, `KbSavedSlot`=shot slot. It preserves X,
returns C=overlap, and clobbers A/Y/NZ and existing Kirby temporaries
`KbTemp=$5C1C`, `KbTemp2=$5C1D`, `KbTempX=$5C1E`,
`KbTempPage=$5C1F`, `KbTempY=$5C20`. No R0..R7, native NMI0..2,
mapper/SMC bytes, persistent state, palette or OAM writes occur in this helper.
World X uses16-bit page/low arithmetic; Y borrow is retained, and only native
Y-high1 is admitted. All rectangle edges are checked against inclusive drawn
pixel bounds. There is no nested helper JSR; the shell route adds only one
2B return frame. The family guard adds1B PHP on its separate path. Actual
Main/ISR stack reserve remains a required parent qualification gate.

The standalone assembly retains the two existing farcall opcode sequences
exactly (KbInputs and MegaMan block proxy). Their actual native bank-switch/
SMC/ISR implementation is not substituted into this isolated test. The input
boundary executes the actual other-bank KbInputs source; defeat and flat208px
floor/no-block callbacks are explicitly declared fixtures.

## Verification and remaining integration gates

The final checker executes45,296 CPU entries, with aggregate receipts:
18,432 family ABI differential pairs,2,160 inhale guard cases, fresh-B and
held9-update sequences,3,042 actual-table rectangle boundary/page/Y-borrow
cases,21 hidden-page/bad-profile denials,28 copy launches,384 exact unchanged
other-projectile contact pairs, and eight original/repaired ground-motion
sequences. Old green shells miss completely; repaired ones reach the existing
native defeat boundary atupdate20 right/update7 left in the declared fixture.

Parent must relink the real source owner, verify exact full-owner byte count
and unchanged other owners, test actual Main/ISR reserve>=12B, and run native
first-frame/held inhale plus earned green/red copies, terrain, defeat/SFX and
ordinary hazard/rear/released-B contacts. No arbitrary fast-target swept
collision, full-level, audio, performance or native completeness claim follows
from the isolated rectangle tests. No captures were generated.

# Karnov Bomb integration

The in-memory transform from installed Thomas image
`15a683321cde608cfe15447e90ef58d5295a16a1a6b607434f98df37162ac533`
produces current candidate
`318a087735b4204c74274b4107efbc302bc15a674a7f6f9d3bed598cea90d08d`,
with cookie `a707011147d338f92c669d26e11e5b71`.
The 49 Thomas edits and 1,137 Karnov edits are disjoint. The patch report
retains exact preimages and can restore either parent.

The live flower collector already grants original Bomb option1 when it
reaches that position in its equipment cycle. The new controller path
admits an owned Bomb on Down and a fresh B press. It calls original EB19
and the existing source BCD stock helper and job2 timer. The actor runs the
donor Bomb's 80→81→82→83→00 phases. Source C0-C3 remain its state and position.
The native camera adapter rebases the parked world anchor once per accepted
update. The native actor coordinate adds 32 to the native Y coordinate, so
the lower viewport cutoff moves from C0 to E0 to include ordinary SMB ground.
The original final donor stage-specific tile scripts have no SMB stage data
equivalent here. Damage uses the original 32-by-16 contact rectangle and
passes eligible ordinary SMB enemies to their native defeat and score path.

The first native contact replay exposed an anchor error: Goomba native Y184
draws at OAM Y192, while Bomb source Y208 also draws at Y192. The old adapter
converted the enemy to its OAM top192, so the original exclusive16 boundary
rejected a visibly overlapping actor. Negative receipt
`53d9ca0ed1d5f2da86a07bb9b9c2f811ebed74d9b30a0444125c4c7fca2737b1`
is retained separately from success.

Original donor bank9 A05D..A065 loads enemy0652/0653. Its A0FC..A108 renderer
subtracts the record origin. Small-enemy record A25E is `21 02 00 91 01 8F`:
an eight-pixel horizontal origin and16-pixel vertical origin, followed by two
8x16 cells. Original A036 actually renders anchor128/208 at OAM120/192 and
128/192. The actual native DrawMetasprite renders the same coordinates from
native position120/184. The adapter therefore adds8 to native X and24 to Y
to produce donor center/feet coordinates. The horizontal addition is folded
into Bomb's original +16, reducing that constant to8. Width32, height16 and
their unsigned exclusive comparisons remain original. All100 native contact
cases now use the actual donor CCFC execution as their predicate oracle.

Root's corrected candidate ground-Goomba fixture passes: native blast callback1
at SP230, Bomb247/Y192 and Goomba244/native Y184, followed by the ordinary
defeat displacement. Both lives, fuse phases and original hardware OAM survive.
Receipt `c912b6e0ae1f5e575152b3dd5f41d95378ec2c6769a8c0fd46e5331d8b38bde4`,
controller `da2b3d7f6901062f70b2109f327e733bf8a03935943f57fe1c2ee62bc424d0a3`.
This fixture seeds stock as described below. Full current-candidate stage
regression and delivery remain root-owned.

The six Bomb sprite patterns come from the original page12. Two mirrored
body packets move to another existing Karnov body page, preserving all 358
body cells and seven projectile patterns. Bomb art stays in the existing
projectile window. The HUD uses original icon84/85/94/95 with the existing
plane swap and prints original BCD stock. Four HUD icon tiles replace the
previous plus glyph and three unused cells. The flashing control text shows
`DOWN B` with a space, keeping letter and digit cells intact.
The explosion packet extends into C839/C83A. The two health routines that
use those bytes assign them before each read and consume them before returning.
The routines execute outside the foreground Draw call.

The options carrier stays D600..DDFF. The source packet contains the dormant
Ladder activation D6E5..D786, Clapper/Glasses/Mask D7EF..D8B1, Shield
D8FC..D93C, and the original D950..DA29 cursor loop. The sole compiled call to
the original equipment activator is the host's fresh B wrapper, which
injects source Select after checking ownership, action range and the four
supported IDs. The source table has five unadmitted vector destinations in
the reclaimed spans. The original D639 jump is the only external direct
reference into those spans. The candidate points all six references to the
existing safe return. The compiled source and exact patch inverse retain
the old implementations. Future equipment integration must repack these
branches and the Bomb workers into a newly proved larger or compact carrier.
The uncopied remainder of physical page1020 is outside the current C2 grant.

CPU proof on the exact candidate covers the 12-row cold copy with 23,064
PPU reads and both complete headers. It checks a real mature flower collector
grant, original BCD stock decrement, controller activation, all fuse phases,
300 original object-update comparisons, 27 native blast contacts, 73 misses,
eight original OAM cases, and the native HUD icon and BCD digits. Five
signed camera, duplicate and pause cases, offscreen removal, same-life
retirement with gear retention, eight existing supported or excluded
activation cases, and ten foreign owners pass. Three actual readback faults
fail before both headers are published. The public service interrupt audit
passes 190 IRQ and 190 FF lag-NMI cuts at minimum SP164.

The private Mesen stage controller uses retained controller input and writes
no emulated state. The separate fixture explicitly writes only source C08E,
C08F and C0BB to supply one earned-stock Bomb. It uses controller input to
select and arm it, observes fuse and hardware OAM, and records native Bomb
contact when a real enemy enters the rectangle. The fixture does not test
natural Bomb acquisition. Root owns both Mesen runs and delivery.

Ladder, Clapper, Glasses, Mask and Shield remain required. The prior original
audio and full earned-equipment gap also remain open.

```
python -B tools/audit/run_bounded_build_v1.py --output build/karnov-bomb-cpu-1112 --max-files 1 --timeout 600 -- python -B tools/audit/check_karnov_bomb_1112.py
```

The anchor correction repeated the complete suite through bounded output root
`build/karnov-bomb-1112`, session96314, exit0. It created zero files.

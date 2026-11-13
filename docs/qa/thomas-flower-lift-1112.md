# Thomas's 1-1 flower lift

The authored flower at world X1248 matures at Y119. Thomas can reveal it from
below, but his original 27-pixel jump and the underside of the block keep his
native Y at 153 or lower on the screen. A controller-only Mesen run on
`8fc57b8b4268a47f8a906af8b5813834bbf76ca7376d1d12767d510708da9582`
earned the mushroom, crossed the first four pipes, revealed the flower and
attempted five ordinary jumps with both lives. At frame 3448 the mature flower
remained on its block and Thomas remained at status 1. Receipt
`c4f40a3acb988ae361da3e747d5aa44610c37ec483dc8281888b1c69faff732a`,
controller `639f54135ab16a991d93da118a4b1d01c2a054a8d6f879b40fd1e9225776044b`.

Candidate `15a683321cde608cfe15447e90ef58d5295a16a1a6b607434f98df37162ac533`
adds one record to Thomas's existing 1-1 lift manager. It constructs native
vertical platform actor `$25` at **left X1200, center X1216, initial top Y192,
width 32**. The original camera gate constructs it when the left edge is 256
to 287 pixels from camera left. The original manager chooses the highest free
actor slot and waits if all six are occupied. Thomas boards the platform to
the left of the block, rides upward, and steps off toward the authored flower.
The lift and flower use separate native actors. The original six Thomas lift
records and Kung Fu jump, movement, combat and rendering routines retain their
bytes. The other characters use the existing foreign-owner rejection.

The exact compositor `tools/audit/compose_thomas_flower_lift_1112.py` adds
the seven-entry coordinate and seen-bit table to the retired Thomas lab query
tail at RAM3 `$B5D2`, then redirects its existing table reads. The manager's
camera, constructor, pause and native slot logic retain their addresses and
behavior. The existing cookie recipe authenticates all 8 KiB of the kernel
template and all 8 KiB of the state template. The new revision-3 cookie is
`a70a400363ab8235a65b66179dbc3647`. Only Thomas's six-page carrier and cookie
change. The source SHA256 is
`86d0bba8c02975693e7fed01fd2b99ce67f99a15c2cdf0ba1df4849bf4815c54`.

The CPU checks pass 108 existing placement comparisons, 18 new camera/slot
cases, six native carry cases, four stage or frozen rejects, seven foreign
owner and Ryu-family alternate register/state pairs, 21 NMI and 21 IRQ cuts,
and one nested IRQ at foreground SP209. The real cold menu and constructor
load the expected kernel and matching headers. The controller-only CPU route
boards at update 2836, departs at 2900, collects the mature flower at 2962,
completes both 60-update freezes, and walks to X1245 at status 2 with both
lives. The tests execute in memory.

## Pickup behavior and physical scope

Thomas's Kung Fu source provides his original movement, melee and health.
His host pickup service uses `MarioSourcePowerupCollision` for SMB items.
Current directed CPU checks execute that route after cold Start and confirm:

| Item | Observed behavior |
| --- | --- |
| Mushroom | Native actor erasure and 60 actual progression updates, status 0 to 1 |
| Flower | Native actor erasure and 60 actual progression updates, status 1 to 2 |
| Star | At statuses 0 and 2, timer `$23`, music `$40`, unchanged status, no freeze |
| 1UP | At statuses 0 and 2, popup `$0B`, exactly one life on native popup update 6, no freeze |

All six directed cases write the native pickup sound. The Star and 1UP
cases use explicit mature actors. Natural Star and 1UP collection remain open.
The flower uses the existing hosted tier and Thomas's original melee actions.
The exact 1-1 level stream places the hidden 1UP at X1024, tile top Y128,
and the Star brick at X1616, tile top Y144. The hidden block needs its own
approach because Thomas's ordinary ground jump peaks below that block.

Root's strict Mesen replay on the candidate completed at frame 3825 with
status 2 and both lives. It boarded the native lift in slot 4 at frame 3552,
departed at frame 3645 from X1216/Y96, collected the mature slot 5 flower at
frame 3743 from X1261/Y112, completed both 60-update transactions and walked
left to X1245. Receipt
`37372e8aea9e5f38f374af9086d24ed1926f76e901a4aa4c87a927c2ab95503a`,
controller `2402b7183e51c041d16dae48638adc20b2a4464b7e835a283750e78ddd4ceaad`.
The first assisted attempt collected the flower and reached status 2 but the
controller sought 16 pixels to the right, then fell back into its approach
state. The final controller resumes to the left.

Run the standalone source `tools/playthroughs/thomas_flower_stdout_1112.lua`
through `run_stdout_mesen_1110.py`. Variant 2 verifies the five-jump negative on
the installed parent. Variant 1 verifies collection and resumed movement on
the candidate, including the mapped constructor, offscreen birth, carry and
departure. Run the checker or native runner through the shared bounded wrapper.

The final Mesen replay also observes the actual offscreen constructor at
frame 2898. The new platform occupies slot4 at left X1200, center X1216,
initial top Y192. Camera left is X913 and right is X1168, so the platform's
left edge starts 287 pixels from camera left. The subsequent board,
departure, natural flower and resumed movement pass at frame3825.
Receipt `10f9baba323255715dc2701722578a99da16498f418decf148d78ae9784af96c`
uses script `cde6a22ba2d5144d82964e095f77db18dbf66a79b03eca3d810507f6b7f5c2cf`.

The separate current whole-stage replay crosses the first four existing
pipe lifts and then fails at the first floor pit. One Up timing rises at
X1372 and reaches X1418 before death. A later timing is consumed at X1374
while already falling. The original jump and ground support need further
route investigation. The latest failed stage receipt is
`bb801f5df9e929af65acc1d9a52ebc82195ee8fafab38b8744339d29c2ab31ad`.
The early retained replay also required an update to its historical Main
return observer before it could count actual current gameplay updates.
The full current stage clear and natural Star/1UP remain open.

The candidate was installed directly over the Downloads nightly with zero
backups. The final constructor, collection, recovery and movement replay
repeated from that exact launch path with identical receipt. Patch guards
passed before and after installation. IPS reconstruction equals the tested
installed ROM. The IPS SHA256 is
`a828d2f721306368fed92a3f9146f7a6529e0cc4a5e562548a72e054ee42c32d`.

```text
python -B tools/audit/run_bounded_build_v1.py --output build/thomas-flower-lift-1112 --max-files 1 --timeout 360 -- python -B tools/audit/compose_thomas_flower_lift_1112.py --route
python -B tools/audit/run_bounded_build_v1.py --output build/thomas-powerups-cpu-1112 --max-files 1 --timeout 180 -- python -B tools/audit/check_thomas_powerups_current_1112.py --part pickups
python -B tools/audit/run_bounded_build_v1.py --output build/thomas-flower-negative-1112 --max-files 1 --timeout 300 -- python -B tools/audit/run_stdout_mesen_1110.py --script tools/playthroughs/thomas_flower_stdout_1112.lua --rom C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes --expected 8fc57b8b4268a47f8a906af8b5813834bbf76ca7376d1d12767d510708da9582 --output build/thomas-flower-negative-1112 --timeout 240 --variant 2
```

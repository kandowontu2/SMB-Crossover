# Thomas: earned mushroom delivery

The tested Downloads ROM is
`C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes`, SHA-256
`6d83dea872b42cd39c14d756334a801c8f7da7dfa63ecea16d9f13835c63638d`.
The in-memory IPS has SHA-256
`8ad06ee63a73991830b26bb9bd9792f33fede4b4c6b3ba91b0afda11febccc5c`
and 2,099,510 bytes. It reconstructs the tested Downloads bytes from the clean
headered SMB World base. GitHub publication awaits the source push.

## Failure reproduced in Mesen

The controller starts from the title, highlights Ryu, presses Select twice and
enters 1-1 as Thomas. It walks, uses the original Up jump beneath the first
authored powerup block, then waits by the first pipe. No emulated state,
position, item, health or terrain is written by the test.

On parent a76
`a76d7610eed8493806200c52b96065af0369b926c55d033e17841f818756e2e0`,
the actual slot 4 mushroom emerges and matures, but Thomas never collects it.
After 1,100 route updates he remains at X402/Y176, unpowered, with both lives.
There are 565 successful original body/CHR/palette/HUD checks. Receipt:
`7c7e4e3856c998a9a8a3f0a9ea937aeead5e2be315a82ece583e9cc3d0194172`.

Two previously rejected policies are repaired: native item maturity admission
and the existing hosted powerup-animation update. The 32-byte implementation
reuses the source-proven, unused 91-byte lab query helper, not live collision
or loader tables. It preserves Thomas's original movement, 27-pixel jump,
rendering, attacks, state, art and helper placements. The cookie is recomputed
with revision 2. See [the source qualification](thomas-earned-powerup-1110.md).

## Candidate and installed Downloads both pass

The unchanged final controller naturally collects the slot 4 mushroom at
frame 1,030: item X411/Y158, Thomas X402/Y176. The native actor is erased,
score 6 is set, and the real pickup sound write `$20` occurs. Exactly 60 native
animation updates finish at frame 1,090. Ordinary Right resumes to X418/Y176,
status 1, engine 8, timer 0, both lives retained.

Each run uses 1,115 physical frames and 823 completed Main calls, with 250
checked OAM/CHR/palette/HUD publications and eight checks after recovery.
The two independent native receipts are identical:
`592d77d0fa34dd2e5975f473b8b611a457fac94cd806663949ae90bb2dcf444a`.

Final controller:
`tools/playthroughs/thomas_earned_powerup_stdout_1110_v3.lua`, SHA-256
`7b0c6c7e9962a4edb867210853da5d5c78b7052778c041904d9c8d60e4a96320`.
Mesen executable:
`8b92daa209ee5052845e02a663aeb1afd6194eca55d86e6628c51114c61da0a9`.

Earlier observer negatives remain frozen. V1 assumed the wrong CHR slots;
v2 read a newer pose descriptor after OAM had already been drawn. V3 captures
the immutable source pose at actual `ThNaturalDrawDone`, then checks that
drawn record against OAM and each consumed physical pattern page. It requires
the original pages 434..441 rather than arbitrary visible sprite data.

This proves one naturally earned mushroom transaction, sound-queue emission
and recovery. It does not prove a flower, Star, 1UP, complete original upgrade
lineup, full stage, audible output or zero lag. 285 video frames have no
completed Main call. The earlier full-stage evidence retains its own hash.

## Storage, helper and delivery scope

The sole active new task ROM is
`build/thomas-powerup-native-1110/candidate.nes`, byte-identical to Downloads.
The superseded task-owned a76 copy at
`build/excitebike-powerup-native-1110/candidate.nes` was removed after literal
path, size and hash verification against Downloads. Its source reconstruction
is retained. No backups, IPS files, videos, PNGs or native receipts were written.
Build remains 3,123,082,970 bytes/19,999 files. Guards before and after delivery
find no same-name automatic patches.

No helper actor or coordinate changes. Thomas's existing 1-1 helpers start at
left edges X400,560,688,864,2560,2816; centers X416,576,704,880,2576,2832;
initial top Y192, width 32. Broader crossing evidence remains in the
[helper inventory](helper-platform-inventory-1101.md).

All 100 menu admissions remain unchanged. The FF and Excitebike repairs remain
included. Original Sonic/Prince integration and full-roster stage/powerup
coverage are still active work.

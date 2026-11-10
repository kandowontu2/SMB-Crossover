# Excitebike earned pickup: tested Downloads delivery

The installed nightly is
`C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes`, SHA-256
`a76d7610eed8493806200c52b96065af0369b926c55d033e17841f818756e2e0`.
The sole Current IPS reconstructs it from the clean headered SMB World base:
`aa6424bd4603d1b30152a64aa65026dc729dab72334ea420678f577fdf70f79f`
(2,099,510 bytes). GitHub publication passed after source push `e85fafbe`:
Current is Latest, with sole asset731354495. The downloaded asset reconstructs
the exact tested Downloads ROM. Downloads was installed and tested directly.
No backup was created.

## Reproduced failure and fix

The same controller-only Mesen test starts at the title, selects Excitebike,
runs the original movement, bumps the authored first mushroom block and
collects the mature mushroom after it returns from the pipe. No actor,
position, health, powerup or controller state is written by the observer.

On the previous a5 nightly
`a5c54d7624ee961f11b45598ca7cf7fecc24de6ee87d8e8aa70dad55834f2eaa`,
the natural pickup erases the actor and starts the hosted animation, but its
private progression vector rejects every tick. After95 further Main updates,
the animation remains active at age0, engine9, X290/Y176, with both lives.
Actual Mesen receipt:
`6505901e0f3175fd4a38e0c97c82eab855e8d7e0af3298c35b7ccce84b5ce0e1`.

The repaired image changes34 bytes: a private vector, an18-byte call to the
existing native powerup updater, and its authenticated fingerprint. The
original Excitebike movement, rendering, art and every other vector are exact.
The helper uses the original linker's declared gap; it does not use guessed
padding. [Source qualification](excitebike-earned-powerup-1110.md) includes
four directed pickup types, pause/resume, old-cache rejection, ABI comparison
and actual paired NMI/IRQ execution.

## Actual Mesen results

The private candidate and the installed Downloads ROM both pass the unchanged
final controller. Each completes exactly60 native powerup updates, returns
to engine8/status1/timer0, then moves16 pixels to X306/Y176 with both lives.
The two independent runs have identical native receipt content:
`412ddb541df22140770c8bbf5ddf01188cbb2d0a39ab2a87ba0e155880b461f7`.
Each uses1,510 physical frames and1,008 completed Main calls, with324 checked
OAM/CHR/palette/HUD publications, including17 after recovery. This is not a
full1-1 clear, a physical flower test, an audio-listening check or a lag-free
claim.471 video frames have no completed Main call.

Controller:
`tools/playthroughs/excitebike_earned_powerup_stdout_1110_v4.lua`, SHA-256
`547675a20cda944233757c664a89fde1a97d98435d98ce5e09be43b5c663b228`.
Mesen executable:
`8b92daa209ee5052845e02a663aeb1afd6194eca55d86e6628c51114c61da0a9`.

Earlier observer negatives are retained. V1 read the restored CPU C-window
as source RAM; v2 corrected this to physical RAM2. V3 isolated the remaining
assertion: the real NMI already consumes the pickup sound queue before the
native call returns. V4 observes the actual `$20` sound write during that
exact call, its later clearing, and requires the write. It does not waive
the sound effect or hold the queue artificially. All versions remain frozen.

## Delivery and scope

The candidate is the sole active task ROM at
`build/excitebike-powerup-native-1110/candidate.nes`. Its bytes equal the tested
Downloads ROM. The pre- and post-install automatic-patch guards find no
same-name IPS/BPS/UPS. The IPS is built and reconstructed in memory. The
installer retains rollback bytes only in memory while repeating the test.

The superseded task-owned a5 duplicate at
`build/ff-mux-performance-native-1110/candidate.nes` was removed only after
hash/size/path verification against installed Downloads. Historical96 and a5
private candidate paths are no longer live. Their source recipes reconstruct
them from the retained c10 input. Build remains3,123,082,970 bytes/19,999 files;
all emulator receipts stayed in memory, with zero new capture files.

All100 menu names remain admitted. The [Select access list](../character-select-access.md)
records the actual a5 menu/opening census; this34-byte Excitebike-only repair
does not change those tables. This delivery does not turn borrowed prototype
behavior into complete original ports. Sonic, Prince, Jay, Steve and DK Jr.
still need the separately tracked integration work. No helper locations change.

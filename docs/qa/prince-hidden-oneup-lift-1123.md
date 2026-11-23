# Prince of Persia's hidden 1-UP in 1-1

The hidden block occupies X1024–1039 at Y128. The Prince can climb the
tall pipe and start a jump at X943/Y112. In the linked CPU replay his
head reached the hidden block's column only after the jump had stopped
rising. Three follow-up routes varied the step near the lip and the Up
press around takeoff. None triggered the native block bump.

The proposed lift uses the same stock vertical platform and position as
Donkey Kong Jr.'s hidden 1-UP helper. It is 32 pixels wide, with left
edge X1008, center X1024 and initial top Y192. The admission probe used
the original `$25` platform constructor. It selected a free enemy slot
while the platform was 256–287 pixels ahead of the camera. It left
occupied slots alone and skipped admission when that platform already
existed. The original offscreen logic kept it active at admission and
on screen, then retired it after the camera passed it. The probe passed
three admissions, 13 exclusions and nine checks of the stock offscreen
logic. CPU receipt
`b4ade93e73a1108a72a7a979c8730d2fa962964e2b93017f9de009e022126a04`.

The separate support probe used the actual player collision and carry
routines in a controlled scene. It let the Prince complete his original
landing poses and stay attached for 41 consecutive standing updates.
It also passed 96 separate ride updates and checked ordinary pipe
contact. CPU receipt
`e77cb16cd291d7f37c44d0c2f3f6582d2fc8cacb220ae787fc670936ddc2d306`.

The integrated trial `deff5edb` puts the lift code in PRG RAM bank 1.
Cold start stages that stream before decoding the state stream, which
overwrites the loader. The loader fits before the existing staging wrap,
and the ROM uses 45 backing pages with 69 bytes to spare. The game
commits both owner headers after decoding, and ordinary floor checks use
the original terrain fallback.

The cold startup test ran the actual game menu and decoder. It checked
every byte of all four decoded streams, the restored runtime banks, the
two owner headers at the first draw and 18 calls into the lift code. The
installed nightly is `6201e3b6`. The remaining gameplay checks are the
1-UP collection and full 1-1 clear with the lift in place. CPU receipt
`2ff29a84f1d0f7706c780a4dedcf88b8bedc02b9b01a01b692866b277ec376b6`.

Mesen measured 168 video frames for 96 game updates in the empty
opening, including 72 frames without a completed update. This matches
the installed build's opening cadence. The Prince again walked from
X40 to X92 after Right was held. The trial added about 540 CPU cycles per
idle update and 525 per update with Right held in that sample. Mesen receipt
`72cfe50e9349b9a259a50a03690e241fbabee5783e3c3b35e96db50d6c1d3417`.

The first controller-only Mesen run saw the lift enter enemy slot 5 at
X1008/Y192 when the camera was at X722. Two Goombas were active in their
own slots. The Prince climbed the pipe and launched his ordinary jump
from X937/Y112, then landed to the right of the lift without touching
it. He retained both lives. This run verifies early actor admission.
Mesen receipt `30d2ee4a2938e7918befc640e6f9ef406b6ed9af9a69b7e8fb0da771ef4b1c5a`.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/prince-oneup-lift-admission-1123 --resume --max-files 1 --timeout 240 -- python -B tools/audit/probe_prince_oneup_lift_admission_1123.py
python -B tools/audit/run_bounded_build_v1.py --output build/prince-oneup-lift-cold-1123 --resume --max-files 1 --timeout 350 -- python -B tools/audit/check_prince_oneup_lift_cold_1123.py
```

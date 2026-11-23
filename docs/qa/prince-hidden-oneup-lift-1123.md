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
installed nightly is `6201e3b6`. CPU receipt
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

A full Mesen run on the same trial cleared 1-1 with the lift present.
The Prince reached 1-2 with both lives and his earned sword, then
completed 25 grounded updates. The run took 17,611 video frames and
wrote no captures. Mesen receipt
`b5a324efc881af77d968bd8adcab8df8418a3d1f0a2fee3b369ecd220fb5f19b`.

The timed pickup attempt put him above the lift while it was descending.
The native collision trace showed his foot at Y187 with the box starting
at Y189. His next downward step moved the foot to Y198 as the lift top
moved to Y192. The collision admitted landings within five pixels of the
top and sent the six-pixel overlap to its side-contact check. Carry never
started. The fix needs to account for the Prince crossing the moving top
between source positions. The hidden 1-UP still needs a passing replay.
Linked trace receipt
`4fc7a1ba4994c0cae80775f71a76952cd9fa9dfe1eac97b6ead67931bc6222be`.
Mesen confirmed the same rejection when the box overlap was six to seven
pixels, receipt `23cd8dddc47c44dc78d35310634d5e73845330d7dbcf096c660f013f1736bbb4`.

A later departure reached the top window. The original platform code
set carry in slot 5 and positioned the Prince for three consecutive game
updates. The next source movement fell to the floor, and the platform
lost contact. The current floor query gives the authored ground priority
before checking the lift. Mesen receipt
`a7256813cf05bd6f05fe5eb6b342f8de66fbc9823729f5f3eaf2b40ad52bf231`.
Private trial `9135e1cd` checked carried support first. Native carry ran
five times on the later departure, and the Prince still fell to the
ground. Mesen receipt
`1bcf832715b1a671c132ad4ca5c7ae496d61a517d9039c9a7132736ad99b7f60`.

## Landing between updates

The next trial checks where the Prince's foot was before and after an
original falling step. When it crosses the actual lift surface, his
original terrain routine aligns him to the top and runs the original
landing transition. The stock platform collision then takes over the
carry. This route is scoped to the Prince's 1-1 lift.

The linked CPU test moved the foot from Y187 to Y198 across top Y192.
It observed the original landing action and native carry. It separately
verified a carried fall from the animated pose, then ran 96 more
updates with sustained contact. It passed 28 rejection cases and 28
comparisons against ordinary movement and terrain queries. CPU receipt
`5454a57d0e77edf4866cfd15c5125ed8ef810703a8ecdfe64998f67e423d4b76`.

The integrated trial `ee3d59c6` uses a 476-byte loader and fits on the
same 45 backing pages with one byte to spare. Cold startup verified all
four streams, 18 calls into the new bank and both owner headers. CPU
receipt `d944de1e4aed5d1cba1d206ce560fe1ae958be1ffc7e565fa28bbf80eada4e4f`.

On `ee3d59c6`, Mesen saw the Prince land with his original landing action
on the lift. His standing jump kept carrying him right through the
landing steps, and he fell past the 32-pixel collision edge. Releasing
Right earlier produced six actual contacts over three moving positions
before his feet went past the edge. Mesen receipts
`44f8fc75772855f76afe30bf0db702c96e831a7b5ef7a65d8e611b4a1daa6996`
and `33fc5b897959731486d96d3c72f854fd74d98786a8b68cc7c99d0ca02b8b6603`.

Private trial `342992b0` uses the full stock girder width drawn in 1-1.
Its 48-pixel surface starts at X1008, has center X1032 and starts at
top Y192. The full cold decode passed with two carrier bytes to spare.
CPU receipt `37e09762341c0afa8aed5cc3e2d28b9c89f8dfd46cf7a7cf7d9ca1f7cacc9d8c`.
The wider case also passed the controlled fresh landing, held landing,
96 ride updates and 28 rejection checks. CPU receipt
`2198f621b3d997ad40be16700faccb81585a062a9cd1083e53adb5a337f00792`.

The wider lift caught the Prince at X1025/Y159 in ordinary Mesen play.
He still lost contact at X1037, inside the girder's collision width,
while the platform was moving down. This narrows the remaining problem
to maintaining support across his landing updates. Mesen receipt
`2d00e9caa3b457e0bc2fffb314a161177e7b1a8c9b4715cdd4aceeeee732bb9c`.

A second Mesen trace followed the real support callback. With the lift at
Y194, the carried pose briefly projected its foot to Y195 and wrote that
value into the previous-foot field. On a later fall step the current foot
was Y202. The sweep declined because its previous foot was already below
the surface, although the last actual carry was at Y194. Mesen receipt
`f2be090e3adf43be8645c41ebf0d0d990c6a5c971c0f435794b1c23a23a9f476`.

The next trial, `1124ad42`, records the lift's actual support plane in
that history field during genuine carry. The original animated foot
projection still supplies the current body. Its four-stream cold decode
passed with nine bytes left on the existing carriers. CPU receipt
`b2794c7bc8e071d4c05768c632c0a4e6c99e88458362ea91c0b5b16feb45e5c8`.
The linked test verified an animated foot at Y195 with recorded history
at the actual top Y194. It also passed 96 sustained ride updates and 28
rejection checks. CPU receipt
`99f7c62e7178127775767200c176ee90a48f9280a9d2f528b47eb03d600f07db`.

On `1124ad42`, the Prince completed the original landing sequence while
the lift moved. Mesen counted 65 attached movement updates, including 32
with a changed lift height. The replay pressed B and Left together
while he still faced right. His careful step followed his facing, and it
took him off the right edge. Mesen receipt
`26b5ac0b5907c435d5ae2a13d8a073c633003360c736af125b7e118e6bf62892`.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/prince-oneup-lift-admission-1123 --resume --max-files 1 --timeout 240 -- python -B tools/audit/probe_prince_oneup_lift_admission_1123.py
python -B tools/audit/run_bounded_build_v1.py --output build/prince-oneup-lift-cold-1123 --resume --max-files 1 --timeout 350 -- python -B tools/audit/check_prince_oneup_lift_cold_1123.py
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 8 --timeout 480 -- python -B tools/audit/run_prince_oneup_lift_native_1123.py --stage
python -B tools/audit/run_bounded_build_v1.py --output build/prince-oneup-lift-cold-1123 --resume --max-files 1 --timeout 350 -- python -B tools/audit/check_prince_oneup_lift_cold_1123.py --swept
```

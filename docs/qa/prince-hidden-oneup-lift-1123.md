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

The 183-byte admission routine and 312-byte support prototype currently
run in isolated CPU fixtures. The installed ROM is still `6201e3b6`.
The next check needs an integrated build that spawns the lift as the
Prince scrolls through 1-1, then earns the 1-UP and clears the level.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/prince-oneup-lift-admission-1123 --resume --max-files 1 --timeout 240 -- python -B tools/audit/probe_prince_oneup_lift_admission_1123.py
```

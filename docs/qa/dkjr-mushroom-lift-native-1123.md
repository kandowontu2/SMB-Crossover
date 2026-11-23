# Donkey Kong Jr. first Mushroom in 1-1

## First lift trial

The installed `82e8da0e` nightly keeps the thirteen existing 1-1 helpers.
The first private trial, `3b7b36ca`, added one existing native `$25`
vertical platform by the first Mushroom block. Its world left edge is
X336, center X352, starting top Y192 and collision width 32 pixels.

The new lift let DK Jr. reach and hit the first powerup block with his
ordinary jump. In Mesen he collected the released Mushroom and continued
through the growth animation and 30 more updates with both lives. The
full-stage replay then exposed a regression. The new lift claimed native
actor slot 5, so later helpers and Goombas filled the remaining slots in a
different order. The ascent lift at X880 did not spawn, and a Goomba caught
DK Jr. at X850/Y176 while he waited for the missing lift. This trial stayed
private.

- First private Mushroom receipt `c47b1d971dcfcc034b82e12b34c79d8a6118e9d57c1bfd9b896f1d0adf9722bb`
- First private full-route receipt `9db3e001c0bbc2e72ff5ca357f31d2b31fa7383778b16c5ca754683e9b691ca1`

## Revised slot preference

The `ffd70810` trial starts the new X336 lift's empty-slot search at slot
4. The thirteen existing helpers still search from slot 5. The native
constructor, carry routine, terrain and movement stay in use.

In Mesen the new lift entered the actor table in slot 4, 287 pixels ahead
of the left edge of the camera. DK Jr. hit the first powerup block,
collected its Mushroom and kept the upgrade and both lives after 30 more
movement updates. The replay took 1,910 video frames and saved no captures.

- Mushroom controller `64b4baafbc049801f78e2c1600fd75199ab3349d28fcb66852f948f7819b561d`
- Mushroom receipt `be3ce07537c38cb5be9364f317776eb092835cafecf3bbbd9cbc04f96ce7c046`

Linked source checks covered all 64 six-slot occupancy patterns for each
of the fourteen helpers. There is no new actor capacity. On the same
empty-area inputs, the candidate used ten fewer CPU cycles per game
update. Its changed search can cost more between later rows, peaking at
213 extra cycles when the left edge of the camera is between X2785 and
X2815. That source result measures CPU work in the room and at the listed
positions.

Mesen measured the empty opening at 96 video frames for 64 game updates,
including 24 video frames for 16 walking updates. These match the retained
nightly's opening measurements. Cadence receipt
`15fbf574b02410e689dd6a22f5360ae393856f2000c5a354f4a72f133f8833d8`.

The next Mesen full-stage run restored the X880 and X944 lifts and reached
the final staircase. The replay exhausted its forward jump attempts on
the third step at X2943/Y112. Extending the existing backward-facing jump
input to that riser let DK Jr. jump from X2931/Y112. The other stair
jumps, the flagpole and castle then passed. This input change did not
modify the ROM.

The passing route took 17,454 video frames. DK Jr. finished in 1-2 at
X40/Y176 with both lives, 25 returned grounded updates and 26 completed
original movement updates. The X416 and X880 lifts used slot 5, and the
existing horizontal lift at X1408 appeared and carried DK Jr. across its
gap. The full-stage replay did not need the special wait at X661.

- Stair-attempt receipt `737e2d23260a9a220fe369e1c74035eb6add2a99c8b72ea1dda8dab8e2596fd8`
- Passing full-stage controller `07c051dfc544c1b82004672d22d935a6c1f1b0d0c1d64b3e0428fdf7781d30a0`
- Passing full-stage receipt `fe1de52fb1b4d6a1f0632734421801fd77c84a04df8b3f74ba21a2ed1f048d06`

## Downloads nightly

The Downloads nightly now contains `ffd70810`, byte for byte with the
full-stage candidate and the shared test ROM. The Mushroom and cadence
tests launched from Downloads and reproduced their private receipts
exactly. Patch guards passed before and after replacement. The replacement
uses no backup files.

The delivery command expects the authenticated `82e8da0e` parent in
Downloads. Use `--route mushroom`, `--route cadence` or `--route full`
with that parent to test the candidate privately.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/dkjr-mushroom-native-1123 --max-files 2 --timeout 480 -- python -B tools/audit/run_dkjr_mushroom_native_1123.py --deliver
```

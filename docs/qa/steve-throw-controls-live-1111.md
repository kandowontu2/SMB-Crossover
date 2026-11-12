# Steve throw controls in the loaded game

Private, in-memory candidate:
`ba5846ebcbdabc430c735836c4ec6dfaa09886cdad9d80dae3a15edce83a95e6`.
The Downloads nightly and public IPS are unchanged. This candidate connects
player controls and recovery; it does **not** yet connect the robot's throw
flight, enemy contact, retirement, or recovery renderer.

## Integration

`tools/audit/check_steve_throw_controls_live_1111.py` builds on the installed
`80e6` image using exact preimages. It moves the expanded 84-byte animation
table to `$C4A0`, reuses the original 64-byte table region for the 58-byte launch
worker, and places the 74-byte recovery worker at `$C980`. Four operands in the
existing animation decoder point to the relocated table. Existing function
addresses stay stable.

`tools/reference/steve_shatterhand_throw_controls_1111.s` adds a 31-byte movement
gate at `$DE92` and 39 bytes of decision/reset code at `$C9CA`. The decision gate
uses the real `JnPressed` B edge, calls the verified launch worker only after
the lift decision accepts a throw, and consumes that edge before companion
weapons or ordinary punches can use it. The movement gate maintains recovery
and cancels it on hurt/upgrade; the scene-forget hook clears its action clock.
The two source-verified recoil clamp operands are also applied.

## Verification

Both commands completed successfully through the bounded runner, with
`--max-files 1`, no generated files and no captures:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-throw-controls-1111 --max-files 1 --timeout 180 -- python -B tools/audit/check_steve_throw_controls_live_1111.py
python -B tools/audit/run_bounded_build_v1.py --output build/steve-throw-controls-cold-1111 --max-files 1 --timeout 180 -- python -B tools/audit/check_steve_throw_controls_live_1111.py --cold-only
```

The gameplay CPU model earned an Alpha companion through the real level route.
Six cloned route states then used controller inputs to face left/right, crouch,
latch, reach lift states 5/6/7, and press B. No player, input-edge, or companion
state was injected. All six launches had the expected original recoil and
pose, consumed B, and completed 17 recovery updates. Ground recovery stayed
crouched through its terminal frame; airborne recovery retained its airborne
state. Both lives remained intact. Cloning is CPU-model isolation, not six
independent emulator playthroughs.

The initial air-case setup released Down before the latch animation finished;
the assertion correctly failed. Waiting for the original bot delay `$FF`
reached the intended states, after which all six cases passed.

Cold loading verified all 134 declared resident edit bytes, 76 injected NMI
cut points, nine readback faults, zero-initialized throw state, and unchanged
384-byte punch suffix. A real Steve → Prince → Steve owner change overwrote
and restored all 224 scatter bytes. Extra initial reads remain 2,050; return
loading read 30,750 PPU bytes. The loaded core still executed the original
direction selection and a six-pixel outbound step.

## Renderer prepared separately

`check_steve_shatterhand_throw_pose_1111.py` and
`steve_shatterhand_throw_pose_1111.s` provide a separate renderer extension.
Root independently reran 96 detached cases: 12 throw-player, 40 ordinary-player,
12 throw-robot and 32 ordinary-robot cases. Native rendering calls are stubs in
this proof; hardware OAM and visible output remain unverified.

The worker is 511 bytes, SHA256
`bc937ab6c81fbe3ec30d2a99e761612eebf6f66e61dc7160c08448fb0514020c`.
Lookup code uses 22 bytes at `$C8A5`, CHR selection uses 11 bytes at `$DA71`, and
the original recovery records need 46 bytes at `$CDC8`. The companion draw
call moves from `$CF9B` to `$CF9D`. A separate signed frame flag at `$C978` must
remain set through the zero-pose reattach frame; the actor's throw selector
alone clears too early for correct drawing.

The helper's additional source-cell check confirmed that thrown poses
`$015E/$015F` use tiles `$6F/$73`, both from sprite slot 5 / CHR711. Eight exact
32-byte fetch comparisons covered both facings with player slot 0 on either
CHR307 or CHR220. Thus those player bank changes do not replace the robot art.

## Next work

Mount the renderer and recovery records into the authenticated candidate;
connect the robot's flight and the frame flag; suppress ordinary orbit and
weapon emission during every thrown update, including reattach. Implement
native contact, two-HP damage, robot damage/destruction and scene retirement.
Then validate actual OAM, collision and a complete Mesen route before replacing
the nightly. No helper-platform changes were made.

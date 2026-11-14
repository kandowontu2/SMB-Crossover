# SMB2 and Doki Flower: actual Downloads checks

Installed ROM SHA256:
`12397b1c2557834f6a2b7e23c9915d5dc40c6cabff7a6ee844c1adebf6564c52`.
These are ordinary controller replays launched from the actual Downloads file.
There are no gameplay seeds, extra helpers, ROM changes or capture files.
All eight full non-shortcut stage passes are recorded separately in
`smb2-postbg-delivery-1113.md`.

## Replay correction and retained negative

The frozen Mario collect controller b6b10f5d reaches a genuine Flower birth,
then repeatedly overshoots its retreat target. Two native runs reproduce
receipt `db83087aa20a8b9a0d6de8abf00f9ca5252f827a1a5900956100ce2c4107e5cd`:
2938 physical / 2600 Main, still healthy at293/176, with no pickup attempt.
This demonstrates a controller limit cycle, not a defective item collector.

The separate followup changes only the Flower-left ordinary input settling.
It releases direction before the estimated stopping point; original friction
and every game byte remain intact. Reverse-text authentication recovers the
frozen controller. The original observations, assertions and bounds remain.
Source qualification and all eight exact controller hashes are in
`smb2-flower-control-followup-1113.md`.

## All eight native collect passes

Each run physically collects the mature kind1 actor at336/119, state128.
Health31/max0 remains; reserve increases0 to3, the actor is erased, sound32
and popup6 occur, and60 ordinary resumed Main updates pass with both lives.
These passes qualify collecting the earned Flower. They do not yet qualify
the subsequent vegetable throw or enemy contact.

| Identity | Physical | Main | Pickup Main | Receipt SHA256 |
| --- | ---: | ---: | ---: | --- |
| SMB2 Mario |849|508|448|`c7e77df63edf96365b120a665f6f2a1382b9cea8b5e16e26025c39b4a04f9b3e`|
| SMB2 Luigi |1016|653|593|`fedab84d8d2f5a3129bf4733f37de40c293e9e02d2d229e36d27ad3b7da21794`|
| Toad |893|530|470|`f192f91d2a58083776b162d0c2e0e5fa48a994a086405666d5cd1d20035db1e3`|
| Peach |975|594|534|`e32cd5b48619e5e7b4011ebdc8bb3e3eff39a42e3ae7bf70a89ae26c7ff82983`|
| Imajin |945|537|477|`a6a5f1f83712e262c5d37b3077729cd7e7a6e528d619c33b98c9fd105799018c`|
| Lina |1145|741|681|`2cf57d79dc29e5f25265314f700a844279a08b6b9df7d0465011c8ef3ad3898f`|
| Papa |1105|681|621|`7b56502eb2dadb03751ba1fd44f8abfbfaa3508b3846192e861225f07f8f946b`|
| Mama |1144|718|658|`9cf712abe0375d9bae281fab23533994fcec8e37e254c5d31ea021626a7a0d45`|

Mario's root session36868 used exact Lua a46346af. Root session97422 ran
the remaining seven in order and terminated successfully. The sole existing
controller slot was overwritten seven times; no new ROM, receipt or capture
files were created. The Downloads sidecar/hash guard passed before and after
each run. Mama's endpoint277/176 is ordinary post-pickup movement; her actual
collector event is329/97 against the mature336/119 item, followed by the same
60-update assertion as every other character.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 600 -- python -B tools/audit/run_smb2_postbg_flower_native_1113.py --followup --variants 1,2,3,4,5,6,7 --scope collect
```

## Retained native Mario attack-approach negative

Root session1277 ran the separately source-qualified Mario hit controller
`204e959e535f99427846fe54d729cff1b483d9e957efe510c7355b6d7a5c4c87`.
Native receipt
`5d9d4a6102795297b28c30fd7dc3cdf7cc0dca5203e4fed5089796c4bd5370fe`
is negative:1184 physical /795 Main, endpoint703/176, HP15 and both lives.
The unchanged healthy-initial-form assertion stops it before the throw
observer. This does not undo the successful collection or establish a
vegetable collision bug.

The real collect at448, pull at509 and carry at540 pass, consuming reserve3
to2. The replay travels to the enemy, enters aim at693/176 on Main778 with
VX24, settles at703/VX0 on791, faces right for two updates and enters throw
phase793. It receives contact damage on795 before the native throw event.
The source run had thrown earlier at695 on784 and defeated its Goomba on789.
Enemy-relative aiming/earlier throwing is now being qualified separately;
the frozen controls, health assertion and this negative remain retained.

## Direct earned throw: Mario pass, Luigi input negative

Root14373 used the existing source-qualified throw scopes, stopping on the
first failure. Mario passes912 physical /571 Main, HP31 and both lives:
Lua `7ffacac34ae161daaf08f45da5691ef8df55f1fa0d35d973d544279f2ac22f52`,
receipt `c3a8a37f2837e91cb7bca7a09d6bb24a69e3a70b798eeb81afb7ace09202b168`.
After collect448, pull509 and carry540, the actual thrown actor is observed
on541 at349/107, kind50/host255, projectile2, lift0, VX48/VY26. Holding clears,
reserve stays2 and30 ordinary flight updates pass. This covers the original
earned throw; it does not include enemy contact.

Luigi's exact throw Lua is
`62338c4a51c3451ddc670498172c58a3ce395831455d9f3b64367a2dbf3b770d`;
receipt `0d96d023493b5cba482790c56bb95a7dba4f7c9256dc826f3313d93e136e6df2`
is negative at the unchanged2600-Main bound (2963 physical),332/112,
HP31/both lives. Pull654 and carry685 pass and spend reserve3 to2, but no
throw occurs. The frozen replay requests B for only the carry-to-throw
transition, then releases it immediately; subsequent source Held/Fresh are0
and Holding stays1. A lost short input pulse is an unresolved lead, not a
demonstrated game refusal. A separately authenticated source-acknowledged
button hold is being qualified, retaining this negative and all assertions.
Variants2 through7 were not run in this stopped batch.

All eight corrected throw and all eight corrected hit source routes now
pass. Those16 source passes do not imply native success: the Mario attack
approach and Luigi one-update input negatives above remain open. A separate
neutral-aim combat controller is also source-qualified for Mario; no native
success is inferred from it. The expanded roster goal remains active and incomplete.

## Source-acknowledged inputs: three actual native passes

Root90336 uses the separate acknowledgement factory8846c50a. For throw-only,
its sole control change holds ordinary B until the source reads it, with a
12-Main bound and release afterward. The hit derivative also retains the
right-facing neutral aim and waits for an unobstructed target within40 pixels.
The old factories, failed receipts, health/reserve/defeat assertions and
game bytes remain intact. A read-only callback authenticates the actual
original `BIT S2Fresh` instruction and records Fresh64/Held64 with Holding1.
Root additionally requires that observation on each passing native result.

| Identity / scope | Physical | Main | Fresh B Main | Thrown Main | Defeat Main | Receipt SHA256 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Luigi / throw |1080|717|686|687|—|`1d7f0818339c781d4023de27f3ebe4799465c06c3d28cb0c7b60196425c09b91`|
| Mario / hit |1210|817|786|787|792|`0818f05912661a3bac3d9cef7f201f1f1acb855c8b543b1f431cf66c84f399cd`|
| Luigi / hit |1445|1044|1013|1014|1022|`c95c698c9fbc4e8b4bb87e0fc5dd20291165e6d9337bda722438504a7d8d534e`|

Exact Lua identities, in the same order:

- `38246a00fa6eda0749bb05c791a6ad13b1a9c48f233dd105157a2190d27547d3`
- `2bb321529317c4ac0afe3a36e9a1d94cb8c25bce657e09ec0e0db346f6bc722c`
- `ed1d738b3cf1d5cf5795904f82b9cae6ee55de66d3b350b168ba2e02d95c37ce`

Luigi's direct throw follows the same collector/pull/carry685 path as the
old negative. Fresh B is now actually observed686 and the actor is thrown687
at335/104, VX48/VY26, followed by30 normal flight updates. This resolves that
short-pulse replay failure without changing the game's attack.

Mario approaches at693/176 with enemy719 on778. Neutral braking reaches
699/VX6 on785; the original throw occurs787. The real native Goomba at713
changes state0 to34 on792 through original object contact and native defeat.
Luigi waits at639/176 until the enemy is within the low-arc range, throws1014,
then defeats the real native Goomba at675 on1022 with state0 to34. Both keep
health31, reserve2 and both lives, and satisfy the unchanged resumed-play
assertions. No ROM/state writes, added helpers or new build/capture files.

The other six acknowledgement hit variants remain under source qualification.
These three passes are not an all-eight combat claim.
GitHub releases remain empty; this controller-only work does not replace the
already verified12397 nightly.

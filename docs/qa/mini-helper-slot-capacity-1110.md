# Mini Mario 1-1 helper slot capacity

This read-only audit binds cartridge
`a1c28fdf0b03bbc652e989083a74fc8365b7a875b821bcb92d63f7cd7144180d`.
It covers loaded outdoor 1-1, world and level zero, area offset `$05`, raw
character `$29`. It asks how many native actor slots can already be occupied
throughout each eight-pixel offscreen admission window.
[Bound cartridge](../../build/mini-graphics-edge-movement-native-1110/candidate.nes)

| Helper left X | Camera right X | Highest enemy-record X admitted | Earlier helpers | Natural occupied-slot bound |
| --- | --- | --- | --- | --- |
| 560 | 552–559 | 592 | 0 | 2 |
| 688 | 680–687 | 720 | 1 | 4 |
| 864 | 856–863 | 896 | 2 | 5 |

`ProcessEnemyData` rounds camera-right plus 48 down to a 16-pixel column.
The exact enemy stream at ROM file offset 19023 has SHA-256
`f091a27d7278196232a796c0fab0f7e44cfea0181b8d0bf69f827655463891da`.
Its first direct records are X352 and X640. The X864 record creates two
Goombas at the current right edge and 24 pixels farther right. The next
direct record is X1280. A group searches slots 0–4 and consumes its record
even if placement is partial. Crossover Hard's group omission at stream
offset 23 is beyond these windows. Native postgame hard mode changes the
Goomba IDs to Buzzy Beetles and leaves the counts intact.
[Enemy admission and group construction](../../src/level_tiles.s#L967) ·
[Enemy stream](../../src/level_tiles.s#L1346) ·
[Crossover Hard variant](../../src/level_variants.s#L177)

The exact terrain stream at ROM file offset 20956 has SHA-256
`162fc0bf0e2e7bd2ecda0ac1bf3551ee5f45a3f116fa6343badda72005c0b4ec`.
Its only pickup before these windows is the mushroom or flower block at
X336. The next possible pickup is the hidden 1UP at X1024. This part of 1-1
has no native spring, vine, platform, or exit actor. The pipe constructor
skips piranhas in world and area zero. Mini's projectiles have separate
native slots, and the raw-41 inventory drop path yields no actor. This gives
the first two bounds even if all earlier enemies and the item persist.
[Terrain stream](../../src/level_tiles.s#L1690) ·
[Pickup allocation](../../src/level_tiles.s#L2250) ·
[Pipe constructor](../../src/level_tiles.s#L2897) ·
[Mini projectile slots](../../tools/reference/mini_mario_fireball_1103.s)

At the third window, camera-left is X601–608. The native left erase edge
for a Goomba or Buzzy Beetle is camera-left minus 73, including the incoming
borrow. For the pickup it is camera-left minus 72. Allowing one prior camera
update of up to eight pixels still gives a left erase edge of at least X520.
The X352 enemy and X336 item are west of that edge by then.
[Screen edge calculation](../../src/common.s#L27) ·
[Horizontal actor culling](../../src/object.s#L429)

- The first pipe covers X448–479 and starts at Y176. Grounded enemies use
  a foot probe at X+8/Y+24 and a right side probe at X+16/Y+20. The first
  Goomba or Buzzy starts at Y176 and settles on the continuous ground before
  reaching the pipe, even if Mini reverses it or kicks the Buzzy shell.
  The shell retains native terrain collision. Mini has no actor carry or
  throw that could place it on the pipe.
- A mushroom moves at up to one pixel per update, and a flower stays at its
  block. The last raised brick ends at X399. Its last possible foot support
  or bump is at X391. Even a bump from the top row at Y144 starts the native
  actor at Y118 or farther down after the two-pixel rise. A conservative
  replay of the native gravity arithmetic over all initial fractional
  phases gives at least 44 pixels down after 40 movement updates, starting
  with Y speed −3. The pickup reaches the pipe's side below its top and
  meets the ground and solid shaft before its base reaches X448. Even if
  Mini walks back and bumps the item block with camera-left at X351, the
  item enters its cull-eligible rise state within 20 updates. Camera-left
  needs at least 31 updates to reach X593 at eight pixels per update.
- A defeated first enemy can pass through terrain, with at most one pixel
  of horizontal motion per update after native defeat. Even if defeated
  at X447/Y156 with an initial upward speed of −3, its Y reaches high byte
  2 by movement update 58 and native graphics erases it on the next update.
  That puts its base at X506 or earlier. The faster −4 upward brick-bump
  death can only start at an earlier raised block. Even with base X391/Y118
  it reaches high byte 2 by update 78 and is erased by X470.

[Terrain probes and enemy landing](../../src/collision.s#L1936) ·
[Native collision adders](../../src/collision.s#L112) ·
[Enemy defeat and stun](../../src/collision.s#L1061) ·
[Gravity arithmetic and speed limit](../../src/common.s#L369) ·
[Power-up movement and culling](../../src/object.s#L3284) ·
[Camera step](../../src/player.s#L1535) ·
[Vertical actor culling](../../src/sprite_render.s#L166)

The terrain buffer has 32 columns and initializes 24 columns ahead of the
starting page. Each subsequent 32-pixel scroll adds two columns. While the
old actors can still matter, the renderer has yet to reach X960, where the
X448 pipe column would alias. Normal death or pipe room loads clear actor
RAM. The 1-1 checkpoint starts at page 5, and the bonus pipe at X912 comes
after the third helper's crossing. The 1-1 start-level cheat starts at page
zero. The injury, air jump, vertical wrap, and countdown cheats write player
or timer state. For Mini, Full Power follows exact PRG 124 `$AA6C` through
the raw-character gate, PRG 79 `$B790`, and PRG 65 `$B0D7` to the carry-clear
return at `$AB4F`.
[Area initialization](../../src/game.s#L832) ·
[Terrain parser cadence](../../src/game.s#L315) ·
[Checkpoint](../../src/player.s#L353) ·
[Cheat implementations](../../src/cheats_four.s#L230)

The retained a1 replay constructed all three lifts in slots 5, 4, and 3
at camera-left X273, X402, and X578. An earlier matching scene at camera-left
X599 showed the three expected later Goombas and three existing lifts. The
eight-pixel-window capacity conclusion is source-derived. This audit contains
no powered or Hard native stress replay. It assumes naturally initialized
actor records and an admission call during the offscreen interval. A controller
or engine path that skips the whole interval needs separate timing proof.
[a1 native constructor observations](../../build/mini-graphics-edge-movement-native-1110/mini/capture/camera-lifts.json) ·
[Earlier six-actor scene](../../build/mini-76bd-falling-profile-1110/capture/instruction-sample.json)

## Powered injury can skip the offscreen window

The private eight-pixel candidate
`9debe5a9cb8046be06a3ed9adef95b3fc1909935f52a5421720ea4400c71a5e8`
cleared the controller-only route with all three helpers and 17 missed reads.
Its separate pickup replay established genuine powered Mini at status 1.
The capacity bound still holds. The current admission call can be skipped
while the camera moves, so the eight-pixel candidate is rejected for delivery.
[Private route timing](../../build/mini-helper-activation-native-1110/mini/capture/timing.json) ·
[Native earned mushroom](../../build/mini-helper-activation-native-1110/native/power/capture/result.json)

The exact injury path has these three relevant steps.

1. `ForceInjury` in physical PRG 126 `$9771` can set engine mode `$0A`,
   player state `$01`, and `TimerControl=$FF` at `$97C2–$97CE`. Each native
   GameLoop update decrements the timer. `PlayerInjuryBlink` in physical
   PRG 1 `$A46F` calls normal player control at `$A47D` for all 39 values
   `$EF` through `$C9`. At `$C8` it restores engine mode `$08` and returns.
2. Player control at PRG 1 `$A118` calls `$A5D7`. Its raw-41 mode check at
   `$A62A–$A632` jumps to vanilla movement at `$A6C1` during injury. It
   bypasses Mini's authenticated row-zero call and lift scan. The private
   `MiniHostMain` at `$AF4D` also requires mode `$08` and a zero timer.
3. Native airborne movement calls `$8C8A` from PRG 1 `$A753` and stores a
   fresh horizontal delta at `$A756`. Ground movement similarly stores it
   at `$A704`. The call at `$A13C` reaches `ScrollHandler` at PRG 1 `$A9D4`.
   At a player screen X of at least 112, with no scroll lock or side hold,
   native scroll applies the full positive delta. The extra camera catch-up
   at `$AA78` declines mode `$0A`. The native dry right-speed cap of `$28`
   in Q4 permits up to 98 camera pixels across those 39 updates, including
   fractional carry. Individual positive deltas are at most three pixels.

[Injury setup](../../src/collision.s#L465) ·
[GameLoop timer](../../src/game.s#L83) ·
[Injury state dispatcher](../../src/player.s#L783) ·
[Native movement and speed cap](../../src/player.s#L1196) ·
[Camera update](../../src/player.s#L1535)

A reproduction target combines the legal powered status with the retained
contact geometry near player X711, camera-left X599, and Goomba X714. A
powered side hit there with Mini facing right, positive horizontal movement,
and no side hold starts injury at camera-right X854. Hold Right in the
remaining flat approach. Ten positive one-pixel camera moves reach X864
before the player reaches the X736 pipe's side. The scan misses the entire
X856–863 window. Hard already applies its native no-stomp contact policy to
Mini, and Easy can take the same injury through ordinary side contact. The
contact geometry and earned power are observed separately. This combined
injury path is source-derived and has no native reproduction capture.
[Retained contact geometry](../../build/mini-76bd-falling-profile-1110/capture/instruction-sample.json) ·
[Mini body policy](../../tools/reference/mini_native_contact_1110.s)

The earlier 80-pixel window also permits late visible entry. A hit just
before its third window at camera-right X831 and player X688 needs 33
pixels of injury scroll to make the helper's X864 edge visible. The pipe
starts at X736, beyond player X721 at that threshold. The 98-pixel source
bound exceeds the full 80-pixel window, although a full-window skip would
also have to clear the pipe during injury. No retained replay shows that
full skip. An injury-only hook at physical PRG 1 `$A47D` could run the normal
player-control routine and test the resulting camera position before the
enemy loop. This would require source funding and qualification of the
loader map, normal foreign return, and actual constructor timing.

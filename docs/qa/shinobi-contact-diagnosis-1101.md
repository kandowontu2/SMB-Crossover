# Shinobi contact diagnosis

Private candidate `build/shinobi-camera-1101-v20/candidate.nes`, SHA256
`fe4e9a6d5aef0c2e3848a501f487e7791cd75b9db5cf5297ebad395162560ad9`.
Not installed; it predates the delivered Metal Storm v41 optimization.

The first four-pipe controller has not passed. Releasing attack before jumping
crosses the first two pipes but loses a life around X648. Holding repeated
attack through the jump prevents the original state machine from taking the
jump; that failed controller is not evidence of inadequate jump height.

The read-only HP trace in `build/shinobi-contact-1101-v21/native/capture`
shows the original seven-hit counter and recovery intervals of roughly49–61
physical frames. Duplicate writes in the trace are the6502 DEC dummy and final
writes, not two independent injuries. Five hits are from the opening Goomba;
two more near X665/648 exhaust health. No instantaneous health-drain bug proven.

Natural standing shuriken use source Y182; crouched shuriken useY196.
The original pose9 hitbox is X-2..X+2, Y-8..Y. The crouch controller correctly
stops atX192 and emits lower shots, but they still fail to hit the Goomba.

`build/shinobi-shot-trace-1101-v22/native-bounds/capture/shots.json`
records actual arguments at `SprObjectCollisionCore`. At physical frame875:

| Box | Left | Top | Right | Bottom |
|---|---:|---:|---:|---:|
| Native Goomba |187|198|197|204|
| Original crouched shuriken |187|188|191|196|

The horizontal overlap is real; the native six-pixel-tall Goomba hurtbox is
two pixels below the shot. This explains the miss without changing source
weapon placement. `src/megaman_weapons.s`, `NativeEnemyBounds`, already documents
this native Goomba limitation and uses the full visible16x16 body beginning at
native enemy Y+8 for hosted weapon contacts.

Next: adapt Shinobi's guest-enemy contact boundary consistently with that
existing visible-body policy while retaining original projectile motion and
hitbox. Do not lower shots arbitrarily or edit the shared native enemy table.
The cached kernel/metadata are nearly full, so replace the existing expensive
query/borrowed-box sequence with a compact equivalent rather than overwriting
unowned space. Preserve clipping/page boundaries, exclusions, score/SFX, source
phase, caller scratch and mapper state. Then replay crouch combat and1-1.

Graphics still need followup: later screenshots contain HUD-area sprite
artifacts and dark body colors. Existing smoke checks are not a release claim.

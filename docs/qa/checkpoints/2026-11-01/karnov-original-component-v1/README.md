# Original Karnov component — private source progress

Karnov is still **COMING SOON** in the installed85-character nightly. This
packet recovers his own NES code and art; it does not enable a Rygar reskin.
The donor SHA and finite verification scope are in `handoff.json`.

The controller covers all32 source selector roots, including the native
injury-timer prefix, jump/walk/crouch/attack and ladder/flying/swimming/script
states. Its generated original instructions and tables, plus explicitly
untouched fixed-bank ranges, reconstruct the complete original16KiB exactly.
The corresponding weapon-bank reconstruction reproduces its8KiB exactly.
Those are byte-reproduction statements, not semantic disassemblies of every
untouched byte. The private actor/weapon/clear component occupies3,969 bytes.

CPU checks compare4,096 actor boundaries and5,760 coherent movement updates.
The declared floor/ceiling cases produce48-pixel normal and88-pixel boot jumps.
Another2,688 projectile boundaries and1,440 coherent updates cover all nine
slots, single/double/triple fireballs and four boomerang phases, catch/reuse,
miss/reversion and the actual clear helper. In total30,848 engine executions
pass. Private RAM/events/flags/Y/SP agree; differing A/X bytes are accepted
only with last-writer proof that they are relocated dispatch-pointer bytes.
Sound/terrain/scene callbacks are explicitly isolated in these comparisons.

Original Mesen observations establish the actual loop order: body rendering,
shot rendering, player update, then projectile update. A separate original
PPU observation verifies the source body page and default0F/28/16/0F palette.
All256 original six-cell render cases retain source pixels, positions and
flips after moving their tiles from sprite window4 to0. The five original
pages and134 unique tile pairs include70 deliberately hidden source cases.

The current85 ROM has an unused13-page ship tail after the live world/UI
pages. Explicit source splits reserve399..<407 for a future kernel and
407..<412 for body patterns. The actual menu helper's remaining FF pad
reserves2,432 resident bytes in bank29/B630..<BFB0. Rebuilding these source
partitions reproduces every installed ROM byte and every old symbol. PRG125
is an active post-link fixed/DMC mirror and is excluded from reclamation.
No RAM, executable host gate, new admission or nightly update is made here.

Health/options/pickups, real SMB terrain/contact/camera/scene adapters, native
sprite publication, audio, guarded owner loading and interrupt qualification
remain required. The [original Data East manual](https://www.gamingalexandria.com/highquality/NES/Karnov/Karnov%20-%20Manual%20(Searchable).pdf)
documents A jump, B shoot and Select option activation; those original option
controls and stock limits still need their actual source integration.

`source.zip` contains only this component, art, recipes and source partition.
`native-reference.zip` keeps bounded original-ROM observers, compact field
logs and selected PNGs. No ROM, object, debugger, video or frame-image forest
is archived. Reuse existing frozen inputs and recover only exact needed files.
The full requested roster and every-character level/powerup goal remain open.

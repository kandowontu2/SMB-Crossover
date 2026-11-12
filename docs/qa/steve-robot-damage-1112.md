# Steve robot damage and destruction

Root independently reran `check_steve_shatterhand_robot_death_1112.py` through
the bounded runner. Its 271-byte source worker matched the pinned Shatterhand
cartridge in 3,584 damage comparisons (606 fatal outcomes) and 1,200 destruction
steps. Sixteen full sequences covered both facings, both gravity polarities,
and four clock phases: each lasted 45 updates with 28 visible updates.
Worker SHA256: `c54a0030a7e49d11829f111ea7a2e29b15567c5fc9d5e7b253e09964d67279b7`.

An admitted positive contact resets robot age to zero and queues the original
hit cue only if the queue is empty. Damage uses the low nibble; values 8–15
become one. Fatal damage keeps the previous HP byte, resets angle, sets timer
$20 and actor $FF. The fatal actor must bypass normal flight and surviving
receipt-bit cleanup. Surviving actors increment age before their next orbit;
new contact requires age at least $0C. Fatal actors retain age zero.

Destruction drifts one pixel per update while the timer counts down, blinking
with clock bit 1. On the 1→0 transition it clears projectile types and emits
the original destruction cue. Subsequent updates drift two pixels and animate
the original $01DC/$01DE/$01E0/$01E2 rows before retiring. The detached proof
models the host projectile clear callback; no live emitter arrays are changed.

The art audit found four donor cells but two already exist in CHR711 as Alpha
shot tiles $77/$79. Only 64 new CHR bytes and 44 bytes of pose records are needed.
These bytes are not yet allocated. Hurt palette and gravity-flip attributes
must be applied when rendering; neither is demonstrated by this CPU proof.

`steve_throw_damage_1112.s` adds a separate 43-byte native outgoing-damage
adapter. It sets the robot's return receipt before checking enemy hurt cooldown,
subtracts two HP on an eligible hit, and tail-calls the existing native defeat
leaf for HP ≤2. The bounded `check_steve_throw_damage_1112.py` passed 432 cases
across actor, slot, HP, cooldown and queued sound combinations. Its defeat call
is a sentinel: this does not claim a real native kill, score, or sound test.

Both checks generated zero files. All these routines remain detached pending
live contact admission, linkage, graphics allocation and Mesen verification.
Downloads and the Current IPS remain unchanged.

The helper extended the donor audit to execute eleven original contact cases
through PRG8 `$83E2` and sixteen original `$A6DA` graphics publications. Root
reran the extended audit successfully. These confirm that flag `$21` can damage
the robot without an outgoing hit/return receipt; a normal surviving overlap
sets the receipt even during enemy cooldown; and fatal contact overrides the
actor with `$FF`. The shot-clear callback must preserve `$92/$93`, which hold
the already prepared death movement delta. Detailed source seams are recorded
in `steve-robot-destruction-1112.md`.

## Combined live-field link

`link_steve_throw_combat_1112.py` assembles the verified flight, destruction,
rectangle, overlap, target-search and damage routines with actual live field
addresses. It packs the routines contiguously from `$AB00` in a two-pass link.
The row uses **656 bytes**, leaving **368 bytes** for contact/update hooks.
The separate nine-byte emission gate remains at `$D777`. Zero-page scratch
bindings reduce several routines relative to their detached fixtures.

`steve_robot_clear_shots_1112.s` supplies the destruction callback: it clears
Alpha type/timer/power and all eleven Laserbot type entries while preserving
the prepared `$92/$93` movement delta. A directed CPU execution with all types
active verified those clears, the unchanged delta and a balanced stack.
The bounded linker check completed with no generated files.

The proposed geometry scratch uses `$00–$0E` only during synchronous contact
processing. Actual caller/interrupt lifetime checks are still required; the
link alone does not prove scratch ownership. This combined code is not yet
mounted in a candidate or connected to native enemy collision.

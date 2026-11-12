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

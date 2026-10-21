# Samus idle weapon work on MMC5

Accepted46 saves142 CPU cycles per ordinary idle Samus update in all20 matched
standing/walking scenes. SamusWeapons changes242→100 cycles and its inclusive
ProcFireball_Bubble caller1052→910. All3,600 paired updates across Samus, Mega Man
and Bass retain all204 recorded gameplay fields. Draw counts, physical frames,
DMA counts and measured enemy visibility are unchanged. The six-Goomba walking
scene still draws30/60 frames: this is a CPU saving, not a visible lag cure.

The27-byte shortcut applies only on MMC5 with an active engine, all three beam
and all three bomb slots empty, and current B released. It preserves initial
sprite cleanup, firing-pose countdown, shared bridge cleanup and return ABI.
It leaves body contacts, inventory drops, remaining weapons, freeze/Screw Attack
and swimming bubbles live. Held B retains the old path and costs one extra
branch cycle. MMC5 SAMUS has15 free bytes; MMC3's entire ROM remains identical45.
Header and CHR bytes are unchanged.

All761 existing emulator checks pass in one unchanged-fixture run, with every
raw log frozen and ROM-bound. The actual compiled CPU proof passes8,508 cases:
8,448 independent idle/flag cases and60 live/guard cases, including all10,240
gameplay RAM bytes and ordered hardware writes. Only actual discarded push
cells and label-proven farcall operand relocations are normalized there.

Each mapper passes138 matched native caller cases, including IDs0..12 and Lance,
live beams/bombs, B/Select, drops, freeze/Screw, pause and swimming bubbles.
Native checks compare return/entry ABI and the explicit effect/scratch projection;
the complete10,240-byte snapshots are also retained. Fresh extraction of401
source files rebuilds both ROMs byte identically.

The first native fixture fails on accepted45 because forced life-loss engine
and Y-high2 arenas contaminate later lifecycle updates. Its original source,
failure and raw snapshots remain intact. V2 preserves all138 case contents:
128 safe cases share a process, while ten hazardous cases each cold boot and
stop at the actual caller return. Bounds/assertions remain unchanged. An attempted
all-character crowd expansion also fails its old45 no-injury precondition for
Pit; it is retained separately and contributes no paired performance claim.

Outlines remain OFF by default, and their option row stays gold. Samus has no
ordinary stomp in the2.02 source; upgraded Screw Attack supplies contact damage.
Dense-scene lag/flicker, remaining source/weapon differences, all14 complete
final-hash routes and all-character final audiovisual review remain open.

Evidence is bound in build/checkpoints/roster-audit-v46/manifest.json. The broader
goal remains active; this component does not certify source-perfect behavior.

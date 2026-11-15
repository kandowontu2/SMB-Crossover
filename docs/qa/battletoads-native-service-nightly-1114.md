# Battletoads native-service optimization

Private candidate: `ae669c7ec7536f1c912b3000597be7b3416c20f312638b2589f52fab55f0bc01`.
Parent verified nightly: `5715bb7e3c772350a2a7420ec9061eabd948964a8789e5d348c49d3cfb3c57ee`.
This note records version-scoped evidence, not whole-roster completion.

The candidate changes160 bytes inside347 funded bytes: public router224,
head/side prefix25, shared side service94, and four prefix operands. Complete
BT8192-byte code/data, cookie, full BtCheck, score correction, graphics,
physics, level data, helpers and every other byte remain exact. The intended
fault-contract change is explicit: raw33 native terrain queries use the real
native query even with invalid private cache; private services still reject.

The old source-only lease is unchanged. Root's private candidate lease is
`allocations/battletoads-native-service-candidate-1114.json`, SHA256
197cfe60a47f505ad818eb01a84d51cf3d4ed46f19c679cc62840d15553adae5.
Initial candidate runner55363 stopped before any output write or Mesen launch
because a hand-copied old-router preimage contained two extra JMP entries.
The corrected receipt stores exactly36 repeated entries plus its suffix,
validates the frozen preimage hash/length, and roundtrips the exact parent.
The candidate bytes never changed; the malformed c011 draft is superseded.

Root's independent source profile28386 reproduces the frozen model exactly:
48idle mean36604.0625 to27528.0625 cycles,32Right36864.5625 to27788.5625,
9076 saved in every Main, complete game/physicalRAM/OAM/VRAM/maps/SMC parity.
Opcode ABI, damaged cache, interrupts, both full source routes, declared
executable ingress and lifecycle parity are in the frozen model/ingress QA.
The explicit DeathStart component staysengine11/lives2 for360 Main in both
inputs; that is not natural death/respawn evidence.

## Native baseline

Root97226, actual Downloads571, terminal PASS. Lua
f06aa6a24d9d6e135931b56bb350acbbdb66952e29e82fd209ee93ececc04236;
receipt be7def6b7e6dde1922a06761c542ffac7764b1e0b23026002808248119933441.

| Phase | Completed Main | Physical frames | NmiSkipped delta |
| --- | ---: | ---: | ---: |
| Neutral idle | 48 | 72 | 48 |
| Right | 32 | 48 | 32 |

Both phases have zero active actors, HP47/lives2/power0/Star0/Y176. Idle stays
X40/camera0; Right endsX81. The inherited controller label says optimized
because it is shared with the upcoming candidate observation; this result's
actual authenticated ROM is571. No new candidate cadence, stage or installed
improvement is claimed by this baseline.

The only active output is the existing two-file flag slot. No captures,
videos, logs, states, patches, backup ROMs or releases are created. Other
project Mesen sessions remain untouched. Candidate native gates and any
Downloads delivery must be recorded below before claiming installation.

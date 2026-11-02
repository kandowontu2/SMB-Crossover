# Prince shared/native proposal — November 2

Current status: private CPU qualification passed; no shared grant, menu admission,
ROM artifact, emulator launch, or installation. Root owns the native queue.

The exact proposal is `build/prince-actor-1101-v1/successor-proposal-v26.json`.
It starts from parent-delivered Bub v9 `613b3300b09e530ec920835b95df53f3115d865ed854e273809d4cafa52407ce`
and reconstructs memory-only successor
`11d58b4dc7090860de54b4269c557256b28f4a093f2484af9a9c599b0817adcf`.
All six Bub v9 event spans, containing all 55 actual event changes, remain exact.
Every changed byte has a declared preimage; all other bytes remain exact.

| Measured storage | Used | Available |
| --- | ---: | ---: |
| Source-funded Sh/Ex frame reclamation | 113 B: manager 92 + selector 21 | 141 B |
| Existing PRG79 native router | 76 B | 77 B |
| Existing scene gate | 19 B | 19 B |
| Proposed third bootstrap descriptor | 8 B | 18 B common-worker spare |
| Private runtime Fresh prefix | 13 B | 17 B owned alignment |
| Private metadata resolver/reset tail | 95 B | 109 B owned tail |
| Granted 43-carrier backing | 44,029 B | 44,032 B |

The actual source phase order is retained: advance/projection, empty phase,
controls, then original falling/terrain. Native Main epochs drive that clock.
The C09E tag reuses existing world SavedY only at synchronous public entry;
world code writes SavedY before its sole read. This needs the explicit owned
lifetime amendment in addition to the existing geometry grant.

Qualification receipts in the same bounded output:

- `shared-frame-CPU-v22.json`: 6,000 fixed public transport cases, 964 real
  IRQ/lag-NMI cuts. Row2 cost increases by 131 CPU for Sh, 15 for Ex, 17 for Bub;
  this storage factor is not an idle performance improvement.
- `shared-frame-consumers-v22.json`: rebound to actual installed 613b; 2,880
  real router cases, all 74 veneers, finite original Proto art/table closure,
  and no remaining reader/control path in the reclaimed tails.
- `successor-foreign-CPU-v28.json`: 5,850 exact-613b foreign public cases,
  128 full-header byte rejections, and 768 raw256-by-three-cookie selector cases.
  Full SMC, ZP, native/private state, maps, and public register ABI match.
- `successor-services-CPU-v27.json`: real shared worker, two verified bootstrap
  rows, all three decoded streams, genuine source constructor and both complete
  header commits; 7,278,020 CPU and 28,650 buffered PPU reads. Four warm
  Fresh/scene cases, 16 native public movement epochs and 16 duplicate rejections,
  25 world SavedY write/read pairs, and 456 real public IRQ/lag-NMI cuts pass.
- `cold-successor-v25.json`: all three codec outputs match; unread source bytes
  survive the metadata staging split. Cold fragment C300..C500 is within the
  existing uninitialized source-state lease. No byte above DD32 is borrowed.

The initial AA73 SMC-table binding was wrong. The earlier apparent parity
receipt omitted page1 SMC comparison and is insufficient. Its negative is
retained in `frame-negative-v22.json`. The corrected AA61 symbol is derived
from the assembled ShCookie and adjacent source-declared 5/9/9 byte tables,
verified against actual current bytes, and explicitly covered by full SMC tests.

Only movement, graphics ownership, original-art draw, Fresh, ROM retirement and
scene construction are currently bound. Other rows explicitly return Cclear.
Palette, native collision profiles, original hurt/health/combat, actual menu,
native Main/respawn and full 1-1 remain required before a playable claim.

`palette-health-authority-v29.json` records natural original palette1 hues
27/16/20 (hex). Original 8574 only changes HP/flags, with no actor reaction.
Original 6DC controls a background flash countdown, not proved invulnerability.
The separate original combat reaction E95A and its action74/action69 admission
must be recovered before native injury mapping. No cooldown was invented.

No helpers have been placed or qualified for Prince. A helper is appropriate
only after an actual original-ability crossing test fails. The previous 36-file
source checkpoint and its archive remain byte-for-byte unchanged.

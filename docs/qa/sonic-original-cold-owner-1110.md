# Original Sonic: relocated core and seventh cold owner

This is an **unpublished, in-memory source proposal** over public c10, SHA256
`c10b7d87f466bf028096bddd33b7ac2baee242870ee83ccc4eebd529af57bd7f`.
No candidate ROM, capture or other build artifact was written. The nightly
still uses the original-art Mario-host Sonic prototype. Public raw43 scene
and service admission remain disabled; a cold cookie is not a playable actor.

The relocated original ordinary-frame core is5,526 bytes, SHA256
`e3606c66ae062243e669809a54edce4019586f2097858480a60da834b3c2657d`,
RAM3 A000..B596; OrdinaryFrame isB3EC. Source qualification reproduces the
earlier4,864-byte component before relocation and compares7,297 whole frames,
40 consecutive80-update episodes,391 animation leaves and12,288 indirect
pointer/flag boundary cases. All four indirect sites are covered. It uses no
ZP instructions/writes; only four private SMC operand bytes change. Ordinary
fixture updates take2,159..3,130 cycles. This does not establish host cadence.

The fixture map C800..D7FF and flags D800..D8FF are **test-only** and overlap
the real metadata/startup window. Native PointRead and16px shape adaptation
remain required; see the [exact source/lifetime map](sonic-native-policy-map-1110.md).

Storage uses the existing
[conditional Zelda-II duplicate-page alias](allocations/sonic-sms-fairy-repack-1110.json).
Only after that exact atomic table change, pages321..327 carry seven padded
code rows and328 carries metadata. The117-byte immutable boot atD25E copies
and reads back all7,168 bytes. Only1,642 additional RAM3 bytes are currently
loaded after the core; the remaining992 bytes beforeBFE0 would require an
eighth carrier/boot row. Source actor initialization is deliberately absent.

Resident funding preserves live users:

- Retired, unreferenced fixed demo entry126:88D8..88EA holds the16-byte Sonic
  cookie plus two pads. The disabled native9 demo data are **not overwritten**
  by the combined proposal. Source and actual current callsites prove there
  is no remaining attract-mode caller.
- Sh's65:ABD4..AC15 carry-result function factors from65 to59 bytes. Both
  current imports move toABD5, and the cold-owner extent grows exactly one
  byte, toAB72..ABD5. AC10..AC15 remain unused padding.
- Common cold descriptors remove the statically/dynamically unread fixedD0
  byte. Zero initialization saves two instructions' bytes; existing resident
  descriptors save three. The five funded bytes hold the Sonic descriptor
  at123:AFFA (`01 00 09 48 01`). Typed filtering remains66 bytes; Getsu's
  following live name tail remains untouched.
- The99-byte common extent contains all seven descriptor pointers, eight
  cookie pointers including Sh, seven retirement lows, the three actually
  used retirement highs, and the12-byte moved DK descriptor copier. The
  actual zero-low branch dominates every high read. The new owner has no
  native associations and therefore no retirement callback yet.
- Prince's current immutable cookie movesAB9D→AB9F. Any later private Prince
  fix must explicitly rebase/compose its cookie; the earlier fixed-offset
  Prince candidate is not disjoint from this proposal.

Combined in-memory image SHA256:
`d07012de9762e93ca76cb283ba84e9b8a9a7bd532364fd94ce4ca6101687cb72`.
Sonic cookie: `a72b0160f88afdf1d404f6a8dc196eb1`.

Actual CPU qualification passes:

- All six existing owners' cold/warm results, complete RAM, maps, PPU traffic,
  caller ABI,192 cookie poisons,18 failure pairs,36 guards and six retire pairs
  retain exact behavior. DK's already-invalid staged descriptor has only its
  explicitly qualified dead-format bytes normalized on readback failure.
- Sonic copies/verifies all eight carrier rows:16,400 PPU reads,300,690 CPU
  cycles, minimumSP187. Warm calls copy nothing.32 one-byte cookie poisons,
  eight real write-protection/readback faults and six cold guards reject.
  Both headers commit only after complete readback; failed copies invalidate
  both. Six existing→Sonic→existing transitions and foreign retirement pass.
- Actual forced-blank NMI/unmasked IRQ cuts cover owners37/38/40/41/43:
  NMI counts485/573/899/745/816,145 IRQ cuts each,24 interruptions resumed in
  the original full cold traces, minimumSP165. Each Sonic startup row is
  distinguished using its real R2 counter. Real handlers preserve private RAM,
  R0..7, SMC, live stack, PPU cursor and mapper state with only the existing
  pending-map-write normalization. This is cold-only, not hot-frame proof.
- Sh's moved cookie index7 and factored carry publisher pass1,188 paired
  owner/header/flag cases, including decimal-set NES flags, with exact live
  state, palettes/CHR and mapper parity. Only dead stack return PCs differ.
- All100 current named menu entries remain exact. The actual public selector
  explicitly rejects raw43 even with its valid cold headers.

Reproducible zero-output checkers and SHA256:

| File | SHA256 |
|---|---|
| `tools/reference/sonic_sms_relocated_core_1110.py` | `f031aad8dfac2b9586df81f303a6b9464db6941095321af23e791a579562b10d` |
| `tools/audit/check_sonic_relocated_core_1110.py` | `4b7b62db9929c59906a1790da10d0a87eb605508ada19519d95355e3c4387162` |
| `tools/reference/sonic_sms_compact_cold_worker_1110.py` | `9be550fe16764fd0eeef3f429d453883fc26edf1d8f4710423eebc8d04939bd2` |
| `tools/audit/check_sonic_compact_cold_worker_1110.py` | `1cec5df468a98aba15503e08926306e5a127fc1a416d74ff47c48ac0afa05bf4` |
| `tools/reference/sonic_sms_cold_payload_1110.py` | `2785c56fe2c625a73c427ac75987b24b64f8ea73065fa0dcbfb2ea4d534a3590` |
| `tools/audit/check_sonic_cold_payload_1110.py` | `65af914b08ee7f014ff9eea64860b9bcff0be7bdc7d0c956c383822d9a382a06` |
| `tools/audit/check_sonic_resident_funding_1110.py` | `4c4a697977c134cab394cdc58e3318752682376c9be11be371da930b56918573` |
| `tools/audit/check_sonic_seventh_cold_owner_1110.py` | `aa5bbd741efd62d153078aed6ac3c046e616339fe7fcda947c71dd44e66a3e80` |
| `tools/audit/check_sonic_seventh_cold_vectors_1110.py` | `6c52a25767dd2666aad47a875d70014145e39756ec76b4feb4722afd91edb63c` |
| `tools/audit/check_sonic_seventh_sh_parity_1110.py` | `01cc9b721a9cbd9336282ac1367e7cdc330f2e1e4e71f25221b8613b85e7ce2d` |

Every producer ran through the bounded wrapper with `-B`, one reserved file
and zero written outputs. The reservation directories do not exist.
Native terrain/shape adaptation, original constructor/epochs, full service
bridge,24px rendering, rings/damage, audio, hot interrupts, real gameplay and
the final Mr. Gimmick menu placement remain unfinished.

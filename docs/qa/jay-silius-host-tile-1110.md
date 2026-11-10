# Jay McCray host terrain seam

The examined parent is `47a7a6aeabe2cc7db593f431591e52331b834485b3d7638e3f10f95cbf43db4b`.
Mike, Jay and Steve share raw 16. Their existing selection is `$730B & $60`
with values `$00`, `$20` and `$40`, respectively. The other bits carry live
continue and campaign information. A Jay-only branch must test both raw 16
and masked `$20`, before executing any private code.

| Current binary entry | Responsibility |
|---|---|
| PRG96 `$A521` → `$A2CB` → `$A0F5` | Mike movement and `SavedJoypadBits` edge handling |
| PRG96 `$A57E` → PRG98 `$A000` | Separate Mike weapon update |
| PRG96 `$A540`, `$A6C1` | Mike body and object drawing |
| PRG96 `$A763`, `$A78D`, `$A7AA`, `$A7C6` | Body policy, probe adder, box, and head consumer |
| PRG96 `$A6EF` → `$A090`, `$A704` | Scene/reset and life inventory hooks |

Three real menu-confirmed CPU openings each reached active 1-1 at X40/Y176
with two lives. The same 60-update opening controller ended at X132/Y112.
Eight more ordinary Main/NMI updates per identity each entered Mike's
movement, input, weapon, head, graphics and draw endpoints eight times.
The native input byte observed at `$A0F5` equaled the controller sequence.

The Mike head consumer invokes native `BlockBufferColli_Head`, then applies a
grid-motor correction that rewrites native Y and cancels Mike's `$5C06..$5C08`
jump fields. A future Jay motor needs a dedicated collision admission that
retains native block and coin effects while preventing Mike's old correction
from overwriting donor state. Mike's weapon callback remains independently
reachable even if his movement ingress changes. The `$5C00` actor page, `$5F30`
persistent inventory and `$7400/$7500` StarTropics audio arenas are live.

## Terrain query

`tools/reference/jay_silius_host_tile_1110.s` replaces only the donor `$D002`
sample contract in an isolated CPU fixture. CF07 still owns the probe order,
geometry and contact response. The adapter consumes the donor coarse Y and X
and the original CF07 direction. The future caller must capture that direction
before CF07 reuses Y for the probe list. On return A contains the class in the
high nibble for even X or the low nibble for odd X. X is preserved, Y is the
original packed byte index, C is X parity and N/Z describe A.

The half-open column interval starts at the native screen-left column and ends
at the current parser cursor plus one only during phases 1–3 and 5–7. The
reader checks initial column completion, parser phase, ring cursor congruence
and a positive interval no wider than 32 columns before reading either native
buffer. `GameLoop` makes the foreground frame private through `NmiDisable`.
The level parser runs at the end of the engine update. Regular NMI publishes
the queued rendering work and the lag NMI preserves the private foreground
frame. The leaf's intended caller is the ordinary, unpaused engine-8 actor
update, with its private bank and scratch mapped and authenticated by the caller.

Native solid nonclimb cells become donor class 1. Native coin tiles `$C2/$C3`
are passable because the native collision consumer handles them before treating
them as walls. Hidden `$5F/$60` cells block the original rising head direction
only. The native temporary hit-block cell `$23` retains its solid attribute.
The raw tile and attribute are published per sample for a later effects bridge.
Failure returns a nonzero status and a conservative class-1 nibble without
reading the buffer. A future frame wrapper must distinguish unsupported queries
from real terrain, including the lower edge of the buffer and native pit/death
handling. The leaf does not award coins, bump blocks, create items or move Jay.

The bounded stdout proof assembled 347 bytes and used 10 fixture bytes in
physical RAM2. The checker compared the direct leaf against 940 live cells and
120 stale or uncommitted cells across all eight actual Jay parser phases. The
invalid probes performed no buffer or attribute reads. It also checked 32
actual native buffer-address calls, 5,120 directed tile/direction cases, 28
explicit guard negatives and 282 matches against the original donor `$D002`
for the same class in both maps. Matching cases preserve the parity nibble,
AXY, relevant flags and stack contract. The donor CPU replay independently
reproduces the three prior hardware anchors. The leaf's maximum measured
valid/query-cycle count in the live fixture was 424. These tests exercise the
leaf on forked host state. They do not add it to ordinary Main or qualify a
loader, an interrupt path, physical behavior, or a Jay route through 1-1.

Source SHA-256 `1a927d85c8958f1765518bf68b6d9133b99ff739028b4bc8f219899aaa1da244`.
Assembled SHA-256 `798948af9cce48408ff1473edc67e7d9da8ff45da95d84e155f516aa9f4e7cdf`.
Checker SHA-256 `9550c018d2988546646eb74a57708cc0eff82c0d2ce4b0ad536020ff1d7cd251`.
No ROM or Mesen run was created. The bounded output root stayed absent.

## Storage and admission

On the pinned parent the Zelda II alias at file offset `574138` is already
installed. Physical CHR pages 331 and 333 equal canonical page 319
(`4e1232b2739425f2e8cdbd670a7d25f2d09b10772e1e1ee9d0df14b82533d12f`).
Pages 332 and 334 equal canonical page 320
(`a0d0f990b24bea911ebcfaeaaf4f3b6a4f3a3805b7cb271b6d318a897edadbfa`).
The existing allocation ledger lists 331–334 in the conditional future pool.
Pages 321–328 and 330 belong to Sonic and page 329 belongs to Prince. The
proposed Jay packet uses 331/332 only after the current publisher and loader
closure is rebound and the pages receive an explicit Jay grant. Canonical
319/320, world 335 and Mike's current art remain outside the proposal.

The actual sole Zelda II low-table reader remains at file offset 566511. Of
54 historical table rows, the only current changes relative to c10 are the
Zelda II alias and a retired Mario 3 array. The 88 historical publication
domains list Zelda II as the sole consumer of 331–334. The current compact
descriptors for raw 37–43 exclude all four pages, as do the live eight Sonic
boot rows and the 45 Prince carrier rows. Thirteen historical private writer
chunks remain byte-exact. The two changed FF writer chunks rebind through
the exact a5 kernel, which is byte-identical on 47a7 across pages 893–900.
That source review checks 37 gateways, four direct and two indirect CHR/MMIO
writer sites. Current post-c10 publisher changes still need a consolidated
poison run before a new allocation. These findings identify candidate pages
without creating a live Jay lease.

The frozen input and contact ranges contain 1,304 original bytes once the
60-byte donor sampler is removed. Converting the 222 direct zero-page
operands to private absolute addresses adds 222 bytes. Seven indirect reads
remain in CF07's two pointer accesses. Adding the 347-byte adapter reaches
1,873 bytes and leaves 175 for pointer translation, branch widening and
external bridges in a two-page packet. This is a budget, before relocation
and branch widening. If a measured link exceeds it, a third conditional page
would leave 1,199 bytes. Donor weapon dispatch, projectiles, rendering, audio
and resident cold/hot hooks still need their own accounting.

The proposed code lifetime is physical RAM3 `$A000..<$A800`. One zeroed
physical RAM2 page, `$C000..<$C100`, could hold the typed actor state and the
terrain fields at `$C0F0..<$C0FA`. The checker uses `$C100` as an isolated
fixture address. In the current compact worker format a two-row packet would
use seven descriptor bytes, `02 02 01 4B 01 4C 01`. The fields specify two
copy rows, two code rows, one zeroed 256-byte state page, and physical pages
331/332. The existing worker writes and verifies code in the C window while
the later foreground call executes those bytes in the A window.

These are the same mutually exclusive banks used by other actors. They can be
considered only after an exact forced-blank retirement and load path, readback
before committing both complete headers, and actual IRQ/NMI map restoration.
Both `$BFE0/$DFE0` headers and the shared `$DFD0` mailbox are outside the
payload. The current native scene, cold selector and public selector range-test
raw 37–43 (`CMP #7` after subtracting 37). A Jay-only alternate-aware ingress,
an immutable descriptor and cookie need their own resident source funding.
Widening the public raw range would misidentify unrelated actors.

# Selected Bub/Bob Star palette routing proposal

This is a descriptor-only proposal over exact public174fa
`174fa29cf05ce1d14526ea3778c74b33a3858301c81da49b982e0ca2200ab0b4`.
No new allocation, composed ROM, CPU overlay, staging, image or delivery is
claimed. Root77929 proves the missing player flash independently of the
successful natural Star acquisition; see `bub-natural-star-174fa-source-1115.md`.

The existing native routine at A53A masks native Player_SprAttrib0587 and
cycles its low two bits; StarInvincibleTimer is079C. Private Pair currently
loads its two original attributes through the delivered palette mapper,
copies them to C3E6/C3E2, then initializes renderer R3 to0. Its body therefore
does not use the already cycling native player palette. The current private
attributes encode original gameplay ownership/status and must stay intact.

## Actual caller boundary

Current Pair is BDC9..BE45. Its only component callers are BD5C for the
selected hero and BD77 for the scan. BbNativeActor B61E..B62B is byte-exact
to retained linked source: identity0 returns X2E/Y00, identity1 returns
X42/Y08. The actual scan passes proxies X68..7C/Y10..38 or bubbles
X88..C0/Y88..F8. Tile conversion and both current attribute-loader calls
preserve X/Y until the mapper. The complete active private8KB word census
finds Pair target words only inside those two direct JSR operands; no
table/indirect Pair pointer occurs.

Current Draw includes the previously delivered empty-scan JMP at BD5F to
B3E2. Comparing it to unmodified retained Draw correctly failed the first
authentication attempt. The corrected audit authenticates that exact hook
and its entire86-byte guard, rather than allowing an unknown difference.
When all21 records are empty it skips the scan without invoking Pair. Its
nonempty fallback restores A, loads X68/Y10 and jumps to unchanged BD63;
the selected BD5C caller remains before this guard. This closes the actual
current caller domain, including the delivered optimization.

The selected-only predicate uses legal Y00/08 versus scan Y>=10hex, plus
identity0/1 and Star timer>0. Synthetic direct Pair/mapper calls with arbitrary
Y01..0F are outside this legal caller invariant; the proposal does not claim
general selected-player recognition for them. Foreign identities2..255,
inactive Star, every legal proxy and every legal bubble retain the delivered
mapper semantics. Selected identity validity is tested with AND FE, avoiding
C/V-changing comparisons or shifts.

Changing R3 alone would not implement the intended replacement: the renderer
normally ORs palette bits, and its NO_PALETTE bit20 chooses another merge.
Instead the selected player's temporary attribute copy uses
`((original XOR native) AND FC) XOR native`, exactly
`(original AND FC) OR (native AND 3)`. All upper six original bits, including
flip/priority/software flags, remain equal; R3 stays0 and renderer semantics
stay unchanged. This formula is checked for all65536 byte pairs in Python,
not yet by executing a composed or mounted candidate.

## Exact measured resource request

NEW recipe `tools/audit/plan_bub_star_palette_174fa_1115.py` exposes
`metadata(raw174fa)` and `measured_bytes(star_timer, native_attributes)`.
It authenticates the frozen old composer and strict inverse to40a, then uses
the frozen source-retirement audit on that exact parent. It never changes
the old API or constructs a new ROM.

| Logical span | Physical file range, end exclusive | Measured change |
| --- | --- | --- |
| Private3 B438..B46F |1499208..1499264|Existing29-byte mapper plus27 declared FF bytes becomes56-byte selected-Star mapper|
| Existing owner cookie |536570..536586|Re-encode the existing16-byte cookie only after a source grant|

This proposes72 owned bytes, no carrier/RAM/capacity growth. Both public
entry anchors B438/B43E and common entry B441 remain fixed. The 56-byte
preimage SHA256 is
`bae2edcb27dbd29b4095f50d72804b4174408d0fe5a62031e18eb5b60a9e5ed7`;
new bytes SHA256
`8902bff2ef34c202cb1c87b8a4f18fef04350d60622090950a9cc44acd7bd06b`.

```text
old = B906C14C41B4B902C148AD00C3D00C684829034903D0046829FC606860 + FF*27
new = B906C14C41B4B902C148AD9C07F0169829F0D011AD00C329FED00A684D870529FC4D870560AD00C3D00C684829034903D0046829FC606860
cookie old = A72702972671056C12E3E4BE9B97AF56
```

The original258-byte retired pool B438..B539 was previously authenticated by
the delivered empty-loop source declaration. The delivered mapper consumes29;
actual174fa B455..B539 contains229 FF bytes, SHA256
`db353c57cb9d77639d4525f1a3244771578f5e5375907ca7d2d0c805031bd1a2`.
This proposal consumes27, leaving202 at B470..B539, SHA256
`343f07cb1d6fd49d3f5006c96f2e30cbc1171f2ea55e2f772040cd62b76134de`.
Remaining padding is not leased for unrelated work. No public label in the
retained source names the extended mapper span. All adjacent words in the
complete current private component targeting it are exactly B43C→B441
(internal JMP), BDFB→B43E and BE01→B438 (the two existing Pair calls).
The actual executable helper tail D320..D3FF has no word targeting the span.
Old internal return labels relocate only through newly measured local
branches; no outside consumer enters those old instruction addresses.

Descriptor receipt:
`f3aa31e40dc9359f8dd54416e877fd41adf87603ed2fe89be2e3632475fb5cf9`.
Bounded root `build/bub-star-palette-plan-174fa-1115` remains absent,0 files.

## Proposed ABI and remaining qualification

Each loader keeps X/Y/SP and C/V/I/D. N/Z describe returned A. The only store
is the existing temporary stack push; original attributes, owner/status/input,
R0..7, palettes, art, positions, hit boxes and other characters are untouched.
The native attribute must stay stable across the two XOR reads. The actual
Star update is after drawing in GameEngine; reached IRQ/busy-NMI cuts must
prove no interrupt changes it between those reads before this is accepted.

After root leases exact spans, required source gates are actual6502 finite
status/attribute tests at both entries, every legal Pair caller with renderer
bit20/flip/priority coverage, full private-state ownership, constructor/cold/
foreign/death/expiry/inverse proofs, and reached IRQ/busy-NMI at every new
instruction. Record ordinary/active Pair cost rather than presenting the
filter as free. Natural M/F/S/L regression controls must stay frozen through
new strict candidate bindings. Root alone stages and verifies actual Star
pictures for both identities, native world P3/CHR, and any delivery.

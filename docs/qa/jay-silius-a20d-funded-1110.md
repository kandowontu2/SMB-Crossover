# Jay movement carrier and hot residency on a20d

The source-only components bind the installed
`a20d254d4730583ee1f039b10abcf873559987e4f989968037a38e17427faac1`.
The frozen 1,925-byte donor movement prefix remains exact. The derivative
finds actual hot residency and fits the constructor, update and export into
the same two proposed carrier pages through a verified compressed stage.
Cold-entry residency remains open.

## Resident bytes

Physical PRG96 `$A276..<$A2CB` is the existing 85-byte Mike prototype pose
lease. Its current implementation occupies 75 bytes and has a 10-byte NOP
tail. Three lossless changes reduce the pose to 70 bytes. Calling the actual
fixed PRG126 `$80C2` setter replaces two mapper stores. Equality from the
facing comparison lets `ADC #6` use the original carry to produce X+7. A
saved bank byte replaces its later absolute reload. This funds the complete
15-byte `$A2BC..<$A2CB` tail.

The only current same-bank call roots are `$A264` and `$A270`, both targeting
the unchanged `$A276` entry. No current marshaled PRG96 call targets the
procedure interior. The compiler retargets its internal branch. There are
224 exact pose pairs across all three characters and the rejected selector,
both facings, seven poses and four flag patterns. All 256 selector bytes
choose the intended route. Mike and Steve retain their native 60-update
controller result and all compared state.

Physical PRG94 offset `$125F..<$1300` is a separate 161-byte source gap.
It lies between the compiled `SunnyArtEnd` at C-view `$D25F` and Rogue Dawn's
fixed art start `$D300`. Its A-view is `$B25F..<$B300`. The current preimage is
`657a1b27954dde1191f6ca14fffd345b33ace502a2353fa07329f638b1c81d36`.
The bounds are established from the source and linked symbols. The proof
poisons the entire gap and runs 512 Sunny pose pairs plus the real opening
and eight controls for Sunny, Rogue Dawn, Little Mac, Doc Louis and Mike
Tyson. The proof also checks all 100 menu entries on the poison image.

The derivative places a 124-byte authenticated hot gateway in that gap at
A-view `$B25F..<$B2DB`, leaving 37 bytes. The Mike tail uses a genuine
FarCallCommon to this physical bank. The gateway admits only raw16 with
`$730B & $60 == $20`, checks both complete headers, maps private state, and
calls the loaded update. Failed authentication or unsupported scope returns
through the original Mike motor. The hot path has real cartridge addresses.
This is a source-funded proposal awaiting review of the changed ownership.

## Two-page streamed stage

| Item | Bytes |
|---|---:|
| Frozen movement and tile adapter prefix | 1,925 |
| Private constructor, guarded update and native export | 315 |
| Decoded RAM3 image | 2,240 |
| Losslessly packed stream | 1,793 |
| Bound-checking cold decoder | 254 |
| CHR331/332 stage | 2,047 |
| Remaining stage capacity | 1 |

The native compact worker uses descriptor `02 00 01 4B 01 4C 01` to stage
both rows into physical RAM2 `$D000..<$D800`, preserving physical RAM3 until
retirement and invalidation have completed. It reads back every staged byte
through the existing copy/verify transaction. The decoder then runs from
C2 `$D000` with A3 mapped, producing `$A000..<$A8C0` and comparing each write
against the destination. It restores the cookie pointer that shares its
temporary back-reference register. The caller commits both full headers only
after decoder success. The typed cookie is
`A710200273160A7ED870E14AFC9EC80D`.

The decoder rejects zero-distance and before-output references. Source and
output endpoints are bounded. The forced-blank test cuts every reached
decoder instruction and the page boundaries of its read/write leaves. It
also resumes the foreground across NMI on each of nine output pages. The
header remains invalid throughout decoding. Current copy/readback faults
fail closed, and the complete warm header avoids another decode or PPU read.
The new decoder passes 135 real forced-blank NMI cuts, 135 actual SEI-masked
IRQ attempts, nine resumed page-boundary NMIs and two malformed references.
The surrounding common transaction passes 437 forced-blank NMIs and 134
hardware IRQs. Bidirectional cold transitions pass with all seven existing
raw37–43 owners.

The stage modifies CHR331/332 only. Sonic333 and every DK carrier retain their
current bytes. The private C2 staging and expanded A3 runtime are proposed
mutually exclusive lifetimes after retirement. They add no concurrent RAM
ownership. The source stage is an alternative encoding for review, not a
new allocation.

## Executed Main boundary and remaining work

The real controller/menu/scene/Main chain executes 86 private updates on
parsed 1-1 terrain, with an original held jump of 52.5 px and a floor landing.
It ends at native X78/Y176, donor center X78.25/Y192, with two lives. Each
weapon input still executes the pinned original no-B donor fixture. Mike
and Steve's 60-update source pairs retain all compared behavior. The actual
hot gateway and streamed private bridge pass genuine NMI/IRQ cuts. Every
single-byte header fault at that real gateway takes the legacy path without
executing or modifying private code.
The real hot gateway and private bridge pass 186 NMIs and 186 hardware IRQs,
including two mapper-shadow split cuts.

The cold selector, scene and copy wrapper still use 154 synthetic test bytes
plus a seven-byte descriptor. The real hot gap leaves 37 bytes. The common
copy caller maps A65 and A123, so an immutable pointer into A94 would become
inaccessible. The remaining space cannot simply be treated as the existing
cold routine's mapped residency. A real resident cold-entry layout, or a
separately proved stack-staged descriptor and cookie design, is required
before the image is executable as a cartridge.

Original weapons, camera progression and host effects remain outside the
qualified opening. No ROM file, Mesen run, capture or generated build file
was created. Existing frozen Jay sources remain unchanged.

The bounded entry points are
`tools/audit/check_jay_silius_resident_funding_1110.py`,
`tools/audit/check_jay_silius_stream_carrier_1110.py` and
`tools/audit/check_jay_silius_funded_hot_1110.py`. Each runs with Python `-B`,
the shared bounded wrapper, `--max-files 1`, an absent owned output root and
`--timeout 600`.

| Frozen file | SHA-256 |
|---|---|
| `jay_silius_mike_resident_1110.s` | `6b689716d190ece2e3c914b33ed9c3e1897b8f7ca74371de10f30f3b71c46fd1` |
| `jay_silius_bank94_hot_1110.s` | `4d131de86190bfd9c163fa2ef6806863bc1167e7b66991d83edb807ba552ce16` |
| `jay_silius_stream_decode_1110.s` | `b269f8a94faa2a88b4a0dae756fece6603eb75c850820e500403ed3d6a68cf43` |
| `check_jay_silius_resident_funding_1110.py` | `bf5866ae1f1e96298e1d4241e2f9d3036ee78d4b2eaadb5f830bd2fc4e0807cb` |
| `check_jay_silius_stream_carrier_1110.py` | `5dc330121018ee61c7d0286bca9789b1ff7f38da759a8b393ae1ad8988efec93` |
| `check_jay_silius_funded_hot_1110.py` | `8f320fc95206fa4748d6ffb4b6e56121a3bc09c52e674bc07fa551dfb2642233` |

The decoded runtime SHA-256 is
`ff5aa4d75cfa4e8d13293fb6a55aa14c952f95db5268c33d460bf4111985307b`.
The staged two-page SHA-256 is
`7dfbce1012038b2440f6335c35e5ec9482e96ad8b2d26c05555bfe185dcca5bf`.
The in-memory derivative with real hot placement is
`af0bac97812fc0a9f85ff35ae6e50eeb1359f52f65c5e2c12a79a8f7931666a2`.
Its three cold hooks still target synthetic memory and it cannot be staged
as a native candidate.

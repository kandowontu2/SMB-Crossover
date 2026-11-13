# Private Bub/Bob empty-loop probe

Parent is exact public `7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc`.
Private candidate is
`a77a71cf9b22837cb58d639b7653f527c7de2376cc1cffb1d1199a9f7081cd38`.
It is ready for a **private native cadence measurement**, not installation.
The current public ROM and Latest IPS are unchanged.

`bub_empty_loops_1113.proposal(parent)` returns `(image, info)` in memory.
`inverse(image)`/`reverse(image)` reconstructs the exact 7ef parent and checks
the forward round trip. It does not depend on the current Downloads contents.
`controller(image, identity=0/1)` returns strict read-only Lua. Optional
`costs=True` adds the already qualified passive inclusive-cost observer.
Neither API writes a ROM, Lua, capture or receipt file.

The patch changes four source hooks, adds 270 bytes in the existing Bub-owned
528-byte reclaimed region `$B32A..$B539`, and updates its complete cookie to
`a72702dac1da2fc79faa02b5b5381392`. The 258 remaining bytes stay FF. No new
PRG, RAM, service row, art, helper platform or foreign callback is introduced.
The body carrier pages remain 301/305/337/362/363/440/819/666; art441 is exact.
The existing init receipt explicitly records the 528-byte remaining region;
this is not a free-space inference from global zeroes or FF bytes.

| Fast path | Actual hook | Original code retained | Empty admission |
| --- | --- | --- | --- |
| Native proxy observation | `$BF18` existing JSR from ShiftCamera | Entire Observe `$B89C` and its internal loop entry remain unchanged | All six association-active bytes are zero |
| Native enemy import | `$B2BA` existing tail-JMP after HeadBegin clears the pending head | Entire ProxiesIn `$B8C2` and its internal loop entry remain unchanged | All six native actor flags are zero |
| Original inactive bubble prefix | Original D887 relocated to `$A8B7`, first four bytes | Original loop entry D88B at `$A8BB` and all D8BA timers/tail remain | All 15 bubble states and pending-shot byte C264 are zero |
| Draw-only inactive scan | `$BD5F`, first four bytes | Loop entry `$BD63`, original player draw and common queue tail remain | All six proxy and 15 bubble states are zero |

Every other case restores incoming A and enters the original code. Empty
paths reproduce the original final metadata, registers and flags. Original
input, movement, jump, collision, active bubble/trap/pop behavior, timers and
source-clock cadence remain owned by the original routines. No auth cache or
physics substitute is used. Both full expected headers still authenticate
the complete mounted component at every existing real service.

Source preimages bind the full installed ROM, complete eight-page cf7 image,
current native cookie selector, exact hook instructions and the retained
source-label manifest SHA-256
`f342a3c646851d3e098f0a45dc4ee77c78596318d687c9abfea48a96c5059818`.
The uniquely matched JSR/JMP callers preserve their original call kinds.

The corrected gate passes **2,598** direct ABI/state cases. That includes all
256 input flag values for each empty path in both identities, one-byte guard
rejections, and **256 complete mixed-slot routines**: every six-slot mask for
Observe and ProxiesIn in both Bub and Bob. These are declared CPU fixtures,
not naturally earned/trapped-enemy claims. Complete RAM2 state/helper bytes,
native RAM, R0..7, SMC, maps, returned AXYP/SP and live stack match the parent.
Separately, 88 paired ordinary Main/NMI per identity include real B-generated
bubbles and jump input with exact source/native state equality.

The original-cartridge oracle reads the existing 163,856-byte Bubble Bobble
cartridge at `C:/NES/Bubble Bobble (USA).nes`, SHA-256
`e34901acf6917495890ef79ddb33e4641ea309a803d777a27a198e8802c9b4a0`.
All 256 flags match actual donor bank7 D887 through D8BA using the established
RAM translation. No source archive or ROM was extracted or copied.

Minimal interrupt gates pass **302 actual IRQ + 302 rendered busy-NMI** cuts,
with minimum ISR SP160. Every one of the **116 emitted/hook instruction PCs**
is reached. Genuine Main cuts resume to the exact full expected Main state
and AXYP/SP; both maps, source/native RAM, scratch, SMC and live stack survive.
The real FF branch increments NmiSkipped once. Its three established native
sound-clock fields use the existing narrowly scoped ISR oracle. Two fallback
cut fixtures are explicitly supplied after genuine cold ingress. No broad
mapper-state exception is used.

The strict successor Lua streams each pass genuine cold/menu plus 138 CPU
Main/NMI scheduler calls, source/returned-Main equality, no source call outside
a pending Main, empty idle/walk and the first naturally parsed Goomba. The
new controller authenticates the exact successor ROM/cookie, all four hooks
and every added byte in mounted RAM3, then retains the baseline control policy.

- Bub Lua: `6c4c6d9ef3e1039adeae14d46ff915ce49d683963c899bcfcbc3d2f10dff0aa1`.
- Bob Lua: `5b498a2c6d966b85cfcffd381e7bca304cf0298f0c5b74e83b1af7bf66e5c299`.

Modeled empty Main saves **2,430 cycles**; the ordinary B-active suffix saves
885–2,430, averaging 1,446.82. Catch-up skips draw and its Observe call, so the
expected normal/catch-up pair saves about **3,818**, not twice 2,430. Actual
parent mean Main is 46,493 inclusive cycles; whether this crosses a video
frame boundary needs the root's physical test. No cadence gain is inferred.

The rejected predecessor
`b6393502f17d8ff501d2e3a436d70b5bcf40b98741d24b36a84792debe691d47`
is reproduced only by `negative_proposal(parent)`. Its two five-byte entry
hooks overwrite the internal Observe/ProxiesIn loop-back JSR labels. Earlier
prefix-only nonempty cases missed the second iteration; its passing ISR tests
did not qualify this behavior. Static closure caught the error before any
native candidate was written or run. It remains an explicit private negative,
and the strict successor controller/inverse reject it. The caller-side hooks
above plus complete mixed-slot routines address this exact defect.

All producers use `run_bounded_build_v1.py --output
build/prince-pickup-reach-1112 --max-files 1`, with zero generated output files.
Root alone owns Mesen and any two-file native probe output. No installation or
publication is authorized by these source results. Cold readback/fault/warm,
foreign lifetime, full-stage, pickups and broader native qualification remain
separate if the cadence measurement warrants continuing this candidate.

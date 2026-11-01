# Metal Storm host resources and verified scatter loader, v8

This is an unintegrated proposal against delivered ROM
`1c073196b51b6aaaaac90d1bea925b68807fcaa3055665cf6dd0cc8f7858fe33`.
It grants no resource and makes no menu, readiness, shared-source, ROM or
nightly change. Frozen v7 remains unchanged. Its actual actor is **8,083 bytes**,
with a separate2,354-byte renderer/lifecycle/metadata image.

The component compiles and executes a ROM-only cold loader and warm renderer
gate using actual native far-call SMC, CHR publication, buffered PPU reads and
native OAM production. It avoids a generic Mario/Sophia fallback. The constructor,
fractions, gravity, frame ordering, shot lifetime and impact routines stay those
qualified in the preceding original-source components.

## Exact conditional RAM layout

| Region | Purpose |
| --- | --- |
| RAM3/A3:A000..BF92 |8,083-byte original actor/constructor/contact adapters |
| RAM3/A3:BF93..BFDF |77 bytes before the cache header; no lease made here |
| RAM2/C2:C000..C7FF |original actor state, foreground savesC7FE/C7FF |
| RAM2/C2:C800..C83C |existing v4..v7 host/renderer state and scratch |
| RAM2/C2:C880..C8A0 |33-byte native OAM packet |
| RAM2/C2:CD00..D631 |2,354-byte renderer/entityAI/metadata |
| RAM2/C2:D632..D8FF |zero carrier padding copied/read back with the image |
| Both banks, C-windowDFE0..DFEF |complete16-byte revision fingerprint |

Both banks use the same16-byte global image fingerprint in v8. It binds actor,
renderer, exact packed art and loader source, and carries magicA7/owner35/rev8.
This replaces v7's two different fingerprints in the new proposal only. Both
must match in full; one valid bank never admits the other. Fingerprints are
not embedded as early validity bytes in the transported image.

Other owners already use RAM2/RAM3 conditionally, including Karnov's options
atD600..DDFF, which overlap this proposed renderer. Sharing is therefore only
through an exclusive selected-owner lifetime and verified replacement, never
simultaneous allocation. No RAM0/RAM1, SRAM/protection remap or NMI00..02 lease
is introduced. Integration must retire the old owner and establish all cache,
actor and scene lifetimes explicitly.

## Proposed physical CHR layout

| Use |1KB pages |Copied destination |
| --- | --- | --- |
| Actor rows0..3 |247,248,249,250 |RAM3:C000..CFFF |
| Actor rows4..7 |827,828,829,830 |RAM3:D000..DFFF |
| Renderer rows8..10 |831,1023,494 |RAM2:CD00..D8FF |
| Five body art pages |495..499 |direct native sprite fetches |
| Original shot patterns |page499 patterns16..20 |direct sprite fetches |

There are **16 proposed pages total**, with no overlap. All have zero preimages
in the pinned1c ROM. Only ten are wholly unemitted;494..499 belong to the
reserved CV3_CHR emission. The exact current six body tables contain236 choices
covering460..493. Valid CV3 variants1..3 select weapon pairs518..523; the
zero interval494..517 is outside these body/weapon selectors.

This closes the specific CV3 body/weapon table evidence, **not the whole ROM's
compiled/indirect ownership of494..499**. Low pages247..250 also still require
their original low-selector closure. The source names/zero bytes do not grant
them. Karnov's current1019..1022 carriers remain untouched; the older Metal
proposal1019..1023 is obsolete. No historical proof graph is rehydrated.

The144 original body patterns consume4,608 bytes. Five shot patterns consume
160 bytes, which fit in the final body's512-byte unused tail. Body patterns
remain byte-exact. The new shot tile bias16 selects patterns16..20 of that last
page; no copied/synthetic projectile art or extra graphics page is needed.

## Proposed physical PRG funding

Every interval below is outside all actual linked segments and consists only
of FF bytes in pinned1c. The source proposal emits **887 bytes** into these nine
separate ROM holes. Available space is1,126 bytes. No old public PC moves.

| Role |Physical8KB bank |A-window PC |Used/available bytes |
| --- | ---: | --- | ---: |
| Warm gate |31 |BF69 |127/151 |
| Entry/save/restore |78 |AB6D |117/147 |
| Cold work sequence |37 |BF89 |88/119 |
| Cold eligibility |21 |BF8A |66/118 |
| Both-header authentication/typed warm eligibility |25 |BF9E |97/98 |
| Invalidation/zero/readback |116 |AF87 |84/121 |
|11-row copy/readback loop |95 |A580 |84/128 |
| Scatter descriptors/PPU row setup |34 |BD9E |89/98 |
| Publish/failure/PPU restore |99 |B76E |135/146 |

These are A-window execution addresses of the **physical** ROM bytes. Some
neighboring existing segments have C-window run addresses; do not treat their
logical PCs as interchangeable with this proposal. Root must explicitly
partition the corresponding source load memories at the recorded physical
offsets and supply A-window run placements, preserving every old output byte
and label. `resource.cfg` is an independent fragment link, not an edited host
configuration or an assertion that appending duplicate host MEMORY regions is
safe. PRG125 is excluded: its apparent gaps are a post-link DMC/fixed mirror.

The loader uses native FarCallCommon to cross these real ROM banks. It never
executes a cached opcode while either image is being cleared, copied, verified
or published. It does not borrow Karnov's full ROM29 resident lease.

## Cold/warm cache contracts

`Ms8Load` requires raw35, OperMode1, active FamilyMainCommit, forced blank,
PPUMASK rendering off and disabled normal NMI before loading or warm reuse.
It preserves AXYP except returned carry, R0..R7, the five public SMC operands,
current A/C mappings and ReloadCHRBank. NMI scratch00..02 and RAM0/RAM1 stay
unchanged. Source actor construction is separate; loading does not synthesize
a player from a RAM snapshot or set source readyC800=A7.

The cold sequence is:

1. Publish/retain the native current CHR context, then invalidate both magic
   bytes before clearing actor state or replacing code.
2. Zero all8KB of RAM2 and read each written byte back.
3. Copy each actual1KB CHR scatter row through buffered `$2007`, reset the row
   and read back every destination byte against a second PPU pass.
4. Write both fingerprints with magic still zero. Publish RAM3 magic followed
   by RAM2 magic as the final two RAM writes.
5. Restore all12 native CHR windows, upper latch zero, PPUCTRL and both scroll
   writes. Restore the caller mappings, scratch, public SMC and registers.

Every failure leaves both caches invalid and restores the PPU context. The
two PPU passes over11 rows, with one real dummy read per pass/row, total
**22,550 reads**. The warm path performs no CHR read or cache write.

`MsRenderGate`, `MsGraphicsGate` and `MsColorsGate` require raw35, OperMode1,
engine8 and CurrentBankC=2. They authenticate both complete headers by mapping
each RAM bank through C, then restore C2. Only after authentication may they
read source readyC800 or jump to C2. An A-ROM gate cannot read RAM3 atBFE0
while its own ROM is mapped atA; v8 corrects that laboratory-only v7 assumption.
The gate retains its save frame through the actual C2 child call and preserves
AXYP except carry, all five public SMC fields and the bank context; the called
renderer preserves R0..R7 as before. Its three ordinary entry return addresses
select graphics/draw/colors within that common wrapper.

`Ms8Auth` is the internal complete-header probe. Its caller owns register/SMC
preservation. It maps only the C window and restores it; it does not inspect
foreign source state or use a RAM opcode. Complete cold constructor/typed
service rows and source/scene lifecycle routing still need host integration.

Minimum standalone SP was187 from224; maximum modeled cold cost503,857 cycles.
The extra nested far calls make actual Main/ISR stack cuts mandatory. This is
not proof of the required12-byte Main interrupt reserve or raster cadence.

## Native world graphics and palette coexistence

V7's first body window4 would overwrite native Podoboo/Bowser/Peach/Toad CHR.
V8 instead uses body windows0/5 and shots6. Windows1,2,3,4,7 and all BG windows
8..11 retain exact original publication. Current firebars use worldwindow1,
as do powerups/score/platforms; native Podoboo and castle actors usewindow4.
The optional mouse cursor also useswindow5: its build configuration must stay
disabled for this placement or receive a separate explicit adaptation. This
proposal does not claim simultaneous mouse-cursor ownership.

Palette coexistence remains a real blocker. Metal's recovered body palette0
uses26/0F/15 and its projectile palette1 uses21/20/01. Native spritepalette1 is
used by green Koopas, Piranhas,1UPs, flags and flower stems. The native world
also needs palettes2 and3. Merely queuing Metal's original3F15 command changes
those actors' colors. Moving it to palette3 instead corrupts Goombas/bricks and
debris. The present code's original palette routine is retained for source
evidence but **must not be admitted as a world-safe color route**.

A proper continuation must prove a palette/CHR/OAM adaptation for simultaneous
actors, or explicitly scope an intermediate WIP's color limitation. No world
recolor, missing sprite, enemy disappearance or fabricated shot color is
presented here as authentic coexistence. The new drawing tests prove original
indexed player pixels and preserved world **CHR windows**, not all simultaneous
world RGB colors. The original body/shot art and physics remain intact.

## Aggregate evidence and next graft

Passing CPU tests cover six cold/warm cases across three C mappings and two CHR
modes, five injected actor/renderer carrier readback failures, six ineligible
no-effect routes,32 complete-header authentication failures and32 bad-header
warm-gate failures with **no source-state read or RAM opcode**. All312 original
reachable body/shot contexts render identical indexed pixels from code actually
copied and read back by the loader. The pose fixtures reset actor data only;
executable bytes remain those loaded from the authenticated carriers.

The native helper witness is1,091 bytes: the v7 exact1,059 bytes plus the actual
32-byte direct-window0 publisher helper at bank62:A9C0. The extra helper was
read from the exact installed1c ROM, not a mutable integration candidate.
The pinned1c debug/configuration inputs are historical; parent rebuilds do not
make those hashes current again. Further work reads only compact serialized
witness/ownership records and frozen source inputs, with no baseline ROM copy.

Root's next actions: close whole-current selector/owner domains, arbitrate and
grant the physical leases, partition the actual host config, bind the new
carrier source objects, add the typed35 cold/service/lifecycle routes and solve
the palette conflict. Then qualify actual Main/ISR/SMC, normal menu selection,
constructor/life/scene transitions, original health/armor/GravityFire/upgrades,
native combat, original audio and full1-1/powerup gameplay before admission.

Every producer ran under `run_bounded_build_v1.py` in the single owned
`build/metal-storm-resource-host-1101-v8` root. No native Mesen/captures, shared
source edits, ROM delivery, commits or pushes were performed by this worker.


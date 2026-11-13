# Karnov remaining equipment and Ladder plan, November13

This is a source/space audit, an in-memory **refactor-only** trial and one
standalone44-byte renderer component. Ladder remains disabled in every ROM.
There is no equipment ROM candidate, emulator run or generated output. Root
reserved624 relinked code bytes in commit389ff135 and the later556 code bytes,
original object and32 glyph bytes in4c027e30. Frozen input is Quick+Jay
`aa50112845d1cf70cae0924f03326647b3d2514f876c756d70b134ee44f971d1`.
The original Karnov donor is `C:/NES/Karnov (USA).nes`, SHA256
`0d49c1120fc13ead1efe4429f7cbb4f01b90e2486c66661c46e922dda6dc830a`.
The current Karnov scene patch authenticates through exact inverse/forward
closure while every unrelated character byte stays in the in-memory input.

Root's current natural earned/use proofs cover Boots/Bomb plus ordinary shot
upgrades, Star and1UP. The remaining original options are Ladder2, Clapper4,
Glasses5, SwimmingMask6 and Shield8. Existing native controls expose owned
Boots0/Bomb1/Boomerang3/Wings7 with Select and Down+freshB. The exact source
pickup adapter already grants all item IDs through its earned cycle; Ladder's
grant is present. Native selection/activation/lifecycle is missing.

## Original Ladder contract

The retained source and original instructions establish:

- Original activation entry `$EB54`, ownership `$8F` bit4, option2, no BCD
  stock. Native mapping must retain the existing Down+freshB bridge to the
  original source Select edge. Preserve actor/ceiling/terrain guards.
- First activation clears `$0624..$063E`, anchors X at player `$63`, Y at
  player `$64-8`, saves `$5E` in `$071F`, requests scene1 and sound9, and clears
  ownership bit4. The deployment is reusable through the original ownership
  return, not by silently keeping that bit set.
- Scene1 adds at most eight segments, each **16 pixels** (`SBC #$10`), stops
  above sourceY32 or on original negative/class1 terrain, saves each previous
  metatile/world coordinate triple in `$0627..$063E`, and resumes `$071F`.
- The original background quad is BE/BF/BE/BF, collision class9, with original
  attribute preservation. This is a climbable background object. A moving
  platform or altered jump would not reproduce the ability.
- The actual fixed-bank `$5E` dispatcher is D5F0/D5F2. State1 targets D6EA
  and bank12 A003 (growth). State2 targets D6F8 and bank12 A006 (restoration),
  then D700 decrements `$0624`; at zero it returns ownership bit4, clears the
  prefix, selects option2 and restores the prior scene. The original actor's
  **held Down at the bottom** (F668..F69E, body class `$89==9`, feet no longer
  8/9) saves the prior scene in071F and writes state2. First deployment thus
  has an original recovery control without granting another Ladder.
- Activating another owned Ladder while one is deployed writes state0B.
  That actual dispatcher target is DAF8: bank12 A006 restoration followed by
  DB00. At zero this **rebuild** owner clears the27-byte prefix/triples, takes
  the new player anchor and starts growth state1. It does not return ownership
  as state2 does. The old standalone sequence seeded0B and directly called
  D700; it did not execute this dispatcher and cannot prove its state mapping.
  `--part ladder-scenes` now executes the original dispatcher/owner paths and
  the original bottom-climb control. Stage/VRAM workers are explicitly stubbed
  for the dispatch/owner check; this remains a source fixture, not native SMB
  Ladder integration.
- Original room-cache overlay and rebuild keep the ladder coherent across
  scroll. Native metadata, camera redraw, saved tiles, scene jobs and original
  climbing must be supplied. Ordinary actor updates are suspended during
  growth/restoration jobs. Source `$AB..$B3` is the Ladder background packet;
  it is a possible pending-redraw transport after a complete writer census.
- `$94` participates in the donor stage3/6 special callback table. The native
  adapter must explicitly bind/bound that metadata, not index donor tables
  using a cleared or unrelated native byte.

The retained standalone report records3259 total bytes including Bomb, shared
tables and wrappers. Its Ladder code islands alone are603 grow/restore,
57 overlay,116 retraction/rebuild owners, plus575 map/probe/coordinate/VRAM
helpers:1351 bytes before activation, wrappers and readonly tables. Copying it
wholesale cannot fit the potential705-byte reclaim below. Native services and
metadata must replace its donor stage/graphics backends.

## Current ownership and measured funding

The current conditional code leases remain:

| Role | Carried bytes | Actually copied runtime |
| --- | ---: | --- |
| Actor CHR399..406 |8192 | RAM3 A000..BFFF |
| Combat CHR1019..1020 |2048 | RAM2 C900..CDFF,1280 bytes |
| Options CHR1021..1022 |2048 | RAM2 D600..DDFF |
| Body CHR407..411 |5120 | Character pattern data |
| HUD CHR1023 |1024 | Private font/pattern data |

The physical combat padding is not an additional copied/runtime grant.
Neighboring gaps and leases are not reserved. Current Bomb actively occupies
the old Ladder/Clapper/Glasses/Mask/Shield-related loans. None is reclaimed.
The actor's original KrKernelEnd isBFC5; its later native head shim occupies
BFCB..BFDC. Measured explicit fill is not treated as free placement.

`--part footprint` authenticates actual source-annotated far-branch sequences
and their current target words, explicitly excluding37 old source branches
inside live Bomb loans.208 actor and27 options far sequences already have
short-range targets. A qualified owning relink could save624+81=705 bytes.
These are **potential savings, not granted space**. Seven nonmatching rows are
kept outside the estimate, rather than interpreted as new free bytes.

`--part relink-plan` refines the actor placement without moving current host
or Bomb code. All original core symbols referenced by retained host fragments
are anchored: F28D atA087, AAB2 atAC06, C2B7 atAFA4. The two source islands are:

| Source island | Original length | Same-island branches | Potential tail |
| --- | ---: | ---: | ---: |
| A087..AC05 actor |2943 |164 |492 bytes |
| AC06..AFA3 weapons |926 |44 |132 bytes |
| AFA4..AFBA clear |23 |0 |0 |

No selected branch crosses these islands, so shortening within an island
does not increase its relative distance. A real owning-source link can pad
back to each fixed external entry, leaving two potential tails while retaining
all37 service slots, the handwritten host and current Bomb positions. It must
still reproduce current source first, rebind every internal label/table,
audit external/immediate references, and prove all continuations and abilities.
The static scan alone is not that relink proof. The following refactor now
performs the exact owning link and its source/CPU qualification.

## Refactor-only link and allocation request

`compose_karnov_equipment_1113.trial(raw)` reproduces the current three source
islands byte-for-byte before shortening208 same-island long branches. It
assembles all internal labels, absolute references and inline dispatch words
from the owning source, pads to each fixed external anchor, and updates the
two authenticated Karnov headers. Current Bomb/Boots loans, options, combat,
art, public service header, native resident code and every other character
stay exact. There is no Ladder entry, art or font mutation.

| Runtime range (inclusive) | Refactor content | Bytes |
| --- | --- | ---: |
| A087..AA19 | Relinked actor source |2451 |
| AA1A..AC05 | EA-filled measured tail; requested for Ladder source |492 |
| AC06..AF1F | Relinked weapon source |794 |
| AF20..AFA3 | EA-filled measured tail; requested for Ladder source |132 |
| AFA4..AFBA | Original projectile clear, unchanged anchor |23 |

This request is limited to **624 bytes in those two actor-owned tails**.
The options' additional81-byte estimate remains unlinked and unrequested.
Handwritten host AFBB onward, the head shim BFCB..BFDC and every existing
Bomb loan keep their original positions. Art/font changes and the complete
native Ladder lifecycle require their own subsequent qualification.

Exact current-parent trial SHA256 is
`13816e9ff6ecb4d4e10d6f1fa2f9be28c683c52e570a8abb29a9f5e944457c2c`;
actor SHA256 is `dc949564171eeeb3ef72bee8947264557d6a152db4f679bc8ccc10b782b54f8e`.
Its cookie is `a707011323896dcc489c8b64173f25aa`. `inverse(image)` authenticates
the compact islands and cookie, rebuilds the original source, restores the
original scene-cookie12, proves the scene inverse/forward closure, and requires
`trial(parent)[0]==image`. It returns exact current aa501 bytes. Both APIs
are in-memory; no ROM or recipe output is retained.

The baseline source plus resolved constants SHA256 is
`de34c6db8c92a61b59eaf0ef66c5d96ef309e525cf64cd33a6ee0f411611ab10`;
the compact source SHA256 is
`59e57a8503d42834fc88a12f8755650c177ffe2f1192c5a60a4efd6a05043592`.
The baseline reproduces all3892 bytes (2943+926+23). The compact link is
2451+794+23 with the same A087/AC06/AFA4 external entries.

Qualified checks on that exact trial:

- All208 shortened branches ×256 incoming status values:53248 CPU cases;
  exact A/X/Y/P/SP and mapped taken/fallthrough continuations. Each saves1..2
  cycles. The complete owning graph visits4027 instructions from all37 service
  roots, binds all9 inline dispatch tables, and finds four outside-core calls
  into only the three fixed core anchors. No outside-core absolute data
  reference or unbound indirect jump targets the moved code.
- Explicit whole-PRG conventional immediate bank3-SMC scan finds two matches
  into the moved address range: file696154/A200 in ROGUE_RELOC_PAGE_3 and
  file765847/AE06 inside BtAcquire in BT_ROM_LOADER. These are foreign owners,
  not Karnov callers. This scan does not interpret arbitrary bytes as an
  exhaustive program graph. The Karnov resident source uses authenticated
  typed A000+row ingress. All37 actual native veneers are executed on both
  parents up to the child boundary (or their genuine ROM return); A/X/Y/P/SP,
  mapping and SMC operands match. Row20 reaches its original ROM prepare body;
  its source body is not fabricated for this test.
- Both real cold loaders read23064 PPU bytes; warm KrCheckCode needs no PPU
  reads. All32 cookie-byte mutations reject; four actual readback faults in
  compact code and both recovered tails reject without published headers.
- 1105 paired public movement updates across no inventory and declared Boots,
  Bomb, Boomerang and Wings fixtures preserve actual public returns, source
  state, native outputs/maps and all live caller stack bytes. Changed return
  addresses appear only in dead slots1BA..1BE below SP224. Source RAM3 stays
  immutable in both inputs.
- The genuine menu/parser opening and175 paired authored1-1 Main/NMI updates
  use ordinary controller bytes, with no actor/position/ability injection.
  Native memory, source state, PPU/maps and live frame stack1FD..1FF match;
  both source-code banks remain immutable. This is **whole-Main-path parity
  for175 updates**, not a full-stage or native-emulator clear.
- 11 foreign HuFresh owners retain exact A/X/Y/P, write deltas and maps.
  673 reached compact instruction/SP points admit673 IRQ and673 lag-NMI cuts;
  exact interrupted CPU/RAM/live stack/maps return, minimum SP166. This
  includes reached actual menu/Main and declared equipment public-service
  paths; it is not every possible program state.

The recipe reports retain `allocation_qualified=False`; the later formal
reservation is the separate root-owned JSON in commit389ff135. The complete
1178-byte source adapter and its additional556-byte code/32-byte art request
are documented in [the follow-up request](karnov-equipment-extra-request-1113.md).
It remains a measured source proposal with no feature ROM or installed change.

For comparison, current LZ packing gives actor5648/8192, options1738/2048,
combat1229/2048. Compression alone does not grant runtime space. A compressed
carrier/phase overlay would also need a funded loader and independent
readback/cold/IRQ qualification; it is a fallback rather than an assumed fit.

## Measured native renderer component

`tools/reference/karnov_equipment_1113.s` assembles to exactly44 bytes at a
standalone coordinate. It reads the actual native metatile quad into an
already reserved native VRAM command. Native table bank3 normally occupies A;
while code executes in RAM3 A it temporarily maps the same ROM into C, reads
the aliases DA97/DC97/DB97/DD97, and restores CurrentBankC/$5116. It accesses
no source-state byte during that loan. It consumes A/P, retains X/Y and the
mapped owner. This avoids copied tables or a newly allocated PRG thunk.
It is not installed, placed or live-interrupt qualified.

`--part renderer-proof` executes that exact44-byte component in a standalone
cartridge-read model for all256 metatile IDs, three valid native queue offsets
and three prior C mappings (2304 executions). It reads the actual current ROM
patterns, retains X/Y/CVID and stack, restores both map mirrors, and changes
no private source-state byte. Minimum standalone SP221 from entry224 is not
a live Main/IRQ/cold result. No executable overlay is applied to a host model.

The Ladder's original BE/BF patterns are exactly32 bytes in donor CHR38,
SHA256 `a695f4fc2d1211572a01a2f65aa755c008f09da2d47d466010d4ddbb905e535e`.
Proposed private HUD font cells2C/2D have zero references in all256 current
native metatile quads. The existing HUD uses neither punctuation in its gear
names/hint; complete other-text lifetime/font ownership checks remain needed.
No palette or glyph bytes change in this audit.

## Implementation gates before any candidate

1. Reproduce the current owning source in memory, then qualify the actor/
   options relink. Preserve anchored entries, current head/scene bridge,
   Boot/Bomb clocks, shots and ownership; prove cold/readback and interrupts.
2. Implement and measure the complete native Ladder adapter in those proved
   islands. Reuse original activation/8×16 growth/count/restore/climbing;
   replace only stage-cell, VRAM/attribute and camera transport. Native
   GetBlockBufferAddr and VRAM command construction are available, but generic
   WriteBlockMetatile handles only a few block types and cannot alone restore
   every saved tile. The44-byte reader supplies exact arbitrary quads.
3. Finish the source callback/state writer census, native terrain policy,
   frame/queue bounds, font lease and same-life/new-life cleanup. Prove active
   Bomb and Boots survive ordinary Ladder operation, and preserve ordinary
   controls outside source-eligible activation. No full lifecycle fit is yet
   asserted merely from the44-byte backend or705-byte estimate.
4. Freeze composable preimages/inverse, then finite/ABI/cold/foreign/IRQ gates
   before requesting root's sole native queue. Require genuine earned Ladder
   activation, visible original art, climbing and restoration.

Read-only source audit runs with zero outputs:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/karnov-equipment-1113 --max-files 1 --timeout 180 -- python -B tools/audit/karnov_equipment_1113.py --part relink-plan
```

The audit also supports members, donor, footprint, renderer-plan,
renderer-proof, relink, branches, references, smc and ladder-scenes.
The exact refactor and reverse check uses the same bounded command with
`tools/audit/compose_karnov_equipment_1113.py`. Its paired checker is
`tools/audit/check_karnov_equipment_1113.py --part cold` (or movement, main,
entries, guards, vectors). Every section produces stdout only. Only exact
needed packet members are read in memory; no historical trees are expanded.
Root owns all Mesen, current reports/inventory and delivery. No new helper
platform is involved.

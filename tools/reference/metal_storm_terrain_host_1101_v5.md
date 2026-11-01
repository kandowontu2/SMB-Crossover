# Metal Storm constructor and native terrain bridge

This is an isolated source component, **not a playable or admitted character**.
No current source, ROM, Downloads file, menu, or mapper allocation is changed.
The qualified lab is `build/metal-storm-terrain-host-1101-v5`; the compact
`source-proof.zip` excludes ROM/PRG snapshots and compiled/debug/object outputs.

## Original code and the actual constructor

Donor: `C:/NES/Metal Storm (USA).nes`, SHA256
`22e7576958e842c564153bf799293cedf90c6a0aaee302b73ec8af88a7481d87`.
The original reset/Start route first reaches actorAD8C on frame525. Activation
is90EB after911B, the pure actor state constructor is9371..93EC, and943C resets
gravity/facing. AB53 is movement/platform reconciliation, **not a constructor**.

Recovered semantic leaves, 133instructions and99B original tables:

| Original | Purpose | Native treatment |
| --- | --- | --- |
| 911B..912F | Clear/deactivate slots2..23; set inactive pages/flags80 | Actual relocated instructions |
| 9371..93EC | Zero motion/interaction fields, select actor-art profile, spawn pose7/frame2, reset source camera bookkeeping throughB08F | Actual instructions and8AE8/8B4B tables; return before93ED indirect map script |
| 9431..9449 | Original small-object reset and gravity/facing reset | Actual relocated instructions |
| E2C4..E2E6 / FF33 | Signed horizontal contact coordinate snapping | Actual relocated instructions |
| E2E7..E323 / FF36 | Signed vertical contact snapping, including original240Y domain rules | Actual relocated instructions |
| DA71..DA7F / FF3F | Original carry-dependent240Y normalization | Actual relocated instructions |

`MsNativeConstruct` clears private source state as a cold-reset equivalent,
runs the real activation and constructor leaves, and then binds the host's
spawn coordinates. It uses **no captured RAM snapshot**. Source area0 selects
the original body-art profile; it does not select an SMB campaign or import
donor level scripts. The host area extent supplied through
`MsHostSetBounds(A=low,X=high)` survives the private clear.

Native YHigh must be1. Other entry domains return C0 and leave source state
unchanged, with local readiness cleared. Valid entries return C1, retain
A/X/Y and otherP bits, and publish local readinessA7 only after initialization.
This local byte does not authenticate an owner or grant a cache lease.

Native center/feet binding is explicit: sourceX=native worldX-8,
sourceY=native screenY, sourceYpage0. This aligns a32px source body with the
native16px player anchor. Constructor source motion clocks/fractions are
initialized by the original leaves, not converted from generic velocities.

The944A placement routine uses a20-column donor collision map. Its initial
actorY=D0 addresses rowE0: **the probe is actorY+16**, not actorY. The compiled
native form preserves that scan order,16px row steps and pose/state result,
replacing only the map-pointer walk with native queries. A16-row budget
terminates an unsupported empty column rather than hanging. The final host
spawn remains authoritative after the original source-map initialization.

Original OAM clearing90F0, global scene loaders9307..9370 (including the EE
busy wait),93ED/8874's indirect map script,843D's scene objects and original
PPU/CHR/audio initialization are explicit **host boundaries**. They are not
executed, silently stubbed, or represented by a saved donor state here.

## Terrain and frame interfaces

`MsNativeTileQuery` replaces FF1E. Source59/5A are worldX, source5B is screenY.
It reads the actual native block buffers using the current MMC5 helper's
column/page-parity/address calculation and32px HUD subtraction. The source
pointer R0/R1 points to a private semantic byte. **X is retained**, as required
by the source actor's gravity-indexed probes; A/Y/P are typed-port outputs.

| Native metatile attributes | Source semantic flags |
| --- | --- |
| SOLID and not CLIMB | E0: full wall/ceiling/support |
| Air, scenery, coins, climbables, flagpole | 00 |
| Outside supplied world extent or screenY20..EF | 00 |

No donor hazard, ladder, breakability or slope flags are fabricated. All256
actual native metatile attributes are covered. The native metatile ID is
retained atC811 for a later head/coin/block transaction adapter. This component
does not yet trigger coin collection, block contents/breakage, moving-platform
attachments, pipes, flagpoles, springboards or enemy contacts. Native original
hidden-block side/floor behavior also needs a dedicated interaction adapter.

The existing frozen v4 actor still owns fractions, velocities, jump clock,
gravity reversal and its delayed input pipeline. The four terrain callbacks
FF1E/FF33/FF36/FF3F are now compiled implementations rather than CPU replay
ports. Remaining ports8874/8BCF/9ED7/FF18/FF27/FF39 remain explicit boundaries.
FF27 must advance the original53 clock once and preserve source object/frame
ordering; no second native tick may be added.

After an accepted `MsHostStep`, call `MsNativeApplyDelta` inside the same
authenticated owner route, then let the native camera run once. It applies
worldX/Y displacement once per accepted source epoch. It retains AXYP, never
subtracts ScreenLeft, never adds a second camera delta, and leaves source
fractions, velocities and gravity untouched. Duplicate/pause epochs do not
apply motion twice. Native platform/transition corrections require an explicit
source-position rebound boundary before the next source step; no generic
SMB body collision pass should independently repeat these source contacts.

## Imports, resources and ownership

New exact imports:
`Block_Buffer_1`, `BlockBufferAddr`, `MTileAttribute`, `Player_X_Position`,
`Player_PageLoc`, `Player_Y_Position`, `Player_Y_HighPos`.
The frozen v4 imports remain SelectedCharacter/SavedJoypadBits/FrameCounter/
GamePauseStatus/OperMode/GameEngineSubroutine. Native helper addresses were
read from actual0162287e ROM/debug symbols, not assumed from canonical source.

| Resource | Use |
| --- | --- |
| A3:A000..BE02 | 7683B compiled actor+ABI+constructor/terrain component |
| A3:BE03..BFDF | 477B remaining before full owner headerBFE0 |
| C2:C000..C7FF | Original private source state; original pointers relocated |
| C2:C7FE/C7FF | v4 saved foreground pointer |
| C2:C800..C80F | Unchanged v4 host adapter fields |
| C2:C810..C812 | Semantic tile flags, actual native metatile ID, column |
| C2:C813 | Bounded placement scan counter |
| C2:C814/C815 | Applied source epoch and valid flag |
| C2:C816/C817 | Area right-bound saved across constructor clear |
| Foreground03/04 | Typed source tile pointer; public actor/ctor restores caller |
| Native00..02 | **Never borrowed**; R2..R7 are not borrowed either |

Every exported entry requires the resident dispatcher to authenticate **both
complete** C2/C3 owner headers before A3 execution. No cache/CHR/resident/main
lease is granted by this test. Frozen v4's body/meta proposal remains external,
ungranted and unchanged. Health/projectiles/GravityFire/audio/rendering remain
next components. The original actor6323B is unchanged semantically.

## CPU verification and limits

Actual native input pair:
`build/karnov-host-resource-base-1101-v1/candidate.nes` SHA256
`0162287ebf5b8fcb8a84dcf108a0d0930c4dc9d6e68928c4804bd774712e1a6c`,
debug SHA256
`b00f55eb8c4d051e0e10bc9505ba8204e8c3a6163f001bf6c584d2fac404af24`.
These are external **read-only inputs**, not copied into this packet.

The aggregate CPU receipt covers:

- 3072 original/relocated contact, normalization, activation and reset pairs.
- 6656 actual native BlockBufferCollision/compiled bridge pairs:256metatiles,
  both map parities and all13rows; six explicit out-of-domain rejections.
- 22 original pure-constructor pairs using all11nonzero original Y profiles.
- 20 matching original/native placement scans with different map row strides;
  empty-column termination and three rejected native entry domains.
- 30 actual native constructors beginning with poisoned private RAM.
- 1920 original actor wall/support consumer pairs over floor/ceiling/wall/air,
  both gravity directions, signed motion and tile boundaries;66responses.
  These run the real donor FF1E/contact code versus compiled native callbacks,
  **not callback tile-effect replay**. No sound calls occurred in these cases.
- 400 world-displacement/duplicate-application cases without source-state edits.

Minimum standalone SP211 includes the constructor and nested contacts; maximum
standalone13289cycles is a cold constructor, not a per-frame budget claim.
Actual Main caller stack,12-byte interrupt reserve, real NMI/IRQ/SMC re-entry,
whole FF27 actor frame, PPU timing, native visuals, controls, menu access and
full1-1 campaign admission remain **unverified**. Parent owns those checks.

Reproduce using the bounded runner with this exact output root. Each subsequent
producer uses `--resume` only while the output is unfinished; a completed
source-stage.json freezes it. Frozen v4/original packets and their source are
read-only dependencies. No whole source graph is copied or rehydrated.

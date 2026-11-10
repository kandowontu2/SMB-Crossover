# Sonic native admission and terrain map, November 10

This is a source plan against public `c10b7d87f466bf028096bddd33b7ac2baee242870ee83ccc4eebd529af57bd7f`, not a native admission or RAM grant. No ROM, emulator run or build artifact was produced. The separate seven-owner cold proposal authenticates transport only. The public selector and scene bounds must continue excluding raw43 until Sonic has its own service bridge, constructor, real terrain adapter and renderer.

## Exact current admission boundaries

All addresses below are physical PRG65, CPU A-window, unless stated otherwise. These are actual current bytes, not historical symbol aliases.

| Current instruction | Purpose | Future separation |
|---|---|---|
| `A750 C9 06` | Public loaded-service owner range after `SelectedCharacter-37` | Native-ready gate; retain6 during cold-only work. |
| `AEE8 C9 06` | Full-header authentication owner range | Cold registry can become7 only with its complete seventh cookie row. |
| `AF06 C9 06` | Cold descriptor selection owner range | Cold registry can become7 only with its seventh descriptor row. |
| `AF4F A2 05` | Retirement loop highest owner index | Must become6 together with seventh retirement entry. |
| `A80D A2 06` | Shinobi cookie index outside ordinary owner rows | Must become7 when the seventh row is inserted. Raw36 predicate atA809 stays36. |
| `B01B C9 06` | Native scene admission | Native-ready gate; retain6 during cold-only work. |

`CoCheckCode AEE2` and `CoSelect AF00` use unsigned subtraction/range rejection, so the finite current set is exactly37..42, with Shinobi36 authenticated separately. Seventh cold tables need seven descriptor lows/highs, eight cookie lows/highs including Shinobi, and seven retirement records. `CoRetireOwners AF4F` authenticates both complete headers before calling any private retire routine, then invalidates before reuse; its final tail `AF81 JMP A849` remains genuine Shinobi retirement.

`B013` saves A/P, checks its owner range and enters `B062`. After successful `JSR AE00`, `B067..B071` immediately calls `B0F8`, service36. Widening this gate alone would invoke a nonexistent Sonic constructor.

The public transport `A740 -> AAF7 -> A743` validates both headers and the service target range. `A76D..A776` accepts offsets0..113 (`CMP #$72`), corresponding to38 three-byte rows. Raw37 selects A500, raw38 selects its special DF1E proxy, raw41 takes a distinct route atA75A; remaining admitted owners use **A000+3*row**. Sonic's core starts with real instructions `AD13C03012...`, not a row envelope; `OrdinaryFrame=B3EC`. Therefore a seventh native service needs a dedicated raw43 dispatch into newly funded private bridge code, or a newly linked envelope with all original addresses relocated and requalified. Never overwrite the frozen core's first114 bytes.

Current exception predicates remain exact: Shinobi `A791/A806/A8A5/AC21/AD2F/ADD9` tests36; Mini direct rare entry PRG124:A716 tests41; Getsu empty services at65:A7E4/AF9D and its head shortcut test42. Do not replace any with a broad high-owner condition. PRG124:A7CA already routes owners>=42 through the ordinary service class; that does not authorize their eventual recipient. Raw43 must not be assigned to raw39/Bub, FmGroups bit6 or another existing alternate.

## Service and lifecycle contract

The existing38-row meanings are documented by `tools/reference/mini_mario_native_host_1103_v22.inc`; they establish ABI slots, not Sonic implementations.

| Rows | Sonic work required before native admission |
|---|---|
| 0 | Ordinary-frame wrapper, once per actual gameplay update, with source24-bit position/velocity retained. |
| 1,2,3 | Own graphics, source24x32/24 draw and CHR publication; do not enter Shinobi/Mini/Gimmick renderers. |
| 4,5,6,7,8,21,23,33,34,37 | Own attack, status, injury, death and pickup decisions. The ordinary-frame proof excludes rings/damage/death and does not fund Mario powerups as substitutes. |
| 9,10,11,12,13,14,16,27,31 | Visibility, head/body/side queries, bounds, stomp/contact and bounce policies for the source body. Retain native effects separately from source position resolution. |
| 15,36 | Fresh-life and scene constructor bridge; a verified cold header is not an initialized actor. |
| 17,18,26,30,32 | Own menu portrait/name, player palette, HUD name and world palette routing. |
| 19 | Current resident `B100 JSR AE0A; SEC; RTS` retires all authenticated overlays. Keep this reset contract; it must not call another owner's reset. |
| 20,22,24,25,28,29,35 | Explicitly preserve the native caller's documented fallback/handled ABI; inspect actual callsites rather than copy Mini's no-op policy. |

Cold overwrite is permitted only under existing OperMode1, committed family, disabled screen, blank PPUMASK and negative NmiDisable guards. The saved cold frame owns AXYP, R0..7, five SMC bytes, C mapping and ReloadCHRBank; it restores PPU state after copy/readback. Both16-byte cookies commit only after the final copy succeeds. Failure invalidates the first byte of both headers. DK's preexisting DFE0 descriptor staging can leave inactive bytes1..7 after failure; they are not authenticated state.

Menu resolution65:AD88 and foreign scene65:AC2C enter shared retirement throughB026->AE0A before their old chains. Reset19 enters the same public retirement. A Sonic retirement callback can be zero only while Sonic owns no native object/AI associations; future owned supports, effects or contact associations require genuine teardown before invalidation. Do not clear foreign enemy state to simulate teardown.

Fresh life must reset actor readiness and epoch validity. Same-life warm calls must not repeatedly clear source fractional positions, jump latch, shoes, animation state or carried contact state. Actual scene relocation/pipe/area spawns need an explicit position-resynchronization contract; an old cookie alone cannot distinguish them from an already initialized actor. Losing authentication must prevent every private code entry, including getters and drawing. IRQ/NMI must not run the actor, advance its epoch or borrow its private state.

Host `src/game.s` increments FrameCounter `$0E` once per unpaused GameLoop, before OperModeExecutionTree; catch-up Main can run without a normal NMI. The donor increments its global tick at00:1E07..1E0B before object updates. Thus advance Sonic's private tick once per accepted source update, never from NMI, draw, head/side getters or a duplicate row0 call. Guard ordinary movement with actual engine8, pause and TimerControl semantics. A separate initialized/have-epoch flag must admit the first update even when the frame byte is0. Test255->0 and a long frozen/nonordinary interval whose frame byte aliases the previous epoch; do not use zero as the sentinel.

## Original actor constructor, not the differential fixture seed

`build/sonic-sms-original-1102-v2/src/whole.asm`00:232B..239B loads Sonic with A=0 and IX=D3FC. It sets X/Y subpixel bytes to0, converts the two level-spec coordinate bytes to integer pixels by multiplication by32, and clears actor offsets7..25. That clears all six velocity bytes, both dimensions, sprite/animation pointers, animation frame/index, shoes/brake timers and flags. It does **not** seed fixture flags88 or pre-ground the actor.

On the first normal source update,01:4A89..4A9E sees old height0, subtracts8 from integerY, then assigns width24/height32. The rolling branch01:532E..5343 adjusts Y when the height changes and sets24x24. The host constructor must choose its imported spawn anchor with this genuine first-update Y adjustment accounted for; simply copying SMB's16px body anchor is not an established mapping. Preserve the native foot/world location while explicitly translating the source top-left24px body. Fresh-level code00:2100..2114 independently resets camera look and the D287..D2A3 timer group, including jump/bored timers; global previous-animation/subframe fields are separate from the actor's cleared frame/index. Do not claim that an arbitrary all-zero256-byte reset is byte-equivalent to every original warm transition.

The relocated fields remain full precision: X/Y positions C070..C075, X velocity C020..C022, Y velocity C060..C062, bounce C063..C065, flagsC030, animationC031, width/heightC041/C042, inputC040, private tickC092 and animation historyC0A0..C0A3. Context bytes for readiness/epoch require a finite unused-state census and typed lifetime; no new address is allocated by this report.

## Exact world seam and proposed native PointRead

The frozen relocated addresses are:

| Site | Meaning |
|---|---|
| B4D2 `JSR B526` | X contact point query, after full source24-bit integration. |
| B4D5 `JSR A7AE` | HorizontalTerrain -> ShapeHorizontal A7BA -> HorizontalContact A5E1. |
| B4EF `JSR B526` | Recomputed Y contact point after horizontal clipping. |
| B4F2 `JSR A7B4` | VerticalTerrain -> ShapeVertical A7EA -> VerticalContact A5EA. |
| B526 | SourceWorldQuery: fixture map C800..D7FF, then fixture flag lookup D800..D8FF. |

Those fixture regions are not native storage. In particular the4KB map overlaps real cold metadata/startup D000..D3FF. Initializing it would destroy the boot. Merely returning `solid -> donor class22` fromB526 also fails to adapt16px geometry: source shape lookup and clipping use `&31`/`&$FFE0`, axis-specific32-sample tables, magnet factors and slide factors. A new derivative must replace both query and geometry selection, while retaining the original motor, caps, integration, ordered X/Y clipping and their grounded/contact flag updates.

True donor reads are `get_obj_level_tile_ptr_in_ram 00:36F9..37DF` plus `PTRLUT_level_tile_flags 00:3A65`, used at horizontal00:3349/3355 and vertical00:3421/342D. Coordinates are actor integer X/Y plus the probe offsets; lookup uses32px tiles, with level widths16/32/64/128/256. Horizontal probe is leading X edge and Y+height/2; vertical probe is X+width/2 and top/bottom Y by velocity sign. Source return-from-object00:32E2 integrates X/Y first. The first terrain pass can alter X and velocity; the Y probe must then be recomputed.

Proposed first host leaf: compute the real world-pixel point in private absolute scratch, select native buffer page by worldX high parity, column=`(worldX>>4)&15`, row=`(screenY&$F0)-$20`, and read the actual metatile. Native Block_Buffer_1=$0300 and Block_Buffer_2=$03D0,13rows×16columns; ABS,Y loads can perform both reads without borrowing ZP. Admit only valid32..239 vertical pixels and the genuinely buffered world interval; parity alone must not alias a distant world page. Return the exact metatile, native attributes, cell origin and out-of-plane result. Do not call native movement or collision resolvers from this leaf.

Current MTileAttribute is fixed `$EF36`, identical in physical119/120/125/127, SHA256 `02ca3678ee8114a3eb336262b9472ee9929237a31f39d5b6886886dc252b8470`. The actual256-byte values use only bitsC7: solid1, climb2, bump4, paletteC0. Source definitions leave water/damage/kill attribute bits unimplemented. Therefore MTileAttribute by itself cannot supply slope, water or one-way geometry.

| Native/source case | Required interpretation |
|---|---|
| Empty/native coin or effect-only cell | Source no-contact offset80; preserve the native metatile for a separate earned effect transaction. Invisible blocks, coins and vines require their actual native state/axis policy, not `metatile !=0`. |
| Native16px full solid | Adapt its exact16px cell boundary into a shape offset relative to the original32px contact base, then use original HorizontalContact/VerticalContact. Native clipping geometry is an explicit world adaptation; donor class22's4/28 side insets andFF floor are not a universal16px solid encoding. |
| Source floors/ceilings, caps and slopes | Source low6 flag indices0..46 select four separate32-sample shape tables. Class22 supplies all directions, classes1..21 include floor slopes/curves, and other classes include partial surfaces. Preserve these tables for genuine source geometry; ordinary SMB1 metatiles do not encode a corresponding slope. Never infer one from palette or bump bits. |
| Water | Original detection01:50E8 and tile-special08 precede/select underwater physics; it is excluded from the ordinary proof. Read actual host area/water state through an explicit adapter, then update the donor underwater flag; do not treat solidity as water. |
| One-way BG/support | A floor-only donor class has empty side/ceiling tables; native platform actors are separate from block buffers. Require direction/previous-foot crossing and genuine native support ownership. A zero callback or flat BG lookup does not implement moving-platform carrying. |
| Velocity/top caps | HardCapsAndTop B350 preserves original signed velocity high-byte caps and unsigned Y<=16 top clamp, before integration. These are separate from excluded donor level-edge clamps and native viewport/status-bar limits. |

Smallest authentic next source piece: implement and qualify PointRead across all256 native metatiles, both buffer pages,16px seams, world-page edges and vertical bounds; then add the host shape adapter at the four seams above, retaining unchanged contact arithmetic. Qualify original32px behavior as an unchanged mode plus explicit16px flat-host geometry cases. Follow with the original constructor and a private bridge into B3EC; test spawn/landing/rolling and once-only epochs before enabling public scene/service admission. The constructor itself is small enough to plan inside the1642-byte loaded tail, but its existence does not make unadapted terrain callable.

RAM3 has2634 bytes after the5526-byte core and beforeBFE0; the current seven-row boot loads only7168 bytes, leaving **1642 loaded bytes** after the core. Using the additional992 bytes requires an eighth code carrier and changed boot/page funding. D25E startup, both cold headers and shared DFD0..DFD2 mailbox remain intact. No frozen source or component was edited.

# Excitebike earned powerup progression — November 10

This is a source CPU qualification and a controller handoff. No Mesen run,
candidate ROM, receipt file, capture or delivery was produced by this helper.
Root owns physical qualification and installation.

## Exact parent and in-memory proposal

Parent: the delivered a5 ROM,
`a5c54d7624ee961f11b45598ca7cf7fecc24de6ee87d8e8aa70dad55834f2eaa`.
The proposal has no dependency on the separate private63d draw proposal.

| Binding | SHA-256 / value |
|---|---|
| In-memory proposal ROM | `a76d7610eed8493806200c52b96065af0369b926c55d033e17841f818756e2e0` |
| Original six-page Ex kernel | `7ceb512a4427abf6ff77ce6a4b1c98badceb9dcb4b3264c453c168eced55e2f8` |
| New six-page Ex kernel | `6742f64689f95384f2fcf0b3953e65484b46d7ea538599d310bf61be94d26d64` |
| New complete16-byte cookie | `a7250288fd2e7241d6b176e36679e09b` |
| Cookie file offset | 536554 |
| Actual changes | 34 differing bytes: row33 target,18-byte helper, cookie |

`check_excitebike_powerup_progression_1110.proposal(a5_bytes)` returns
`(image, kernel, cookie, record)` entirely in memory. It checks the exact a5
parent, the complete current Ex kernel, live retained metadata/art and the
sole old cookie before replacing anything.

## Confirmed failure and repair

The current native collection path already calls `GuestBeginPowerup` for
Excitebike's mushroom/flower tier pickups. Native engine9 then dispatches
`NrNativePowerupDispatch -> HuPowerup -> Ex service33`. That private row was
`JMP $A56F`, the explicit rejection leaf. The transaction could never age.

This was first characterized by same-epoch directed row33 calls, then confirmed
with85 distinct normal-NMI/Main updates. A separate controller-only route
confirmed the actual naturally earned failure; it does not rely on a synthetic
actor or a frozen FrameCounter.

The repair changes row33 at RAM3 `$A563` to `JMP $AF7A`. The18-byte helper
uses the ordinary native FarCall transport to existing `GuestPowerupUpdate`.
Funding is the original explicitly linked gap from exported `ExHostEnd=$AF7A`
to the next `CODE` segment at `$B000`,134 bytes. The original host-end label,
segment starts, absence of intermediate labels and exact original kernel/fill
are checked. Only18 bytes are used. Original motor/air/temperature routines,
body, terrain, art, metadata, every other vector and native callback code stay
byte-identical. The complete kernel+metadata+art fingerprint is recomputed
with cookie revision2; no cached old header is retagged as current.

The current integrated resident dispatcher/guard differs from old Ex build
labels. The qualification derives its real guard from the current source call
at physical65 `$A75E`, which targets `$AEE2`; old `$AE00` is not reused.

## Natural route and source result

The ordinary controller path begins with actual menu slot29/raw37 and the real
1-1 parser/constructor. It runs the existing60-update opening, drives Right+B
to X400, allows the original Goomba crash/recovery, reverses Left+B to X365,
uses4 updates of Left+Up+B then8 of Left+Up+B+A, and coasts. The head hit births
the authored mushroom at X336. The item moves right, bounces from the first
pipe and returns to the parked bike at X290. No terrain, actor, health, gear,
power, immunity or controller-state grant occurs after the legitimate menu.

| Observation | Delivered a5 | In-memory repair |
|---|---|---|
| Native collection | route epoch519, X290/Y176; mature mushroom X302/Y184 | same |
| Collector effects | actor erased, SFX `$20`, floaty6, Active1/engine9/timer255 | same |
| Subsequent tick callback |90 `HuPowerup`,0 `GuestPowerupUpdate` |60 `GuestPowerupUpdate` |
| Recovery | after90 actual updates: Age0, Active1, engine9 | Age60, Active0, engine8, timer0, Status1 |
| Ordinary movement after recovery | blocked by transaction | Right to X306 at route epoch617 |
| Lives |2 |2 |

The first Goomba crash is an ordinary original bike interaction and recovers
before the item jump. This is not a no-contact route. All gameplay after the
menu uses normal NMI/IdleLoop/Main and the controller peripheral.

Four separately labelled directed mature-pickup cases check kinds0..3. Both
tier pickups recover after exactly60 actual Main/NMI updates. Star starts its
native35 timer;1UP produces native floaty11. Those synthetic actor tests are
not natural Star/1UP coverage or a life-award qualification. Natural flower,
Star,1UP, full-stage and physical emulator qualification remain open here.

## Lifetime and real interrupt qualification

The dedicated lifetime checker passed:

-96 exact active native `GuestPowerupUpdate` ABI/application comparisons,
  including terminal age59 and tier0/1/2 directed fixtures.
-256 inactive input-P cases;256 individual bit faults across both complete
 16-byte headers;255 foreign owners through the typed Ex veneer.
-Old revision warm rejection, new complete warm authentication with zero PPU
 reads, and4 real paused Main updates followed by one real resume update.
-32 reached instruction contexts cover every instruction of the new helper
 and redirected vector, at ordinary and terminal ages with IRQ enabled/masked.
  Real native vectors pass32 NMI,16 IRQ,16 masked IRQ and one nested scanline
 IRQ during the actual lag-NMI CLI window. There are98 paired ISR executions;
 resumed foreground, native hardware transactions, AXYP/SP/live stack,
 scratch, SMC, PRG mapping and private state match the unchanged native ISR.

## Physical controller handoff

`tools/playthroughs/excitebike_earned_powerup_stdout_1110.lua` is standalone and
uses the existing `run_stdout_mesen_1110.run` unchanged. Root must bind the
actual candidate path/hash. It emits one `SMB_NATIVE_RECEIPT`, no files or
images. It selects slot29 naturally, ports the successful CPU input policy,
observes the mature native actor and collection return, requires all60 native
tick returns and16px resumed movement, and checks original bike CHR736..739,
OAM alignment/pointer, palette and EXBIKE HUD before and after recovery.
Bounds are4000 physical frames,2500 Main entries and1100 route updates.

The controller's Lua syntax/symbol/API-only tests pass the exact menu sequence,
60 opening input samples,4 prelean/8 A updates, accepted collection/60-tick
success, unchanged-freeze negative and wrong-hardware negative. These mocks
are not ROM execution or Mesen evidence.

All source tests used Python `-B` through `run_bounded_build_v1.py --max-files1`,
with zero generated output files. The output reservations were
`build/current-roster-powerups-cpu-1110`,
`build/roster-powerup-real-continuation-1110`,
`build/excitebike-powerup-progression-cpu-1110`,
`build/excitebike-powerup-lifetime-cpu-1110` and
`build/excitebike-stdout-source-1110`; they contain no produced artifacts.

## Frozen sources

| File | SHA-256 |
|---|---|
| `tools/reference/excitebike_powerup_progression_1110.s` | `f335b8811ab6ac5c05c45fdf669c3f342b4b5d31385477b72e781309bdbcff66` |
| `tools/audit/check_excitebike_powerup_progression_1110.py` | `109af8fe62731830c11d6a8fe3151414750f2a0cf287049cd5ecaa1368622d62` |
| `tools/audit/check_excitebike_powerup_lifetime_irq_1110.py` | `b6d270b04a32ded2f6078003644dfcb043c94a897badfeec3af58757875d8f2d` |
| `tools/audit/check_roster_powerup_continuation_1110.py` | `9fa49336520dd66056938427a742365a699f3a524315d3367dc45b0c91799d0b` |
| `tools/audit/audit_current_roster_powerups_1110.py` | `3965823a4cf091d240b5b77ede4dabc31b5e4f5617dc4262cc2752ad4a84467e` |
| `tools/playthroughs/excitebike_earned_powerup_stdout_1110.lua` | `20fcef1f4bb2a98a384d24cf457a8f0f4a58acad6cf3cbb411935c0cf1955794` |
| `tools/audit/check_excitebike_stdout_controller_source_1110.py` | `1b1db097f3c89d96eeb8502d017e4857d3f8574022bc15644cdd28231aee6362` |

## Current100-name census limits and next candidates

Actual a5 menu inventory resolves100 names, all confirmable. The census cold
starts every one through the real parser and60 ordinary opening updates, then
executes400 explicitly directed prepared+mature native collection callbacks.
This is100 current identities, not historical37-name coverage. It checks
ingress/admission/progression only; it does not prove original benefits at
capped health, powered attacks, natural acquisition or full-stage routes.

The initial same-epoch fixture flags37 cases across11 identities. Excitebike's
two tier freezes are now confirmed by distinct Main and a natural earned item
as above. The remaining candidates require source admission/epoch followup:

| Current names | Directed diagnostic |
|---|---|
| Hulk Hogan, Ted DiBiase, Bam Bam Bigelow, Honky Tonk Man, Randy Savage, Andre the Giant | All4 mature synthetic cases are not erased by the called leaf |
| Shinobi | All4 mature synthetic cases are not erased by the called leaf |
| Arthur | All4 mature synthetic cases are not erased by the called leaf |
| Metal Storm | Synthetic flower case is not erased by the called leaf |
| Thomas | Mushroom/flower start generic freeze; same-epoch row33 calls do not advance it |

Non-erasure at an isolated native leaf can be an intentional fallback or a
fixture missing an owner's maturity/admission contract. It is not itself a
confirmed gameplay defect. No repair is made for those cases in this proposal.

## Root physical v1 negative and observer-only v2

Root ran the frozen20f controller on actual Mesen before the naturally earned
item. It stopped at the logical1100 bound in Recover, X400/Y176, with no item
birth or collection. Receipt
`504740012da0461acd8b3ca190fd953eef898484014e55c0a4e979a660ad38f1` records2037
physical frames/1435 Main entries and568 successful original hardware checks.
Its source-state readings were wrong: the Main-return C-window had restored
PRG, so CPU `$C090/$C094/$C0AC/$C0B0/$C098` read `$C0`, producing speed49344
and crash192. The CPU controller had always read physical `m.ram[2]` directly.
This physical result confirms no pickup or recovery; it is retained as a
negative controller/observer receipt and does not reject the repair.

The new `tools/playthroughs/excitebike_earned_powerup_stdout_1110_v2.lua`, SHA
`5605c4f2a73c21ecfcc7c8013ad67ce427bdd713a722fe91e08c5fca1d053056`, changes
only comments, one physical bank2 read helper and those five source-field
reads. Native memory, ROM bytes, controller policy and all assertions stay
unchanged. Its API-only checker
`tools/audit/check_excitebike_stdout_controller_source_1110_v2.py` reruns the
complete earlier controller cases and proves the specific poisoned CPU-window
case: CPU C-window bytes remain `$C0`, physical bank2 has actual zero
speed/crash, Recover issues Left+B66, and no CPU C-window read occurs. V1 and
all earlier frozen sources are preserved. V2 physical qualification is root's
next step; no new physical pass is claimed here.

The unchanged directed continuation checker also confirmed Thomas's mushroom
freeze across85 distinct actual Main/NMI updates: native actor erased,
Active1/engine9, Age0, no `GuestPowerupUpdate` call. This is a directed
progression failure, with natural acquisition and any repair still pending.

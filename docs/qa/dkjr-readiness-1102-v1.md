# Donkey Kong Jr. original component — November 2

Private source recovery only. No host resource grant, roster/menu edit, ROM
composition, Mesen run, install, Git commit, or helper placement was performed.
The Donkey Kong Jr. alternate remains absent pending integration review.

Donor: `C:/NES/Donkey Kong Jr. (World) (Rev 1).nes`, SHA256
`1bc7fdc98c29b2c51438c3ce92ca37fac61b939a7cf100c644fed37206cf2cf6`.
This is NROM128: mirrored 16KB PRG, 8KB CHR, vertical mirroring. The CPU oracle
executes original reset, NMI, input and game instructions, with an explicitly
untimed PPU and one original foreground RNG iteration per supplied NMI.

## Concrete component

`build/dkjr-source-1102-v1/component.bin` is **4,853 bytes**, including 256 bytes
of original tables and ten three-byte import vectors. It recovers 3,117 original
instruction bytes / 1,594 instructions. The expansion relocates RAM and branches
and implements indirect accesses through writable local instruction operands.
Measurement placement is A000..B2F5 exclusive, with original RAM relocated to
C000..C7FF. These addresses are not host leases. Code must execute from writable
RAM; actual interrupt/reentry safety is not yet qualified.

The original private state request is **2,048 bytes**. No native adapter state,
37-row service table, loader/router, owner cookie, save/restore frame or host glue
has been allocated or measured. A nominal 8KB code image would have 3,339 bytes
left before any owner header reservation; that arithmetic is not a glue-fit claim.

`body.chr` is **1,728 bytes**, fitting two 1KB CHR pages: 1,408 bytes of original
body patterns, 192 bytes of fruit patterns, and 128 bytes of four original hit
tiles paired with transparent lower halves. `body-poses.json` contains all 22
body render variants. Each body uses four 8x16 sprites, equivalent to the original
eight 8x8 cells. A falling fruit uses two sprites and the hit effect one sprite.
The body is 32x16 pixels including transparent margins. Preserve its original
state/facing-dependent collision rectangles rather than treating all 32 pixels
as solid. The original sprite palettes are:

| Source slot | Colors |
| --- | --- |
| 0, fruit/hit | 0F 30 2A 16 |
| 1, body | 0F 30 06 36 |
| 2, fruit | 0F 2A 17 37 |

No palette quantization or redraw was applied. `body-preview.png` decodes the
recovered tiles using these source color indices; hardware publication remains
unproved.

## Original controls and movement

The original controller at F219/F22D publishes held bits in 14 and its processed
sample in 15. Actor input CE6C accepts one direction at a time: Up=1, Down=2,
Left=3, Right=4 in 54. A uses the held bit in 14 to enter jump state when not
already in vine state. A does not launch a jump from a vine. B has no actor
attack binding. Lateral vine movement changes grip/facing or releases the vine.

| Behavior | Original measured result |
| --- | --- |
| Ground/air horizontal motion | 0.625 pixel per source update |
| Unblocked single-vine ascent | 0.25 pixel per update |
| Unblocked single-vine descent | 1.3125 pixels per update |
| Unblocked two-vine ascent | 0.625 pixel per update |
| Unblocked two-vine descent | 0.5625 pixel per update |
| No-vine jump | 15-pixel rise, 44 airborne updates, returns to original support |
| Fall motion | 2 pixels per update; original fall-distance injury tests retained |
| Falling fruit | 2 pixels per update |

The climb rates above are source leaf tests with an explicit unblocked grip
fixture. Natural reset/start sequences also earn the first vine; their original
platform/wall probes correctly stop further climbing at authored boundaries.
Do not misread those boundaries as slow or missing acceleration.

This jump cannot independently clear SMB's 32/48/64-pixel pipes. A future adapter
needs real native climbable support or verified existing native platform helpers;
no jump boost, helper location or assisted crossing is claimed here.

## Entry and state contract

`component-layout.json` contains exact current exported and imported addresses.
Original PCs below identify the source routines independently of measurement
placement. All original RAM addresses in this section become private base+offset.

| Export / original PC | Contract |
| --- | --- |
| Initialize / CA82 | Original actor clear/defaults through CABF, then an explicit typed RTS before stage art/UI initialization. Caller clears private RAM, supplies stage 4A=1..4, initializes body position/attributes and fruit/native terrain inputs. |
| Input / CE6C | Reads player index 49 and controller 14..17; publishes direction 54 and jump state 6B. |
| LandPose / CEA2 | Consumes original landing-pose flag 63 and original short effect timer 38. |
| Transition / D251 | Initializes state transitions, fractions, jump/fall phases and grip entry. |
| Move / D412 | Builds original bounds, dispatches ground/vine/jump/fall motion, renders body and checks fruit touch. |
| Bounds / D2BD | Reads body anchor 0210/0213, state 6B, facing 6D and grip 71; writes rectangle 3E..41 and 05FC..05FF. |
| FruitAdvance / DBB3 | Advances original active fruit OAM 0230..023F or hides it at the source lower boundary. |
| FruitCollision / D43A | Tests active fruit against original enemy OAM/state families; publishes hit family 68 and object index 69. Host enemy transactions must be supplied deliberately. |
| FruitHit / D1AE | Original enemy-hide and hit animation; clears 68 on completion. Original CD91 skips actor movement while 68 is nonzero. |
| Damage / D405 | Enters original defeat state 5 and requests the source sound event. |
| DefeatTick / CF37 | Original delayed defeat/fall/pose progression, ending at imported life transition CF62. |
| Clock / F1AF | Original short timers and divide-by-11 long timers. Call in the original phase, not during the fruit-hit freeze branch. |
| Pose / E9EE | 00=X, 01=Y, 02=source tile base, A=render mode 0/1. Writes eight original body OAM cells at 0210. Other renderer scratch and AXYP behavior remain source-defined. |
| Gravity / E9AE | Original fractional launch/gravity integration, using 01 and actor air phase. |

Normal source order comes from CD6E: input, landing pose, state transition,
movement, fruit/enemy transactions, then clock and previous-direction 55=54.
The 68!=0 branch executes the fruit-hit sequence instead; state 5 uses defeat
progression. Native landing must resolve through the original support contract
before final body draw. OAM Y is the source NES OAM coordinate; source landing
DAA5 derives it as support Y minus 17.

Key original fields: state 6B/previous 6C (1 grounded, 2 vine, 3 jump, 4 fall,
5 defeat); facing 6D (0 left, 1 right); horizontal/climb fraction 56; grip 71
(one/two hands); vine centers 73/74; captured jump/fall Y 76; wall result 78;
jump epoch 7E, fraction 7F and gravity 82/83; launch magnitude 86/87; fall step
7A and injury threshold 7B. Source sound mailboxes FE/FF are requests, not
implemented host audio.

The authentic attack is touching an authored hanging fruit. Original D955 checks
availability 9A..9D and the list at 91/92 (length 93, seven bytes per fruit),
publishes active index 8C and renders the falling fruit. There is no punch,
throw button or generated projectile substitute. Ported table pointers 02/03
and 91/92 must name the relocated immutable source data when used.

## Imports awaiting native implementations

Every unbound vector is a local self-JMP, so the standalone image cannot silently
execute an unbound host service. CPU tests replace these vectors with independent
execution of the corresponding original service on equivalent donor state.
This qualifies relocation across those seams, not an SMB implementation.

| Original service | Required native meaning / source effects |
| --- | --- |
| E893 | Single-vine intersection for rectangle 3E..41; return A/0F, contacted rectangle 42..45, vine center 73/74. |
| E897 | Separate hand probes; source result 0/01/10/11 and contacted vine centers 73/74. |
| E89B | Original wall/obstruction probe; preserve source scratch/bounds behavior and return A/0F. |
| E89F | Original support probe just below the current rectangle; publish support rectangle 42..45, preserving the caller's bounds. |
| ECB7 | Original jump-over-enemy bonus/contact bookkeeping; native equivalent remains open. |
| ED44, ED7B | Source score/popup transactions for fruit impact and fruit release. |
| EFCE, F1C5 | Source background-update queue transactions for fruit removal. |
| CF62 | Life/scene transition after source defeat. |

No host mapper, PPU, palette, audio, enemy, block, scene, menu, authentication or
retirement implementation is implied by these imports. The source indirect
helpers are validated only for the declared OAM and immutable table pointer
domains; their writable operands require actual NMI/IRQ proof before admission.

## Reproducible proof and files

`CPU.json` passes **11,326** comparisons: original reset/start and 640 natural
NMI frames, naturally earned vine continuations, explicit unblocked climb
leaves, all 12 authored fruit contacts, fruit fall, nine enemy-hit fixtures and
original hit animation, initialization and life-boundary seams. It compares all
original non-stack RAM, AXYP (ignoring B) and SP. Minimum observed CPU SP is DF.
There are 22 exact body render cases / 11,264 pixel comparisons. No hardware
timing, ISR, native gameplay, earned full-stage fruit collection or SMB 1-1
success is claimed.

Source recipes:

- `tools/reference/dkjr_original_cpu_1102_v1.py`
- `tools/audit/recover_dkjr_source_1102_v1.py`
- `tools/audit/prepare_dkjr_component_1102_v1.py`
- `tools/audit/check_dkjr_component_1102_v1.py`
- `tools/audit/report_dkjr_source_1102_v1.py`

Run the compiler, checker and reporter, sequentially, each through
`python -B tools/audit/run_bounded_build_v1.py --resume --output
build/dkjr-source-1102-v1 --timeout 180 -- python -B SCRIPT`.
`source-report.json` binds exact source/output hashes and commands. The private
root stays below 32MB / 128 files; no large donor tree or historical graph is
copied. Existing Excitebike source and installed ROM are read-only inputs.

# Prince original actor component

Original donor: `C:/NES/Prince of Persia (USA).nes`, SHA-256
`5f14d4d31cc588ddcdfb2b4d46eb7051b06d02655c9208037ef7ae137c4740e4`.
Mapper2,128KB PRG,8KB CHR-RAM. This remains a private source component,
not a playable menu identity or native1-1 result. On November2, root granted
the42 physical pages and conditional overlay RAM in
`docs/qa/allocations/prince-1102-v1.json`, rebased to installed cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8.
Code uses conditional RAM bank3 A000..BFE0; original state uses conditional
RAM bank2 C000..C800 and pose metadata C800..DD32. BFE0/DFE0 headers and shared
DFD0..DFD2 clock ownership remain explicit. The later Metal-only installed1cd8
rebase preserves these resources; see `allocations/roster-rebase-1102-v3.json`.
The current private contact/native-leaf image uses7555 code bytes and leaves751
live bytes across two owned spans. Its measured lossless backing uses41880 of
43008 bytes, leaving1128 bytes; the common worker does not yet support this codec.
The247-byte shared resident reservation is granted in
`allocations/common-cold-1102-v1.json` and is coordinated by the Bub owner.
Prince shared routing, codec integration and menu admission remain unqualified.
Raw38 is reserved
for the existing Excitebike alternate. Excitebike owns raw37's
current dispatcher and its own granted resources; none are Prince resources.

All temporary outputs are in `build/prince-actor-1101-v1`. No asset tree,
native frame capture or emulator instance was created. Source fixtures stay
in memory and aggregate into compact receipts.

## Current source and native-leaf measurements, November2

The separate `recover_prince_contact_1102_v4.py` successor includes original
D17A/D4F5 post-physics support, wall, fall and landing selection, F882 ledge
catch, D427 landing and both8574/8710 HP leaves. It reassembles4665 original
instruction bytes across2017 boundaries, SHA
`97522f3bbfb28a7f40a935c08f2cece851d97d7cc8d2c5cc10c50bbc1e5fce65`.
Local branches whose linked targets are in range save1287 bytes. The resulting
source image is7105 bytes, A000..BBC1. `contact-CPU.json` passes26454 directed
instruction cases; `contact-sequence-CPU.json` passes1570 genuine donor frames,
including976 reached replacements and240 full terrain/contact calls. Source
application RAM, physical flags, live stack, bank, PPU, OAM and APU match.
Four original trap/potion/sword-room boundaries remain explicit alongside the
world/audio boundaries; they are not invented native tile behavior.

`check_prince_contact_point_1102_v2.py` places the94-byte actual native point
reader in B310..B36E of the source-declared B310..B400 alignment span. It passes
6144 pairs against the real native BlockBufferCollision, including all256
metatiles, page carries and both buffers. The146-byte remainder is still free.

`prince_host_render_1102_v1.s` is450 bytes at BBC1..BD83. It executes the genuine
FarCallCommon, X5SetPhysicalChr and MetaspriteRenderLoop. All408 source poses
and280 clipping/capacity/alignment cases match exact source packet order,
attributes and geometry. It uses only the granted31 body pages. A completed
native NMI publishes the requested physical pages. The742 actual IRQ/lag-NMI
instruction/SP cuts preserve both private banks, R0..R7 and SMC state. Four
farcall cuts occur immediately before STA5115: NMI restores the pending shadow
bank early, and the resumed identical store plus complete foreground result
and return mapping remain exact.

The native packet occupies exactly C200..C235, within original OAM that no
recovered source direct/indexed/data-indirect operand can access. Every indexed
operand is conservatively expanded through all256 indices. It remains mapped
while the native emitter replaces A000 with ROM. The leaf also exports original
04BC,04C3,070F and06F1 projection values; the latter uses original actorY,
independent of the host render anchor. It does not repurpose source-live OAM.

`measure_prince_host_storage_1102_v3.py` combines those qualified leaves into
`host-private.bin`, SHA
`31cf2b987ff50c589ee9ae67d45e9a0fe745b0955be4666f1d17d9a4fb6cf260`.
The actual6502 decoder reproduces its7555 bytes from5850 bytes and the5426-byte
metadata from4778 bytes. Including unchanged31072-byte art and180-byte decoder,
physical cost is41880 bytes. Total cold decode cost is1171232 cycles. Decoder
C000..C0B4 and staged tail C200..C332 exist only before initialization; return
from decoding, zero the full original2KB state, initialize, then publish headers.

The private payload still contains explicit fixture environment addresses.
World material/coordinate bindings, real update/camera/health/combat ingress,
owner/header/cold dispatch and native raster remain incomplete. Direct
SetAction motion envelopes omit controller takeoff alignment, so they do not
establish a low-jump ability limit or any helper requirement. No ROM, emulator
capture, install, playable identity or full1-1 qualification is claimed.

## Historical v1 instruction and caller closure

`recover_prince_core_1101_v1.py` walks the actual donor instruction graph and
explicit script command vectors, reproducing3042 instruction bytes at their
original PCs across1312 boundaries. The reproduced instruction-byte SHA is
`b98957ef45fb9abcde37d41ca7648563a1267b6d49309a6634d95af8c22d0692`.
The relocation is `prince-core.bin`, SHA
`34b4029da5a89be5f06bdaf6f9e9cc19eafa59ea3e945c463938f00d7cc3cfef`.

The recovered entries are original actor animation advance7:F158, action
selection5:8730, fall5:8133, input decode5:839F and control prefix7:EFF2.
Animation stops before the genuine renderer continuationF1A2; controls stop
before the original combat selectorF090. The source action table contains
94words, including null action0;93 scripts are recovered with all15 command
handlers. This retains original script-driven X/Y movement, turn, jump/fall
setup, ledge transitions and audio/scene command boundaries. It does not
replace them with a Mario movement curve.

Actor records have stride14. Original060E is active;060F/0610 are X;
0611/0612 are Y;0613/0614 are script pointers;0615 is facing;0616 action;
0617 animation frame;0618 actor mode. The component retains the complete
2KB original application state at the private fixture C000..C800. Original
zero-page fields relocate into this state, so no host zero page is borrowed.
Source script pointer values remain authentic through a private translated
read seam; the command vector's temporary pointer is normalized in comparisons.

Twenty original environment boundaries remain explicit, with actual donor
instructions used as the CPU oracles: world contextD4A2, feetD499, tileCE63,
tile-at-Y CE66, gateDB18, aheadF649, rowD147, offsetF655, offset-X FA60,
add-X F870, columnD12C, alignC8D4, supportD4B5, gate supportD9B5,
room-aboveDE0B, gate heightCAAB, fall damageF882, scene-end2:BB4F,
music6:AA19 and soundD6CE. Their fixture callback addresses are not host grants.

`check_prince_core_1101_v1.py` passes11526 original-vs-relocated CPU cases:
558 action selections,7728 script advances,180 fall cases,180 direct command
cases,2048 input decodes and832 control-prefix cases. All93 script pointer
cycles are bounded and qualified. Seventeen environment boundary types occur;
scene-end, gate-height and room-above remain unexercised. Original action10
climbs Y128→65 and action68 reverses Y128→191. B is careful stepping; running
A selects the original running-jump path, while Up enters the ledge/vault scan.

`check_prince_sequence_1101_v1.py` also passes1570 natural donor CPU frames,
including900 startup frames from the genuine reset/NMI/main flow. It replaces
744 actually reached entries in a cloned running donor:256 actor advances,
240 control prefixes,240 fall updates and8 action selections. The240 control
continuations resume the genuine original combat selector. Real donor world,
combat, renderer and audio code still execute. Application RAM, registers,
physical status flags, live stack, bank, PPU, OAM and APU match each frame.
Only the ever-reached discarded stack-write interval is excluded; application
buffers in the lower stack page remain compared. This is an untimed CPU
oracle and does not qualify Mesen timing, source cadence on the host or1-1.

## Original art and measured resource request

`recover_prince_art_1101_v1.py` executes original bank4:B449 rendering and
F325 CHR-RAM upload for204 nonzero source frames in both facings. The408
generated8x16 packets reproduce original8x8 source pixels, order, attributes,
geometry and original projection witnesses. The historical9-cell/262-pixel
body packet is reproduced for source frames118/119 in both facings, SHA
`2e057652662d52a346cb6f2f5ca3414d22557d20b465baf5f6e834f7109fcb13`.
Projection witnesses070F/06F1/04C3 are recorded, not claimed as host hitboxes.

| Component | Bytes | Conditional runtime placement proposed |
| --- | ---: | --- |
| Recovered code |3999 | Private code bank |
| Original scripts |1765 | Same code bank |
| Original tables |220 | Same code bank |
| Aligned complete code image |6081 | Fixture A000..B7C1 |
| Original private state |2048 | Fixture C000..C800 |
| Packed original pose packets |5426 | Same state bank after private state |
| Native8x16 body patterns |31072 |31 physical1KB CHR pages |

The2KB state plus pose metadata uses7474 of8192bytes, leaving718bytes before
any new host state/header requirements. The code image leaves2111bytes in
an8KB bank before host adapters. Body art has971 unique8x16 pairs; a pose
needs at most13 sprites and3 simultaneous physical1KB pages. All408 facing
packets decode exactly from the5426-byte compact metadata artifact.

ROM payload is42579bytes. Storing all three artifacts separately on1KB
boundaries needs43 backing pages; packing their unused page tails could use
42, but that is not an implemented loader. A resident loader, renderer,
publisher, dispatcher and host environment adapters are not included in6081.

The following November2 proposal evidence predates the formal pool/RAM grant
above. Its source receipts retain their original proposal-only status and bind
to the prior installed
Arthur/Excitebike d8a87050beefefe96869ebd4d188beeb52733241cd2c0fa64392a55ec8ebca05.
Excitebike's target-specific728..739 closure cannot be inverted into a general
free-page inventory. Its dispatcher has no Prince loader seam and only8
resident spare bytes as of the sibling handoff. Common bootstrap/router funding
is now coordinated by root and the Bub/Bob owner; no shared dispatch was edited.

The revised42-page proposal is:
`341,343,345,347,349,351,353,355,357,359,361,365,369,373,377,381,383,385,387,389,391,393,544,545,605,607,609,611,613,615,617,619,621,623,625,627,690,691,692,693,695,795`.
All nine Bub/Bob reservations are excluded:301,305,337,362,363,440,819,666,441.
WWF's live zero page667 and Parodius's actual special-pool846 are excluded.
The first proposal's six Bub overlaps were replaced before any grant or write.

`audit_prince_pool_1102_v1.py` rebinds816 unchanged main-ROM writer sites and15
complete private1KB source chunks, actual new-owner/cold-loader domains,
Kirby/full Kirby/Meta Knight/TMNT tables and finite source publication contracts.
All195 WWF metadata records and the six256×256 selector domains remain bounded.
Later named owners remain conservative full reservations; this is a finite
source-domain proposal for root review, not arbitrary mutable-shadow safety.

Rogue's actual body/facing60 supported cases, two death cases and all40 typed
item/four-phase cases plus three drop kinds publish only680..689 and694.
Dragon Power's66 actual records and1024 all-pose/facing/wave combinations publish
only788..794. Five current selector/renderer routines, including the34B mixed
page helper, reproduce exact ROM instructions from the explicit mixed-render
and flagpole source adaptations. These constrain the six replacement candidates.

Page795 is also excluded by the actual SMB3 selector, rather than by reading
retired table labels. All7 forms×81 frames×2 faces execute M3SetFrame:1134 cases
yield only524..543. The exact current caller clamps form0..6; all seven low
pointers name M3Form0ChrLo; its values24..27 combine modulo256 with offsets
`0,4,4,244,0,248,252`; the high byte is literal2. Old form1/2/3/4/6 table spans
were retired by the source low-table factor and cannot be interpreted as live
CHR tables. Exact caller/helper instructions and pointer/offset bytes are bound
in `smb3-pages.json`.

`check_prince_chr_publication_1102_v1.py` passes6840 actual setter instruction
cuts,2376 actual native-Mario menu clear/restore cuts and38 busy-guard identity
cases:9254 real lag-NMI returns. All42 proposed pages occur as unpublished
intermediate shadow pairs; none is published. The audio child is an explicit
return port. This qualifies that protocol, not gameplay or a resource grant.

`prepare_prince_pool_layout_1102_v1.py` produces one43008B component blob,
not a host ROM. Body bytes0..31072 occupy31 logical pages; core6081B begins
at logical page30+352; pose metadata5426B begins at logical page36+289 and
ends at logical page41+595. All408 facing packets and2578 actual body-pair reads
remain below31072, so sharing the unused last art-page tail does not expose
code as art. All971 pairs remain reachable. Physical spare is429B: the2111B
runtime code-bank spare is not additional backing storage for host adapters.
The current core still uses20 explicit fixture callbacks at5200..5330 and must
be relinked to real owned host leaves before hardware execution.

PRG123 has three proposed source-declared pads:AF40..B000(192B),
B9D6..BA00(42B),BF93..BFA0(13B),247B total. The complete8192B Mac native music
source reproduces current ROM bytes exactly. Read/fetch instrumentation executes
all nine legal tune state machines until exact66B source-state repetition:
138131 updates and65856630 actual source-bank reads, none in a pad. Tune23's
period is124160, so the earlier20000-update attempt did not close it. Source
request/restart/retirement review and a measured common resident fit still
precede any grant. No Prince-exclusive claim is made on these shared candidates.

## Durable recipes and remaining integration

Durable files are `tools/reference/prince_original_cpu_1101_v1.py` and
`tools/audit/{discover_prince_actor,recover_prince_core,check_prince_core,
recover_prince_art,pack_prince_resources,check_prince_sequence}_1101_v1.py`.
Their output receipts bind the donor, source tools, code and packed artifacts.
Run each artifact producer through the bounded runner with the exact output
root above and `--resume` while this remains an unfinished component.

The resource proposal adds `audit_prince_pool_1102_v1.py`,
`check_prince_replacement_pages_1102_v1.py`,
`check_prince_chr_publication_1102_v1.py`,
`audit_prince_resident_padding_1102_v1.py`,
`check_prince_mac_padding_consumers_1102_v1.py` and
`prepare_prince_pool_layout_1102_v1.py`, all under `tools/audit`.

Remaining work includes real host bindings for the20 declared environment
boundaries, original combat beyondF090, health/death/pickups, body terrain
contact, lifecycle/retirement/cookies, actual source-clock and ISR ownership,
physical CHR publication, native controls and full1-1. No helper has been
added or qualified. Host allocation must precede any integration edits.

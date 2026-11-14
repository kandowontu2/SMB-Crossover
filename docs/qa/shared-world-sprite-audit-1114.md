# Current421 shared world-sprite audit

User-reported families: Prince of Persia, classic Donkey Kong (raw28, not DK
Jr.), and all six WWF wrestlers. The initial ordinary image probes cover
Prince, Donkey Kong, and Hulk Hogan. No graphics change is composed or granted
by this note. Root owns native runs, allocation, delivery, and cleanup.

Input: installed421
`421379021e775e6e03357c0aa11d4cab04008452f94bc9e8938f0662cc0c979f`.
The explicit typed421 normalizer preserves the installed hidden-response and
fa66 fixes. The factory rejects dirty/truncated images and the exact older
fa66/12397 parents. Frozen existing factories/defaults are unchanged.

## Frozen ordinary image probes

API: `replay_shared_world_sprite_images_1114.controller(raw421, key)`.
Factory SHA256:
`eaec9ad2d54d6d9d0230a287f814c03c33ed4ed4ad95b088efcd63bd24a10440`.
Template SHA256:
`623a075ec25b5c7df77e9a34fa6dacb08b4da9126c80fdd31435b59a0fffa00b`.

| Key | Actual compiled menu | Frozen LF Lua SHA256 |
| --- | --- | --- |
| prince | slot29, Select1, PRINCE PERSIA, raw38 | `96411abb6d747a894c77a6923902c5b1849a79f335c2ce0cf03454b592652004` |
| donkey_kong | slot27, Select0, DONKEY KONG, raw28 | `b4ce38d5d2d5e3afacdac842cd726e5f719efb7358f1f7b0498ee3c9484984c6` |
| hogan | slot28, Select0, HULK HOGAN, raw29/role0 | `e9bf0fdd30ac5c61542763e73a1729a834493d1a36147b8f9030ccba51d57957` |

Each uses the real cold title/menu and ordinary controls. The first image is
the live first Goomba; the second is the naturally born kind0 Mushroom after
original emergence to state128. There are exactly two stdout/in-memory PNGs,
at most65536 bytes each. No screenshot file, ROM, save state, actor, terrain,
health, ability, position, or cheat seed is produced. The Prince runtime cookie
is checked after Start, when that runtime actually exists.

Each image receipt records actual hardware OAM and the CPU shadow separately;
PPUCTRL writes and sprite height; MMC5$5101, $5130, and $5120..$5127 writes;
software CurrentCHRBank/X5ChrMode bytes; native actor/metasprite metadata;
palette bytes; physical CHR-ROM bytes for the selected OAM patterns; and the
first eight eligible OAM slots on each relevant scanline. MMC5 PPU-debug
pattern reads are deliberately not used as sprite-pattern authority. Pattern
addressing is selected by the observed PPUCTRL8x8/8x16 bit, including the tile0
pattern-table convention from tile bit0. Scanline eligibility is a bounded overflow diagnostic,
not a claim that every eligible sprite produces visible opaque pixels.

Root completed native Prince35667 with this exact frozen factory/script; its
observation result is recorded below. The five other wrestler
keys are explicit selectable parameters, but their individual ordinary image
routes are not qualified by Hogan's receipt.

## Source route components and limits

`check_shared_world_sprite_images_1114.py` performs actual compiled Select,
Start/parser/constructor and full original Main/NMI execution. Only the
peripheral clock/controller are supplied after ingress. The model does not
render: a marked PNG-header API fixture tests bounded screenshot/base64 plumbing
only. Initial mapper latch observations are exposed from that established CPU
fixture; its $5101 starts0, unlike the native cold mapper setup's intended3.
Consequently these runs establish route reach and CPU writes, not art, raster,
hardware sprite-mode, or native launch acceptance.

| Route component | Main passes | First Mushroom birth | Mature observation | Receipt SHA256 |
| --- | ---: | --- | --- | --- |
| Prince | 510 | Main445, actor336/136, kind0/state1 | Main510, actor336/119, state128; player349/176, HP5/lives2 | `a4c66792436fe7c0227e94dd1c70585425fd6563dafb5f1845f0a20864f77809` |
| Hogan | 550 | Main485, actor336/136, kind0/state1 | Main550, actor336/119, state128; player328/176/lives2 | `26d61da7ee29c0de2a9cdc2aec5e637f2bbadba2a161703f003c108c55cf4cee` |
| Donkey Kong | 330 | Main264, actor336/136, kind0/state1 | Main330, actor336/119, state128; player382/176/lives2 | `e06ed09794acb838f48debf8f30089aead43eda3cf84ab1db9f91bf44d0be6bb` |

These component receipts preceded the final native-menu cookie-order guard;
their CPU_CONTROLLER_OPENING execution paths are unchanged. Prince/Hogan also
preceded the DK-only earlier-barrel threshold change. The frozen final scripts
were separately regenerated, compiled and pinned above. Root's real cold runs
remain required for those final native frontend paths.

The first DK route requested original B only within40 pixels, reached the first
Goomba image, then failed to reach the Mushroom (source1600 bound, x283).
Requesting original B within100 pixels allows its real age16 barrel spawn to
defeat that Goomba before contact; the source330 route above passes. This is a
controller calibration, with no game or jump/helper change.

## Bound native records and current source observations

Compiled native record bytes equal the typed12397 reference:

* Goomba records PRG4:$AF2F/$AF38/$AF41/$AF4A, eight-byte bodies, tilesA2/A4,
  attributes03 or43, native palette3.
* Mushroom PRG4:$AD4D, record `08 7c 02 08 00 7e 02 08 08`, native palette2.
* CHR initial logical sprite windows1/2/3 are20/21/22, mapped to physical16/17/18.

The project already defines native metasprites as8x16. X5ChrMode131 is a
per-window direct-physical marker80 plus upperCHRbits3, not PPUCTRL sprite
height. Source gameplay PPUCTRL writes are168 (bit5 set). Native PPUCTRL and
$5101 still require the real write witness.

Actual source execution resolves the same native OAM tiles through unexpected
pages:

| Family/source spot | Window1 | Window2 | Window3 |
| --- | ---: | ---: | ---: |
| Hogan, live Goomba | 532 | 533 | 534 |
| Hogan, mature Mushroom | 532 | 533 | 534 |
| Prince, live Goomba | private345 | 533 | 534 |
| Prince, mature Mushroom | private383 | 533 | 534 |
| DK, mature Mushroom | private823 | 533 | 534 |

The corresponding Goomba OAM remainsA2/A4/palette3; Mushroom OAM remains
7C/7E/palette2 (priority32 during its native emergence draw). This supports a
CHR-window investigation, independently of palette/overflow questions. It is
not yet a native screenshot result.

Static421 CHR pages are not duplicate copies: pages532/533/534 differ from
native16/17/18 in883/848/913 of1024 bytes respectively. Private823 and383 differ
from native16 in790/795 bytes. Native page SHA256:

* 16: `fbdfcb689bab3c74a0f5ad235ab24dea6625378658f3e70fbbe0144200c6709d`
* 17: `006c3d8e9cf3760a610ab3a8f89519d464e6d25fac12f26ab204eb538680269e`
* 18: `2d6b5b5278fc526cbd3fcad6e1f0209cf5348160c1227af958f7ebc41fbbd41c`

## Cold writer closure so far

The separate `--writers` diagnostic instruments both genuine CPU entry aliases:
the native source runner and the compiled menu runner. It records opcode-entry
PC independently of the CPU object's advancing operand PC. During ordinary
navigation into Hogan:

* Actual X5SetPhysicalChr mode store is PRG62:$A27D, `99 e0 73`.
* Actual X5ClearChrModes mode store is PRG62:$A2A2, `9d e0 73`.
* The last four-window preview occurs while SelectedCharacter28/menuState2.
  PRG76:$BC50 repeatedly JSRs FarCallCommon$015A; lowRAM$016B then calls
  X5SetPhysicalChr$A275. It writes82 into windows1/2/3.
* The earlier preview clear is reached through PRG76:$BC36 calling
  X5ClearChrModes$A29E. The source corresponds to FmDrawPreview's four direct
  physical700..703 windows. After Start, Hogan writes only its private window0
  mode81. Modes1/2/3 stay82 although bank bytes become logical20/21/22.

Actual Start reaches native LoadAreaPointer PRG126:$8A30 from PRG9:$BC1D
(`JSR $8A30`). Its LoadAreaTypeCHR macro writes logical windows1/2/3 at
$8A65/$8A69/$8A6D, bytes `8e4801 / 8e4901 / 8e4a01`, replacing preview low
bytes189/190/191 with20/21/22. The source macro in src/mmc5.s resets windows1..7
and BG8..11 when the area CHR type changes, leaving their direct-mode flags
unchanged. The exact full macro/preimage and caller contract remain to be
measured before any proposal. A shared reset must preserve the owner's
subsequently published private windows. It would not alone repair Prince/DK's
active private ownership of native window1. Those need a separate measured
owner/tile-range allocation using existing sprite windows, with all poses,
pattern-table bits, BG mode and NMI publication contracts checked. No blind
tile-bit OR or CHR repack is authorized or implemented.

## Native Prince35667: corruption confirmed

Root reports the exact frozen Prince96411a script completed the observation
assertions on actual Downloads421:1640 physical frames,1639 input polls,
889 Main entries=returns,512 original commits; lives2/HP5/power0. Receipt:
`cb8d4d25d09bdd29a934597338524b89b67286fd56ea01269b5e84c3fba1d1ad`.
This is a successful observation run, not acceptance of the corrupted art.

Root viewed both in-memory images: the Goomba appears as a brown sliver and
the Mushroom resembles a flame/Prince tile. The PNGs are2652 and2767 bytes,
SHA256 respectively
`eff892b044bddccd2cda5c52b5f1464b2773f52026b0cec4d3bc958cba3fbb4a`
and `595e13dbdc682834d4d7ae252f32418efbae1a19ca26d1257dfd8bdbe9256f55`.
Root retained the receipts/images in memory; no files were created.

Both actual hardware observations have PPUCTRL168($A8), sprite height16,
MMC5 CHR mode3. Thus the native8x8-versus8x16 hypothesis is not the cause in
this Prince run. At the Goomba image (physical943/Main511/source134), actual
sprite banks are `[351,345,533,534,19,20,21,21]`; direct flags are
`[81,81,82,82,0,0,0,0]` in hex. Goomba OAM A2/A4, attr3/palette3 reads
window2/page533, with pattern hashes differing from native17.

At the mature Mushroom image (physical1640/Main889/source512), banks are
`[341,383,533,534,19,20,21,21]`. Mushroom OAM7C/7E, attr34(decimal,
palette2/background priority), reads private window1/page383 and differs from
native16. The actual actor is337/119, state192/kind0; natural birth was336/136
at physical1507/Main822. This confirms both the stale direct-mode problem and
the separate active private-window conflict in a real launch. No seed, helper,
ROM output, capture file, or patch guard violation occurred.

Root75510 then completed both frozen Hogan/DK probes on actual Downloads421.
Hogan:1490 physical/1489 polls/908 Main entries=returns; receipt
`1047d179103b00c2e620174f43c29da691f0900210c10c4366fb6c41b335b063`.
Both spots use `[446,532,533,534,19,20,21,21]`. GoombaA2/A4 reads533 instead
of17; Mushroom7C/7E reads532 instead of16, with actual pattern mismatches.
Goomba scanline maximum7 and Mushroom maximum2 exclude the eight-sprite limit
as the cause in those views. Root viewed corrupted art. PNGs2630/3130 bytes:
`f433ba07279e8c0c809133e38c1c030444c544b92316f7e38241f24fb17d70eb` /
`11457176187137c4f7b2bae5ff731ac5a6a318c3ddb613fe68097a2f009cbf80`.

DK:721 physical/720 polls/666 Main entries=returns; receipt
`2eb34840b19c15df73f8984b52243fd621692a332d683cc75c534876b55158a8`.
Goomba banks `[820,823,533,534,19,20,21,21]`, mature Mushroom banks
`[821,823,533,534,19,20,21,21]`. GoombaA2/A4 reads533. Mushroom7C/7E reads
private823; both32-byte patterns are all zero
(`66687aadf862bd776c8fc18b8e9f8e20089714856ee233b3902a591d0d5f2925`),
and Root's image shows no Mushroom. Maximum relevant scanline counts8/2 do
not exceed the limit. PNGs2598/2674 bytes:
`d3639c9ec4b4e7fed4f9b247bd0798721934d20825a6ae3a041c08bf9911aac5` /
`80d7a864a79b1607b65d3bff2c9e780399cf2a44b8145f2b683a4e656d7e55aa`.
Both families retain lives2/power0 and have natural kind0 birth. All actual
shots are16px sprites/MMC5mode3; PPUCTRL is168 except DK Goomba172 (still bit5
set). Guards are clear, two in-memory PNGs per run, zero capture files.

## Unplaced common reset fit

`measure_shared_world_chr_reset_1114.py` authenticates the existing29-byte
logical sprite restore at PRG126:$8A63..$8A80, file1034867. Old preimage:
`a2148e4801e88e4901e88e4a01e88e4b01e88e4c01e88e4d01e88e4e01`, SHA256
`f4efbe278fe85632f7582264e8413fbe9e8e144f84ee9953b9c4eaf2822ee229`.
It measures this23-byte body plus6NOP within the same29 bytes:
`a20ba9009de073cad0faa206bdc7e09d4801ca10f7a21aeaeaeaeaeaea`, SHA256
`2f917519169bf443bb9d051d20d65fc6baefc175d2304ac84e54890cf9076ce2`.

The proposed loop clears modes11..1, preserving private0 and wide/special/HUD
state; restores logical windows7..1 from existing CHRBankInitValues; and
restores live outputX26. The original following
`INC ReloadCHRBank / LDA AreaType / RTS` remains byte-exact
`ee4601ad530760`. No helper, farcall, new RAM, CHR data, storage, or extra stack
is used. It executes only on the macro's existing area-CHR-change path.

4096 isolated CPU cases cover all256 incoming flags, all4 legal AreaTypes,
and4 register/RAM patterns. A/X/Y/P/SP and every RAM byte match original,
apart from the intended modes1..11 zeroing. Window0 and wide/special/HUD
state are identical. Including the retained suffix, cycles are58→242
(+184 on that area-type change, not per Main); minimumSP206 and extra stack0.
This is a proposed instruction-fit/ABI measurement, **not an allocation or a
composed ROM**. Cold Start, pipe/next-level/same-pose constructor, native palette
and CHR refresh, genuine NMI/busy/publication, and owning-image composition
gates remain open. A correction and the private slot1 solutions remain pending.

All producers use bounded `build/shared-world-sprite-audit-1114`, max-files1,
timeout<=600. The directory was never created: zero generated files/bytes,
zero Mesen runs, and zero ROM/capture outputs by this helper. Existing retained
symbol/ROM inputs and the authenticated Prince carrier are reused read-only.

The CF stage checkpoint is separate: all four native full1-1/25grounded1-2
routes are recorded in `contra-force-full11-source-1114.md` at commit aa5a13cc;
their measured idle/walk30Hz performance deficit remains open.

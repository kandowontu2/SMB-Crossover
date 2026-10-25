# Mike source graphics and effective-weapon HUD

Private NX follows `vic-hud-font-nw`. It fixes three source-art findings and a
HUD refresh bug; it does not complete the full verification gate.

The accepted ROM is
`17b8ae45a1973e252c1f9e8683137c6829dfa5bab8dcb44bce1c25080e4df095`.
Large source/native captures, rejected trials and full replay frames remain at
`C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-mike-art-nx`.

## Confirmed source findings

The original USA StarTropics cartridge is pinned to
`ff20d5e9600565ae61e4eae6594c9f1e55e2a748a46bba0c88285140420a219a`.
Its existing debug-loader flag is enabled only in explicitly labelled source
component ROMs. Inventory and drop arrangements in those fixtures are not
original campaign achievements.

- The native small heart and star use two horizontally mirrored sprite halves.
  Their physical CHR205 tilepairs12/14 are also present in CHR248. The old port
  instead copied unrelated CHR243 tilepairs62/60 and drew one8x16 part. Both
  pickups now use the complete native16-pixel composition.
- Super Nova's outbound frames use CHR205 tilepairs32/34 in the original7-1
  dungeon. The old extractor forced Nova into the first dungeon, whose active
  CHR248/249 pages supply unrelated fragments at those indices. Actual native
 7-1 mapping/OAM now establishes the source association; a checker-like held
  weapon frame alone was never sufficient evidence of a defect.
- Collecting Nova could leave “SSTAR” in the HUD. Collection queued the label
  before the next effective-tier update, then cleared its dirty flag. Effective
  tier changes now invalidate the HUD for the next available publication.

The four32-byte source pairs replace existing slots; the4KB asset does not grow.
The original body/common pages and all other weapon/item bytes stay unchanged.
Two pickup records gain their mirrored half. Four combat operands follow the
relocated art labels. The tier function retains its original four-byte tail
footprint, and a same-bank helper is appended after existing profile code.
All pre-existing Mike code/state addresses remain unchanged. Only PRG96/97/98
and CHR710/711 differ from NW; no mapper/physics/collision/audio changes are made.

The stable SMB world-palette2 hue adaptation remains explicit. This repair
proves source masks/indices/composition, not original StarTropics hue parity.

## Accepted checks

| Check | Evidence |
|---|---|
| Original native heart/star halves |48 OAM witnesses per item, plus mapper/palette trace |
| Original outbound Nova |Both original7-1 frames observed with physical CHR205 |
| Linked tier ABI |5,760 cases preserve effective tier, A/X/Y and meaningful status; HUD invalidates only on tier change |
| Native Easy and Hard components |Physical star/heart/Nova collection, real B releases, two real enemy defeats/drop calls, pickup sound requests, correct committed item/projectile CHR and visible NOVA label |
| Actual opaque source glyph pixels |8,002 pixels in136 rendered frames per mode; zero mismatches |
| Existing arsenal |Both modes pass physical13 item kinds, health gates,10 selectable specials, Mirror reflection, Asterisk second-B split and target defeats |
| Easy1-1 |3,849 frames, zero deaths, independent input/trace byte-identical replay |
| Hard1-1 |3,940 frames, zero deaths, independent input/trace byte-identical replay |
| Endpoint |25 controllable underground1-2 frames in each replay |
| Actual body CHR |Easy2,326 and Hard2,339 active frames; zero mismatches |
| Cold entries |All37 identities pass their ordinary menu/movement/interrupt checks |
| Ordinary flag-off builds |Both existing14-character mapper hashes remain exact |

All7,389 replay PNGs from frame200 through the penultimate frame are retained,
alongside endpoint images. Full native inputs and telemetry match independently
within each mode. Camera telemetry's largest single-frame step is4 pixels;
world-X steps are at most6/3 pixels in Easy/Hard. These bounds are not a complete
PPU-scroll or universal visual-clean proof. Root inspected both sampled route
overviews and the actual item/Nova/HUD component images.

Opaque-pixel checks use the original source pairs and actual DMA coordinates.
A single fixed+1 screenshot boundary applies throughout. RGB is calibrated
independently from the unchanged NW palette2 capture, rather than assuming a
different NES palette's gold RGB. Source hue parity is not claimed.

## Retained failures and fixture corrections

- Original `native-d12-v1` requested a later dungeon with inputs during the
  startup transition and did not actually select it. It is not accepted as7-1
  evidence. V2's one-frame confirmation also failed its new admission assertion.
  V3 uses ordinary held menu inputs and asserts actual chapter7/room133 loading
  before arranging inventory.
- The first drop arena omitted its native world-X field and placed graphics
  at an edge. The accepted arena initializes both world and screen coordinates.
- Shallow overlay v1 silently used the root nested art. V2/V3 stage the parent
  module and an explicit staged binary path. An overly narrow PRG-diff guard
  initially rejected the four legitimate relocated art operands. The final
  guard checks those operands against linked labels individually.
- Early enemy arrangements fell before a distant projectile arrived. Moving
  the arranged target nearer, as in the established arsenal arena, allows the
  actual attack/drop paths to be observed. No terrain/gameplay patch hid this.
- The old arsenal test's single-frame second-B pulse was not sampled:
  SavedJoypad/Pressed remain zero in `arsenal-diagnosis-v1/split.csv`. It fails
  on unchanged NW too. Merely widening the observation window still fails and
  is retained. A three-frame fresh B hold and immediate live-blade observation
  pass on both baseline and candidate, with unchanged weapon code.
- Candidate v3 reproduces the stale NOVA label; v4 fixes it and passes actual
  nametable assertions. The art-negative NW arena also fails on its missing
  star half, as expected.
- The first RGB checker assumed gold RGB254/174/50 and rejected4,328/8,002
  pixels. Independent unchanged-parent calibration yields234/158/34. Its masks,
  coordinates and global screenshot alignment are unchanged by that correction.

## Remaining work

Source music/SFX for Mike, other weapon-source art associations, original
utility inventory, broad performance/graphics work, TMNT secondary equipment,
the final every-identity/every-item matrix and the37-identity MMC3 port remain
open. Component item arrangements do not certify natural emergence from every
reward block or every applicable damage/expiry path. Existing public ROMs are
not replaced by this private checkpoint.

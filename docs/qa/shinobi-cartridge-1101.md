# Shinobi cartridge integration — incomplete

Private successor:
`build/shinobi-cartridge-1101-v2/candidate.nes`, SHA256
`4e21828fc696a17491fa63f3e015e3223f04f701ea6a343c244e3cb5a41a98dd`.
Base is the installed Metal optimization128915. Not delivered or menu-unlocked.

The existing6811-byte source actor,1696-byte metadata,3072-byte native artwork
and980-byte loader now occupy actual cartridge bytes. Previous loader tests
used a synthetic4000 fixture; this successor executes actual bank65 through
the native farcall mechanism.

## Resident allocation

Reserve physical PRG65 offsets0800..0E00 (A-window A800..AE00; C-window
C800..CE00) exclusively for Shinobi resident code. Current loader+dispatch
uses980/1536 bytes, leaving556 bytes for integration hooks.

This allocation lies within explicitly authored Proto Man padding, not merely
an FF scan. `src/protoman.s` pads from `ProtoArtEnd` to offset1108 before the
retained common projectile records. Current compiled ProtoArtEnd=C738. All54
left/right pose descriptors end before that label; the27-entry selector table
uses bounded/source-defined pose IDs. No existing debug symbol lies in the new
range, and all1536 bytes wereFF. The common records atD108 and audio atD368 are
untouched. Existing DK/WWF code later in bank65 is untouched.

The12 previously reserved CHR pages are retained:
503,504,505 artwork;506,507,508,509,510,513,515 actor;516,517 metadata.
Their pre-write bytes matched the earlier reviewed baseline exactly. All70
declared host addresses and three bank imports still match the current build.
Existing RAM ownership/retirement conditions remain mandatory.

## Actual cartridge CPU evidence

`build/shinobi-cartridge-1101-v2/loader-CPU.json`:

- Cold forced-blank load:18450 actual buffered PPU reads; all7168 actor bytes
  and2048 metadata bytes verified against the original component.
- Both complete16-byte headers match; all32 single-byte header corruption
  cases rejected. Both headers invalidated on retirement.
- Foreign RAM banks0/1 unchanged; originalAXYP retained by native farcall.
- Cold445775 cycles, warm1201; minimum standalone SP193/194.

These are forced-blank CPU fixtures, not a native menu/Main/IRQ playthrough.
No memory-backed synthetic code, PC override or unlock was used.

Next: connect raw36 resolver/dispatch, forced-blank scene ingress and foreign
overlay retirement using the actual cartridge loader. Implement required
native collision/health/death boundaries before admission. Existing private
actor services only cover movement0,draw2,construct15; numeric donor callback
targets still need resolution. Then native controller tests,1-1 and lag.
Keep the full roster/powerup goal and helper-platform list open.

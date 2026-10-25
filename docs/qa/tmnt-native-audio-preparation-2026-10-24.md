# TMNT native audio: verified preparation, integration still open

The subsequent [OC integration record](tmnt-native-audio-integration-2026-10-24.md)
documents functional native audio in an external stage and a still-failed
performance acceptance gate. The preparation results below remain historical;
live game source is still OA.

The live game remains private OA,
`06908a38ac7c658c40f6c064b82e71f84ecc0b5f4617ed8b9a17fba6ad677701`.
Its turtle music still routes to Rygar through `KbAudioFamily`. The work below
prepares a replacement; it does not install or certify that replacement.

Evidence is retained at
`C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-native-audio-ob`.
An additional read-only main-thread profile is at
`C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-hotpaths-ob`.

## Original engine and independent source evidence

The pinned original is
`reference/new-roster-audio/tmnt/Teenage Mutant Ninja Turtles [Gekikame Ninja Den] (1989-05-12)(Konami).nsf`,
SHA256 `f220e8d069e321f392526d41e46f5d0f72966d5a22e56d2b269607c678bd58d9`.
It has16songs, load8000, initC000, play8644 and no NSF bank switching.

`probe-v2` executes every song for12000play calls, plus initialization. It
identifies channel state0100..01AD and14 borrowed zero-page bytesE0..ED.
There are1171observed instructions and368 ordinary pointer words. Closing
both sides of branches covers1289instructions.

The command dispatcher loads the pointer word9014/9015, target918B, then
adds3*command before use. Simple load/store provenance misses that arithmetic
root. The generator explicitly checks the original load instructions90B6
and90BB and relocates the word. Its corrected driver-v3 retains369pointer
words and preserves every original instruction width.

The standalone raw driver uses two8KB banks, A000/BFFF andC000/DFFF. Source
8612..BFFF translates by+2000, preserving all music-data adjacency and page
crossings. The NSF bootstrap and four-byte drum tableC000..C02B move toA000.
The source8000..8611 prefix is unused by the closed sound code and the
observed source reads; its corresponding A02C..A611 area remains available
for buffering helpers. Native init/play/command entries becomeA000/A644/B057.
Channel state relocates to an owned RAM slab; E0..ED retain zero-page addressing.

`driver-v3/golden-v1/proof.json` verifies all192016original/relocated calls:
549602ordered APU events and every call's CPU-cycle count match. The raw
binary SHA256 is
`0f4da02dd003be70632753457d9dd1c67a7656e3bf784603a2c5ce6f71834fbe`.
The maximum original call costs6266cycles, before the future game adapter.
No constant frame-rate or final music performance claim follows from this.

`original-mesen-v1` independently captures all16NSF songs by actual native
init/play entries. The capture stops before the host initializes another
song, including short cues. `original-mesen-proof-v1/proof.json` confirms
83439original call groups and335098ordered APU events against the CPU
reference. Longer songs advance after7208play calls; short-cue boundaries
range325..2358calls. End-of-video-frame recordings spanning those boundaries
must not be treated as a single source song.

These checks cover original/standalone engine requests. They do not cover
the forthcoming game mixer, borrowed-state adapter, mapped DMC playback,
hardware waveform or gameplay integration.

## Fixed drum storage without removing another sound

All6207observed DMC starts use rate15, source addressC040 and length129bytes.
The sample hash is
`225add377a86b0499c2c902cf9ba410c2edcdfec7e0d530f2dc719b58f886dfe`.
The fixed bank is otherwise full, so reserving a new sample requires moving
existing code rather than discarding part of another character's audio.

`space-v3` is a private prerequisite ROM,
`84cbf9a6d0d183ea08d795bfd8542321e7b043bff70c304ec710f3e28e6e0c56`.
It moves the718-byte Samus audio adapter to previously empty PRG bank7D,
atC000. That adapter cannot execute from A000 because it selects native
Metroid banks there. Its bank-restoring return remains fixed atEB3A..EB41.
The original entry staysE874, and every other global label stays put.

The source drum occupies aligned fixed addressE8C0..E940. E941..EB39 retains
505unused bytes for resident dispatch/bank bridges. The first11entry bytes
and the eight-byte return stay executable; the rest is guarded padding/data.
All CHR bytes remain unchanged. Only PRG banks7D/7F change in this prerequisite.

`space-v3/CPU-v2/proof.json` passes16008instruction cases: eight2000-update
Samus music/effect/pause/mute/restart streams plus initialization. A/X/Y/all
flags/SP, application RAM, final physical bank mapping and ordered hardware
audio writes match. The relocation adds14..16CPU cycles per Samus call.

`samus-native-baseline-v1` and `samus-native-space-v1` use real cold Samus
menu entry followed by explicitly arranged audio requests. Both complete4096
audio calls in4410video frames and exercise12nested mapper IRQs. Complete
native state/image/hardware-write CSVs match byte-for-byte, and interrupted
foreground state is restored. These are audio components, not level clears.
Both ordinary14-character mapper outputs retain their existing hashes.

The prerequisite source remains staged outside the live worktree. Earlier
assembler/padding, flat private-label guard and pointer-root failures are
retained; `retained-negatives.json` explains their corrections.

## Remaining implementation

Use the validated prerequisite as the staged base, preserving live OA until
the integrated candidate passes. The two native music banks can use unused
7B/7C; bank7C must map atC000. The Samus cold code in bank7D leaves room for
the turtle adapter. Source page1 state and native/foreground copies ofE0..ED
can occupy the inactive compressed-audio history while character19 is active.
Use a distinct XgAudioCharacter marker so other native/recorded families reset
their state on a character change.

The existing23-byte `VgAudioDispatch` has no room to grow. Its Legacy JMP can
target a new fixed dispatcher in the reclaimed Samus padding: admit exact
character19, otherwise retain the existing ExpandedAudioTick entry and C-bank
mapping. Fixed bridges must select7C around source init/play, then restore7D
before returning to a C-bank adapter. A final fixed return must restore the
ExpandedAudioTick C bank before the resident caller invokes KbAudioFamily.
Do not bank a C-bank routine away underneath its own next instruction.

Buffer native4000..400F writes through the common guest mixer, preserving
the replaced STA's registers and flags. Preserve timer retriggers and unused
register bookkeeping. Handle the00Y initialization stores through4013 safely;
they must not index beyond the16-byte native APU image. Preserve native DMC
off/on edges and remap its virtual source address1 to the fixed sample atE8C0.
The common DMC owner/status logic must retain active TMNT samples and avoid
restarting a completed sample. Pause, silence and character changes must
release ownership correctly. Original native weapon/effect command bindings
still need source-cartridge evidence.

The original129-byte drum starts atDAC0 and ends atDAC44 (peak106), using
LSB-first bounded two-step DMC output. `drum-DAC-steps.json` records this
digital calculation; it is not a hardware waveform check. The current shared
`GuestDmcStatus` clears4011when an effect finishes. A native music drum must
retain its source hold level instead of taking that cleanup path. Preserve
existing Bass/Link/Simon cleanup and verify pause/resume and character-change
ownership explicitly. A sample-byte match alone would miss this difference.

Prepared one-based area songs are2,5,3,10,8,1,11. The event table is
15,13,12,12,13,12,6, following the existing playlist's area/event assignment.
These mappings adapt the soundtrack to SMB areas; they do not reproduce
TMNT's original campaign order.

Required next evidence includes linked source-event/owned-memory checks,
native music/DMC/mixer/pause/SFX/interrupt fixtures, timing measurements,
fresh gameplay discoveries and independent replays, graphics/scroll checks,
other native audio regressions, ordinary mapper preservation and exact source
rebuild. Oversized MMC3 still needs its corresponding bank integration.
The full every-character/every-item gate remains open.

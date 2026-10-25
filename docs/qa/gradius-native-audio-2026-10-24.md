# Gradius native audio — private NV candidate

This is a narrow MMC5 music integration, not completion of the roster or its
every-powerup matrix. The candidate ROM is
`52188a7be0446ee1634cc261ea6f584f631b570c9a292776e8bac3c35a8952b9`.
Its source-only reproduction and final evidence are recorded by the NV
checkpoint manifest. Published ROMs remain unchanged.

## Implementation

Original Vic Viper now runs the pinned Gradius NSF's own music engine and data.
It no longer routes to Pit's recorded music. The three Parodius alternates keep
their existing routing; their dedicated music remains unfinished.

The source is `reference/new-roster-audio/vic/Gradius (1986-04-25)(Konami).nsf`,
SHA-256 `1486e05d3368dda1b830ed454fa4772b7ecd47d6595b42df80348ef95be82119`.
All 5,136 original payload bytes are retained, with instruction/pointer
relocation, private channel state and buffered APU stores. Original branches,
note programs and looping music run as code; there is no finite capture to
truncate, restart or advance to another song.

The area table uses one-based NSF songs `3,6,4,9,5,1,10`; the event table uses
`13,13,14,14,13,14,10`, preserving the prepared playlist's numerical mapping.
These are SMB area/event assignments, not a claim that SMB rooms reproduce
Gradius's original campaign music order. Weapon/world effects still use the
existing shared mixer; this change does not add native Gradius weapon SFX.

Only the compressed-audio history's first 80 bytes are used for channel state
while this character is active. Six original indirect-pointer bytes and the
pause input are borrowed and restored around each call. No additional RAM or
CHR is allocated. Code/data use previously unused PRG bank `$7A`; a 23-byte
dispatch occupies the existing audio bank's 24-byte tail. The resident caller
keeps its original size and all other resident addresses.

## Source and hardware evidence

- Original NSF execution covers all 32 songs, 227,000 play calls, and 171
  observed pointer words. Closing both sides of branches covers 494 source
  instructions. The relocated standalone driver produces identical ordered
  source APU writes.
- Independent Mesen captures indexed by actual native driver calls confirm
  44,706 original initialization/play call groups across the nine assigned
  songs. The capture stops before the NSF host initializes another song.
- Actual linked code and the actual linked APU buffering helpers match
  127,543 ordered original APU events over all 227,000 calls. State writes stay
  within the owned history, six pointer bytes and APU images/dirty flags.
- A real cold menu entry followed by an explicitly stationary audio arena
  exercises 12 area/event cases. It passes 133,120 source-register comparisons,
  115,967 hardware-register comparisons and 8,320 interrupted-state checks.
  Shared effects, music restoration, pause and resume are included. The arena
  is not a natural campaign or collection test.
- Optimizing pointer transfers and avoiding redundant channel-enable work
  reduces adapter work from 8,589,901 to 6,409,543 cycles in the same arena,
  about 25.4%. The final peak is 3,005 cycles. This is not a claim that all
  gameplay lag has been eliminated.

Final controller discovery/replay and visual results are bound in
`build/verification/roster-audio-nv/proof.json`. Full native replay PNGs,
unsuccessful attempts, original captures and intermediate candidates remain at
`C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-roster-audio-nv`.

The final Easy/Hard clears take 4,774/4,879 frames, with zero deaths and
25 frames of controllable underground 1-2. Entire discovery/replay inputs and
traces match within each mode. Native CHR commitment checks pass. Sampled image
review nevertheless finds an open Vic HUD problem: the power bar is illegible
and sometimes shows inappropriate tiles. Similar illegibility is visible in
the retained NU baseline. A passing CHR-ownership check does not certify its
glyph design or the background bank used for each displayed HUD scanline.
This checkpoint is not a clean graphical sign-off.

## Capture flaw found during this work

The older end-of-video-frame captures are not a reliable source-song boundary.
For the nine Gradius inputs, Mesen's NSF host demonstrably reinitializes a
different song: short cues at 240/465/738 native calls, and continuing music
at 7,209 calls. The old 1,800/15,000-frame captures include that later playback.
Video-frame quantization also splits some native calls across frame boundaries,
preventing a valid exact-repeat search from finding their musical loops.

The initial read-only compression studies preserve those inputs exactly, but
their round-trip checks do not certify musical fidelity. Their nominal
26-bank capacity was also optimistic: the current linker has other owners in
part of that range. None of those experimental streams was installed.

The source-capture boundary for other recorded NSF families, including the
installed Kirby/Meta streams, must be re-audited. Gradius's native-code path
avoids both host advancement and capture-length limits. This does not certify
the other families, DPCM support or full sound-effect fidelity.

## Test limitations and retained negatives

Earlier linked v1/v2 builds failed to link and were never accepted. The first
v3 audio fixture incorrectly compared unused APU registers, and a later one
allowed the game timer to inject its own hurry cue. Both failures are retained;
the corrected stationary fixture freezes its displayed timer and compares all
16 source-image registers plus the 14 meaningful hardware registers.

An old roster fixture could interpret uninitialized power-on RAM as an already
open menu before frame 60. Its original Lance run timed out; the unchanged
fixture passes with zero-filled power-on RAM. The fixture now waits until its
real title-input window before admitting a menu transition. No game menu code
was changed for that harness issue.

No claim is made of all-item collection, exact Parodius audio, source weapon
effects, complete lag repair, all castle hazards or the full 37-identity MMC3
port. Those remain part of the active final verification gate.

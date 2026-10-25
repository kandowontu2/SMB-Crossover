# Sophia freeze and the inventory stack

Private MMC5 candidate OG is SHA-256
`2e916d5da5448bec576a930fddf3d1469472b976756c95da6fadddb2ca98729a`.
Its parent is the accepted OF checkpoint
`f8571591a8d829210ec9dd352ac36bbfcf44f8700aabbaa88deca6e2be9e0008`.
The complete roster/every-item goal remains open.

The retained Sophia Easy controller stream reproduces a real hardlock on OF
at video frame 2997, world X1971. An audio-NMI JSR writes into $017A, the last
byte of the live bank-switch trampoline. Later pushes also overwrite $0178
and $0176/$0177. Its RTS and bank-restore instruction become invalid, execution
falls into $017B and jams, and game/NMI/IRQ counters stop. The HUD then wraps
to the bottom of the display. The passive reproduction records the first
incorrect write, the instruction ring, RAM and PPU writes; it changes no game
state. Minimum observed SP is $75. Reproduction v7 freezes its observer source
and pins the original controller stream and ROM.

The read-only InventoryLegacyClassic query previously entered Roll, Mac, CV3
and Zelda II gates in four nested bank calls. OG replaces only that entry's
target with a direct predicate containing exactly the same rules. It preserves
the unusual returned A value for Roll and the normal Bass case, preserves X
for alternate-specific branches, and preserves every returned register and
processor flag. No RAM, CHR, movement rule or existing linked address changes.
The appended predicate shares the existing bank66 tail; only PRG59/66 change.

Evidence is retained under
`C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-sophia-lock-og`:

- 20,180 actual linked old/new CPU comparisons cover all256 IDs, modes0/1/2/255,
  all256 selector values and combinations for legal profiles, with flags and
  register seeds. Returned A/X/Y/fullP/SP, final mappings and application state
  match. The maximum query stack falls from15 to4bytes; each query saves15–354
  CPU cycles depending on the path.
- 4,260 actual scroll-IRQ injections cover120 paths and every instruction
  boundary through the entry, banked predicate and return. Registers, status,
  live caller stack and ordered IRQ stores match the interrupted old path.
- Two fresh Sophia discoveries and independent exact replays clear1-1 with
  zero deaths into movable1-2: Easy5410 and Hard5368 video frames. A second
  independent guarded replay in each mode observes every immutable trampoline
  write and execution outside ROM/declared copied code throughout the run.
  No corruption occurs. Minimum SP is $88/$92, with the lowest actual stack
  write at $0189/$0193, safely above the trampoline's end at $017A.
- All10,378 replay PNGs are retained. Body CHR has no mismatches; all visible
  scroll publications use scanline31. Adjacent committed movement is at most
 2pixels and camera movement at most3pixels in both modes.
- Root viewed both24-frame overview sheets and Easy frames1900–1902. Those
  samples show no new displaced/green background tiles or tank displacement.
  This is sampled human inspection, not an exhaustive human pixel review.
- All37 cold character entries and seven existing source-audio regressions
  pass on OG, including4096 exact original Samus audio calls with nested IRQs.
  The two600-update turtle performance components match OF in gameplay bytes,
  CPU measurements and lag. The existing heavy-shot27/25 lag NMIs remain.

The first raw-video movement review correctly stopped on a71pixel RAM change
at Easy frame1901. Source/native observation establishes that MegaManWeapons
temporarily borrows the player coordinate bytes for PlayerHeadCollision while
a projectile hits a brick. That raw coordinate is exactly the contacted cell
(1248,144); MmSavedPlayer contains the actual tank origin(1179,176), within
2pixels of the last drawn body. Completed GameLoop and body drawing restore
the borrow. Only that positively observed borrowed sample is projected for
the strict movement check; the original trace and failed report are retained.
The original world<=8/camera<=4 bounds, adjacent-video-frame admission, replay,
death, PNG, CHR and scanline checks remain unchanged. A separate first attempt
incorrectly compared engine8 states63frames apart across an injury state;
that failed report is also retained and the final check uses the original
adjacent-frame admission.

Other retained failed diagnostics include the initial observer's unsafe nested
debug read, an endpoint check that incorrectly required an IRQ on almost every
video frame including transitions, and the old frame-timed controller stream
on OG. That old stream dies earlier because the optimized code changes update
timing; it is not relabeled a passing replay. New OG discoveries are replayed
with their own exact saved inputs. No game behavior assertion was weakened.

The route measurements still show substantial lag (2270/2235 lag NMIs). This
repair removes a proven stack overflow, and does not claim that lag, full
audio/source fidelity, every powerup, other route failures or the oversized
MMC3 port are finished. Published ROMs remain unchanged. Source-only rebuilds,
ordinary mapper hashes and the30GB cap are required before adoption.

# Prince ordinary underground entrance

The public62 and cache209 builds both hand Prince to his original actor at
native Y48. The remaining scripted drop reaches the donor's seven-step fatal
fall threshold. Root's actual Mesen trace on public62 confirms raw3 A03B
increments C6C6 and raw3 A342 drains HP5 to0 on landing; this is a preexisting
transport defect, not a cache209 regression. Normal controllable donor falls
retain those exact instructions and thresholds.

The private entry build is
`309bbdae23b2dbe76951d3320c5afcb895e25b0fd081a558e93241b12f96389c`.
Its strict parent is frozen cache209
`209abc2fd6144d59720e54352ed6f9f7384e2fa9ede0fbb1fb37f9e02d385008`.
`prince_entrance_handoff_1113.proposal(parent)` returns image/info;
`reverse(image)` reconstructs that exact parent. No ROM file is produced.
All three Prince cold streams and cookie
`a726026f8a1229edf5a0683733ba6baf` remain byte exact. The frozen cache repair
and earned-sword Lua848c67e3 remain unchanged; the latter requires variant3.

The only changes are two native PLAYER bank1 envelopes,52 bytes containing41
actual changed bytes. At A04F..A059, LSR/CMP3 recognizes precisely header6/7
and preserves the original pipe branch. Every other header jumps to the new
25-byte gate AB69..AB81. Existing AltEntranceControl2 handling precedes the
hook, so alternate pipe and vine entry bypass it. The gate sends foreign
characters and AreaType0 water directly to the original PlayerRdy A0AD.
Ordinary nonwater Prince runs unchanged AutoControlPlayer(0), remains in
engine7 while unsupported, and reaches PlayerRdy only after that call reports
native floor state0. There is no pending bit, new RAM, source actor write,
health/counter edit, new helper, jump change, or fall immunity.

Root's conditional allocation is
`allocations/prince-entrance-player-1113.json`. The native41-byte
CrossoverJumpProfile at AB5E..AB86 becomes its equivalent11-byte dispatcher
for Luigi and every other reachable owner, plus the25-byte entry gate and5
EA padding bytes. The legacy Mega Man1 branch has no legitimate caller:

- The sole compiled native profile JSR is bank1 A8A2, after fresh-A jump
  admission in PlayerPhysicsSub. Spring motion rejects before that admission;
  state3 follows climbing and returns before it.
- Ordinary engine8 Mega Man uses SpecialMovement and MegaManMovement. The
  native fallback is restricted to spring/climb conditions above. Engine1
  climbing also cannot reach fresh-A admission.
- Scripted engines2/3/4/5/7 supply only0/1/4/8, with no A bit. Engines0/6
  perform setup/life handling. Guest size/flower engines9/12 dispatch guest
  power updates and return; Mega Man death11 uses its own death update.
- Modern Mega Man injury keeps engine8, clears action controls and uses
  MegaManHurtMovement; legacy injury freezes in engine9. The generic native
  engine10 injury timeline is not Mega Man's injury owner. Cheats retain
  engine8 source movement admission.

The four numeric AB5E words in native PRG are fully classified. One is the
JSR above. Native23 A8E4 is the sound_table_00 row15 pointer to Contra's own
sound_0f command data, read by its SOUND_CMD pointer. Native37 AAC3/AACB are
CMP/LDA DiskReach,Y table reads in its own bank. Neither data reference calls
native1 or changes. The original profile assembles exactly from its retained
source; source and compiled bindings are recorded by the new checker. Native1
has no literal word pointing into the profile's interior, no native81 constant
farcall targets it, and all224 actual Rogue raw-page rows exclude native1.

Completed source checks include65,280 non-Mega-Man character/all-flag AXYP/SP
cases,4,096 complete Luigi native jump cases, and all256 header values.
Actual compiled branch fixtures prove Mega Man's spring/climb/source dispatch,
native fresh-A admission and positive control, modern/legacy injury ownership,
parsed-control masking, and guest size/flower/death call targets. These are
declared instruction fixtures, not naturally earned gameplay.

The unseeded309 cold/menu/Main/NMI full-stage run exited0 under the unchanged
600-second bounded runner. The frozen stage3dbbf79a controller completes
authored1-1 flag/castle and the underground continuation. It genuinely reaches
engine7 X40/Y48 at source update7873 with HP5/lives2/fall0. The new handoff
occurs at7906 only at Y176/state0/speed0/fraction0; the original constructor
resynchronizes from that floor at7907. Neutral continuation ends X40/Y176,
HP5/lives2/fall0/sourcephase120. No actor/position/input-outcome state is
seeded. Its verbose stdout exceeded the tool view limit, so this note does
not invent a missing receipt digest. Native cadence, raster and physical
qualification remain root's separate work.

The completed directed matrix receipt is
`ff63b71c4bd61ea1e6497c4d37d1a792978a600f0266e5116ab9aca193c030e3`.
Both actual common cold loads consume31,336 PPU reads and8,029,104 CPU cycles,
minimum SP180, and leave identical source RAM. Every one of255 foreign IDs
has identical entrance returns/private RAM. Water, headers6/7, alternate pipe
and vine fixtures remain exact, including native RAM for those exclusions.
The ordinary flat-ground fixtures run the real native header constructor;
both initially false-grounded state0 and falling state2 wait for actual
support, then hand off at Y176/state0/speed0/fraction0 after35/34 calls.
Source HP5, fall0 and phase0 remain untouched. These directed controls and
terrain are explicitly fixtures, separate from the unseeded whole route.

The falling gate passes15 actual IRQ and15 real lag-NMI cuts. A separate
actual-cold supported-header2 fixture covers the gate's Ready branch and the
unchanged PlayerRdy:24 IRQ plus24 lag-NMI cuts, minimum SP170. Its receipt is
`4caae49e305516cd78af185a084c1668ba1bd07584225ab4ce1744944f9d53e2`.
All cuts retain complete source RAM, native scratch, SMC, mapper state,
AXYP/SP and resulting foreground state. No generic mapper assertion was
relaxed and no pending-STA exception was needed.

Two unsuccessful harness attempts are retained in scope. The first exceeded
its300-second bound while deep-copying cold write/PPU histories per case;
the existing slim_fork and cleared logs fixed that without changing its
bound or candidate. The next completed cold/foreign/exclusion comparisons
but its artificial ordinary drop lacked native scene setup/terrain. The
corrected directed fixture explicitly runs Entrance_GameTimerSetupCore and
declares flat native terrain. Neither unsuccessful attempt is called a game
regression or a completed interrupt check.

Repeat the source gates with zero output files:

```
python -B tools/audit/run_bounded_build_v1.py --output build/prince-pickup-reach-1112 --max-files 1 --timeout 300 -- python -B tools/audit/check_prince_entrance_handoff_1113.py --matrix --interrupts
python -B tools/audit/run_bounded_build_v1.py --output build/prince-pickup-reach-1112 --max-files 1 --timeout 180 -- python -B tools/audit/check_prince_entrance_handoff_1113.py --landing-isr-only
python -B tools/audit/run_bounded_build_v1.py --output build/prince-pickup-reach-1112 --max-files 1 --timeout 600 -- python -B tools/audit/check_prince_underground_entry_1113.py --entry --compact
```

This private source checkpoint is not a nightly delivery. Root owns the
separate current526 composition/API and all later Mesen runs. No helper
platform, stage data, shared game source or Downloads file changed here.

Root has separately physically qualified the entry case on combined current
candidate `7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc`:
16,465 physical frames/7,037 source commits through authored1-1 into quiet
1-2 X40/Y176/HP5/lives2, with the exact frozen stage3dbbf79a Lua. The first
engine8 entry is already grounded at frame16,345;120 further neutral frames
retain health. Root receipt:
`98e6cd908d9ecf3713cb2bd364440e58854abf3febd85912f07a29529ff06b09`.
That separate combined build includes the current Karnov update and cache209;
it is not a physical test of bare309, an earned-sword whole-stage route, or
a delivery claim. Root's combat and foreign physical regressions remain
separate gates.

## Render diagnosis after the functional gate

The read-only actual-cold directed probe
`check_prince_entry_render_1113.py` confirms zero player-body emission while
source pose0/epoch0 is retained during the native drop. It does not seed
those source fields, health or actor state. At directed native Y96 and160,
the actual graphics handler clears ObjectMetasprite; the current private
GraphicsCheck points SmPosePtr at the zero header SmPose6B05. PpHostDraw
returns C0 with unchanged OAM, and the native zero-header emitter also emits
nothing. The current pointer differs from the historical06E1 recipe; the
probe authenticates the actual runtime instead. Receipt:
`23d0cecc90a3f5e77198fdbe197c681c395122d672bdfe8c778fd5594af741a4`.

Root's separate actual7ef shots at engine7 Y99/Y163 confirm the invisible
drop, receipt
`252f9d60df0be361de719f91dff44bbf724798f6679fa9c022f3681f597991dd`.
A settled phase4/pose15 snapshot emits five shadow-OAM cells but its sampled
body region is black. Root then completed a fourth bounded physical shot at
phase30/frame16,404: Prince's brown/white body is visible at nativeY176.
All four shots have correct hardware sprite palette3F11..13 values27/16/20.
Six actual1-2 color calls show the queue empty before backdrop, offset4 after
backdrop, and successful body-palette publication at offset10. The palette
drop hypothesis is refuted; no palette retry is warranted. Four-shot receipt:
`4e11add0aaedc5bc190d76f7aaf2abc05178991a068750c68f7cb57c78d96230`.
The early shadow-OAM/PNG difference does not establish a persistent black-body
defect or a particular hardware-DMA cause. Root separately reports all five
functional physical cases green. These observations do not claim perfect
raster output or a Downloads installation by this helper.

There is an exact original fall-art witness for a later render-only fix:
root's public62 cause trace sees action7/pose106 while the native drop passes
Y96 and160. Current pose106 is a five-part original8x16 packet with source
projection delta5. A faithful native projection would use horizontal anchor
native world X minus screen-left plus8, and vertical anchor native Y+27.
This does not justify priming C617, advancing source physics, or modifying
health/fall counters. No render repair has been implemented in this
checkpoint, and the frozen309/7ef image bytes remain unchanged.

The read-only funding check found no immediate qualified80–90-byte renderer
worker interval. Each remaining nine-byte retired material span A487/A51E
needs a three-byte ordinary-flow bypass, leaving two six-byte helpers.
The apparent historical PpReadProjection compaction is already installed;
its recovered BD82..BDA1 tail contains a live action42/support helper and
cannot be borrowed. The extended invisible engine7 drop is noninteractive;
the user regains source control after actual support with full entrance
health. Its appearance remains recorded for the later per-character
cosmetic review. This checkpoint adds no unqualified code allocation.

## Independent current menu comparison

The exact root-owned7ef candidate was independently read from
`build/metal-flower-native-1112/candidate.nes` and reversed through
`compose_prince_entrance_current_1113.reverse` to exact parent526. Actual
menu input, Select cycles, native portrait rendering and NMI ran through
`check_menu_facing_1112.audit(include_images=True)` on both images. All101
identity/facing/portrait/silhouette rows match, together with all101 portrait
and101 silhouette RGBA images:350,404 pixel bytes compared exactly.

The sorted-key JSON row digest is the established baseline
`f58ec905102307ca87d9c302248fa7da9c44cd5550df154323e67024da245db7`
using Python's default JSON separators. The source auditor hashes to
`4e886d4259f4ba308c91d9779e052c3756a878bdfdc074551ed82494a576c671`.
Independent comparison receipt:
`c3e2d01241d330c1f7ed438be958091d7e8bb72bf4ec8ba3ec33015658dd0f3e`.
The existing owned bounded root,600-second limit and one-file cap were used;
the completed run wrote zero files and launched no emulator. This is exact
menu/pixel parity in the CPU peripheral model, not a new physical raster or
art-orientation review.

# v34 source injury, wall contact and native collision

Component checkpoint: `build/checkpoints/roster-audit-v34`. Final roster
routes/recordings and source/performance follow-ups remain in progress; this
is not a completion or zero-lag claim.

- MMC3 SHA256 `5f62764c0e531fecd5e1f6e146fc5d50f6ad9cbc237365a44838c50896b36707`.
- MMC5 SHA256 `45e4717f32c7461c85ca3bea4885a2e2e730c9dbd5bec5405333e8b8fe33d414`.
- Rebuildable source archive `source-v34-rebuildable.zip`, SHA256
  `f91b7607d28b6a63183d5ede21b7706dfc54eae4dccd89c9d2fd1c2005cd3198`.
  Both ROMs rebuild byte-identically from a fresh extraction with the separately
  supplied compiler/Python/Pillow. Earlier archives and the smoke test that
  exposed missing cached provenance/build-fixture inputs are retained with
  their qualifications.

## Actual wall and scrolling defects

Guest side collisions clamp fractional motion against terrain. That helper
previously skipped the native sixteen-tick scroll hold. Holding Right against
a pipe could therefore keep moving the camera while the player's world
position remained fixed. Actual successful clamps now install the hold;
moving-away returns preserve their previous position, velocity and timer.

The 78 authored pipe scenes per mapper exercise all thirteen roster IDs,
both directions, walking/jumping and shallow-overlap moving-away controls.
On provisional-b, 3,677 actual clamps per mapper set sixteen, all 83
moving-away-only returns preserve their state, and 22 blocked guest walking
scenes pan at most three pixels. Mario/Luigi bypass the guest clamp. The raw
packets and source hashes are under
`build/verification/mm-bass-camera-probe/accepted-v34-*-provisional-b.json`.
These are explicit unit arenas, not ordinary route clears.

An ordinary Luigi underwater replay revealed a separate dispatch error:
Luigi entered that whole-cell guest clamp despite using Mario's physics.
At frames15258/15259 the actual stores displaced him13/16 pixels inside the
updates. A separately labeled synthetic same-state Mario dispatch control
instead displaced one pixel. Luigi now takes the native path. The independent
648-case matrix per mapper covers directions, forms, page seams, stationary/
toward/away motion and active/scripted engines, including native flags and
unchanged guest fractional sentinels. Originals, controls and positives are
bound in `luigi-v33-native-wall-negative.json` and
`luigi-v34b-native-wall-positive.json` under `build/verification`.

## Source injury and geometry

Link, Simon and Ryu now use source injury while the world continues running,
with distinct motion/end conditions, input restoration and protection.
Real clamped injury contacts publish their contacted-side bit. The source
audit and independent motion, body-pixel, DMC and input fixtures are retained
separately; NES temporal opacity/palette adaptations are not exact Flash alpha.

The source Link body is15 NES pixels tall. Its previous body/head tables used
14 pixels/top18. v34 corrects both top offsets to17, with sides and feet
unchanged. This is the only final-candidate difference from provisional-b:
exactly two ROM bytes per mapper. Independent source-sheet transforms and
archived fixture migrations live in
`build/verification/guest-injury-v34-migration`.

Link and Simon's source injury cues are pure DMC samples. The old four-voice
effect importer omitted them. Their161/193 source bytes, rate and initial
DAC are now included, alongside Ryu's injury/jump effects. Shared DMC ownership
survives Bass's noncharacter cleanup and stops when hardware playback ends.
These cues share the NES DMC voice with Bass's retained Water Shield sample.

A later independent raw-matrix audit found remaining source geometry gaps.
Normal Simon/Ryu still share approximate31/13px profiles. Their source shapes
vary with the active pose/state: Simon30/25/~15.75px and Ryu27/25/~15.75px.
Simon also changes to his stand frame/30px shape after a recoil ceiling contact;
v34 retains hurt art/25px there. The original focused fixture assumed fixed25
throughout and does not prove that source transition. These known limitations
are retained in `build/verification/lsr-normal-hrect-readonly-v34.json` for a
separate correction; they are not claimed as source-complete positives.

## Resident space and native behavior

OBJECT-only native enemy terrain/bounding-box code moves into its existing
OBJECT bank. Three always-visible helpers move to the resident low bank.
This frees fixed space for DMC without adding mapper calls to native enemy
terrain processing. Shared stun/defeat routines remain resident.

The original baseline remains byte-identical, SHA256
`0511c6844d0e9fa61f4b4fbc34e6f9c67d8247d3ca964ebbb0c9c2718cdc5146`.
The actual-ROM unit interpreter checks8,568 native helper arenas per mapper:
registers/all flags/SP/native RAM and common named SRAM, including real
farcall/drop-hook execution. It excludes discarded stack/SMC contents and
uses coherent live-stack positions. A fabricated direct landing entry that
bypassed the real defeated-object guard is excluded and retained as a fixture
negative. Entry branch cycles can differ by a few cycles; no exact native
cycle-timing claim is made.

## Crowd measurements and remaining work

The frozen full run passes749 of753 mapper/test slots. Two old Link fixtures
fail on both mappers: one expects the former engine10 injury, and the other
fails to clear the newly persistent source recoil between independent cases.
Read-only observers confirm both causes. After that run closes, only these
two fixtures migrate; their four actual test invocations pass without changing
the ROMs or weakening the104-case contact assertions/watchdog. The consolidated
coverage is753 distinct slots, **not one green full run**. Original failed
summary/logs and before/after hashes remain intact in
`build/verification/roster-audit-v34-consolidated.json`.

The unchanged aligned probe compares v33 and provisional-b across12 runs,
14,400 completed updates and204 gameplay fields, with zero differences.
`build/profiling/plain-walking-v33-v34b-aligned-comparison.json` preserves
every scene and physical/DMA/draw metric. This includes both outline settings,
standing/walking and0/1/2/4/6 real Goombas. It is not route evidence.

v34's added source behavior and relocation are not a CPU optimization. Four
Goombas with outlines off still yield only30 draws per60 updates for Samus
and Mega Man. Some scenes draw more often; others draw less often. Several
dense six-enemy scenes cost another1–5 physical frames per60 updates. The
comparison retains these regressions. v33's independently accepted savings
are documented in `crowd-performance-v33.md`; further performance work remains.

Default-off outlines and the bright gold menu row remain verified. The NES
eight-sprite scanline limit and skipped redraws remain separate sources of
flicker. Final ordinary-controller routes and recordings must use the exact
final ROM hashes; historical32/33 clears are not substituted for them.

Mario's final34 ordinary replay/recording clears all six stages without deaths.
All16,990 captured frames decode; metadata permits the measured one-frame
capture offset. The read-only review reports zero split/CHR/motion/background
pixel/audio-confirmation flags. Contact-sheet inspection is separate from
automated every-frame checks; there is no manual every-frame listening claim.
The MP4 is about13MB with native audio. Its verified raw AVI was removed after
encoding. Evidence/video:
`build/roster-through-2-2/root-v34-mario-capture-a-0-v0-mmc3`.

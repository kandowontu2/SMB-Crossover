# MM/Bass native audio investigation, 2026-10-18

This is a read-only proposal measured against checkpoint
`roster-audit-v41-provisional-e`, subsequently accepted as `roster-audit-v41`
with the same MMC5 SHA
`c83a24fa60df0660e9a7ea171fcefd008d47d2a74363c8098f3579e6540fbedd`.
No runtime, generator, tests, shared tools, ROM, or debug tree was changed.
The CPU-only probe and its small aggregate output are in
`build/verification/mm-bass-audio-v41-readonly/`.

## Recommended narrow changes

1. **Inline the already-protected MM2 buffer store.**
   `src/megaman_audio.s:416`, `MmFilteredWrite`, saves P/A/Y before filtering.
   Its admitted path restores A/Y, calls `GuestNativeStoreSTA00X` or
   `GuestNativeStoreSTA01X`, then executes its own PLP/RTS. The generated
   helper repeats PHP/PLP around an identical STA/INC pair.

   Replace that admitted-path JSR with the corresponding
   `STA GuestNativeApu+$00/$01,X` and
   `INC GuestNativeDirty+$00/$01,X`, retaining the outer PLP/RTS.
   A/X/Y and every returned status flag remain unchanged. The dirty-byte
   increment, its wrap behavior, and the shadow-register write are identical.
   Rejected channels remain unchanged. Temporary stack use decreases; only
   discarded stack contents differ.

   Saving: **19 cycles per admitted write**, removing JSR(6), RTS(6),
   PHP(3), and PLP(4). Growth: **6 FIXED bytes total**, three per expansion.
   Compiled entry addresses are `$E795` and `$E7B2`; their nested helper
   targets are `$EC2C` and `$EC4B`.

2. **Tail-call the unchanged MM3 writer.**
   `_init_channel` and `_handle_channel` in `audio/megaman3/imported.s`
   become `JSR GuestNativeStoreSTA00Y; RTS` after generation. Replace those
   two tails with `JMP sameHelper; NOP`. No helper implementation or flag
   contract changes. Both routines have balanced temporary pushes, and the
   writer never inspects the caller's return address or SP. Its final RTS
   returns directly to the original caller. All A/X/Y/P/final SP and live
   memory remain identical; only discarded stack bytes differ.

   Saving: **9 cycles per tail**, with **zero size or address change**.
   On 41e, MM3 bank 11 spans `$A0BF..$A0C2` and `$A0D1..$A0D4` contain
   `20 35 EC 60`; the same-width proposal is `4C 35 EC EA`.
   Implement from the two documented symbolic source tails, with an exact
   count/assertion, rather than scanning arbitrary ROM opcode patterns.

3. **Unroll Bass's exact descending clear.**
   `src/bass_source_sfx.s:68`, Decode/ClearDirty, currently clears all sixteen
   `BassAudioSavedDirty` bytes with LDA #0, LDX #15, STA abs,X, DEX/BPL.
   Keep LDA #0, emit sixteen absolute STA instructions in the identical
   offset order 15 through 0, then LDX #$FF. Final A=0, X=$FF, Y unchanged,
   N=1/Z=0, and all other flags are identical to the original final DEX.
   The whole private buffer still clears on every original Decode path.
   Pause/title and the explicit F1 stop path retain their original bypasses.

   Original cost: `2+2+16*5+16*2+15*3+2 = 163` cycles.
   Proposed cost: `2+16*4+2 = 68` cycles.
   Saving: **95 cycles per Decode clear**, growth **42 XG_BASS_GFX bytes**.
   The linked loop begins `$CC85`, bytes `9D 16 7C CA 10 FA`.

Each change can be MMC5-only to preserve the currently retained MMC3 bytes.
None requires new RAM or zero page. Root owns integration and builds.

## Baseline counts

`profile_writers.py` executes the existing compiled full AudioUpdate in a
seeded 2A03 CPU model: eight coherent 128-update streams for each character,
with area/event changes, native effects, specials, charge, landing and pause.
It counts the actual helper/loop entries and maps MMC5 PRG and multiplier
registers. It neither patches code nor copies ROM/debug trees.

| Character | Updates | Counted predicted saving |
| --- | ---: | ---: |
| Mega Man | 1024 | MM2 inline 67.08 cycles/update; MM3 tails 20.14; combined 87.21 |
| Bass | 1024 | 991 Decode clears; 91.94 cycles/update including bypasses |

The MM combined estimate ranges from 11.39 to 133.38 cycles/update across
these short streams. Bass's active Decode saving is exactly 95 cycles;
the average is lower because of pauses and one F1 stop. Bass does not call
the MM generated APU writers in these streams, so their flag optimization
does not help his ordinary update directly.

These are counted instruction estimates, **not compiled after-build deltas
or measured NMI/DMA improvements**. The model omits PPU, IRQ/NMI scheduling,
sampled waveform generation, and DMC playback. Existing 34b ordinary-input
traversal proofs remain qualified by their older ROM hash.

## Independent acceptance experiment

After root builds an audio-only candidate and same-revision control:

- Assert unchanged RAM ABI and execute the actual before/after binaries.
  Use `tools/profiling/verify_mm_audio_v40.py --outer` for its eight
  2000-update coherent MM streams. Require identical A/X/Y/all P/SP, RAM
  including live farcall SMC, and ordered APU writes. Only discarded upper
  stack bytes may differ under the established oracle.
- Extend the owned probe into a dual-binary Bass fixture using the same
  strict comparison. Include all source requests, explicit F1 stop,
  pause/title, source replacement, previous-mask restoration, and DMC
  running/completed status controls. Check the private clear for arbitrary
  initial bytes and status flags. Do not waive RAM or flag differences.
- Count admitted MM2 stores, both MM3 tails, and original Decode clears in
  each before-call. Require the exact measured cycle delta to equal
  `-(19*MM2 + 9*MM3 + 95*BassClears)`, rather than accepting a loose speedup.
- Re-run existing actual-mapper hardware APU goldens and source SFX/DMC
  checks. Then profile both characters with full Water Shield, measuring
  NMI CPU, max CPU and actual completed DMA/physical frames. Retain current
  41e bounds and exact state/pixel/corner assertions; do not weaken them.
- If MMC5-only, retain the original emitted paths under the mapper guard,
  and independently assert complete MMC3 ROM byte identity between that
  same-revision control and audio candidate. Unrelated v42 fixes must not
  be folded into this comparison against v41.

Static integration guards: exactly two symbolic MM3 tails, each four bytes
before and after; MM2 growth exactly six FIXED bytes; Bass growth exactly
42 XG_BASS_GFX bytes; no RAM/zero-page address changes; no MMC3 audio-byte
changes. MM3 NOP padding preserves later code addresses. The MM2 and Bass
growth can move subsequent labels and branch/page-cross timing; investigate
any resulting cycle discrepancy rather than widening an exact delta check.
The complete bundle uses six resident bytes, below the seven-byte ceiling.

The existing independent MM unit command is below. These prospective paths
are placeholders for root-built binaries, not existing outputs or commands
already run:

```powershell
python tools/profiling/verify_mm_audio_v40.py build/checkpoints/roster-audit-v42-audio-control/smb-crossover-mmc5.nes build/checkpoints/roster-audit-v42-audio-candidate/smb-crossover-mmc5.nes --outer --output build/verification/mm-bass-audio-v42-mm-outer.json
```

This executes 16,008 compiled calls, covering eight 2,000-update streams
plus initialization. The proposed strict dual-binary Bass comparison still
needs implementation; the MM command does not validate Bass. Existing
actual-emulator checks can then run against the root-built candidate:

```powershell
python tools/run_mesen.py tests/bass-source-sfx.lua build/checkpoints/roster-audit-v42-audio-candidate/smb-crossover-mmc5.nes --timeout 120
python tools/run_mesen.py tests/bass-native-sfx.lua build/checkpoints/roster-audit-v42-audio-candidate/smb-crossover-mmc5.nes --timeout 120
python tools/run_mesen.py tests/bass-water-audio.lua build/checkpoints/roster-audit-v42-audio-candidate/smb-crossover-mmc5.nes --timeout 120
python tools/run_mesen.py tests/megaman-water-performance.lua build/checkpoints/roster-audit-v42-audio-candidate/smb-crossover-mmc5.nes --timeout 120
python tools/run_mesen.py tests/bass-water-performance.lua build/checkpoints/roster-audit-v42-audio-candidate/smb-crossover-mmc5.nes --timeout 120
```

The purpose is a small exact reduction in audio work. No source-perfect,
sample-identical, final-playthrough, or zero-lag claim follows from this
proposal alone.

# Sonic shared native audio fallback

This source-only component admits raw43 to the existing SMB music/SFX driver.
It changes only physical PRG63 B53B..<B57C, the current relocated legacy-audio
fallback. No ROM, build output, emulator capture, or installed file was written.
Original Sonic audio remains unfinished; this is host fallback behavior.

The original Sonic effects fixture reaches the native pit-death threshold and
queues death music1, but its current raw43 audio route leaves queue1/buffer0
after 400 full native NMIs. The shared fallback adds CMP43/BEQ before the
existing Sunny23 comparison. Existing title, Mario0, Luigi8, Sunny23, raw28,
and other routes retain their paths and flags. Actual original Sonic pit/music
completion is tested separately by the Sonic effects owner.

## Exact funding

The original `src/music_drivers/audio.s` five-byte padding is already live:
F0D3..<F0D8 contains the frozen guest-audio quiet-tail bytes `8d1551d091`.
This component preserves that code and the entire fixed audio bank.

The current relocated fallback starts with `PLP; PLA; PHP; PHA`, then performs
the existing Rogue retirement cleanup, then `PLA; PLP`. The entry owns savedP
above the saved software A bank. Keeping that order across the cleanup removes
the initial four instructions; `PLP; PLA` then restores the two values. Cleanup
reads neither incoming A nor flags. Its following LDA OperMode redefines N/Z
before every old branch, while saved C/V/I remain intact. This funds exactly
the added four-byte raw43 comparison without growing the 65-byte span.

The exact current 23-byte IsActive worker at B431 and 25-byte RdsNmiGate prefix
at B448 are asserted before assembly. Both paths to B53B retain the saved I
value: neither prefix nor IsActive changes I. The two original absolute incoming
jumps target unchanged B53B. The selected-audio decision is local to this source
function. Following CommitContext starts at unchanged B57C; both fixed audio
destinations F06F and F0D8 remain unchanged.

## Source CPU evidence

6,144 directed valid fallback-frame pairs cover every raw byte0..255, three
OperMode values, four saved-flag values including both I states, and both prior
DPCM-owner states. Every non43 result keeps its exact destination, A/X/Y/P/SP,
live stack, native/private state, mapping, and ordered non-stack writes. For
raw43 gameplay, the sole destination change is guest F06F to vanilla F0D8.
Retired stack bytes are outside the caller's live stack.

Eight actual full regular NMIs from a genuine menu/cold seed reach all 28 new
instruction positions. Each reached cut passes a real nested scanline IRQ and
the remainder of its full NMI. AXYP/SP, live stack, R0..7, SMC, native/private
state, mappings, and final NMI state match uninterrupted execution exactly.
No audio or private-state normalization is used. The actual fallback entry's
live I bit equals its saved I bit. These NMI cases explicitly select directed
owner/previous-audio contexts; they are not natural Sonic gameplay or Mesen.

## Frozen bindings

- Source: `tools/reference/sonic_shared_audio_1110.s`, SHA256
  `7f90dacb40743a5d5db9183fca7da71469d821fe2f12dd3cc674a73f4d1e3333`.
- Checker/API: `tools/audit/check_sonic_shared_audio_1110.py`, SHA256
  `b6a60217f191787a3d28a6c0477bcf90ecf9a2e9d5dce2f6ebd79b99145bc086`.
- API: `proposal(raw) -> (image, record)` asserts every replaced preimage and
  its real entry context. It writes no files and can be composed with an
  explicitly pinned parent whose audio bytes match.
- Declared 6d83 parent with only this component in RAM:
  `152cb836bf4b081f9f5cab3621d06eb500c74c5755ad631907b097c169fff09a`.

Tests use Python `-B` and the bounded runner with `--max-files 1`; zero output
files are written. Natural Sonic cold/service admission, full stages, body/art,
and actual pit/music/life progression require the composed Sonic fixture and
root's separate physical qualification. No platform placements change.

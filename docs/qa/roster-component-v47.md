# MMC5 walking-Goomba renderer

The MMC5 renderer now uses an unrolled two-sprite path for the four native
walking-Goomba poses at interior coordinates. It preserves allocation, sprite
order, tile/attribute values, clipping fallbacks and postprocessing. The
161-byte helper occupies previously unused space. Only its bytes and the
existing call operand differ from v46; all old addresses, CHR and the entire
MMC3 ROM remain unchanged. The MMC5 metasprite bank has124 free bytes.

All761 existing emulator cases pass in one unchanged-fixture run with raw logs
frozen and bound. Actual compiled comparisons pass14,608 cases, checking every
CPU flag/register, all10,240 gameplay RAM bytes including the whole stack and
live self-modifying operands, and every ordered write. Two native read-only
observers supply another128 actual caller receipts, with zero interrupted or
silently discarded calls. Fresh402-file source extraction rebuilds both ROMs
byte identically.

All13,200 matched crowd updates preserve204 gameplay fields. In repeated
six-Goomba scenes for Mega Man, Samus, Simon, Bass and Ryu, foreground work
drops by about128–143 cycles per completed update. Both versions still draw
only30 times per60 updates in those scenes. Over1,200 updates each, physical
frames change by−27/＋3/−6/−47/−9 respectively. The Samus increase and every
individual timing/visibility counterexample remain in the raw reports.
Raw visible-enemy totals also depend on the differing physical-frame counts;
they are not interchangeable with completed-update gameplay equivalence.
This change does not remove crowded-scene lag or the eight-sprite scanline limit.

An ordinary-input Samus comparison matches all1,199 literalRGB24 captured
frames with identical actual input receipts. Literal continuous PCM differs:
252,784 of1,915,112 interleaved samples differ, first at6.878395833seconds,
maximum absolute delta1782 and RMS delta115.9811 (−49.0213dBFS).
Both original WAVs and the original negative result remain intact, with no
alignment, resampling, trimming or replacement of the failed PCM comparison.

The separate read-only APU observer records4,463 APU writes and15,486 source
queue writes per version. Address/value order and physical-frame assignment
match exactly. APU code origin, physical bank, interrupt context, mixer
ownership and native/combined channel enables also match. Paired APU writes
shift by up to112CPU cycles. This supports a timing/phase explanation for the
waveform difference; it does not certify waveform identity, perceptual identity
or all-character audio behavior. The causal classification is separately bound
in the accepted manifest.

Generic renderer fallbacks cost extra cycles, normally10–31 and up to71 in
the tested edge cases; eligible paths save up to56. Therefore a universal
performance improvement is not claimed. Original preparation/binding corrections,
the initial preparation syntax failure, crowd counterexamples and PCM negative
are retained. No old fixture or expected result was rewritten to obtain a pass.

Player outlines remain OFF on reset, with a gold menu option row. Samus has no
ordinary enemy stomp in the requested2.02 source; the acquired Screw Attack
provides damage during an active spin. All-character final routes, every
weapon/upgrade check and final audiovisual review remain open. Mario and Luigi
have verified current-MMC3 full-route recordings; that does not complete the
whole roster goal.

The accepted checkpoint manifest binds the evidence and source archive. This
is a bounded component update, not certification of source-perfect behavior.

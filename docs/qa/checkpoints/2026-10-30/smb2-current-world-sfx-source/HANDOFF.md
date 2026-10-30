Private SMB2 current world-SFX source successor v12

Candidate 256a1ea00fd196cd90bb40502ad8ab5729ddd563336dcfa6ac3d0f80c6396e69
is a genuine source successor to frozen current-joint v11 c15b50da. Only 551
ROM bytes differ, inside allocated A74 BF75..<BFFC and approved C82
DD94..<DFC2. The A74 worker uses 135 of 139 bytes; C82 uses 558 of 560.
All other ROM bytes, including every current Main instruction, common gate,
header, CHR, menu artwork/readiness, Celeste label, KamaV1, cache streams,
Quick loader/cookie/DMC suffix and all final127 mirrors/clones, stay exact.

The actual unpaused source NMI now sends real native world effects through
the existing shared SFX engine: bump/flag, coin/grow/vine/blast/timer/pickup/
extra life, and brick shatter. SMB2's native jump/throw/hurt/death cues keep
their original source music/effect/DMC driver. World pulses use MMC5 voices;
world noise temporarily owns native noise, then returns it to the real music
image. The helper uses the existing mixer body/expansion flush through genuine
source lexical exports. No original mixer instruction, pointer or PC changes.
The source DMC status function supplies the actual active/completed sample bit;
the Bass-specific status function and owner-begin DAC reset are not entered.

Passing exact-candidate controls:

* 240 real-vector/literal native-mixer wave-register pairs: all four classes,
  both rules, every allowed one-bit world cue over three updates. Native and
  world register images, ordered wave writes and channel ownership agree with
  the real existing mixer. Active original source samples neither stop nor
  restart while a world effect plays. Noise release restores actual music.
* Eight actual SetupJumpCoin -> GiveOneCoin producer paths queue the coin,
  update the tally, then play it through the next real NMI on MMC5 pulse2.
* 48 real nested IRQ cuts at the new worker stores preserve live outer CPU,
  raw mapper state and all33 SMC bytes.
* Current regression: 48 normal/lag/pause/busy source NMI records, all eight
  original DMC samples, 137 source nested IRQ cuts, 520 paired foreign vectors,
  four complete Quick16KB copy/verify loads and six interrupted loader seams.
* Ordinary current Main is byte-identical to qualified v11, whose 490 caller
  pairs measured +0 CPU against the fix-only current reference. It is not a
  newly rerun Main suite. Foreign NMI is +133 CPU versus current8062, one more
  than v11 due to placement; this remains an explicit integration cost.

The retained cba3eacb source negative demonstrates a real pause defect in the
first version: $5015 disabled the voices but left a coin effect buffer active,
so a stale cached timer could pretend to resume a disabled length counter.
The corrected actual paused path clears the three native world buffers like
the existing mixer's silent path. The negative ROM/source/receipt are retained
under pause-negative; the fixed real-vector pause control passes. The original
negative receipt's mutable candidate path is explicitly resolved by its exact
SHA in the negative handoff, rather than silently relabeled.

Two fixture corrections are also recorded: GiveOneCoin alone neither queues
the tone nor increments CoinTallyFor1Ups, so the test now calls its true native
SetupJumpCoin producer. Also GuestAudioFinish can skip an unchanged status
write; its Bass status API drops the source DMC bit, but that alone does not
prove a particular finish call truncated hardware playback. The receipt makes
that distinction and checks the true source sample independently.

All four SMB2 profiles remain pending. Natural raw25 typed transport, actual
post-Ic Fresh/current scene lifecycle and real foreground carry/body/terrain
boundaries are coordinated with the dispatcher owner. This packet closes the
world-SFX CPU/mapper gap only. It does not claim cold-menu/controller gameplay,
analog output, DMC stealing, PPU deadlines, FPS, admission or installation.
No native emulator, new lease, shared source or Downloads operation occurred.

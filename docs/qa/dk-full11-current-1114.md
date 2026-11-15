# Classic DK functional 1-1 source investigation

Root's delivered current is exactcf7
`cf7b6d2964ae0ef18d08c726f66afe9bf5be3dc6f3ec9c7a43279121ee09d968`.
`current_dk_gameplay_input_1114.py` authenticates the owning Gimmick inverse
to exact1daca and strict forward roundtrip, then rebinds only image-controller
provenance and changed bank hashes. Actual runtime bytes remain cf7; the
frozen classic/common/Gimmick composition and controller APIs are unchanged.

Classic DK uses real native SMB movement and A jump. `DkMovement` calls
`DkEnsure`, clocks the authored attack and tail-calls `CrossoverVanillaMovement`.
The jump-profile routine changes only MegaMan/Luigi. Fresh B throws barrels;
earned tier2 Down+B selects a vertical barrel. There is no additional DK
jump or ground-pound movement ability to infer from the original NPC.

## Retained first-pipe negative

Session88805 completed the genuine compiled-menu three-image opening in352
source Main updates, receipt
`a2a30d36070c53d8cdff6353fd5401234f4b8a40bef22b24c535150f24577544`.
It then retained the earlier first-pipe controls: approach x396 grounded,
hold Right+A38 updates, continue Right, for250 total source updates.
Diagnostic receipt:
`c0ea82e7633ef8e876f9e01f66786c06c2b1a8f619dfb11070c8428a81c52eb2`.

The jump is genuine: takeoff x396/Y176, prior A0, native speed16/16.
The first returned jump update reaches x397/Y172, state1, VY252 and force30.
It reaches x402/Y157 on the fifth update, where VY changes from252 to0,
then descends and lands at x416/Y176. It subsequently stalls x417/418 at the
first pipe, with engine8 and lives2. Only one actual jump-profile call and15
JumpSwimSub entries occur. This rules out a missing A edge at takeoff. It
does not yet identify the instruction causing the early upward cancellation.

The initial first16/last16 writer ring missed that causal middle writer.
The subsequent same-control head-cause arm5777 retained it explicitly:
receipt `c582ed81be4a14443894542d016a7a629677ab4d8a0e91095fd812d74020646c`.
Native PRG254 PC8DC7 writes VY252→0 at Main32/x402/Y157. The actual
BillBGHeadConsumer return at9BC5 reads tile81, R2=112 (world row144),
R5=133 (the left probe at world389), pointer03D8. By the later VY writer,
world384/Y144 is tile35: the native head transaction has cleared that brick.
Later empty-cell sampling alone would have missed the genuine head contact.

## Ordinary first-pipe retry passes in source

Session62476 preserves the same genuine opening and250-update negative
prefix, then supplies two ordinary Right updates with A released, followed
by fresh Right+A38. The second actual jump is acknowledged at Main252,
x418/Y172/state1/VY252, with A sampled128. It clears the pipe and reaches
x513/Y176/state0/engine8/lives2 after89 successor updates. The full physical
body is past the pipe: left500 exceeds pipe right479. Receipt:
`abbbe842dbf514e0c680fe16568893b9be23fbd324aa800e6d7a9547b955f22f`.
The first-pipe failure therefore supplies no basis for adding a helper or
changing DK's jump/collision code. This remains source proof, not native proof.

The new full-stage controller's initial strict/compile gate96390 passes on
exactcf7, rejecting truncated/unowned-byte/fa66/12397 inputs, without mutable
nightly rereads. Initial Lua SHA256 is
`1dbddab40b17764b04841e72a170bf3fd0b89ef872b38e3081126b30c764dd8c`;
policy SHA256 is
`4637f7d0946c03cb46609873e159d3c449696d3c85da31eddd0dc1937cc96c5a`.
It bases decisions on actual DkMovement followed by authenticated Main
return, caches buttons for input polling, releases A after a real early
landing and requires flag/castle plus25 actual living grounded1-2 movement
updates at40/Y176. Full source session43163 is pending at this checkpoint.

No full1-1 clear, native playtest, new helper, game change or delivery is
claimed. Source jobs use absent `build/dk-full11-current-1114`, max-files1,
timeout600 seconds, and zero output files. Root owns the single Mesen queue.

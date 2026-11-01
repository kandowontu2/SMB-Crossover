# Karnov terrain component — private progress

The installed nightly remains the tested 85-character build. Karnov is still
COMING SOON. This packet does not claim a native stage clear or playable admission.

The 5272-byte kernel adds cold construction, source movement export,
head/side queries, body geometry, easy/hard stomp policy, landing/ceiling/ledge
reconciliation and the native collision profile selector. The 977-byte
ROM resident now has genuine 36 JMP rows: caller Y is the terrain probe coordinate,
not the service index. Child A/X/Y/flags and scratch return live through the
guarded dispatcher, while mapper and SMC operands are restored.

The native Mega profile supplies the same (2,32)/(13,32) foot probes. Custom
standing/crouching probes query block buffers without moving the player anchor.
Source FA06 screen clamps redirect to the original FA5C facing update because
SMB owns screen bounds. Original land physics instructions/tables remain intact.

Evidence: 2112 cookie checks, 1188 corrupt/foreign route rejections, 840 comparisons
with actual SMB queries, 64 HUD head-extent cases, 11 declared contact boundaries,
1140 original source-step comparisons, 420 updates through the real ScrollHandler
without horizontal drift, and 272 actual host NMI/IRQ cuts.
Ordinary and boot jump rises remain 48 and 88 pixels across world-page wraps.

Terrain support/contact inputs are explicit unit fixtures. Shared gameplay/menu
hooks, full native BG collision, rendering, combat, health, options/pickups,
original music and controller playthroughs remain required. See handoff.json.

The ZIP contains only listed source inputs and compact receipts, without ROM,
objects, debug images or captures. It is a component packet using retained
current-game linker inputs, not a standalone clean-build release.

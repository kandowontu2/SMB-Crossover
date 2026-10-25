# Score popup position repair

The defeat popup used a shared relative X left by an earlier actor or the target before it moved. It now uses the defeated slot's own world X minus the camera position. Y, timer and popup selection retain the native behavior. This repair builds on the installed green-terrain publication repair.

The 19-byte resident entry retains its old address and calls a small cold body through the existing selector-preserving native-call mechanism. The new body occupies the unused A-mapped bank $24 tail at BFC0. The header, CHR, all old code/RAM labels and baseline ROM builds are unchanged; no new RAM is allocated. Only the entry and previously unused tail change (58 ROM bytes MMC3, 50 MMC5). The reserved 64-byte score tail leaves B600-B6FF for the private Water candidate and B700-BFBF for Ryu; the frozen Ryu F body ends at B9D4.

## Verification

- An ordinary 6,000-frame Bill controller run on each mapper produces 16 score calls. The old ROM misplaces seven; the repaired ROM misplaces zero. Both return all observed caller registers, flags, stack depth and mapper state correctly. These are bounded, zero-death runs into 1-2, not full clears.
- The permanent native fixture passes on both mappers: six authored target slots, camera/page boundaries, actual prone shots, and the actual number renderer. The old ROM fails specifically on the stale anchor. This is a diagnostic arena, not a controller-only route claim.
- Twenty unchanged scoped native checks passed in the original AQ matrix. Its initial MMC3 score fixture failed because an attempted debug-register write actually patched the emulated code. That harness error was removed; the corrected AU score fixtures pass on both mappers. The original failed matrix and diagnostic evidence are retained. On-disk ROM files were unchanged.
- A separate compiled CPU test passes 9,072 cases, including all eight foreign MMC3 selectors, flags, slots, camera boundaries, stack and bank restoration. The rejected standard-call prototype fails the selector check. This is not an interrupt-injection or cycle-cost claim; no interrupt occurred inside the observed ordinary score calls.

Checkpoint: `build/checkpoints/score-popup-location-az/manifest.json`. Evidence: `score-anchor-aq/summary.json`, `score-popup-fixture-au-*.log`, `score-anchor-native-an-*/summary.json`, and `score-abi-at/summary.json` under `build/verification`.

The old fourteen delivery videos retain their original identities. They were not re-recorded by this repair. Bullet Bill duplication, missing firebars, underground block colors, late HUD splits, remaining private component composition and final all-character captures remain open.

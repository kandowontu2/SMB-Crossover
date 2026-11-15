# Battletoads private idle candidate: native cadence unchanged

Root32500 independently runs the frozen literal controller-read observer
on installed7a80 and privatea90c. Both finish the ordinary cold-selection,
48-idle-Main/32-Right-Main observation without injury or actor activity.
Official Downloads remains7a80; the candidate is private and undelivered.

| Image | Native receipt SHA256 |
| --- | --- |
| Parent7a80 | bca70b266e6f7f2716b72c2525e11f1d47d6d06eedc8f60c00aca4ee3eb0882e |
| Candidatea90c | 32cc20826e9f7188b70f1452ccf56656d1692a45da0b3e6eedb0c5bccc40ad4d |

The actual results are identical:48 idle Main returns over48 physical
frames with24 NMI skips;32 Right returns over32 physical frames with16
skips. The sparse literal4016/4017 read observer samples47 idle frames,
23 without a read, with a Main histogram of24 zero-update and23 two-update
frames. All32 walking samples show16 missed reads and16 zero/two-update
frames each. Hero stays40/176 while idle and ends81/176 walking,
HP47/lives2/power0, with zero active actors in the idle window.

Thus the actual native read/update cadence has not improved in this
window. The source result of1966 fewer cycles per Main remains valid in
its model scope; it does not prove a native speed gain or explain why this
cadence remains unchanged. A new read-only native observer will verify
actual guarded getter execution and Main/IRQ/NMI cycle contributions.
The frozen parent/candidate benchmark bodies stay unchanged.

The exact a90c image changes535 bytes within556 owned bytes and preserves
all other7a80 bytes. Source flags/foreign/constructors/lifecycle/ISR/full
routes passed, as recorded separately. Full Rash/Zitz native routes are
now qualified separately below. No delivery decision, zero-lag claim,
gameplay repair or audible-output claim follows from this benchmark.
No ROM backup, capture file, video, patch asset or release is created.

## Private full-level regression checks

Root35986 passes both frozen ordinary full routes on exact privatea90c:

| Identity | Main / video frames | Native receipt SHA256 |
| --- | ---: | --- |
| Rash | 4359 / 4897 | 797ae2f02d3f2ebaa3cb82897da416a636b90a8c53533d7b5de3d449716c1e9f |
| Zitz | 4380 / 4912 | b3bf1f6de2cf3da86082b60d4a57384dfaf0e817d85850f6d35e90b78a96c314 |

Each reaches the flag, castle and next-area entrance, then completes25
living grounded1-2 updates at40/176, HP35/lives2/power0. These are real
controller routes without gameplay-state writes, additional helpers or
capture files. HP35 is the native result; the source model's HP43 is not
promoted to the emulator. The different total frame count from older
versioned full-route receipts is not an isolated performance measurement.
Installed Downloads7a80 remains byte-identical and the sidecar guard stays
clear. The identical idle/read cadence above remains an open native gate.

Root67124 subsequently confirms the optimization executes in actual Mesen:
all160 mapped getter entries return to their actual callers; getter12 costs
994→21 cycles and getter13 costs992→24. Exclusive Main saves about1966
cycles per update, while the NMI work leaves the same alternating lag-frame
cadence. The full aggregates and sparse rows are in
`battletoads-native-profile-root-1115.md`. The profiler distinguishes actual
hardware interrupt returns from the authenticated audio software RTI.

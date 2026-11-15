# Battletoads native idle diagnostic observer, November15

Official Downloads remains exact7a80. Root32500 measured the qualified parent
and private a90c with the frozen literal-read benchmark. Both assertions passed,
but the observed cadence was identical: idle48 Main/48 physical/+24NmiSkipped;
Right32/32/+16. The47 complete idle frames missed23 controller reads with Main
histogram0:24,2:23. Walk missed16 of32 with histogram0:16,2:16. Both retained
HP47/lives2/zero actors, x40 then81. Parent receipt:
`bca70b266e6f7f2716b72c2525e11f1d47d6d06eedc8f60c00aca4ee3eb0882e`;
candidate receipt:
`32cc20826e9f7188b70f1452ccf56656d1692a45da0b3e6eedb0c5bccc40ad4d`.
This negative remains separate from the1966-cycle mounted source reduction.

Root35986 subsequently passed both private a90c ordinary full routes. Rash:
4359 Main/4897 physical, receipt
`797ae2f02d3f2ebaa3cb82897da416a636b90a8c53533d7b5de3d449716c1e9f`.
Zitz:4380/4912, receipt
`b3bf1f6de2cf3da86082b60d4a57384dfaf0e817d85850f6d35e90b78a96c314`.
Both passed fullflag/castle/entrance and25 living grounded1-2 updates at40/176,
HP35/lives2/power0. SourceHP43 is not transferred to these native runs. No nightly
delivery is claimed by this helper.

The new read-only profiler is
`tools/audit/replay_battletoads_idle_native_profile_1115.py`, SHA256
`93af79300b34f62161b5ff5a8c794cea0ab91dba8d726000542a17d9abdd892c`.
APIs: `controller(raw)`, `config(raw)`, `metadata(raw)` accept only exact7a80 or
exacta90c through the frozen typed benchmark boundary. Frozen composer2ecaff,
stagefactory401a and benchmark3bee are unchanged.

| Current input | LF profiler Lua SHA256 |
| --- | --- |
| 7a80 parent | `2ee638103698ae7e5f2f2d38969670ab4a6316c774644f2562e9f3060aaa276c` |
| a90c candidate | `1158970e6dd4c492c5587ef83c3c319674f439826771cbf6c8e6896cf10dedc6` |

The observer retains genuine menu/Select/Start, idle48/Right32, literal4016/4017
reads and physical-frame histograms from the benchmark. It adds authenticated
mapped B8B8 Y12/13 entries and dynamic mapped caller-PC/SP acknowledgements,
Main wall versus completed outer hardware ISR cost, and separate regular/busy
NMI and IRQ aggregates. Hardware spans include entry7/RTI6; nested IRQ cost is
subtracted from NMI exclusive cost and counted only once in an outer Main span.
Every hardware closure requires matching kind, entrySP, saved status and dynamic
returnPC. Output is at most12 aggregate groups and32 sparse rows, with no PPU,
full-state, image or file capture.

The first source observer failed before Main because it assumed every8043 RTI
was a hardware IRQ exit. Source57670/27569/5016/67687 negatives are retained.
The actual regular-NMI path reaches a software dispatcher in PRG96. Its exact
48-byte producer atDE9F..DECF is:

```
A9BF8D1551688DA17DBABD0101A8BD03019D0101BD020148A9009D0201A9B69D030168AAA98048A94248ADA17D4CC580
```

This actual ROM code rewrites a software RTI target toB600, pushes8042, and
jumps to fixed PRG126:80C5 (`8D165160`, mapC/RTS), which enters8043. The observer
authenticates the full producer and mapper thunk. It dynamically captures the
software frame's SP/status/target and depth, acknowledges the mapper RTS, and
recognizes that exact transport at8043 without closing the outer hardware NMI.
It does not waive other mismatches or hardcode a native hardware returnPC.

Source8433 passed the first version with a literalB600 assertion. Final33836
passes the version with dynamic target capture and full48-byte authentication.
The source callback checker is
`tools/audit/check_battletoads_idle_native_profile_1115.py`, SHA256
`168b2e55e74ac154049a2e9df82784df08c435a2f58fd7981924c49a023c910f`.
Final receipt:
`7647dbff56ab3fbaad55008accd1b8909e6f806ba7528ca3d6b5b0e5d204b07f`.
Both exact images independently ran82 genuine source Main updates; the sampled
48idle/32Right periods each acknowledged160 getters, with zero pending Main,
ISR or getter spans,80 software RTI dispatches and16 sparse rows. Parent guard
spans cost994/992 cycles; candidate21/24. Regular scheduled NMIs execute; this
source peripheral model supplies no physical scanline IRQ or native cadence
qualification.

All source invocations use the existing absent
`build/battletoads-remaining-idle-1114` root through the bounded runner,
max-files1/600seconds. Generated outputs are zero. Root alone runs Mesen and
stages the existing private image; no helper ROM, native run or Downloads write.
Actual native profiler results are pending.

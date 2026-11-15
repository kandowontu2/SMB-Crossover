# Current-nightly cadence baseline for the corrected carry candidate

Official174fa remains installed. Root39854 runs its actual Downloads ROM
with strict compiled Lua
`b8b325ae2b49219242d2ba6481a8ea2557afae85de3f25c8f7285677f881c069`.
Native Mesen receipt **passes**:
`66235036ec9d14ad0f7a4e8b48322d4d45cfc67326e34a64a94223f71f878005`.
It observes existing behavior; it does not qualify or install a new candidate.

| Actual174fa window | Returned Main / physical frames | Frames with no4016/4017 read | Actual Main histogram |
| --- | ---: | ---: | --- |
| Idle |48 /48|23 of47 fully observed frames|0:24,2:23|
| Right |32 /32|16 of32|0:16,2:16|

The average is one Main per video frame, achieved by skipped and doubled
updates. It is **not smooth60Hz**. NmiSkipped increases24/16 respectively.
There are zero active enemies in the idle window, HP47/lives2, and the final
state is81/176.353 Main entries equal353 returns over377 total video frames.
The Lua body uses actual read callbacks at4016/4017; its separate input_polls
counter is host input application and does not establish hardware reads.

Root preserves the exact tested19,663-byte LF source as
`tools/reference/bt174fa_cadence_b8b3_1115.lua`. Its body SHA256 is
`f76943af78cedc9d38c6433ed438a2040ccc186c18c2dd6fb686a4fbde179f7e`.
The separately named fixture facade
`replay_battletoads_carry_cadence_fixture_1115.py` SHA256
`53656a3dc35669535f4db5dc20d739db154fbaee4dab020e217b17eb6d5cee25`
reuses that body with strict frozen C/F and actual hook-bank bindings.
Source13991 proves both complete texts byte-for-byte equal the original
qualified factory outputs, receipt
`e85d3796fbe9045a595fbf3315a2c43d18df72918bd668d860e103bfcd5a33c6`.
The candidate observer pin is8f88463c; no original factory is changed.
This avoids reconstructing a historical observer for subsequent comparisons.

The corrected source candidate is
`aceedaf2151fdf673b489a742831a0844abbb3837e0bcba68408d3ba5c3a4cfe`.
It remains source-only until mounted lifecycle/profile/ingress/interrupts and
both full routes close. Root will compare it with the same literal read and
Main-return observer before any speed claim or delivery decision. No physical
candidate exists at this baseline gate; source savings do not close cadence.

Both before/after patch guards and official/private bytes are unchanged.
Only the existing controller file is replaced in the two-file native slot.
No capture files, ROM copies, backups or release assets are created. The root
source fixture proof uses absent `build/battletoads-carry-root-review-1115`,
max1/600s and zero generated outputs; native root uses its existing2-file slot.

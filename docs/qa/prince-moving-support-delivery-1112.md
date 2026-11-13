# Prince moving support — delivery qualification

Downloads verification and publication status are recorded below.

Parent ROM: `464c8f1af0401ba7d5393e331833af5bdd68882c536dfc3c77534b71508213c0`.
Candidate ROM: `6d0346164b7099f8e75cdbe22a9e9f1fd5f4f673116fd1dcb48a3cee620734c2`.
Candidate IPS: `e2662c8439e226fa5fd3a2684427c97affb3f3a3be6ef3dc1d80f7d4acec897d`.

Prince could stand on an exposed ordinary brick after climbing, but the next
walking update rejected that same support. The candidate removes the redundant
idle-only test after the existing action/mode, grounded position, native tile
and empty-above checks. Five decoded bytes change; the authenticated compressed
packet and cookie are rebuilt. No movement constants or graphics change.

Verified privately in actual Mesen: first-row walk remains at Y112 and reaches
X383 with HP5/two lives. Full1-1 then clears into active1-2 with both lives,
frame16355, using the controller's adaptive retreat based on its prior ledge
position. Receipt `a3c15de76676ba9ebdf3ffdbc84049ef953b70d14015285e31e05251c0fd773c`.
Old controller assumptions and negative runs remain documented in
`prince-pickup-input-trace-1112.md`.

`deliver_prince_moving_support_1112.py` verifies forward and reverse rebuilds,
clean-base IPS reconstruction and the exact candidate, and will test the direct
Downloads replacement in its normal launch context. Failure restores the old
bytes from memory; no backup ROM is created. Forward/reverse and IPS checks
passed locally with zero generated files.

CPU qualification passed: 1,280 material comparisons, 2,552 action/mode cases,
256 idle-pose cases, 126 geometry rejections, 12 source-sole normalization
cases, 486 facing-foot positions, 48 full support decisions and 20 unchanged
non-support decisions. All 462 IRQ and 462 lag-NMI interruption checks passed.
Checker SHA256: `329a8ee9c63bbfc80ee22655f2a481aca5f851c4e3c397b60e43ae722fbaed59`.
Controller SHA256: `a115265b9c2a3cc12fbf792a3460e01c5ce67264e2829dc901dfe5ee37ce33d0`.

Downloads was replaced directly, with no backup. Full1-1 replay from that exact
launch context passed with the identical receipt above. Installed bytes match
the tested candidate and both automatic-sidecar checks pass.

Published: Current is Latest, with sole IPS asset741831523 (2,099,510 bytes).
Independent download reconstructed the exact installed ROM. Publication used
source750778d7e472761f062d2c037273372cbfd40c00 and report SHA
925bb1bee67ca242db0ae58e3839b4c2a05295507d70ebc1e54b90ec32cdc1c9.
Natural Prince powerup collection remains unfinished and is not claimed here.

# Separate enemy-aware Flower hit controls — November 13

This owns the new `replay_smb2_flower_hit_followup_1113.py` and this note. It
preserves frozen52f/045/f78 factories, default b6 and all previous receipts.
The parent hit0 native aiming negative is recorded in
`smb2-flower-control-followup-1113.md`; no game attack defect was established.
All new experiments use exact12397, ordinary menu/controller input and real
Main/NMI CPU execution, with no gameplay seeds or generated outputs.

The original Ready85 native member remains authenticated as
`c929f894f8d6f4723e6371d140c85fef76de47eb9f53bff0af6b544325f80cb0`.
The new factory binds current `S2Face`, native enemy flag/ID/state/world-X/Y
fields and the actual compiled facing/fresh-B/throw classification windows.
The existing source-facing calculation uses1 for right. Exact current VX table
is `00 00 d0 30 d0 30 d0 30`, and VY table is `18 00 18 f8`.

An initial interpretation of the VX table was corrected before qualification:
vegetable type$32 makes the preceding CMP#$36 set carry, so both stationary and
moving right-facing vegetables use VX$30. Speed8 selects the vertical arc,
VY$18 versus$F8; it does not enable horizontal vegetable velocity. The first
moving-Right+B experiment, Lua
`9240b9d63bda9a4cfeae3a5bc0114b3cb33aaed85427b1841d5494bbb4744835`,
is a source negative: throw771 at689/176, observed VX48/VY250, no native contact,
then health15 at805 (806 iterations). Its upward arc misses the target. It was
never offered as native-ready or run by this helper in Mesen.

The revised factory keeps right-facing, neutrally brakes and presses fresh B
below the original8-unit arc threshold. Its file SHA256 is frozen at
`f6a6b42c825328be662acd7016ac095959315aca82a2d8077ebb8df7d2c69957`.
It preserves the existing24..72 forward live-Goomba/height/grounded admission,
adds a read-only clear-path/facing check, and records target/aim decisions.
Removing the two control replacements and the added Face symbol must recover
the exact parent text. All original pickup/reserve/HP/native-hit assertions and
2600/180 bounds remain. The CPU cap is1500 logical iterations.

| Variant | Source outcome | Logical / returned Main | Lua SHA256 |
|---:|---|---|---|
|0|PASS|808 /807|`53c0b85fc74f89b9a0dd52c24996884167ddf75a5cc7d29bbb40493c254009df`|
|1|NEGATIVE|1097 /1096|`ed58c50c8b049e8dbb0e45aacd4c5db03f3dcf5f015ca1ca75aedc680dc55e50`|
|2|PASS|795 /794|`b967a85b7cd3ef3b78c50dc0e9732a30bd8e9a037c509234e0b5821cbeef80db`|
|3|NEGATIVE|977 /976|`f02e7742e9813c151c940a9c29dd28e4ce28ff83dac0a4346cdc77a78caab512`|
|4|PASS|808 /807|`398909607cdaac8f93b51f097615427f65fb4ea676c5101f06c23366d854a059`|
|5|NEGATIVE|977 /976|`29a0528a2cad358fb0475ec3e5ee1276455c08a75803d5da3e0d35624fe2f4aa`|
|6|PASS|795 /794|`69b0e896caf3c3370112014bf09ccf98985a712a6b24031884a396de18f39c9d`|
|7|NEGATIVE|967 /966|`ece880f3533ff74aad8c2223a9d2574a25335a80f9e0e5e21be06f6512a5d1a5`|

Positive cases reach the real source projectile/native Goomba defeat0→34,
health31/lives2/reserve2 and30 resumed updates. Odd variants stop at641/176 and
throw toward706/184, gap65. Their low arc ends before reaching the approaching
enemy, and the unchanged health assertion later fails at15. The older
odd-family controller already waits for gap24..40. These are controller range
negatives, not demonstrated ROM defects. The batch finishes all seven cases
before reporting its four negatives. This factory is partial, not an all-eight
native-ready replacement.

The separate acknowledgement successor in
`smb2-flower-ack-followup-1113.md` retains this frozen factory, adds the existing
close-range wait, and addresses root's independently observed lost B pulse.
No helper launches Mesen, writes a ROM, creates captures or publishes assets.

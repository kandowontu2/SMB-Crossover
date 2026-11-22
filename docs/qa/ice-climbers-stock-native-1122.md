# Popo and Nana pickup checks

The [Mesen replay](../../tools/audit/run_ice_climbers_stock_1122.py)
selects an Ice Climber from the actual title menu and uses ordinary 1-1
controller inputs. It preserves the completed stage clears and Mushroom
checks from `a7ccbaaa`. The current tests use the installed MMC5 nightly
`a6d91e36` and the retained difficulties of Popo Easy and Nana Hard.

## Fire Flower and Star

Popo earned the Mushroom from X336/Y144. He opened the Fire Flower block
at X1248/Y144 from below, backed away, and jumped onto the row from the
left. The Fire Flower increased his power from tier 1 to tier 2. He then
opened the Star block at X1616/Y144 and caught the emerging Star. The
native invincibility timer and music started, and the Star remained active
after another 25 movement updates.

| Character | Physical frames | Mesen receipt SHA-256 |
| --- | ---: | --- |
| Popo | 2,531 | `05579c1248c5c2089c71f717de252654c543364b413ab3b1217c5fbefbcda9fa` |
| Nana | 2,666 | `e39a003ba9f9bfd7015b5e00e0c34336051e3e44d9e8649d1aafe5b78319d133` |

Popo's controller SHA-256 is
`390a82b91a588e35d0be59d6744debd1e73a06dafec70c94629da0b94453ec5e`.

Nana collected the Mushroom and kept tier 1 for 25 more movement updates
on Hard. On the same route she lost the parka at X797/Y167 during the
descent past the third pipe, before the Fire Flower. The next Flower
attempt needs a safe crossing from that pipe. Receipt
`8a8bb030c1cadf8cd70662b28d38609a4c913b6c9745548544743a17c7f55e6f`.

Nana's next run used a fresh rightward jump from the third pipe at
X752/Y112 and landed with the parka. She opened the Fire Flower block,
jumped onto the row from the left, and kept tier 2 for 25 updates after
the pickup. The run later revealed the Star and missed it. The Fire
Flower check completed at physical frame 2,031, before the later failure.
Receipt `d27f84b5938ad61cde7f53a69642d20e16bc7fa427c6a5630fcb1778fa23bfa1`.

The successful Star replay repeated that pipe jump and Fire Flower
pickup. Nana reached X1678 ahead of the first Star bounce and jumped
straight into the descending item. The native timer and music started,
and the Star stayed active for another 25 movement updates. An earlier
enemy hit reduced her to tier 1 before the Star. Nana's successful
controller SHA-256 is
`f304bbe74891ca2c3d7c996ad0f98f92f6ad3945e15a1c86395eae40f0396af7`.

## Hidden 1-UP

Both climbers hit the invisible block at X1024/Y128 using a jump from
X1017. The item emerged, was collected, and triggered the native delayed
life credit. Both went from two lives to three and kept all three through
another 25 movement updates.

| Character | Physical frames | Mesen receipt SHA-256 |
| --- | ---: | --- |
| Popo | 1,661 | `8c7cef503bbfa3ff645edd9d2a6b7b40804b2130d58faff18d083d6806856bb5` |
| Nana | 1,835 | `951a5da8a245f31ab026eebad19c14d1ce72e75aef828290504514f6607addf6` |

Popo's hidden 1-UP controller SHA-256 is
`53f1fea490d5138e7bef9ddd0a4159ce3b1245b6e04e7a8b162dec437e33e083`.
Nana's hidden 1-UP controller SHA-256 is
`b6dce3aa3b8dc3bed60de6cf1ed32d9f9287c6daaf834839424c60ed6338e3da`.

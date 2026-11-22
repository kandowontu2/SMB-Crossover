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

Popo's controller SHA-256 is
`390a82b91a588e35d0be59d6744debd1e73a06dafec70c94629da0b94453ec5e`.

Nana collected the Mushroom and kept tier 1 for 25 more movement updates
on Hard. On the same route she lost the parka at X797/Y167 during the
descent past the third pipe, before the Fire Flower. The next Flower
attempt needs a safe crossing from that pipe. Receipt
`8a8bb030c1cadf8cd70662b28d38609a4c913b6c9745548544743a17c7f55e6f`.

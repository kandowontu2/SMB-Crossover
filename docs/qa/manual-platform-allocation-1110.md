# Manual vertical platform allocation

Requested controls: Mini Mario and Karnov use Up + Select to create or replace one native vertical platform directly beneath the player. Select alone retains existing behavior. This note records allocation review, not completed gameplay verification or delivery.

The common constructor uses 130 bytes of the 136-byte alignment interval at physical PRG64 `$B378..$B3FF`. Mini's caller uses existing private code padding. Karnov's caller may use the corresponding 136-byte interval in physical PRG11. Neither grant includes `$B377`, `$B400..$B4FF`, or the next segment at `$B500`.

The PRG11 allocation was independently reviewed against released ROM `94650fbc11ede25b9d08e579bdc6b1d6da81fca8f29c6b0c25dadad2e685ede1`:

- The complete bank matches the symbol-bearing Karnov base. Bank SHA-256: `44ecf7ce03d13850d75ba8c7bafb9990c5700638c76d4abb81a6ac2ef49a28b7`.
- File interval `$17388..$1740F` is the generated MM3 multiplier's `.align $100` padding, distinct from the Proto Man copy in PRG64.
- The preceding routines return at `$B370` and `$B376`. `$B377` is a one-byte overflow mask, read by BIT.
- The indexed table reader at `$B34A` uses `$B400,Y`; its bounded nonzero byte index reads `$B401..$B4FF`.
- No linked bank11 symbol or decoded absolute code/data target enters the gap. The 64-entry track-pointer table contains 19 nonzero pointers, all `$AC85..$B2DA`.

Root accepts these exact finite intervals for the helper. The producer must assert the original alignment bytes and surrounding code/table identity before patching. Native carry, replacement, input-edge behavior, capacity handling, transitions, and music/interrupt regressions remain separate checks.

# Kirby red-shell return catch, November 12

The candidate retires a returning red shell before its next 3-pixel step would
reach or cross Kirby's world X. This removes the installed X598/X601 bounce.
The installed turn age remains 32, with the original outbound and return speed,
native terrain handling, swept enemy collision, and native defeat routine.

Input was the installed sword/menu successor
`c5ce8c1557f6eb27c97f1fb1b0404c7854f59feb18717f27171d7dcb890efbbd`.
Candidate:
`f228e61399432c1a205b8f5ac6dad13d990515f9c2e2f5024bcd5ce443c76653`.
This follows the cebb red-shell observations in `kirby-red-current-1112.md`;
the installed Kirby routine is identical in the affected span.

## Scoped implementation

- `tools/reference/kirby_red_catch_1112.s`: 72 assembled bytes plus 2 NOPs,
  replacing only the existing 74-byte PRG74 `$A5D1..$A61A` envelope.
- `tools/audit/check_kirby_red_catch_1112.py`: exact-preimage compositor and
  actual linked CPU checks. API: `candidate, info = proposal(raw)`.
  `info` contains `file_offset`, `preimage`, `replacement`, and allocation data.
- No new RAM, carrier, code bank, ROM output, gameplay art, or helper platform.
  No menu, Prince, Metal, or delivery files were changed by this helper.

The source authenticates the installed bytes and private internal jump callers,
then keeps the existing motion entry `$A61B` and retirement entry `$A694`.
Unlike the older `src/kirby_weapons.s` text, the installed comparison is 32,
not 24. That installed behavior is the input authority.

At age 32 or later, the replacement computes the unsigned 16-bit horizontal
distance to Kirby. Distances -3 through +3 retire through the existing Kill/Next
path. Larger distances retain the original +/-3 homing velocity. There is no
new Y gate; the installed homing target was also horizontal. The adjacent kind8
wave decision is factored to the same -1/+1 vertical result, funding the catch
inside the original allocation. Other motion and contacts remain at their
existing addresses.

## CPU evidence

Command, zero generated outputs:

```text
python -B tools/audit/run_bounded_build_v1.py --output build/kirby-red-catch-1112 --max-files 1 --timeout 180 -- python -B tools/audit/check_kirby_red_catch_1112.py
```

All gates passed on the input/candidate pair above:

- 1,080 directed slot/page/age/distance cases: 576 catches and 504 moving cases.
  Cases cover every shot slot, page boundaries, world endpoints, both sides,
  pre-turn motion, and late returning shells.
- Eight original traces reproduce two-position oscillation through age89 and
  expire at age90. The corresponding repaired traces retire at age68 facing
  right and age62 facing left, without reversing during the inbound leg.
  Four independent age32 turn traces match the original exactly.
- 1,014 complete final register/RAM comparisons cover every non-red kind0..13,
  13 significant ages, all three slots, and both velocities. Cycle deltas -7..0.
- 320 complete red-shell native-enemy pairs: 125 hits and 195 misses, using the
  actual native defeat path. Cycle deltas -13..+1. Both directed moving-actor
  corner contacts still hit through the existing swept helper.
- 64 complete green-shell pairs preserve 20 hits and 44 misses; cycle delta -7.
- 243 puff/star/TTL pairs preserve the complete final state. Three mixed-slot
  cases catch each slot in turn while the other two wave shots still update;
  copy3, health6, lives2, and ObjectOffset are preserved.
- 36 NMI and 36 IRQ instruction cuts cover the replacement, with exact resumed
  state and final continuation comparisons. A nested IRQ also passes; deepest
  parent SP201. These use the actual native busy-NMI/IRQ paths in the CPU model.

Source SHA256:
`e2c9672291403d15a7368e55cf3b417574155fd4b9ef70a5ac73e99ad75f3af5`.
CPU fixtures use pinned, retained symbol metadata and current ROM bytes; no
historical tree was extracted. Fixtures are directed CPU states, not claims
of naturally acquiring every copy power or completing a stage.

## Root-owned native replay

Root reports strict `--return-flight --expect-catch` Mesen replay passed for the
candidate above. Kirby naturally inhaled and swallowed the authored Red Koopa,
kept copy3, and the first shell still killed the later native Red Koopa.
The second shell returned X613,610,607,604,601 at ages63..67 and retired at
frame1852, with health6/lives2 and `catch_verified=true`.

- Receipt SHA256:
  `0ba2031f64825b6188e67ecd7d6f849c70c365af5ba0e5072f61b3001e9128f6`.
- Controller SHA256:
  `c76e0e3236aa81a845d47c06a81605072d9f1930f7a4a26f8ab0464a862190c1`.
- Root retains the candidate/controller in `build/kirby-red-current-1112`.

Root separately verified the unmodified input fails the strict catch observer:
receipt `7ab8497b5bb817a63db45352519bec7d44b651e3a409b553c8385ddcbc6372b8`.
The helper ran no Mesen and made no delivery. Root owns installation/release.
This closes the red-shell return defect; full Kirby stage clearance,
underwater behavior, every enemy, and all copy powers remain separate work.

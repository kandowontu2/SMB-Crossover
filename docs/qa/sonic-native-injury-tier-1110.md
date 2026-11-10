# Sonic powered injury returns a valid native tier

Both powered tiers now return to tier zero after native injury. On the
delivered d254 image, `InjurePlayer` entered raw43 row 5 with A43. The shared
decline leaf returned C0 without setting A. Native `$97A4` stored that A into
`PlayerStatus`, producing the invalid tier 43. The original ring and hurt
investigation records the exact failing trace. [Donor and host audit](sonic-original-rings-hurt-1110.md)

The source derivative changes raw43 row 5 from `JMP $BD73` to `JMP $D31B`.
The new leaf is `LDA #0`, `CLC`, `RTS`. It uses the exact approved four-byte
tail `$D31B..<D31F` in the already authenticated CHR328 metadata. The
common decline and other rows retain their existing behavior. The two JMP
operand bytes, four executable bytes and 13 cookie bytes account for all 19
changes. The original movement kernel stays byte exact.

| Binding | SHA-256 or value |
| --- | --- |
| Current base | `d2542ff3c9f78ac26eb7e19d64a7708711bc766515f634b05952bab1be9103f0` |
| In-memory successor | `19a5ea9001f22afd529c96c6c2401a237f487c0f851678363fb859f0ec7c1936` |
| New cookie | `a72b0194a989064ae62ef75a04986523` |
| `tools/audit/check_sonic_native_injury_tier_1110.py` | `91c1e52679b7d4ede2e459b2ebe7f97644fda2887330a872cf00e2fcaacbcddf` |
| `tools/audit/qualify_sonic_native_injury_tier_1110.py` | `b73756d4e524cad96f00af5b97b0985a4e6f30b1b477f357437f76e27c765236` |

The controller starts Sonic from the native menu and reaches X81 in 40
original updates. Each directed powered injury then uses the actual native
entry. Tier 1 enters through `InjurePlayer` at `$976C` and tier 2 through
`ForceInjury` at `$9771`. Both store A0/C0 and enter native engine 10 with
TimerControl 255 and InjuryTimer 8. After exactly 55 normal Main/NMI updates,
engine 8 resumes with TimerControl 0 and both lives. The original movement
clock stays at 40 through the scripted recovery. Holding Right advances
24 original updates and moves Sonic from X131 to X198 at tier zero.

Four tier-zero or native-immunity comparisons and six prior-owner row 5
comparisons matched the predecessor. A fault in either header rejects the
new private row. Real cold loading verifies the full 1 KiB metadata after
18,386 PPU reads in 397,199 CPU cycles, with minimum SP 187. A warm load uses
zero reads. The old cookie triggers a fresh copy. Faults at each of the six
changed metadata bytes leave both headers invalid. Six actual lag NMIs, six
foreground IRQs and one nested IRQ preserve the live state and complete the
same native injury return. All three new instruction PCs are covered.

`check_sonic_native_injury_tier_1110.proposal(raw, p)` composes the owned
delta after checking all eight existing code pages, metadata, cookie and the
native store preimage. Both source checks use the bounded runner with zero
output files. The repair uses the existing SMB injury policy. The separate
original ring, shield and damage port still requires its own integration.

PRIVATE CURRENT-SOURCE MMC3 BUILD, 25 OCTOBER2026

Parent MMC5:220be8247baf877785c91244876038354442e68502b3f837920f39a674a1fa3e
Private MMC3:417e254d331cbf0b8df0c7ec1081273f7d9f867830a9596d2fd272a5050acf2f
Recipe:b8c3487a60a77b227566767ebe4712069458a7b64961fee2def0670060ac2c87

NOT ADOPTED. No native gameplay/IRQ/PPU/audio/performance qualification of
this hash. The active ROOT recipe and all user ROMs remain unchanged.
The retained earlier V42 native cases belong to bc89, not this build.

The prior proposed e319 recipe prepares the current source but its link
fails: SPECIAL_EXTRA overflows PRGA_06 by4 bytes. The new Sophia triplet
reservation helper requires22 bytes. Its same-bank implementation fits in
24 existing NOP bytes skipped by AvHomeFriction's unconditional JMP HighByte.
This preserves the original function prefix/suffix and its asserted58-byte
HighByte offset, uses no new RAM or bank switch and restores18 bytes of tail
headroom. Only this proposed MMC3 recipe relocates the new helper.

2,048 actual linked CPU cases exercise all1,024 occupancy masks, both with
and without an existing standard missile. The helper admits only three-free
pools without an existing missile. Every fetch stays in A6; no mapper I/O.
This does not exercise complete native volley allocation or interrupts.

The source builder makes a separate prepared tree and compiles all37-source
identities; raw CHR is bound to parent220 by the existing preparation checks.
Compilation is not a full-roster gameplay pass. The current source also has
ZeldaII platform/body and pickup repairs which were absent from oldV42.
Graphical Parodius fonts still need the MMC3 loader/IRQ implementation.

Reproduce privately:
 python tools/audit/mmc3_current_source_build.py --reference <220.nes> --output <fresh-external-folder> --compact-sophia
 python tools/audit/mmc3_sophia_pad_cpu.py --rom <new-candidate.nes> --baseline <old-bc89.nes> --output <fresh-external-cpu-folder>

Full logs, source and binaries:
C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/mmc3-current220-v42-v3

Before adoption, rebase to the next final MMC5 source, requalify rare/tiny/SMC
and native mapper/stack/cache/OAM/CHR/motion paths, independently replay the
roster, qualify all items and compare actual update/draw cadence. No60Hz claim.

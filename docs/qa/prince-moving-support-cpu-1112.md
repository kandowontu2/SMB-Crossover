# Prince moving-support CPU qualification

Passed bounded run 35733, exit 0, on November 12. This qualifies isolated CPU
support decisions and real interrupt returns. Root owns native controller
routes, Downloads installation and release qualification.

- Parent ROM SHA-256: `464c8f1af0401ba7d5393e331833af5bdd68882c536dfc3c77534b71508213c0`.
- Candidate ROM SHA-256: `6d0346164b7099f8e75cdbe22a9e9f1fd5f4f673116fd1dcb48a3cee620734c2`.
- Checker SHA-256: `329a8ee9c63bbfc80ee22655f2a481aca5f851c4e3c397b60e43ae722fbaed59`.
- Checker: `tools/audit/check_prince_moving_support_1112.py`.

The checker reads the installed parent and existing private candidate. It
verifies complete decoded-stream equality except metadata `$D736..$D73A`,
where `AD16C6D017` becomes five `EA` bytes, and rebuilds the exact candidate
in memory. Runtime and state streams are unchanged. The metadata packet grows
from 5,939 to 5,940 compressed bytes; the other streams remain 6,400 and 1,233.
Both actual cold loaders authenticate their complete headers and loaded
metadata. Cold PPU reads are 31,276 and 31,278 respectively.

The 1,280 paired material cases produce exactly 12 newly accepted combinations:
brick `$51`, brick `$57` and question `$C0`, for moving actions 1/42 in modes
1/255. The other 1,268 results are unchanged, including all idle cases and
existing pipe/coin-brick behavior. The separate action/mode matrix has 2,552
paired cases, with eight moving accepts and 2,544 unchanged decisions; all
256 idle poses retain the original pose-15-only rule.

Both facings pass 126 rejection fixtures for native state, Y position/page,
previous sole and covered cells. An 81-position sweep per facing/material
checks 486 positions. Original nonempty material results pass through unchanged
in 126 of these positions. Where the original provider is empty, new support
requires the actual facing-foot query inside the exact exposed native cell.
Forty-eight full translated D297 decisions preserve the moving actor on the
supported surface; 20 nonsupport decisions remain unchanged. The recorded
right-facing fixture uses native X307/Y112 and actual tile at X320/Y144:
parent source X292/action7 becomes candidate source X315/action1/surface144.
These source X values include the existing eight-pixel native/source offset.

Five scenarios pass 462 actual IRQ and 462 actual FF lag-NMI cuts: moving
brick51 (101 each), mirrored brick57 (103), careful questionC0 (107), covered
brick rejection (97), and jump-action rejection (54). Minimum SP is 189.
The checks retain complete owner RAM, native pointer scratch, SMC, AXYP/SP,
mapper mappings, OAM and CHR latches. They verify the real FF lag branch and
one `NmiSkipped` increment; nested IRQ inside NMI is outside this scope.

Three initial harness expectations were corrected from actual instruction
evidence, without changing game code: BDE2 refreshes the current sole before
testing support, so stale current-sole inputs are canonicalization positives
(12 checks); original nonempty material results bypass the fallback; and the
left-facing foot offset is +2 because `ADC #1` consumes the set carry. Previous
sole mismatches and unsupported geometry still must reject. The optional
`--diagnose` mode retains the sole-refresh trace.

Reproduction, before installation changes the default Downloads parent:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/prince-moving-support-cpu-1112 --max-files 1 --timeout 600 -- python -B tools/audit/check_prince_moving_support_1112.py
```

The runner's shared pre/post storage checks passed. The checker creates no
output root or files, ROMs, captures or backups. Only this new checker and this
note were edited. No existing hard pins, candidate bytes, helper platforms or
user roster files were changed. Natural powerup acquisition, Mesen route
behavior, full-stage progression and installation remain separate evidence.

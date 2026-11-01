# Nightly automatic-patch incident

The installed ROM was `c864e46a8f333ab7a936c8d8f330944041a3eff12bc6dd4d9ba96892144ff3c7`.
Mesen's settings had `AutoLoadPatches: true`. Its most recent entry paired
`Downloads/SMB-Crossover-Latest-WIP-MMC5.nes` with the same-name `.ips`.
That patch was dated October 31 and had SHA-256
`bd3d15622a423f2d85ffdedb9e05471fa824f62df1b371577826809b421d18f7`.
It changed the effective loaded game despite the on-disk ROM matching delivery.

The stale generated IPS was removed. The user reopened the ROM and confirmed
it works. No ROM replacement or engine change was needed for that incident.
The nightly guard now rejects matching IPS/BPS/UPS files; AGENTS.md requires
the check before and after delivery.

The independent cold controller test of the unpatched build reached Karnov
gameplay after Rygar → Select → Start (510 frames, selected 34, mode 1,
task 3). The test now also supports `--installed-path`, preserving symbol
bindings without placing debug files in Downloads. That direct-path automated
run was deferred because the user's Mesen session was playing that file;
the session was left untouched. User confirmation is not relabelled as an
automated test.

A separate actual-Main Kirby sweep subsequently reproduced damage when
holding forward and inhale at close range. It remains an independent engine
issue under repair; removing the stale patch does not establish that every
Kirby collision case passes.

# Conservative CHR capacity receipt

22 October2026. Read-only audit of the immutable `ryu-overlap-hr` cartridges.
The subsequent user decision is **full expanded roster on MMC5; current roster
on MMC3**. This receipt is retained for evidence; do not force new art into MMC3.

## Measured result

| Measurement | MMC3 | MMC5 |
|---|---:|---:|
| Header CHR capacity |256KB|256KB|
| Existing unreferenced physical1KB pages, including alignment padding |2|10|
| Additional full1KB pages freed by the offline proposal |3|3|
| Total proposed free1KB pages |5|13|
| Total free aligned2KB pairs |2|6|
| Unreferenced8×16 pair slots, including free full pages |208|464|
| Pattern bytes in those slots |6,656|14,848|

These last two rows are **fragmented capacity**, not contiguous whole-bank
capacity and not a promise that unextracted new character artwork fits. A pose
must fit completely in one active1KB sprite window. Worst case, with no pattern
reuse at all, the MMC3 holes can hold26 independent poses of six unique pairs
each, or20 of eight pairs. MMC5 can hold66 or52 respectively. A selected new
profile would need its own projectile publication policy; these body holes do
not provide a universal new common-weapon prefix.

MMC3's proposed free pages are164,165,166,167,255. Thus starts164 and166 are
aligned2KB slots;255 alone cannot back a paired register. MMC5 additionally has
247..255, with aligned starts248,250,252,254. Pair start246 is unavailable.

Raw MMC3 byte deduplication gives209 distinct1KB pages among256, but **zero
duplicate aligned2KB pairs**. The47 duplicate halves are largely necessary
neighbors: special weapons retain a native1KB half beside their custom half,
and each MMC3 HUD icon family retains its native adjacent half. Those duplicate
halves cannot be independently discarded under the installed publication scheme.

## What was actually checked

`build/player-guide-agent/chr_reachability.py` reads linked debug segments,
record offsets and compiled bank-table bytes from both HR ROMs. It does not run
the mutating asset builders. It analyzes2,553 installed table entries across
Bill/Lance/Link/Simon, seven expanded profiles, Samus+her separate crouches, and
MegaMan/Bass special body tables. Both facings and aliased/generated entries are
included conservatively. Ordinary MegaMan, native world/menu/enemy graphics,
death banks, direct special/HUD publications and literal viewport/injury banks
remain protected. A shared record used with different bank-local pattern data
is quarantined rather than incorrectly merged.

The best measured proposal uses99 body pages. It retains exact original pattern
bytes, sprite counts/order, position offsets, attributes, flips, palettes and
priority. It rewrites only offline record tile indexes, logical bank selections,
and an offline CHR image. Per mapper, checks passed for:

-33,940 individual original8×16 patterns.
-4,934 complete indexed metasprite renders, including every underlying sprite
 layer even when another sprite covers it.
-The same4,934 renders after filling **all** proved unused slots simultaneously
 with opaque diagnostic patterns.
-15,603 fixed weapon-pattern references after that poisoning pass.
-Every protected page and every live aligned pair remaining byte-identical.

This is a **data relocation feasibility proof**, not a boot, scanline, gameplay,
or hardware compatibility proof. No ROM or main source/asset was written.

## Pairing and ownership constraints

The installed MMC3 mode uses two aligned contiguous2KB background registers and
four independent1KB sprite registers. Special art and HUD physical tables are
direct publications, not logical-map entries; moving the logical map alone
cannot relocate them. MMC3 tile-bank inversion would change the pairing problem
and can require many repeated body/misc pairs; it is not free capacity.

Existing Bill/Lance, Link, Simon, Pit, Rygar, Luigi, Bass, Ryu and live Sophia
body pages contain shared weapon prefixes. The proposal preserves every used
prefix at its old tile index, on every relevant pose page. Death/injury jobs
that lack that prefix are treated separately. A reused raw pose pointer cannot
be independently reindexed for different bank-local artwork. Old literals for
ordinary walk alternatives and injury recovery remain frozen.

The1KB/2KB proposals must be integrated with their accompanying logical map,
bank-table edits and record tile patches together. Do not copy `proposed.chr`
alone into a game. `reachability-poison.chr` is deliberately corrupted diagnostic
data and is never a game asset.

## Reproduction and retained outputs

Run the bundled Python against `build/player-guide-agent/chr_reachability.py
--tries160`. It writes only `build/player-guide-agent/chr-audit/`:

-`summary.json`, per-mapper `report.json` and `bindings.json`.
-`proposed.chr`, `logical-map.json`, `table-bytes.json`, and
 `record-tile-patches.json` describing the reproducible offline candidate.
-`reachability-poison.chr`, the unused-slot stress image.

Pinned MMC3 SHA256:
`9b820cd8aecb31872167f4b87a412c03e4fce2e7c0e4f17a61f34fe87b21a4d5`.
Pinned MMC5 SHA256:
`67905bc8bbdbbcb193e9925f3239bbd18a88949c4f9c6f1820b11f8d3cb3cb85`.

The new MMC5 expansion work supersedes using this limited capacity for the
expanded roster. Preserve this audit and the unchanged MMC3 roster.

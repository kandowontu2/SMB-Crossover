# November 10: startable roster and Level 2 helpers

The installed MMC5 nightly is
`C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes`.
It replaces the previous file directly; no backup was created.

| Identity | SHA-256 |
|---|---|
| Tested / installed ROM | `c10b7d87f466bf028096bddd33b7ac2baee242870ee83ccc4eebd529af57bd7f` |
| Sole Current/Latest IPS | `76c918b4bd1fb51319a28f1e09a19f98ba1b47b063c647616cc23530e059e663` |
| Source composition manifest | `448bf27874fe4f5a1268dc087aaacb635111d25811a4f63b00e17fe8c2480449` |
| Delivery receipt, after publishing | `c3f9a8862506435849b2f0e3874a13c752fd89793cd8cdf649d5ae742b302b70` |

The user explicitly accepted unfinished prototypes for tonight's remaining
characters. **All 100 current distinct named menu entries can confirm a new
game**, with zero locked entries in the exact-ROM CPU inventory. That is a
menu admission result; it does not claim all 100 complete a stage or have
their final original abilities.

## Added access and limits

| Character | Access | Current implementation / remaining work |
|---|---|---|
| Sonic | Highlight Mario; Select ten times | Master System-derived sprite adaptation on native Mario movement, abilities and audio. Original Sonic physics, rolling, rings, hazards and audio remain pending. HUD still says MARIO. |
| Jay McCray | Highlight Mike Jones; Select once | Original sprite core on Mike movement, weapons, health and audio. Original donor moves/audio remain pending. |
| Steve Hermann | Highlight Mike Jones; Select twice | Original sprite core, reduced palette/outer-limb fit, on Mike movement, weapons, health and audio. Original donor moves/audio remain pending. |
| Prince of Persia | Select on Excitebike | Original donor startup, sprites, movement and short opening passed; later Easy landing/contact at X891 still failed. Full 1-1 remains unqualified. |
| Donkey Kong Jr. | Select on Donkey Kong | Original donor startup, sprites, movement and short opening passed; first-pipe lift/jump-detach still failed. Full 1-1 remains unqualified. |

Jay/Steve choices survive ordinary confirmation and their scoped life/respawn
CPU tests. An active level-select cheat clears the prototype choice. A known
Mini preview-header corruption remains when cycling toward Sonic. Comparison
with the preceding Mini nightly showed the same corruption; no claim of a
clean full-menu graphical sweep is made here. Sonic/Jay/Steve gameplay and
menu screenshots were visually reviewed on the final ROM.

## Platform support

Both Level 2 controls now work for Hulk Hogan, Ted DiBiase, Bam Bam Bigelow,
Honky Tonk Man, Randy Savage, Andre the Giant, Fighter, White Mage, Black Mage
and Thief. Mini Mario and Karnov retain them. Up + Select summons the vertical
platform; Down + Select summons an independent horizontal one. One of each
can coexist; a new matching chord replaces only that type. Horizontal starts
right and repeats 112 pixels right / 112 left regardless of player facing.

These reuse native moving girder actors. Stage, initial left edges, centers,
heights, per-character observed births, fixed Mini/DK Jr. helpers and limits
are recorded in [the helper inventory](helper-platform-inventory-1101.md).
Ten opening helper replays verify native carrying, endpoints, held-button
edges and separate replacement. They do not qualify every assisted pit or
full-stage route.

## Exact verification scope

- Frozen source composition: 50 disjoint patch rows over public `d1333adf`;
  all bound source/component hashes checked and both component orders identical.
  Actual interrupt, nested-interrupt and normal-NMI source proofs remain bound.
- CPU menu census: 101 select states, 100 distinct named entries, all 100
  confirmable, no locks; all seven requested/recent identity queries startable.
- **Seventeen final-hash controller-only Mesen tests pass:** four FF helper
  variants, six WWF helper variants, five prototype openings, Mini full
  non-shortcut 1-1 into active 1-2 and Getsu's natural mushroom/flower pickups.
  Tests use controller input with no script RAM writes.
- Mini: **3,494 gameplay updates / 3,494 gameplay frames; zero lag NMIs and
  zero missed updates**, both lives. The additional helper owner gate adds no
  baseline CPU cost for Mini/Mario/Mega Man in its scoped comparisons.
- Actual Downloads launch repeats Sonic's named startup/walk/jump/turn and
  Fighter's complete V/H helper replay. The other fifteen native cases use
  the byte-identical candidate; they were not all repeated from Downloads.
- Nightly patch guard passes before/after installation, with no matching
  auto-loaded patch files. IPS reconstruction equals the tested Downloads
  bytes. GitHub API confirms the sole expected IPS digest in Current/Latest.

## Live local evidence

- `build/complete-roster-native-1110/combined-proof.json` and `candidate.nes`
- `build/complete-roster-native-1110/packets/` (17 bounded cases)
- `build/complete-roster-inventory-1110/inventory.json`
- `build/complete-roster-delivery-1110/verified-delivery.json`
- Component proofs: `build/manual-roster-platform-1110/final-qualified-proof.json`,
  `build/mike-alternate-prototypes-1110/proof-v3.json`,
  `build/sonic-native-prototype-1110/qualified-proof.json`

The composition manifest intentionally remains a source-only receipt with
`native_pending=true`; its bytes were not rewritten after testing. Native
qualification and delivery are the separate hash-bound receipts above.

Build storage after publishing: **3,118,417,408 bytes / 19,951 files**, below
5 GB / 20,000. Workspace inventory is **6,645,696,649 bytes / 55,854 files**,
below 70 GB. Automatic approval review rejected the earlier scoped recursive
cleanup with only “blocked by policy”; it never ran. Old test directories
remain live. Do not bypass that rejection or create more output without
checking the remaining file budget. No videos or capture sequences were made.

The broader goal remains active: original donor abilities/audio, prototype
route failures, full-roster 1-1 and shortcut routes, every powerup and remaining
lag/menu issues still need the later character review.

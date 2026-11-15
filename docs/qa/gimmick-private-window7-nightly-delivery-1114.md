# Mr. Gimmick world sprites — November 14 native qualification

Candidate `cf7b6d2964ae0ef18d08c726f66afe9bf5be3dc6f3ec9c7a43279121ee09d968`
contains exactly192 changes over delivered1daca: two private CHR publisher
operands and190 source sprite-address metadata bytes. All source pixels,
geometry, palettes, physics, levels and unrelated bytes stay exact. This frees
native window1/page16 for the mushroom while Gimmick's same private page818
and pair offsets are addressed through window7. No capacity is added.

Root grant `allocations/gimmick-private-window7-1114.json` and source gates
are recorded in `gimmick-private-window7-1114.md`, source commit `e279fedb`.
The full goal is incomplete; stage clears do not close every natural stock
pickup, ability, sound, visual or performance gate.

## Private native checks

Both runs use the bounded runner with the existing two-file
`build/smb2-flag-native-1113` slot, `--resume --max-files 2 --timeout 600`.
Only that candidate and controller are replaced. Captures remain in memory;
no images, video, state dumps, backups, patches or releases are written.

- Root2054: frozen image Lua `d3bd74075725a490d81c99ba20c216a7d14e2d36035d1c8a21ca4c0d187bcf9a`,
 714physical/622 completedMain,2lives/power0, actual MR GIMMICK menu and
 ordinary charging/movement/head hit. Receipt
 `435e53a70a7d01d485facdce5a4b60a2e239868ceb0f689b67ea4b5384e30314`.
 The two RAM PNGs are2824B and3066B, SHA256
 `6999d64224a9e2fa2c863803092d60ae1f13bbceb9b94c9638d39b05c55cef60`
 and `638091d61dcbf68f91951602cf9f25d10ccd677bc1fb5c6f61e1284801f3ddd8`.
 Root viewed both: first Goomba is unchanged; the formerly corrupt flame-like
 mushroom is now the normal red/cream mushroom. Gimmick's body and charging
 stars remain visible with unchanged art. Hardware MMC5 mode3,16px sprites,
 actual banks `[816,16,17,18,19,20,21,818]` in both observations. Root compared
 all11 actual captured pattern pairs against the exact candidate bytes:
 all match across native pages16/17 and private816/818. No native acceptance
 is inferred solely from the source peripheral model.
- Root10746: frozen stage Lua `84834664a8399bb5debcff2fde65912e0d6fc5fb06ed6e6223bc84786d81b3e9`,
 full non-shortcut1-1/flag/castle/entrance and25 living grounded1-2 updates
 PASS8959physical/7402 completedMain. Terminal40/Y176/high1/native0/engine8,
 HP2/max2/lives2/power0/Star0. Receipt
 `61531263c41804c81145812b72b2b0b0c7ad7db2a4d78bf664afb556ed3ab122`.
 Source physics, ordinary controls and full-stage assertions are the exact
 previously qualified route body; only ROM provenance/bank hashes are rebound.

The installed1daca bytes and sidecar guards were checked unchanged before
and after both private runs. The new delivery installer pins these exact
controllers, receipts and PNG hashes. Actual Downloads verification follows;
this section alone is not a delivery claim.

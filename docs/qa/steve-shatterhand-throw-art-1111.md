# Steve original lift and throw artwork

The source pack now includes all 12 lift, throw and recovery poses in both
facings. This is an in-memory allocation proof, not a playable ROM update.
The installed nightly remains SHA-256
`235de3ed2487cd3f93c695e1eb2ceec55c172cede3cb6d98c5309afbc7cfbe38`.

`tools/audit/check_steve_shatterhand_throw_art_1111.py` recovers the exact
Laserbot parent in memory using the existing authenticated inverse, then
extends the qualified lift art pack. The new recovery poses are donor
`$00AE` and `$00B2`. The original ten poses use CHR339 and four existing
CHR711 cells. Recovery uses eight cells in CHR307, selected through sprite
slot zero. Slot five remains unchanged for companions and projectiles.

The full set has 41 source cell addresses but 38 distinct cell images.
Three pairs are identical across donor pages 72 and 75. Even with these
duplicates removed and the four CHR711 aliases retained, 34 new cells would
exceed one 32-cell page. A second page avoids dropping recovery artwork.

The extra allocation changes Roll's pool-four slot-seven blank page from
CHR307 to its byte-identical CHR304 mirror. The finite publisher ledger,
compiled mapper readers and native mapping copies are checked before any
edit. Roll's pool-five alias remains the previously qualified CHR339 to
CHR304 change. Both allocations are verified together.

The bounded run passed with no output files.

- Fixture SHA-256 `ffed8206532acd831b6470b74157e1e6a9bbe720154e6733055f20990e3fe8c0`
- 110 source cell comparisons, including tile bytes, attributes and offsets
- 24 compiled Roll publisher cases and 72 exact page comparisons
- 60 matching Roll OAM frames and matching stage outcomes

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-lift-art-layout-1111 --resume --max-files 1 --timeout 180 -- python -B tools/audit/check_steve_shatterhand_throw_art_1111.py
```

Still required before delivery: bind pose selection and CHR publication to
the live lift states, preserve the native player OAM reservation and PRG
owner, implement the original throw lifecycle, and verify actual rendered
frames in Mesen. The existing nightly and release IPS were not replaced.

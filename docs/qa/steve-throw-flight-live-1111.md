# Steve robot flight and reclaimed storage

Private in-memory candidate:
`bc7d0ff551d91bc41e339c575442a911b5395026be91b3486b2066ad6a6c65eb`.
It is not installed in Downloads or published as an IPS. The installed build
remains `80e6aa3e32574f38b23fa6da6ab3c94bbe7b5ae11b29339b32b11a624fe6f1ed`.

## Storage ownership

`check_steve_shatterhand_throw_raw3_1111.py` audits raw3 `$AB00–$AEFF`, a 1 KiB
copy of the live `$BB00–$BEFF` bytes. Its original content is CHR232's final
256 bytes followed by CHR234's first 768 bytes; SHA256 is
`6e87cdb9fe18847462832848f09097ef65c32da2f13daad372a2e2948e11b51d`.
The static scan classified all 32 candidate direct/indexed references as
instruction overlaps or the known LaserTiles/lift-animation data. This is
source and tested-route evidence, not a universal claim about arbitrary code.

The helper observed zero bank-tagged reads or writes to that range across
8,801 authenticated updates: Steve Alpha/lift 2,551, Steve Laserbot 2,512, and
Jay's earned 1-2 machinegun route 3,738. The duplicates stayed byte-identical.
The combined run timed out during Jay, so Jay was rerun separately to completion.
The persisted audit exposes `static`, `steve`, and `jay` modes.

`check_steve_shatterhand_roll_blank_1111.py` and the matching `.s` replace the
108-byte Roll publisher envelope at PRG79 `$B03D–$B0A8` with 90 bytes of shared
publication code. Blank CHR304/306 requests now select the identical native
blank CHR21, including slot 7 for the empty pools. Other pools and nonblank
publications keep their images. The caller's registers, flags, stack and bank
maps remain equal. Root independently reran all 24 publisher cases and 60 real
Roll opening frames, with the retired pages poisoned. All passed.

The carrier now loads the new CHR304 row at raw3 `$AB00`. Its scatter copier
ends with a jump to seven bytes at `$C4F4`, which tail-call the existing verified
row loader. This keeps the cold bootstrap at 132 bytes. The copier grows from
36 to 37 bytes, moving the recovery CHR helper to `$DA72`. The existing punch
suffix `$DA80–DBFF` stays intact.

## Live dispatcher

`steve_shatterhand_throw_flight_live_1111.s` packs the native camera X into the
original Q4 coordinates and calls the source-derived throw core for admitted
surviving actors. It retains a signed frame marker throughout the reattach
update, clears surviving contact bits, and keeps the ordinary orbit and weapon
emitters out of thrown updates. The two emitter checks call the nine-byte gate
at `$D777`.

The unpaused companion prelude clears the previous frame marker. Accepted new
token grants and scene retirement clear the private throw state, while keeping
the companion's identity and health. Reset preserves X. Token handling wraps
the existing token tick; it does not patch its staged duplicate code.

The small detached leaf comparison exercised 12 actor/facing/camera combinations
on cold-loaded code. Explicitly injected surviving contact receipts returned
in 4 or 31 updates, with no body on the reattach update and no ordinary emitter
admission. That fixture was not evidence of native enemy collision. Its first
run retained the deliberately poisoned upgrade-state byte from the cold model;
the fixture now explicitly establishes the ordinary, non-upgraded state.

## Current candidate verification

These completed through the bounded runner with no files or captures:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-throw-flight-live-1111 --max-files 1 --timeout 300 -- python -B tools/audit/check_steve_throw_controls_live_1111.py --flight
python -B tools/audit/run_bounded_build_v1.py --output build/steve-throw-flight-storage-1111 --max-files 1 --timeout 180 -- python -B tools/audit/check_steve_throw_controls_live_1111.py --flight --cold-only
```

Cold verification passed 78 NMI cuts and 11 readback faults, including both ends
of the new raw3 region. It checked 701 declared resident edit bytes, 23 cleared
state bytes, 224 scatter bytes and the unchanged 384-byte punch suffix. The
actual Steve → Prince → Steve sequence overwrote and restored the 1 KiB raw3
row as well as the scatter region. The new row adds 2,050 PPU reads beyond the
previous throw carrier: 4,100 extra reads over the installed build in total,
and 32,800 reads for the return load in the ownership test.

The game-model test naturally earned Alpha, then cloned that route for both
facings in each lift state 5/6/7. All six cases used controller input to launch,
preserved both lives, and completed the original recovery and full throw cycle.
The observed hidden-frame counts were 254, 255, 255, 255, 254 and 254. Every
case had exactly one zero-body reattach update, followed by a cleared frame
marker. No normal weapon emitter ran during a thrown update, and no robot body
renderer ran with its throw pose zero. The 102 player-recovery DMA checks still
passed, including physical CHR339 → CHR307 → CHR220 publication.

These are CPU/PPU model checks, not independent Mesen validation. The live
natural return tests cover Alpha; Laserbot's actual throw caller is patched but
still needs a live throw test. Native enemy contact/two-HP damage, incoming
robot damage and destruction, audio, hot-code interrupt checks, and a complete
Mesen route remain pending. No helper-platform changes were made.

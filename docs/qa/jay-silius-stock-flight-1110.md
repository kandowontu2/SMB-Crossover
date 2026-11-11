# Jay McCray stock bullet flight

The installed CPU test parent was
`3d327d47b8127c1e76d9868191d34b8ebb1ca9ec29d6bb609ccab9c60c6cb3d8`.
The source recipe reconstructs the installed bytes and preserves all 2,810
Sonic edits and 248 later DK Jr. edits. The in-memory Jay image is
`05930ebb755329be4bf905b4dcd51e3040a7d91270cdf88664c6b095c412be49`.
Its cookie is `a7102005e5f23a6373377265acab8d88`.

## Donor motion

The original stock row in Journey to Silius PRG6 `$8865` enters the
no-gravity update `$E1AA` with probe index 2. The original `$D097`
one-point record samples the current X before the next X commits. The
signed velocity is four pixels per update. A solid probe stops X, clears
velocity, and retires the shot. The original `$CD88` projection also
retires offscreen rounds. Near X edges still project Y before retirement.

The real donor opening trace executed 170 stock updates and observed four
live donor hits through `$E747`. A separate paired test executed the real
donor `$C49E` loop and the relocated host flight for 156 full 16-byte
records. The 104 moving cases used the actual host D002 class at the
donor's D002 boundary. Both CPUs produced the same query coordinates and
record bytes. The host adapter returned 52 clear and 52 blocking results,
including its fail-closed response beyond the valid Y range.

The naturally selected Jay CPU path ran 60 ordinary 1-1 Main updates.
One new B press creates its first projected shot at X56/Y191 on update 4.
The shot advances four pixels every update through X252/Y191 on update
53, then expires on update 54. Held B creates no second shot. There are
zero Mike shots and both lives remain. This witness uses the authentic
cold loader and no post-cold state writes.

## Carrier

Physical CHR218 was the exact native page 2 duplicate. Its SHA-256 was
`efccdef7770977105d4a8cad48965ebeb8eeda25d27a37e4624795601373e5ba`.
The audit rebinds 88 inherited selector domains, 49 table preimages, and
the current Zelda and Final Fantasy exceptions. The native MMC5 map
excludes page 218. The compiled roster weapon reader maps its even 218
table entry to physical 219. The installed Sonic and DK Jr. source deltas
use other CHR pages, and their bytes remain exact.

The native scatter descriptor is `03 01 01 DA 00 4B 01 4C 01`.
The worker loads and reads back page 218 to A3 `$A000`, then pages 331
and 332 to C2 `$D000` and `$D400`. The 56-byte prefix copies and reads
back the 583-byte stock service payload into A3 `$B000`. It then enters
the existing two-page decoder at C2 `$D000`. The movement stream uses
2,041 bytes and calls flight at the actual position-publish site.
The remaining ROM changes are in the existing Jay resident
envelopes. CHR216 keeps its existing art in this flight-only image.

This image verifies projectile flight. Native enemy impact, visible
stock art and native drawing, alternate weapons, host audio and complete
1-1 traversal are outside this image's qualification. No emulator, ROM
file, capture, or generated build artifact was created.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/jay-silius-stock-flight-1110 --max-files 1 --timeout 600 -- python -B tools/audit/check_jay_silius_stock_flight_1110.py
```

- Flight source SHA-256 `35fd6d9cdba26c1af7cd6b4044b1f43047fd2fbe79b422a9278df854ab9cf479`.
- Checker SHA-256 `89b4e10966346e57a71fbf1bc4e0c4d57451d2b2b5c219457eb2d775526a9e3b`.

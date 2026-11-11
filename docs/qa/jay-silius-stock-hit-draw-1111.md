# Jay McCray stock bullet impact and sprite

The installed parent is `3d327d47b8127c1e76d9868191d34b8ebb1ca9ec29d6bb609ccab9c60c6cb3d8`.
The [stock flight source image](jay-silius-stock-flight-1110.md) is
`05930ebb755329be4bf905b4dcd51e3040a7d91270cdf88664c6b095c412be49`.
Its impact and sprite derivative is
`20bd447db2cb77d0724ec5ae329de422341833bc288cd9453e480926b63d62fa`.
The full cookie is `a710200642a4a5c71fc3321e37fa0847`.

## Donor and host impact

The original donor controller moves right and fires every eight updates.
The original enemy row 9 reaches `$E747` with 20-pixel strict bounds on
both axes. Three actual hits reach `$E780` at updates 44, 50 and 55, in
slots `$F0`, `$E0` and `$D0`. The enemy has 3, 2 and 1 HP before the
respective hits. The donor clears each stock projectile and sets the
enemy hurt timer to 48 and source sound request `$1D`.

The host adapter uses those bounds on the center of a live native Goomba.
The real `$9AF5` `ShellOrBlockDefeat` performs the native defeat, score
and sound queue update. The shot is consumed and source sound `$1D` is
recorded. The source keeps the host object cursor across the defeat.

An unchanged origin-camera 1-1 controller produced three shots and zero
hits over 60 ordinary Main updates. The directed fixture forks the actual
post-fire state at update 4. It calls the real `ProcessEnemyData` on the
unchanged first authored Goomba record `6B 06`, temporarily setting the
parser's right boundary. The parser creates slot 4 at X96/Y184. The
fixture restores the parser fields before continuing ordinary Main.
At update 11 the live stock shot at X84/Y191 contacts the Goomba at
X93/Y184. Native defeat sets state `$22` and score control 1, the original
shot slot becomes inactive, and Jay retains both lives. This verifies
the actual impact path with a directed native actor birth.

## Sprite and storage

The original row `$17` points to PRG2 `$83DA`, with one 8×16 cell at
offset −4/−8 and palette 0. The original donor emits OAM `A7 6C 00 6C`
in its opening shot. Both exact original CHR tiles `$6C/$6D` are placed
at Jay body page 216 tiles `$28/$29`, within its previously qualified
blank tail. Their SHA-256 is
`1ead741ca86f517fcb0adb217a3656390613e5b821f20f2bfee52a7852303021`.

The proposed drawer executes the real `MetaspriteRenderLoop` on a clone
captured during the normal Jay draw ingress with a live projectile. Six
isolated cases verify both facings, rotation, exact OAM cursor advance
and preservation of every other cell. Two full-capacity cases decline
without a sprite write. A production draw ingress still needs resident
dispatch funding and separate in-game verification.

The new worker is 229 bytes. The verified A3 payload is now 812 bytes
under the 928-byte CHR218 limit. The only derivative changes are CHR218,
the two Jay cookie instances and the 32-byte CHR216 sprite pair. The
source checks wrote no ROM, build file or capture and ran no Mesen.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/jay-silius-stock-hit-draw-1111 --max-files 1 --timeout 600 -- python -B tools/audit/check_jay_silius_stock_hit_draw_1111.py
```

- Source SHA-256 `58c03255ae818904de791dfbd2894c4d8d76076680383e02a6715cfdc21a22ef`.
- Checker SHA-256 `d3ec1e7b41d53312bfab8eb1148c2d0a07b0203a91752c382d496186f0919cd8`.

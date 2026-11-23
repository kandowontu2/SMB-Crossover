# Getsu head and powerup repairs

Delivered ROM: `c6ab56107cf78954ff24f0fddbd40a0207afd4e7743eaeb8c762a53329d30f1b`.
Current/Latest sole IPS: `0c430162a081a5173e5821060226d68e73c61921975dde6e552f977dd65bbc06`.

The earlier095c build had two distinct missing callbacks. The head service was
declared empty and its fast path returned the selected-character value as though
it were a tile. The upgrade service was also empty, so a genuine pickup started
the global freeze without advancing or completing it.

The repair restores the native head getter and the existing generic upgrade
update. Factoring Getsu's own standing/gait renderer releases20 bytes for a
19-byte farcall wrapper. The loaded colors entry and authenticated header follow
the changed layout. No new carrier or RAM allocation is used.

The native controller selects Getsu through the real menu, defeats the opening
Goomba, activates and collects the first mushroom, then activates and collects
the second Fire Flower. Both transformations complete at age60. After reaching
status2, Getsu moves16 further world pixels. Both lives remain. The exact installed
Downloads ROM repeats the pickup test. A separate unchanged controller clears1-1
into active1-2 with both lives.

CPU checks cover1120 donor gait cases, original sprite/palette output and eight
real draw interrupt cuts. The restored public head entry preserves516 foreign
AXYP/SP/SMC/mapper entry states before the unchanged canonical gateway.

Evidence:

- `build/getsu-callback-delivery-1110/verified-delivery.json`
- `build/getsu-callback-final-native-1110/{powerup,route}/capture/result.json`
- `build/getsu-head-callback-1110/proof.json`
- `build/getsu-powerup-callback-1110/proof.json`
- `build/getsu-head-foreign-1110/proof.json`

The genuine head query adds cost compared with its old no-op. The final route
records1567 missed reads over2913 active frames. Combat optimization, complete
donor progression and the broader roster audit remain open.

## November 23 natural hidden 1-UP

On Downloads `06336f15`, Mesen selected Getsu Fuma through Simon's
fourth alternate and started Easy 1-1. Getsu earned the first Mushroom
and hit the hidden block at X1024. He caught its moving 1-UP at
X1049/Y135. The native cue played and the delayed award brought his
life count to three. He landed at X1039/Y176 with his Mushroom and
three lives after 25 more movement updates. The run took 1,582 video
frames and saved no captures.

Mesen receipt `eeec8c52bc29bfe3741c671d88a99aa9d422e1b368383b52ab94f504deaf49f8`.
Controller SHA-256 `f2403163a515956b128268dd5d1563653caf5d2270f8973c429993fb65971993`.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 330 -- python -B tools/audit/run_getsu_stock_1123.py --route life --run
```

## November 23 natural Star

On the same Downloads build, Getsu jumped past the Koopa, returned to
X1621 and hit the Star brick at X1616 from below. He caught the moving
Star at X1664/Y97. Invincibility started, the game queued the Star
music and he earned 1,000 points. He reached the ground at X1695/Y176
with the Star still active, his Mushroom and both lives after 25 more
movement updates. The run took 2,443 video frames and saved no captures.

Mesen receipt `81375a3b06eb380eb48cdf243114b6d45134ec0017104b61c404029b09f2281d`.
Controller SHA-256 `e6d254a89cad008b01c1ddec31160b2911a7ab99169c4c6076cfe66448e7d47e`.

The Mushroom and Fire Flower passed on `c6ab5610`. These two new runs
complete Getsu's four standard pickup checks.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 330 -- python -B tools/audit/run_getsu_stock_1123.py --route star --run
```

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

# Toad's four natural pickups on the current nightly

All runs launch the unchanged actual Downloads ROM
`91dc4ac58ae749bc81f1ef91953c7c3e5aba73dd07e4b6ea2cd3059d1cdb41cc`.
Real title/Mario slot0/Select2/Start selects raw0/variant5/CHR131, Easy,
cheats0. The actual BmNativeMovement B938/bank62/SP230 first64 bytes and
completed returns are observed. No gameplay seed, ROM change, image or new
output file is used. All pre/post patch guards are clear; the shared candidate
and Downloads bytes remain identical. No backup, patch or release is created.

| Pickup episode | Native run | Receipt SHA256 | Main / Bm returns / physical |
|---|---|---|---|
| Mushroom |85032 PASS|`8d18bd7528b9148fbdf1104a7d5328ccfcfbb47a7a3c1ef824e3ac4a2f93f5e9`|926 /615 /938|
| M then Fire Flower |35385 PASS|`06d785a6d330ef5cc418b53761d0f8e19505804468e1eb6b451b972e3d8fb006`|1729 /1358 /1756|
| M then hidden1UP |24797 PASS|`a716846ae15d3e51d1fcdca9b1101f4874bde2f7f67e46950e6df0aa50a1ce47`|1504 /1193 /1519|
| M, legitimate shrink, then Star |76000 PASS|`957229652e09b46ec76cc6d6c5083d26f82d112509bf3acb3502922b91d62981`|1836 /1465 /1849|

Each stock replay first independently completes the genuine M/60-growth-tick/
1000-point/25-return prefix. Detailed M chronology remains in
[Mushroom report](smb1-toad-mushroom-native-root-1116.md).

Fire Flower: factoryd18e2f63/Luaa77c07b6. Genuine birth Main1473 at1248/136,
maturity1540 at1248/119. Ordinary supported right runway reaches actual native
speed class36, then fresh Left+A+B jumps onto the row. Real9B28/SP243 collector
Main1643 sees player1258/97 versus item1248/119, positive3x2 contact. Erase,
popup6/cue20, actual DEC897C→83D6 gives1100→2100 atMain1648; all60 upgrade
ticks finish at1703/016E/SP232. Then25 completed Bm returns finish at
Main82BE/SP252,1250/112/lives2/tier2, no pending witness. Earlier fixed mounting
and enemy-contact input negatives remain source-versioned, not game defects.

Hidden1UP: factory1acaa08a/Lua0ed162ab. Actual hidden raw60 block creates
kind3 at1024/120, Main1375; maturity1440 at1024/103. Collector9B28/SP243 at
Main1473 sees1055/176 versus1058/165, positive10x3 contact. Erase/popup11 and
the real delayed INC8987→898F atMain1478 give lives2→3/cue64. Then25 completed
Bm returns finish atMain82BE/SP252,1084/176/lives3/tier1. Source counts and its
1082 endpoint are separate.

Star: factoryf8dd1da4/Lua9b5f86fc is explicitly a damage-recovery route. Actual
BD4A/SP230 injury atMain1710, player1620/176 against enemyID0 at1632/184, naturally
shrinks tier1→0 without losing a life. The earlier powered-Star route negative
ef523d7e remains a negative; this pass does not claim retaining M throughout.
The genuine Star is born Main1622 at1616/136 and matures1688 at1616/119.
Collector9B28/SP243 atMain1805 sees1668/123 versus1674/124, positive6x3.
Actual AF88/SP219 takes the C0 native effect branch; AF8D writes timer35 with
C0 and music64 follows. Erase/popup6/cue20 and real delayed credit1420→2420 at
Main1810 precede25 returned Bm updates atMain82BE/SP252. Endpoint1682/176,
lives2/power0/Star34, no pending witness.

These close natural acquisition and resumed play for M/F/S/L on91dc. They do
not recertify the separate421 full-stage pass, Star expiry/protected hits,
complete abilities, artwork, audible SFX/music or performance. Queue writes
prove the code request, not how the sound is heard. Source receipts/counts and
all earlier observer/control negatives remain in
[source report](smb1-toad-natural-stock-91dc-source-1116.md).

# GB Pit: native stock pickup checks

The tested Downloads ROM is
`98261effbc214d24a00b2f8bd2950eca8ea3bf3675b331956a2ad42a7ab819e6`.
The independent source Mushroom and Flower passes are recorded in the
helper's GB Pit stock notes; they do not close native Mesen qualification.

## Ground-route control negative, actual Downloads23405

Receipt `1e6ed2d705a6d471c2c2aa8a53622f76415d28c2c5f482348a7c5436c8188f43`
returns false after 1401 balanced Main calls, 1129 balanced PitMovement and
PitFlight calls and 1527 physical frames. Factory39fc5b09 / Lua5230e253
is the frozen source-qualified Mushroom controller. The ROM is unchanged.

The cap exit begins at Main651, world416/34. The attempted left descent
stops at world308/112 with camera307 and relative X1. The source run could
reach305 and fall to176; this native run remains supported by the block
row at320. The terminal condition is still308/112, alive with both lives.
There is no head hit, item birth or pickup. The assertion retained is
`One bounded grounded firstM route`.

This is an input-route negative, not evidence that the item or Pit's
collision code is broken. The successor must leave the row at its actual
right edge, reach genuine ground176, then return beneath it for a fresh
upward jump. Preserve this frozen result and all original item maturity,
physical pickup, score, sixty upgrade ticks and twenty-five returned-worker
requirements. No game state seeds, game patches, helper changes, images or
capture files were used. Native Mushroom/Flower remained open after this
negative; the separate successor below now closes those two gates.

## Genuine Mushroom and Flower: actual Downloads25403

The owning ROM is the verified cb95 nightly. Factory6335c079 replaces only
the old Mushroom input fragment with the clear-right route; the original
head, birth, maturity, physical collector, score, growth and worker-return
assertions remain exact. Actual native row320..400 clears at416. Pit lands
there at416/176, Main718, camera307/relativeX109, with both feet on ground54.
He then returns beneath the block to331/176 and makes a fresh jump.

Both actual Downloads cases pass, exit0, without changing any ROM bytes:

|Case|Native receipt SHA256|Main / workers / physical frames|Endpoint|
|---|---|---|---|
|Mushroom|b12c4a7487f4d4715f3de03ee44431789e78f748b279a0760c7b7280e2bb3284|1026 / 694 / 1207|409/176, tier1, life2, fuel60|
|Mushroom then Flower|ea21d29882da333072eb9199bd2588fd215bba07c1e18fcfbec7689ee19d304f|1849 / 1457 / 2401|1254/112, tier2, life2, fuel60|

Mushroom: real native head9EF5/SP230 at Main799 nests Setup8F34/SP221;
birth800, maturity864, collector940 with positive10×2 overlap, C1, erase
and cue32. Real score writer945 changes120→1120. All60 hosted upgrade
ticks finish before25 new movement/flight workers and a completed Main
return82BE/SP252. The old left-exit negative is retained above.

Flower: the exact Mushroom prefix remains present. Native head1669 at
1242/149 nests Setup; birth1670, maturity1736, collector1763 with positive
8×1 overlap, C1, erase and cue32. Score writer1768 changes1320→2320;
all60 upgrade ticks and25 new movement/flight workers finish at an actual
Main return82D0/SP252. Every Main, ExpandedMovement and PitFlight call
balances in both cases. Lua pins are72630250 and4a4bd1e5 respectively.

No helper, gameplay seed, image, capture file or new nightly was needed.
This qualifies natural M/F acquisition and recovery, not complete powered
abilities, Star/1UP, art, audible sound or performance. Earlier full-stage
receipts retain their recorded ROM versions.

## Hidden1UP: actual Downloads65170

The separate strict-cb95 factory98556fad / Lua32b203fe passes, exit0,
receipt `59057e8273b406d894cfeb3bcb742913722d7c8eabe14e89ac7e13db6addbd84`.
There are1554 balanced Main calls,1222 balanced movement/flight workers
and1979 physical frames. The same genuine Mushroom prefix is retained.

This hidden60 is triggered by an ordinary kind27 arrow, not Pit's body.
At Main1422, MmBlockAttack is1 and PRG8:A4FC calls9EF5, returningA4FF/SP200.
The arrow is1021/131; temporary collision-query coordinates are1024/128.
The saved/restored player and first completed Main are940/92. Those query
coordinates are not misreported as a player displacement or bodily hit.

Real birth1423 reaches full maturity1488. Ground-only pursuit collects the
moving1UP at Main1523, hero1047/176 versus item1060/171, positive1×9 overlap,
C1, erase and popup11. Actual native INC8987→898F at1528 changes lives2→3
and requests cue64. Twenty-five new completed movement/flight workers
follow at actual Main return82BE/SP252. Final1047/176 retains tier1/fuel60
and all three lives. No helper, game patch, state seed or capture is used.
The earlier source interception/jump-chase negatives remain versioned in
the owning source QA. Star acquisition remains open at this checkpoint.

## Star: actual Downloads35493, completed before the pause

Native cb95 passes, exit0, receipt
`76fb3813f0ad1fbb04439199eea002d4371273223b658f8986a135196f54e7e8`.
Factoryd685aa27/Lua98e78a40 uses ordinary bow combat and actual-X neutral
alignment after the frozen real Mushroom prefix. There are2321 balanced
Main calls,1989 balanced movement/flight workers and3148 physical frames.

This is a bodily hit: Main2057,1609/149, MmBlockAttack0, native head9EF5/
SP230 nests Setup8F34/SP221. Birth2058 reaches full maturity2124. Physical
collection2290 at hero1777/120 versus Star1783/143 has positive9×1 overlap;
the actual AF88 branch carries clear, then AF8D writes35. Erase, cue32 and
music64 occur. Real score writer2295 changes1625→2625. Twenty-five new
completed movement/flight workers finish at Main82D0/SP252,1777/176,
tier1/life2/fuel60/Star34. The terminal score2725 includes another100 points
that this pickup check does not independently attribute.

All M/F/L/S natural pickup scopes now pass on cb95. This does not promote
the older full-stage run or close all abilities, expiry/protected hits,
graphics, audible sound or idle/walk performance. No game patch, helper,
inventory seed or capture file was added. Gameplay work is now user-paused.

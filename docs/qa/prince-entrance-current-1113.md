# Prince movement and entrance delivery, November 13

Downloads now contains tested7ef, retaining the prior Karnov Ladder and adding
the Prince movement/entrance fixes. The explicit visual limitation below
remains. This is not a full-roster or complete visual-review claim.

Root's separate pure recipe is
`tools/audit/compose_prince_entrance_current_1113.py`. It explicitly recovers
exact62 from public526, builds frozen cache209, and authenticates the frozen
309 entry repair. The existing Karnov-on-cache composite C5 receives only the
41 changed native-entry bytes, inside two complete52-byte envelopes whose
preimages match. All three Prince streams and its cookie stay exact209; every
Karnov source/feature byte stays exactC5. The inverse returns public526 exactly.
The bounded metadata/inverse check99434 passed with zero output files.

| Image | SHA256 |
| --- | --- |
| Public parent526 |`526ef1df172c3172fccbd35aa0471a9ff9a5a256a416acba8f7530d147a5b3f2`|
| Frozen cache209 |`209abc2fd6144d59720e54352ed6f9f7384e2fa9ede0fbb1fb37f9e02d385008`|
| Frozen entry309 |`309bbdae23b2dbe76951d3320c5afcb895e25b0fd081a558e93241b12f96389c`|
| Prior Karnov/cache C5 |`c5afaa7b9693655e283a8bdd6a21fc78041d91c4c6bc9f5c91943a045eb42359`|
| New private composite7ef |`7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc`|

The conditional source-owned native allocation is documented separately in
`allocations/prince-entrance-player-1113.json`. It requires a complete caller
closure for the retired Mega Man legacy branch, all non-MM dispatcher ABI,
native header/exclusion/interrupt tests, and physical verification before
delivery. It grants no new RAM, CHR or neighboring native code space.

## Root Mesen baseline on public526

`check_player_profile_native_1113.py` uses real D-pad/Select/Start, then24 Main
updates walking, a released/fresh A jump, a complete landing, and24 updates
of standing B input. It never writes emulated state or files from Lua. These
are short movement regressions, not complete stage, weapon-hit, graphics or
audio coverage.

| Character | Physical frames / Main | Walk X | Jump apex Y | Terminal X/Y | Native old-profile calls |
| --- | --- | --- | ---: | --- | ---: |
|Mega Man|504 /110|40→61|111|65/176|0|
|Luigi|395 /108|40→56|103|122/176|0|

Both retain both lives and finish grounded. Mega Man's baseline controller is
`630ac2f9f991812c519fb05b230d23d2773c1ed17020d96209616e9e18fe884e`,
receipt `301037a4a14689188936eced6328d1574454399d62c46b6651c1fd0e779e07ec`.
Luigi's is
`18fcaaa7575aafd7b10f992989fe4b5a52608a106c8419826cd4079b3281b911`,
receipt `4fbc37e5cdc3691876c56110888cd4d2df30d68a317737e31c8db0c3bd228f4a`.
No screenshots or capture files were produced. These samples support the
comparison; they do not replace the static and compiled caller closure.

## Actual native verification

Initial metadata4274 reproduced all five controller texts, including frozen
entry3db and combat848. Actual execution then exposed the combat ROM guard
described below; current combat79263 binds that identity explicitly. Mega
Man/Luigi use the exact baseline scripts above. Karnov's binder replaces only
the old ROM identity in the qualified001874 controller; its new script SHA is
`e0265938b429e5878f4c48bd39edd777143b42bb3f0201bb6f6c372dc344dfa1`.

All five physical cases now pass on exact7ef:

| Case | Frames | Controller SHA256 | Native receipt SHA256 |
| --- | ---: | --- | --- |
|1-1 and safe1-2 landing|16465|`3dbbf79a4881fc9f6bf5c320b692c686231832a17c2899297af5df294000eedb`|`98e6cd908d9ecf3713cb2bd364440e58854abf3febd85912f07a29529ff06b09`|
|Earned sword combat|7849|`79263decae00c6effeba0c2ee12b7373ee0048b0960349d20e38107012abb153`|`d2e72c6f3aee69b25e020b50abba42ae5772b3144aba255e46fc28801b3c7ea8`|
|Mega Man motion|504|`630ac2f9f991812c519fb05b230d23d2773c1ed17020d96209616e9e18fe884e`|`961fe6377540bb296f2e4f14869f8294a55c2bd4c2e0c85e05cd99fd140df3a5`|
|Luigi motion|395|`18fcaaa7575aafd7b10f992989fe4b5a52608a106c8419826cd4079b3281b911`|`cbf909a0f01353386ff8bfce391203df72331caeb3bb0cfd170efcc51318b284`|
|Karnov full stage and four upgrades|12915|`e0265938b429e5878f4c48bd39edd777143b42bb3f0201bb6f6c372dc344dfa1`|`2d748ed34b757a348c015b1568e2274dd575d554c8161b2057f679edd4dde03d`|

The entrance case reaches the actual flag/castle, then begins engine8 already
at1-2 X40/Y176, HP5, both lives. Another120 physical neutral frames retain
full health and native floor support. Normal original fall damage remains;
there is no fall-counter or HP patch. No helper platform was added.

The sword case collects the authored mushroom and flower, draws the sword,
parries, attacks and defeats a real native Goomba (state34, popup1). Its
original guard-loss and native defeat occur at commit3499; the controller
asserts the intervening proxy/call chain at that instant. Its final proxy
field is overwritten by a later follow-up export at3502, so that final field
alone must not be described as the original causal event. HP4/lives2 and
Star0 remain after12 further updates.

The first combat attempt did not enter gameplay: the exact frozen848 script
has a top-level `rom==209` guard. Root initially missed that guard when
running it on7ef, causing no receipt and a180s testRunner timeout. The new
binder changes only that one authenticated ROM identity; the frozen848
factory and all input decisions remain unchanged. Corrected79263 passes.
This was a replay-binding error, not evidence of a game hardlock.

Mega Man and Luigi match their baseline motion endpoints, apexes, frame counts
and zero old-profile calls. Karnov matches the entire prior12915-frame
sequence, including four authored pickups, Boots, Bomb and the same three
existing manual platforms. No new helper locations or policies exist.

Independent source-model menu receipt
`c3e2d01241d330c1f7ed438be958091d7e8bb72bf4ec8ba3ec33015658dd0f3e`
compares all101 rows and202 images/350404 RGBA bytes exactly; row digest is
the supplied `f58ec905102307ca87d9c302248fa7da9c44cd5550df154323e67024da245db7`.

## Explicit visual limitation

Three actual spot PNGs first confirmed that Prince is hidden during the
extended, noninteractive engine7 drop (sourcePose0/no player OAM). An early
grounded phase4 sample has player shadow OAM but black body-region pixels;
this alone does not establish a DMA, CHR or palette failure.

A separate four-PNG observation, controller
`2b640f7c619b1eb383b2950f6f92d2c7e5ffd3fdd5c661a9ea3e0603786a425f`,
receipt `4e11add0aaedc5bc190d76f7aaf2abc05178991a068750c68f7cb57c78d96230`,
shows the correct visible Prince body at grounded phase30. Spritepalette0
contains27/16/20 throughout. All six sampled color calls successfully append
their body packet: queue0→4 after backdrop, then10 after body publication.
The proposed lost-palette hypothesis is refuted; no speculative color retry
or actor/pose prime was added. PPU-debug pattern reads have the usual MMC5
sprite/background-view caveat and are not physical-CHR proof by themselves.

The original public62 trace directly witnesses fall frame106/action7 at
nativeY96 and160, projectiondelta5; a faithful future intro render would
reuse that art. Current source-owned free space cannot fit the measured
80–90-byte render-only fallback without additional qualification. A seemingly
free projection tail is live action42/support code and was not overwritten.
Under the user's current playable-first/cosmetics-later priority, entrance
appearance remains explicitly unfinished. It is not claimed fixed by7ef.

Every spot run used at most four PNGs, kept only in memory. No capture files,
video, frame sequence, new RAM or new CHR allocation was created. The root
task still has only candidate ROM and controller files.

## Delivery status

IPS `3b896934169854e3fd668c27e9c3dacc78037dfc80568c84c3d216ff4cf12fa9`,
2099506 bytes, reconstructs exact7ef from clean headered SMB World.
The direct Downloads replacement passed both actual launch-context repeats.
Entry receipt98e6 and combat receiptd2e72 above match the private cases
exactly. Installed bytes equal the tested candidate; before/after automatic
patch guards are clear, with no matching IPS/BPS/UPS. No backup was created.
Current is now Latest with exactly one asset,
`SMB-Crossover-Latest-WIP-MMC5.ips`, asset744354526. Root downloaded that asset
and independently reconstructed the installed7ef ROM exactly. Publication used
source `bcca3c14c1573c511cb4153614aa3d8450842de1` and this report's prior
snapshot SHA `ff2ddf6a542ad45aa5638a7d1b108116785dfa3532dbd98a2354462f8f0bd09c`.
No private test level or unqualified DK candidate was installed or published.

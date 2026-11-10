# WWF: earned powerups and original role palettes

Downloads was directly replaced, without a backup, with tested ROM
`d76e070ef5923e05e61088fc7e91e05a637e0c4184c6ccf29feea23637252486`.
The IPS is2,099,510 bytes, SHA256
`a8b2bd9a2fe1677e87e7119f07b10eac5607fc5e4f6d26d9f2b10c49b90ffd1e`.
Its clean-base reconstruction equals the installed ROM. The automatic patch
guards before and after installation find no same-name IPS/BPS/UPS files.
Current/Latest publication is pending the source push and remote roundtrip.

The six wrestlers previously rejected native pickup maturity/progression and
native armor queries. Five existing resolver triples now use the native
handlers. A naturally earned mushroom completes the hosted60-update animation
and grants ordinary SMB tier armor. Original WWF motor/combat stays intact;
original endurance/gear is still unfinished. This is an interim host adaptation.

The unchanged controller
`tools/playthroughs/wwf_earned_powerup_stdout_1110.lua`, SHA256
`c98caae3c61adea500b15403d2eb6642ba29d758ece5f9f3492722d114817c79`,
uses real title/menu inputs, the first authored block, each wrestler's own
jump, native mushroom emergence and collection, and ordinary movement.
It writes no emulated RAM, terrain, items, position, health or lives. It checks
drawn OAM against consumed original CHR, each role's palettes, alignment, HUD,
the real pickup sound-queue write, all60 updates and resumed movement.

## Actual Mesen results

| Wrestler | Physical/Main frames | Body checks | Resumed X/Y | Receipt SHA256 |
| --- | --- | --- | --- | --- |
| Hulk Hogan |1711/1023|340|419/176|`b4cb7d292d80b03fd6dcf749a1592faf408a39abda7aa873c7e05517a86d3065`|
| Ted DiBiase |1751/1050|343|417/176|`ccad3c9cfbd6cf2513346c194910934b3b18e1b6e6de801292905aa48d9432bf`|
| Bam Bam Bigelow |1729/1034|336|417/176|`2accb9e826bba6b30a3c6ce36a658d7def36b343052636eba411b2d3585c752f`|
| Honky Tonk Man |1806/1087|352|418/176|`1ca220c3a624077c17dcf7114090375fa11826d5eef659dd39bf4f03c948a674`|
| Randy Savage |1748/1059|338|417/176|`5b22883301a0ed6326f0c3bac3061c40464249c4444e070a1aaf98bc091c5c08`|
| Andre the Giant |1756/1078|337|419/176|`c2acfc6269a15ab9f38e6604d3f902abcacbdc284bd5157941f7320c79210730`|

All six finish with status1, engine8, powerup age60, no active freeze, timer0
and both lives. Each has11 recovery body checks. The independent actual
Downloads launch repeats Hogan's same receipt. Native measured zero-completion
frames remain671,684,678,702,672,661 respectively; no zero-lag claim.

## The additional color bug

Before this palette fix, Hogan alone passed on private62c9:
`439c5e9cd56a98ee6987206853f284744ce4bc2bb9928a86c993d9dfdffdace8`.
Ted failed at frame392, receipt
`61377a0ceda04cf1a4c186b7e481011f4560a37c2cc44ff94a0b2847b33aabe8`.
His primary colors, original art, body alignment and HUD passed, but the
secondary palette became Hogan's16050f instead of his original27070f.
The existing palette mux hardcoded Hogan on every owned turn.

That mux now uses the original role colors, and retirement recognizes all
six authored secondary color pairs without trusting an invalid private
cookie. The old145-byte native mask table is losslessly packed to37 bytes,
funding the helpers within its original range. No new RAM, PRG or CHR is
allocated. The next audio entry and every following address stay fixed.
All six full A1/selected-C2/audio-A3/body-page cookies are regenerated.
See [the exact allocation](allocations/wwf-role-palette-1110.json).

CPU checks pass1740 mask/actor/status cases,1024 complete original-vs-packed
EarlyActor register/application comparisons,384 owned/native packet cases,
36 all-role retirement cases,30 unrelated/malformed packet negatives and all
six actual cold initializers/cookies. New instruction contexts pass98 actual
lag NMIs and98 actual scanline IRQs with identical foreground continuations;
30 old/corrupt headers decline without executing a private opcode.

The vector fixture initially mapped RAM2 without updating its native mapper
shadow; the genuine ISR correctly restored the shadow's old bank. The fixture
now binds both hardware and shadow as the actual authenticated caller does.
The shared FarCallCommon return also redefines N/Z from returned A; the header
test now compares against the actual old decline rather than invented flags.
Neither correction changes the product ROM or controller.

## Limits and retained storage

No fullstage, natural flower/Star/1UP, complete original WWF gear system,
audible output, perfect animation or60fps claim. Separate CPU policy evidence
in [the source report](wwf-earned-powerups-1110.md) distinguishes natural
mushroom recovery from directed other-item and injury fixtures.

No helper placements change. All six WWF characters retain Up+Select vertical
and Down+Select horizontal native platform summons described in the
[helper inventory](helper-platform-inventory-1101.md), including its world
left-edge/center/initial-height conventions.

The sole new task ROM is `build/wwf-powerups-native-1110/candidate.nes`;
it equals the tested Downloads ROM. The earlier unqualified62c9 private file
was replaced in place after source reconstruction; no duplicate was retained.
Build remains3,123,082,970 bytes/19,999 files. All capture/receipt data stayed
in RAM: no videos, PNG sequences, IPS files or backup files were generated.
Other emulator processes were left untouched. All100 starts remain available;
public Sonic is still the Mario-family prototype pending original integration.

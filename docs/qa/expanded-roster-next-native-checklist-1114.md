# Expanded-roster next native checklist — November 14

Current delivery is `79fd089f80b06038e68b968d2ff80d09caba72a133735b3fef6bb86ffa3ed2df`.
Rogue Dawn's HUD, Bomb, missile and level checks are recorded in the
[November 22 verification](rogue-hud-native-1122.md). Passing results carry
forward unless a change or regression affects the tested behavior. Opening
enemy/powerup pictures cover Prince on16a and DK/all six wrestlers on590
separately; see `prince-body-transition-native-root-1115.md` and
`named-world-sprites-590-native-1115.md`. Separate actual16a M/F transaction
checks now cover all six wrestlers in `wwf-natural-flower-native-1115.md`.
All 101 named choices can start and have a recorded 1-1 clear. Remaining
pickup, move set, graphics, sound and performance checks are still open.
This checklist covers **all64 additions beyond the37 identities** in the
read-only October27 progress file. The original37 retain their separately
versioned stage/item audit; this document does not certify them anew.

**C** = native pass on the development-line ROM named in its row.
**H** = native pass on the named earlier ROM. Both C and H count as completed
unless a relevant change or regression warrants a retest.
**U** = no full native stage pass located in the compact evidence reviewed;
startup/smoke/source results exist, but a full-route assignment is needed.
U is not proof of a game defect or a claim that no historical run ever occurred.
**N** = a specifically retained negative, not a replacement for an older H.
Items: **M** mushroom/health token, **F** flower/second upgrade, **S** Star,
**L** 1UP. Fixture-only effects do not close natural acquisition.

| Added identities — each named choice is in scope | Best native1-1 evidence | Genuine remaining natural-item/native gate |
|---|---|---|
| SMB1 Toad | **C**, actual Downloads421 native89041/294b, full flag/castle/entrance and25 living grounded1-2 | **M/F/S/L C91dc**, actual Downloads85032/8d18bd75,35385/06d785a6,76000/95722965,24797/a716846a. Genuine emergence/maturity/contact/erase, actual score or life credit and25completed Bm returns atMain82BE/SP252; M/F60growthticks, F→tier2, L→life3. Star is explicitly power0 after ordinary injury/shrink, nativeC0/timer35/music64/+1000; no powered-Star claim. Old421 stage remains versioned separately. See `smb1-toad-stock-native-root-1116.md` |
| SMB1 Peach | **C421**, full flag/castle/entrance and25 living grounded1-2; earlier stage remains separately versioned | **M/F/S/L C91dc**: actual Downloads10544/94711d34,84839/f7cc5ead,46914/534f7d50,36803/4f07c003. Each genuine birth/maturity/physical collection/erase/score or life credit and25 completed Bm returns passes. Powered Star retains tier1; F reaches tier2; L gives life3. See `smb1-peach-stock-native-root-1116.md`. Complete float use, expiry/protected hits, art/audio/performance remain separate |
| Kamikaze Mario | **C421**, full flag/castle/entrance and25 living grounded1-2; earlier stage remains separately versioned | **M/F/S/L C91dc**: actual Downloads16025/ee354da0,72369/665a76f9,94629/9e6fb191,84472/1e78788a. Each genuine acquisition and25 completed MarioSource returns passes; M/F60 growth, F tier2, L delayed INC life3. Star explicitly follows original injury/60 shrink to power0 with life2 retained. See `kamikaze-stock-native-root-1116.md`; expiry/protected hits, art/audio/performance remain separate |
| SuperMaaa Mario | **H**, Oct29 Easy clear and earned M | **M/F/S/L C91dc**: actual Downloads56804/4fa00110,40963/2894c7c9 and71250/d94ac104 include genuine M/60/1000/+25 prefixes. F uses original crouch head/native state6 emerging admission/positive9x5/C1/60/tier2/+25, not full128 maturity. L reaches128, delayed INC life3/+25. Star reaches128 after real injury/60 shrink to power0, positive9x1/C0/35/music64/1000/+25, airborne endpoint life2/neck47/Star33. Hard and full abilities remain separate. See `supermaaa-stock-native-root-1116.md` |
| Celeste Mario | **H**, a7ccbaaa Easy natural clear,3900 frames, both upgrades/earned dash | **M/F/S/L C00bb**: L69031/5648f4d9, S27797/d1f77541, F26052/083deff3 all real items/credit/+25 returned owners at Main. F1844Main/1530owners/1856physical; real C1/tier2 then freshB stock0/State6/Timer12 and8returnedDash/18px motion,1188/175/size1/life2. L gives3lives; S retains tier1/Star34. Visual51563/f9efcbbb exactly recovers083deff; both RAM PNGs reviewed coherent, direct tier1 WallJump drainsstamina/setsKick1. Alwayssmall, no helpers/game changes; old one-pixel head input miss corrected. Fullstage remains versionedH; wider abilities/audio/art/cadence remain separate. See `celeste-stock-native-root-1116.md` |
| Mario the Tank | Completed 1-1 and continued through 25 grounded updates in 1-2 on `421`. | All four pickups passed. Mushroom and boots on `7ec9cd5c`. Hidden 1-UP and Star on Downloads `59e1a591`. Boot attacks against enemies and terrain still need testing. [Pickup tests](mario-the-tank-stock-native-1123.md) |
| Mini Mario; Mega Giant Mario | **Mini C9826**, private89875 and actual Downloads21549 exactf95e3631:4905Main/3340original-public/4961physical, all4pipes/3pits/flag3699/castle3762/entrances4276+4774 then25livinggrounded1-2 at40/176/life2/power0 after real injury, no wall restart. Giant retains **H**677aad54 | **Mini M/F/L/S C1327** remain separately versioned. **Earned two-shot C9826** actual21549/private89875 exact531922c1: genuineM/F/60/credit25 then2spawns/3rdreject/107core+motion/4bounces/tier2/life2. Private79115 two root-viewed RAM PNGs matchfunctional5319; exactGBC6x6 art/4x4collision authenticated/userchosen. Existingnative25fixed560/688/864 andmanualFlower1203 worldlefts unchanged; canonicalinventory hascenters/tops andallotherpickupspawns. No game seeds/capturefiles; no zero-lag claim. Enemydefeat/expiry/widerart/audio/performance andGiant ensemble remain separate. See `mini-weapon-owner-native-root-1116.md` and `mini-stock-native-root-1116.md` |
| Rogue Dawn | **Ccb95**, actual Downloads36683 and private7132 exactd11ef5cb:4734Main/6795physical, fullflag/castle/entrance then25livinggrounded1-2 at40/177/lives2/power1. Earlier C82 and **H**f23af095 remain versioned | **Earned M/F plus missile Ccb95** actual36683/private7132 exact5b4fb48d:2022Main/1865balancedworkers; genuine tanks, score2200, ammo5→4,43moves/172px/21nativeRender/offscreenexpiry/+25. Two root-viewed movingRAMPNGs91084; HUD94269 actualPPU E191/M004. **Natural Bomb Ccb95** actual38822/728a8c62:5138Main3882balancedworkers, actual1-2 D0 mature/physicalC1/OR01/1000/+25 thennormalDown+B/8→9→10→0/place+explosionrequests/five native terrain calls/F7expiry/+25, life2/ammo5/gear1. **M/F/L/S C1327** remain versioned75541/c9f1,31099/0bb8,82339/fb18,21813/e18e. Other seven gear acquisitions, actual Bomb brick/enemy effects, missile impacts, audible audio and performance remain open. No helpers changed. See `rogue-missile-native-root-1116.md`, `rogue-bomb-native-root-1116.md` and `rogue-tank-native-root-1116.md` |
| GB Pit | **C1D**, actual Downloads1daca root17738/b4ac,5589physical/4386Main, fullflag/castle/entrance then25 living grounded1-2 at40/176, lives2/power0; separate **C82**44721/75b5 | **M/F/L/S Ccb95** actualM/F25403 b12c4a74/ea21d298 withgenuinephysicalpickup/1000/60upgrade ticks/+25owners, tier1then2. Hidden1UP65170/59057e82 hasintendedkind27arrowtrigger, fullmaturity/physical1×9/C1/erase/popup11/actualINC2→3/cue64/+25. Star35493/76fb3813:2321Main1989owners3148physical; bodilyheadMmBlockAttack0/birth2058/mature2124/physical9×1/AF88C0→AF8D35/music64/1000writer/+25completedMain82D0/SP252,1777/176/tier1life2/Star34. Allfourbasicnatural scopes closed; no helpers/gamebyteschanged. Fullstage retainsitsversion. Complete abilities/expiry/protectedhits/audio/visual/performance remainopen. Gameplayuser-paused. See `gb-pit-stock-native-root-1116.md` and `gb-pit-full11-current-1114.md` |
| Ryan | **C1D**, actual Downloads1daca root37312/8b18,6415physical/5800Main, full flag/castle/entrance then25 living grounded1-2 at40/176, HP64/tier1/power1/lives2 | Natural M/F/S/L policy and ability/audio/visual coverage remain separate. The route's tier increase is not complete item proof. See `ryan-full11-current-1114.md` |
| Mr. Gimmick | **CCF7**, actual Downloadscf7 root60011/8483,8959physical/7402Main, full flag/castle/entrance then25 living grounded1-2 at40/176, HP2/power0/lives2; eight genuine native star-support events | **M/F/S/L C7a80 Easy**: root67035 real M/hidden1UP with delayed2→3 life credit and25 later moves; separate real Star/timer35/music64/cue32/score+1000/+25. Root34274 and actual Downloads29773 real reflected-star support/fresh jump/physical Flower/code2/next2/cue1C/erase/score+1000/+25. Side marker35→empty is privately native-confirmed, real walls remain solid; root79338 two native images/11 ROM pattern pairs pass. See `gimmick-empty-side-native-root-1115.md`. Expiry/protected hit, full current stage, complete abilities, audible audio and performance remain separate; cf7 full stage retains its version |
| Donkey Kong | **C571**, actual Downloads root93535/4601: earned first M, full flag/castle/entrance and25 living grounded1-2 at40/176/lives2/tier1/power1/Star0;3873Main/4717physical,8 real barrel spawns/0 injuries; receiptb7df22aa134728c6e98d656506de37573b5c00df268e058d005454ab2665956d. Earlier tier0 native negatives retained | **M/F/S/L C571**: root73346/40bc M; root77438/2bca Flower/spent-shield→tier2; root89926/3920406a Star/timer35/music64/cue32/+25 and earned Down+B supported roll; root90739/73709db8 real mature hidden1UP/popup11/delayed INC2→3/cue64 and25 returnedMain snapshots (24 strictly post-credit DK moves), receipt74066f1a848ed035009c2ebb15ac395a896daadd781966107b0370c2f7439a31. Star expiry/protected-hit and complete abilities/audio/visual/performance remain open; see the `dk-natural-{mushroom,flower,star,oneup}-1114.md` receipts |
| Doc Louis | **C**, actual Downloads421 root18076/b2e4, full flag/castle/entrance and25 living grounded1-2 at40/176/HP96/lives2 | Natural item/audio ensemble remains separate. Existing actor28 at initial left3096/center3104/Y64 was present; no support event, so assistance is not claimed. See `doc-louis-full11-source-1114.md` |
| Getsu Fuma | **H**, c6ab5610 full clear plus earned M/F | Natural S/L; full donor arsenal remains later work |
| Karnov | **H**, current7ef full stage and all five stock pickups/Ladder | Natural S/L; Bomb enemy kill remains distinct from arming/blasting and normal-fire kills |
| Quick Man | **H**, aa501128 full/grounded1-2 plus four authored items | No uncovered authored stock item in these receipts; physical F is not claimed under the existing no-growth policy |
| Shinobi | **H**, exact6f319d20 native full8924 physical/lives2→2/no helpers; retained packet and all12 current421 carriers inspected | Current421 full rerun remains a separate regression: resident65 changed408bytes. Natural stock items/remaining abilities are open; do not reopen old locked-menu/contact negatives |
| Thomas | **H**,65ee94ca full M/F/S route plus separate natural L/Downloads repeat | Four stock families covered across separate runs; not one uninterrupted all-item route |
| Metal Storm | **H**,8fc57b8b full route and natural M/F/upgraded shot | **M/F/S/L C00bb**: Downloads53024 matches private84341, La8b7d81c real INC2→3 retains armor128/native1/saved3/noctor/+25; Stard3437046 genuine nativeC0/35/music64/1000/+25, armor128/lives2/Star34. Flower8004/05a98205: genuine mature contact1x13/original item0/weapon128/native2/1000credit then25 returned MsFrame+Movement+HostStep; later real moving81 shot/nativeGoomba defeat/shot retirement.1631Main/1338workers/2525physical,1502/176/lives2. Immediate original armor/weapon policy, no60growth. Delivered34owned30changed life repair; source lifecycle/ABI/reached11IRQ+11busyNMI pass; baseline7c0f failure retained. Full-stage regression, complete arsenal, audio/art/performance remain separate. See `metal-life-snapshot-root-1116.md` and `metal-flower-native-root-1116.md` |
| Mike Tyson; Alex | **H**,33d2c7a7 Tyson Hard4861 frames;4cbd0191 Alex6018 | Complete natural stock-item evidence per identity remains unqualified in these route receipts |
| Jay McCray | **C1327**, actual Downloads52522 exactly matches private94610/full786ccd62: 3885 Main/2391 original workers/5674 physical frames; full flag/castle/grounded1-2 entrance then25 completed original returns at40/176, HP6/max3/lives2/size0. Earlier machine-gun proof remains versioned | **M/F/S/L C1327:** actual Downloads52522 matches all private receipts: F2d745e96 (1821 Main/1486 workers/3040 physical), L97ecb448 (1245/910/2154), S08af4e40 (1634/1299/2779). Real first heart HP6→8/max3→4, correct private82 Flower/tier2, actual brick51 shatter/chunks/noise and1000 score writer followed by more than25 returns and a pistol defeat. Life2→3/cue64/+25; Star35/music64/1000 by endpoint/+25 after collector, HP4 already present and retained. Full original Status+Size0 publication repaired;116 owned/72 changed bytes, all unowned00bb/Metal/graphics/helpers exact. No seeded outcomes. Full arsenal, Hard, Star expiry/protected contact, audio/art/performance remain separate. See `jay-status-size-native-root-1116.md`; earlier00bb and failed private-only status-only df0e retain their scopes |
| Steve Hermann | **H**,62ba full stage;7ef four stock pickups | Four-stock route closed by combat chase; do not reopen the earlier death-before-Star controller failures |
| SMB3 Toad; SMB3 Peach | **C**, actual Downloads421 native95857/52d post-damage Toad and33056/30e Peach; full flag/castle/entrance and25 living grounded1-2 | Individually earned SMB3 powerup ensemble remains separate; preserve old c8f second-pit input negative without reopening the now-cleared identity |
| Popo; Nana | **H**,a7ccbaaa natural clears5190/5285 frames, tier0→1 | F/S/L and additional original abilities; do not reuse the old pipe/route negatives |
| FF Fighter; FF White Mage; FF Black Mage; FF Thief | **H**,a5c54d76 full routes, earned M/F/tier-two attacks | All four **M/F/S Cae66**, actual Downloads42192 Fighter9b69dc9d and43523 White707b24a8/Black44d7f2f0/Thiefc2e9b16e; real matureStar/timer35/music64/cue32/1000score and25 actual post-collector entries, tier2 preserved (White charge3). **L** individually closed Fighter **C571**93311/3d6fc, White/Black/Thief **Cae66**3651/5bfac741,14546/83b8abdd,75126/afe41faf; real delayed INC2→3 and at least25 post-writer entries. Thief pending entered Main is distinct from completed Main; no grounded-endpoint claim. Star expiry/protected-hit and full ability/audio/art/performance remain open. Exact receipts: `ff-natural-stock-current-1114.md` |
| Sunny | **H**,16a9de64 Hard full route and separate M/F/fireballs. **S/L Cbc5**, actual Downloads10845: hidden1UP9d804214 (1473Main/1078Sunny/1502physical), Staraccd6754 (1793/1338/1852); real birth/maturity/positive collector/erase/cue/native delayed credit and25 completed Sunny returns at completed Main/no pending | All four stock families have versioned evidence; current S/L preserves form/lives, actual1UP2to3/cue64 and Star35/music64/popup1000. Star route retains genuine preceding injury. Current fullstage/HardS-L/Star expiry-protectedhit/audio/performance remain separate. See `sunny-stock-native-root-1115.md` and `sunny-natural-stock-bc5-source-1115.md`; palette-deadline fix remains retained |
| Rash; Zitz | **C91dc**, actual Downloads22050 matches private71807: Rash4254Main/4644physical, HP39; Zitz4611/5005, HP43. Both full flag/castle/entrance then25 living grounded completed original BT returns in1-2 at40/176,lives2,real variants0/32. Earlier bc5/ACE routes retain their versions | **M/S/L C91dc:** both genuine mature Mushroom food, hidden1UP delayed INC/cue64, Star/1000credit and25 completed original-worker/Main returns individually passed private and actual Downloads. M heals8 capped47 and retains nativepower0; later question blocks may remainM, so no inventedFlower progression. New mature-only admission27owned22changed preserves all6a3 unowned bytes/Bowser/carry/draw fixes. Prior bc5 direct118 cadence improvement remains versioned/partial. Nativeexpiry/protectedhit, completeabilities/audio/visual/performance remain open. See `battletoads-mature8-native-root-1116.md`, `hot-draw-bt118-native-root-1115.md` and `battletoads-stair-progress-1115.md` |
| SMB2 Mario; SMB2 Luigi; SMB2 Toad; SMB2 Peach; Imajin; Lina; Papa; Mama | All8 **H** full12397; Luigi **C** full421/25 grounded1-2 | All8 M7ef, F/vegetable combat12397, and **C** S/L421 now qualified. No missing four-stock family; other7 exact421 full reruns are regression coverage, not never-cleared identities |
| Bub; Bob | **H**,f88 full stage. **C67 M/F/S**, actual Downloads12602 matches private50103: Bub2979Main/6339physical, Bob2986/6374; real M/F then Star/1000credit and25 completed workers, lives2/flags7/power2. **L C67**, actual Downloads61151: Bub1586Main/3504physical,c874ada6; Bob1585/3522,a055b306; real hidden birth/maturity/collector/erase/popup11/cue64/delayed timer42 lives2→3 and25 later original worker entries, score1500 retained. All four standard families now have native current67 witnesses for both identities | **Player Star flash repaired C67:** all6 actual RAM PNGs reviewed; physical P0/P2 hero64/66 matches completed selected draws while original private Bub67/Bob64 and worldP3 remain intact. Both Downloads receipts and all6PNG hashes match private exactly. Failed3080 capture and31581 diagnostic remain recorded: only request scheduling was corrected, no physical assertion weakened. Full current stage, expiry/protected hit, audible audio and wider ability/performance coverage remain separate. Hidden1UP counts25 worker entries, not a new completed-Main-return claim. See `bub-star-prince-native-root-1115.md` and `bub-selected-star-source-prince-1115.md`; all older stock/stage receipts retain their versions |
| Sonic; Super Sonic | **Ca2**, privateFull2047 and actual Downloads45911 bothPASS/exactprivate receipts88f1d54f/a7a3a0fc; route2660Main/1466original,5030/5056physical, realflag/castle/entrance then25livinggrounded1-2 at40/176/lives2 | **L Ca2**, private84495 and actual27306 bothPASS/exacta248b954/7b0aec04. Actualhidden60/head/eightTimer0gravity/fullC0positivephysicalcollection/erase/popup11/cues32+64/delayedINC life3/+25originalreturns; capturednative rings0/resources preserved, sourcefixture5 not imposed. Delivered94owned91changed preservesall5526originalmotor/unowned13bytes, nohelpers/art/music change. Oldfixed5 observer9824 negative retained. Natural F/S and broader abilities/audio/art/cadence remainopen; historical M/ringloss keepownversions. See `sonic-ceiling-native-root-1116.md` |
| SMB3 Bowser; SMB1 Bowser | **C6a3 full earned1UP routes:** actual Downloads55517 SMB3/2883a154 (3619Main/6141physical/HP33),7245 SMB1/63ad0d76 (4696/7627/HP4), both full flag/castle/entrance then25 living grounded completedcore+tail pairs in1-2 at40/176, tier1/lives3. Separate **L/S C6a3**37075 all4 match private83453/94864; genuineM/F60 precede Star, tier2/lives2/actual+1000/+25; SMB1Star ends airborne | **Earned-life reset repaired/delivered6a3:** signed40B Ensure plus two cookie views,72owned/56changed/allunownedbc5exact. Genuine emergence/maturity/contact/INC/cue64, savedlife3/noCtor until legitimate nextarea; retained baseline36997 proves old upgrade reset/heal. Sourcefull39a67b62/native results retain distinct timing. Naturaldeath/expiry/protected-hit/audio/performance remain separate. See `bowser-life-gain-native-root-1116.md`, `bowser-life-gain-candidate-source-1116.md` and baseline QA |
| Donkey Kong Jr. | **C7c0f**, actual Downloads96918 matches private97412/4ca23a66: full1-1 flag18018/castle18112, real1-2 entry then25 grounded D65E returns and26 grounded original SourcePhase Move+Clock returns; final40/176/lives2/power0/Ready2/source1/camera0. All13 native helpers unchanged | Delivered forced-entry gravity/body/admission repair preserves original22 fall limit. Both falling/grounded PNGs reviewed clean and match installed hashes exactly; public1453owned/1131changed/allunowned91dc and wholeBT8192/header487 exact. Earliera3fb strong-entry negative30f29 retained. Current natural M/F/S/L remain missing: older private firstM requires a different336 helper/head bridge; seeded fixtures do not close acquisition. Performance/full donor abilities remain open. See `dkjr-entry-native-root-1116.md` and helper inventory |
| Hulk Hogan; Ted DiBiase; Bam Bam Bigelow; Honky Tonk Man; Randy Savage; Andre the Giant | **H**,8fc57b8b six separate full routes; **C7a80 Easy**, all six real M/F60/+25, mature Star/35/music64/cue32/1000score/+25 and hidden1UP/delayed2→3 life credit/cue64/+25 | All four stock families are individually covered per wrestler. Star expiry/protected contact, original endurance/gear, audible output and current full stages remain separate. Earlier Bigelow/Savage gap input failures are retained; later-edge controls pass using the existing native helper. See `wwf-natural-star-native-1115.md` and `wwf-hidden-oneup-native-1115.md` |
| Excitebike | **C91dc**, actual Downloads96571/21e23eb6 full nonshortcut1-1 flag/castle/exterior+underground entrance and25 grounded originalMotor+Movement returns atMain82D0/SP252;4175Main/2636workers/6468physical,125/176/life2/power0/1-2Area2/type2, no helpers. **M/F/S/L C91dc**, actual46091/7014b9e8,F58625/cd66639c,S40074/cc12713e,L30568/1a80d9bd; genuine items/credit/25returned workers, F60ticks→power2,L INC2→3 | S uses actual moving-actor feedback and a four-pixel earlier target:84 feedback calls, positive3x1 contact at1690/176 versus1700/163, nativeC0/timer35/music64/actual1000/25returned Motor+Movement;3014Main/2619workers/4745physical,lives2/tier1/Star34. Earlier fixed-head/stationary/chase negatives remain versioned. Other abilities, Star expiry/protected hits, audio, visuals and performance remain open. See `excitebike-stock-native-root-1116.md` |
| Prince Persia | **C7fb Easy**, actual Downloads97939 matches private37914: full earned-M/F/sword1-1/flag/castle then25 living grounded completed1-2 returns;9336Main/7757Prince/17249physical,HP5/lives2/native2/Sword1. Hidden5F/60 point-query false wall/backward snap is repaired; native head path/real pipes remain intact. Current67 leaves the full Prince packet/code/cookie exact, without relabeling this as a new67 route | **S C7fb Easy**, actual Downloads97939 matches private28784:4707Main/4015Prince/8508physical, genuine collector/erase/cue/credit and25 completed Prince updates,HP4/lives2/native2/Sword1/Star33. Natural L, equal-facing target loss, wider abilities/Hard/audio/art/performance remain open. 1-1 cap/running/grounded-Up controls genuinely do not reach hidden row128; retained negatives do not establish a head-query rejection. A typed67 2-1 authored ledge/controller investigation is active. No helpers changed. See `prince-hidden-point67-native-root-1115.md` and `prince-hidden-point67-ace-source-1115.md` |
| Burns | **C**, actual421 root16139/94b,8864physical/4442Main/2818CF, full flag/castle/entrance and25 grounded1-2; no helpers | **Currentbc5 idle lag OPEN/measured:** root77416/c95fafe9, idle48Main takes96physical frames (71/95 missing port-read frames); Right16 takes32 (23/31 missing),0actors/shots/lives2. Actual RAM1 Input/Body and Main returns balance; observer pass is not a lag fix. Source attribution and detached proposals precede any overlay lease. Natural weapon/container ensemble and other abilities remain separate. See `contra-force-idle-native-root-1115.md` and `contra-force-full11-source-1114.md` |
| Smith; Beans | **C**, actual421 root93241,8954/8951physical, full flag/castle/entrance/25grounded1-2 at40/176/lives2; no helpers | Natural weapon/container ensemble and remaining abilities are separate; idle30Hz deficit remains open. Evidence: `contra-force-full11-source-1114.md` |
| Iron | **C**, actual421 root7285/db850,10736physical/5243Main/3759CF, full flag/castle/entrance and25 grounded1-2 at40/176/lives2; no helpers | Natural weapon/container ensemble and remaining abilities are separate; idle30Hz deficit remains open. Evidence: `contra-force-full11-source-1114.md` |
| Arthur | **H**,d8a87050 full5950 frames and real source-lance/native defeat;379590 flower/torch | Other naturally earned weapons/S/L; original no-weapon-tail negative was repaired |
| Goku | **H**,22d09909 Hard full5837 frames; later f205 qualification cited by current audit | Natural powerup ensemble and Easy remain separate; retain authenticated helper/camera policy |

## Assign next, without resetting completed work

1. DK Jr.'s7c0f repair is now **delivered and native-verified**. Both private
   97412 and actual Downloads96918 pass the same complete1-1/grounded1-2
   receipt4ca23a66 and both entry PNG hashes. Source full83da and reached
   IRQ7290 passed before staging; original fall22 and all13 helpers remain.
   Do not replay the closed earlier fourth/stair/forced-entry failures.
   Next is read-only natural-item policy/access inventory: all four current
   families remain open, and private336-helper/head-bridge M positives are
   not current7c evidence. See `dkjr-entry-native-root-1116.md`.
2. **U0 (previously U1):** classicDonkeyKong now has the actual571 full
   earned-M route93535/4601, including25 living grounded1-2 updates. Natural
   DK's natural M/F/S/L are now covered by the separately versioned row above;
   Star expiry, protected hits, complete abilities and performance remain open;
   the whole goal is not complete. The two Battletoads choices have actual
   f11 full passes. Shinobi's
   recovered historicalH and Rogue Dawn's retained native pass correct the
   earlier U counts; neither recovery alone is a newC pass.
   Burns root16139 is an independent currentC closure after that correction;
   receipt `ad9e59dbd50f2f5290c39d01540c258aa99e92f497ed2a4b7c02308919016d26`.
   Smith/Beans root93241 close two further identities: receipts
   `fe78cd48ce840284206d0a0505c6e1149991e27897e7f6f2d308fb654bcd2c7c` and
   `9ee1738671adab8c32a3542bd8399799dbd6730e10271d4699a73d90721f6b24`.
   Iron root7285 closes the fourth CF identity, receipt
   `e7546a81bd1a95062b71188bc31dc3cd39856e7594255db763a7d7d6f461fe5b`.
   All4 CF full-stage gates areC; their idle30Hz deficit is a separate open gate.
   Doc Louis root18076 closes another identity, receipt
   `b5d2076424783ba0a361d77ea9964d1a3ddc7b4a0862def0ff98c32b174fc395`.
   Ryan root37312 now closes one more current-stage gate, receipt
   `3d894fe0c489d495e90542821182cf9e27f2c399db626bd5c3ac73609efdfc74`.
   Mr. Gimmick root64354 closes another, receipt
   `a6f2ada1ada24b24daaecd33352b60e95d7525bf2863eaaad62f371afc0965d9`.
   Actual Downloads47036 closes Rash and Zitz after the52-byte camera repair:
   receipts `f64ec257be8f7dec5c59b10bc7fb26f1519fbc328b6cf2f10b506e314197b48b`
   and `48619365f3fbb73a02c9c205df2a8330d602d82049b4645e836d3ec4f1397579`.
   Use their intended abilities. If assistance is needed, root owns native
   actor placement/allocation and must record the assisted crossing.
3. Jay's **M/F/S/L and full stage are now native1327**; Metal's four stock
   families are native00bb. Continue current Mini, Rogue Dawn and Sonic item
   work, and retain **Prince L** as an open natural acquisition. Peach,
   Kamikaze and SuperMaaa M/F/S/L are now native91dc
   passes; both Bowsers S/L are already native6a3 passes. A mature-actor seed is diagnostic only;
   collector/erase/score/sound/resumed-play effects must follow ordinary access.
   All four FF M/F/S/L are already covered in their recorded versions; their
   next work is expiry, protected hits and remaining abilities/audio/art/lag.
4. Keep H positives and explicit byte-preservation evidence separate. Current
  421 changes are exactly110 owned hidden-head bytes overfa66;fa66 adds66
   granted cheat bytes. The new hidden behavior intentionally changes SMB2
   host probing. It does not retest every old route automatically. Kirby's
   **actual571 four close-inhale runs plus green-shell/full1-1 and red catch**
   are now in `kirby-current-native-1114.md`; green's falling1-2 endpoint
   is kept distinct from25 grounded updates. The earlier current421 source
   preservation remains in `kirby-shell-current-audit-1114.md`. Kirby also
   passed all four natural pickups from the November 22 Downloads nightly.
   Mini's exact retained carrier/
   hooks and Bub/Bob's disjoint preserved carrier have their own proof notes.
   Do not extrapolate that evidence into101 new native passes.

## Compact evidence anchors and limits

Use `roster-stage-regressions-1112.md`, `roster-native-followup-1113.md`,
`smb2-postbg-delivery-1113.md`, `smb2-natural-items-native-1113.md`,
`smb2-flower-native-1113.md`, `smb2-hidden-native-1114.md` and
`smb2-star-native-1114.md`. The latter two supersede every older SMB2
Star/1UP-pending sentence. Use `steve-four-pickups-current-1113.md`,
`thomas-oneup-lift-1113.md`, `quick-current-powerups-1113.md`,
`jay-pickup-helper-delivery-1113.md`, `karnov-five-current-native-1113.md`
and the per-character delivery reports for their later closures.

Older positives for Celeste/Popo/Nana are retained compact Oct30
`*-natural-11/receipt.json` records at a7ccbaaa. Alex/Tyson's compact Oct28
results retain their exact4cbd0191/33d2c7a7 versions. SuperMaaa's Oct29
progress JSON records its actual Easy clear. No historical build/expanded
path was assumed live, restored or recursively rehydrated for this review.

This was read-only receipt inspection and one new checklist, with no builds,
ROM output, Mesen, or progress-JSON edits. The protected progress file remains
SHA256`bd99b4ee9143380aabf12da8ee1e56beda5a1491abe26c92e6c789afecaaa0a7`.
No helpers were added or moved. Existing exact helper coordinates/initial
heights remain in `helper-platform-inventory-1101.md`; final reporting must
name affected alternates and distinguish left edge from center. Releases
remain empty; source pushes and verified local nightlies continue.

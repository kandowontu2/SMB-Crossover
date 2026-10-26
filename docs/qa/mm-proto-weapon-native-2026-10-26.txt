Mega Man Hard: six native weapon components on adopted3b
2026-10-26. No game patch or new ROM. One corrected-oracle launch; worker released.

Exact scope and inputs
  ROM 3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287.
  D = C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py
  Immutable source: D/root-current-roster-composition-v1/source,869-file manifest
  SHA86eacaf0a954abf8cf0ff7fc8ee6b03b13fc406f2335b5d864eb96c554f868a6.
  Actual numeric Hard readback1, owner1, ProtoVariant0, tier1, facingright.
  Cold controller selection. Declared before-component arenas/tier/ownership/
  energy and complete small-capsule actor are setup, not natural acquisition.
  Rush contact additionally uses a declared descending-player setup after the
  actual summon falls and lands. No within-phase outcome forcing.

  Original native-ready-v2 failed its first art oracle: pointer-table bank66
  was incorrectly treated as the pointed-to record bank. Actual linked primary
  art is C12. The source-only correction,9 full renderer calls/36 true-negative
  callback controls and the untouched first failure are documented separately
  in mm-proto-weapon-art-oracle-2026-10-26.txt. ROOT separately authorized v3;
  this was not an automatic retry. Two historical native attempts total:
  one old-oracle failure, one corrected-oracle pass; no later attempt.

Corrected actual result
  D/mm-proto-weapon-boundary-v1/native-ready-v3/launch-outcome-v1.json: exit0.
  Six cumulative components completed,656 actual GameLoop updates:
  - Basic buster: type1, charge0, special stocks unchanged; completeupdate92.
  - Weak charge: initialtype1 then type2 at charge56; complete239.
  - Full charge: initialtype1 then type3 at cap87; complete431.
  - Rush: free summon at20; actual landing479; existing Rush redirects B to
    free ordinary buster; controlled contact499 debits20->8 directly through
    MegaManRushBounce. Full caller launches body with nativeF9 velocity,
    spring/exit/flight clears; complete570;122 source Rush art draws.
  - Stock3: actual B refusal, no primary/special spawn or debit; complete612.
  - BALANCE: real Select8->0 skips passive slots. Complete small capsule under
    default schedules native ammoindex18; credits4->8->12 at updates619/622.
    ARM60/Rush8 remain; exact8 restored, pickup/timer/refill clear; complete656.

  Native guards:655 NMIs/655 IRQ31 scroll stores,7860 CHR latch checks,
  645 post-publication DMA checks, minSP223;6686 APU/DMA/controller writes.
  Fresh offline verification independently checks every byte/write of all997
  completed all-mode physical DMA pages (255232 writes), page2, zeroOAMADDR,
  disabled rendering throughout each transfer,669 scoped render enables safe.
  NMI assertion covers A/SP and mapper/SMC, not an all-AXY preservation claim.
  Original uninitialized-read diagnostics remain in the emulator log.
  This unit has no matched baseline performance comparison or FPS-gain claim.

Actual graphics and explicit remaining issue
  1030 actual completed PPU frames (253132800 bytes) retained externally.
  All34 named whole images independently hash-match their actual completed
  PPU frame. I reviewed both primary/support whole-image sheets. Source event
  request time is not publication time: queued data.wall375 is actual complete
  image376. New reviewer v1 incorrectly required Hard on the initial menu;
  reviewer v2 incorrectly equated that request time to completed-frame time.
  Both offline failures are retained. v3 checks actual completed outer-event
  time and allows mode0 only in pre-profile menu, without changing native data.
  Native art filenames containing ':' created Windows alternate streams;
  every stream is explicitly hash-bound. Public sheet names are sanitized.

  Graphics are NOT universally clean: charged-shot samples still contain
  visible player-body omission. The current overloaded-sprite visibility issue
  remains open despite correct logical primary records and exact DMA transfers.

  Rush followup reads36 consecutive actual frames850..885. The original2.02
  timeline contains stand1..3, spring4, landing5..8, exit9..12, fly13. The
  original fly/transition art genuinely contains a vertical beam and cloud.
  Captured853 reconstructs the identical6/10/13 beam record with exactCHR181;
  source chronology is before the real landing479, identifying fly13 there.
  Captured856 matches original5/11/12 with exactCHR185; current landing stage
  identifies5. The later clouds7/8/9 useCHR183. Native mode/art arrays were
  not serialized each frame; identical-record ambiguities remain in the data.

  At872 all eight standing Rush2/3 OAM parts exist with exactCHR181, but the
  actual16-high first-eight selection rejects several parts on lower rows.
  At873 those Rush parts are admitted;874 begins the genuine spring4/CHR183.
  Thus teleport form is authentic, while standing fragmentation includes real
  overload flicker. Complete36-image sheet and actual pose/priority rows are
  retained. This is not a per-pixel proof for every missing opaque color.
  The source SWF skin is before GraphicsManager runtime recolor; native white
  transformation colors use an adapted shared NES palette. Exact final Flash
  colors are not established by matching shape, CHR family or pointer records.

  The apparent TC HUD icon is original MegaManPickup frame10, labeledrushCoil.
  Source HUD slot8 selects index7/physical243 and tiles2A..2D. Independently
  recomputed quantized icon tiles exactly match frozen inventory-hud.chr and
  the native243 dump. No wrong pickup-frame/item-index was found. Legibility
  is distinct from correct mapping; no original reference art is published.

Limits and replayable evidence
  No Proto native/Easy/tier2, both facings, full primary pool, actual enemy/
  block damage, shared seven-special gallery, every powerup, audio listening,
  natural acquisition, full-route or universal graphical acceptance claim.
  Source controls include finite Proto/threshold cases; they do not replace
  native coverage. No production/default/settings/Git changes by this agent.

  D/mm-proto-weapon-boundary-v1/native-review-v3/proof.json
  D/mm-proto-weapon-boundary-v1/native-review-v3/external-raw-manifest.json
  D/mm-proto-weapon-boundary-v1/rush-visual-v3/proof.json
  D/mm-proto-weapon-boundary-v1/rush-visual-v3/actual-rows.json
  Public compact checkpoint:
    docs/qa/checkpoints/2026-10-26/mega-hard-primary3b-v1
  Catalog/checkpoint proof records the exact hashes, tools and explicit Git
  review map. External raw ROM/audio/settings/reference art are referenced
  by hash only. Tool prerequisites are finite versioned/local dependencies,
  not a claim of a turnkey fresh-clone native environment.

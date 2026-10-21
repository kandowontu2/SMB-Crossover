# Easy and Hard source behavior update

The user renamed the existing options to EASY and HARD and requested the
original linked six-character build's behaviors under Easy. Those label edits
and the user's rebuilt ROMs are frozen in
`build/verification/root49-easy-hard-user-baseline-a/baseline.json`.
The working source and ROMs currently match checkpoint GQ, bound by
`build/checkpoints/roster-audit-v49-link-ceiling-gq/manifest.json`. It includes
the Easy/Hard behavior work, the Contra laser rendering repair, Simon's castle
transition repair, Link's normal-form victory animation and the scoped Easy
Link normal-jump solid-ceiling response. Bill's more precise
body/head successor remains private while correctness and processing cost are
checked. The checkpoint notes below preserve their original historical ROM
scopes; they are not interchangeable with a current integrated replay.

Easy uses the original source for Mario, Mega Man, Samus, Bill/Lance, Link and
Simon. Hard retains Crossover 2.02 rules. Later additions have no character in
that original source and retain their requested current abilities, plus the
existing common Easy ordinary-stomp policy. Luigi's requested modest jump and
traction differences remain intentional. Mario now has a dedicated source
implementation and independent component checks. Shared native fireball motion,
normal death and NES opacity remain explicitly qualified approximations.

The pinned source comparisons are:

- Mega Man: `agent49-megaman-easy-hard-source-b/audit.json`.
- Samus and Bill: `agent49easy-samus-bill-source-a/freeze.json`.
- Link and Simon: `agent-lsr-easy-hard-source-a/source-freeze.json`.
- Mario: `specialist-mario-easy-hard-source-a/source-freeze.json`.

These paths are under `build/verification`. They bind actual decompiled
functions, constants and timelines rather than recollections of the web game.

Shared private implementation and execution:

- `root49-easy-inventory-base-a/build-review-b.json` admits the two-file
  inventory/drop boundary. Easy classic guests use the original three tiers,
  without 2.02 collectible inventory, selection UI or energy/ammo drops. Hard
  and later characters keep their existing inventory path. The seven generated
  includes differ only in admitted CRLF normalization in the private build;
  the user's source files remain byte-exact.
- `root49-easy-inventory-base-a/query-cpu-b.json` records 109,056 executions of
  compiled ownership/support query routines across both mappers, with
  independent carry oracles, complete registers for unaffected modes and all
  10,240 physical RAM bytes checked per call. This is a pure CPU component;
  pickup/drop traversal and ammo commit require separate checks listed below.
- `root49-easy-injury-private-a/spend-cpu-c.json` separately passes 107,520
  compiled ammo-commit cases per mapper. Easy classic calls reject without
  changing ammo, scratch or inventory; unaffected modes match the original
  full registers and complete RAM with exactly predicted stack residue.
- The same folder's native `pickup-m3-e` and `pickup-m5-f` each pass 36 real
  Mushroom/Flower contact cases: all six classic identities, every initial
  power tier, one-tier progression for either pickup, capped-tier behavior,
  exact60-update transforms and no stale Hard inventory/ammo changes or HUD.
  Initial pickup placement is seeded; block emergence remains separate.
- `root49-easy-injury-private-a/build-review-c.json` admits private builds of
  the original guest damage lifecycle on both mappers: a powered hit freezes
  the world for 1,000 ms, alternates power forms, loses the upgrade and then
  grants 2,500 ms of protection. Easy Bill/Lance keep the original powered
  extra hit. Hard Bill/Lance retain their one-hit rule and other Hard guests
  retain live recoil. One new byte is appended; old RAM addresses, CHR and DPCM
  remain exact. Binary NES opacity approximates source 0.65 alpha over time.
- Native seeded contact checks are in that injury folder's `native` directory.
  The first smoke and first 48-case run are preliminary. An independent review
  found that the initial safe actor could cause a second contact late in Hard
  recovery, so that run is not admitted as a clean Hard regression. The updated
  fixture makes that actor move away and requires exactly one actual injury
  and an alive Hard endpoint. `full-m3-c` and `full-m5-d` each pass all 48
  contact arenas. These are contact components, not ordinary full-stage routes.
- `root49-easy-injury-private-a/hard-regressions-b/report.json` also passes
  all16 existing injury regression groups across both mappers, including
  Mega Man/Bass motion and timing, Samus Morph injury, Link/Simon/Ryu source
  entry and the other profiles' native scripted injury.
- `root49-easy-contact-private-d/build-review-f.json` builds the additional
  original enemy eligibility rule. Easy Mario and original guests may stomp
  eligible enemies in water, while Bloopers and swimming Cheep Cheeps remain
  non-stompable. Native `eligibility-m3-g` and `eligibility-m5-h` each pass144
  actual body-contact cases across modes, areas, classic identities, Lance,
  Luigi and Bass. Hard and later-character restrictions retain their prior
  behavior; this does not certify every shared Hard enemy rule. The first
  swimming Blooper arena missed the body handler and is retained as a coverage
  negative; the corrected placement reaches genuine body overlap. Resident
  global PCs, old RAM, CHR and DPCM remain exact; one new byte is appended.

Character implementations are being tested privately. Mega Man's initial
relocation and off-edge coast-cap failures were retained and corrected. His
independent movement and Buster checks pass Easy/Hard on both mappers.
Samus/Bill tier weapons, Link/Simon numeric movement and primary attacks, old
Link attack-before-body priority and whole-clip Boomerang origins are frozen
separate layers. Easy Samus's 24-update enemy stop and Hard's 9-update
stop/invulnerability have distinct source-backed native checks. Their scope
does not establish complete-character fidelity.

The first complete numeric/tier union is `root49-easy-union-a/report.json`.
The three shared-file merges are clean. Its actual link fails because GUEST
exceeds its bank by13 bytes and SPECIAL_ROSTER by16 bytes. This is an
integration failure, not a published ROM. Union B includes the next Link layer,
both Samus effect layers and U's drawing filter; its link exposes a further
20-byte GUEST overflow. Union C moves the already bank-called Mega Man palette
closure to INVENTORY, with no additional bank crossing, and builds both mappers.

`root49-easy-union-c/native` contains actual combined native execution of the
shared damage, pickup, contact and projectile graphics components. Its first
two aggregate reports intentionally retain a failing older Hard oracle: the
earlier Easy STOP fixture expected Hard to have no stop/invulnerability, which
the later source-backed Hard repair supersedes. All 27 unchanged Easy cases
pass separately, and all 66 final Hard cases pass on each mapper. No runtime
change was made to satisfy the obsolete expectation.

`root49-easy-link-spring-e` adds the original Link spring powers, 400/800 under
Easy versus 450/950 under Hard. Its compiled CPU checks pass 3,472 cases per
mapper, preserving the calling contract and unrelated RAM; each original
control disagrees on all 512 Easy Link cases. Eight actual native spring
contacts per mapper verify landing, compression, fresh-A boosted launch and
live rebound across both modes and actor-slot extremes. These are seeded
components, not ordinary stage routes. The earlier D validator's whole-bank
byte identity was too strict for legitimate farcall target relocation; that
negative remains retained, and E verifies unchanged resident entry addresses.

Union F merges Bill's frozen full-vector/fractional-muzzle correction without
overwriting U's laser filter. G stages Mario V and Samus's head mode gate;
its first validator correctly rejected an unqualified full-symbol equality
claim because Mario adds nine aliases of existing exclusive-avatar state.
H explicitly requires all old RAM addresses and SRAM size unchanged and admits
only those named aliases, with zero added allocation. Both H mapper builds
preserve the full CHR payload and DPCM bytes. Its native `combined-h-m3-a` and
`combined-h-m5-b` each pass all six component groups: 48 injury, 36 pickup,
144 contact eligibility, 60 Bill/Lance drawing, 27 Easy STOP and 66 final Hard
effect cases. Six additional upright Samus head contacts per mapper verify
Easy suit0/1 brick breaking, Easy suit2 bumping, all Hard suits bumping and
unchanged horizontal position. Morph Ball's separate NONE/item interaction
is not certified by that head hunk.

`root49-easy-union-k/report.json` builds the further frozen Link source-rectangle
layer with all those changes. It preserves H RAM and CHR exactly. Fresh
combined K execution now passes Link's unchanged 162-case rectangle core on
each mapper, Mario's two source CPU oracles and all 34 native groups, and all
four Contra projection partitions per mapper (4,960 executions per mapper,
including repeated launch/ground-history controls). Mario V's
independent final handoff passes 34 native groups, covering dry/water motion,
pickups, injury, fireball terrain, Blooper immunity, gap support, spring/stomp
forces, Luigi control comparisons and actual pickup/combat/SFX queue groups.
The original V results and fresh combined K results remain separately bound.
Ordinary Mario route development on K is now active without duplicate large
captures; final recordings wait for the remaining art/behavior integration.

The seven generated includes that differ from the user's files in these
private builds compare exactly after newline normalization. Their raw bytes
remain preserved in the working tree. This is a source-format distinction,
not a claim of eight byte-identical private source files.

The later private integration is recorded below. Remaining body/cache
differences, ordinary pickup emergence/drop traversal, full integration,
all alternate attacks and final ordinary route recordings remain open.

`root49-easy-samus-bomb-m` implements the original Samus bomb boost's immediate
position update. Easy integrates both source velocity components and refreshes
the existing native collision projection, preserving the earlier jumped flag;
Hard retains its separate behavior. `root49-easy-cold-bank-n` moves that helper
and the already bank-called 199-byte coin-block closure into unused padding
after MM3 audio. Existing MM3 music addresses and bytes, DPCM, RAM and ROM size
remain exact. The relocation adds no further bank crossings to M.

N's actual native bomb groups pass 222 cases per mapper, including six bombs
created with controller B. The other 216 seeded components cover both modes,
horizontal velocities and fractions, jumped history, upright/ball forms,
three camera states and rotating bomb slots. The original K control fails all
111 Easy cases and passes all Hard cases. This verifies the existing native
hitpoint/cache projection, not every Flash body rectangle or an ordinary route.
Six further coin-block/music/audio regression groups pass on N. Their first
wrapper attempt omitted the old tests' menu bootstrap; that negative is retained.
The corrected wrapper explicitly runs the unchanged bootstrap and test bodies.

`root49-easy-union-t/report.json` combines frozen Link animation layer L and
Bill/Lance spread growth with N, regenerating their shared artwork once from
the source generators. Earlier R retains the one merge conflict; T explicitly
keeps both the Bill enemy-bounds entry label and Simon's whip envelope. S
retains a generator preparation failure caused by its missing atlas dependency.
T supplies the pinned atlas, builds both mappers and preserves all RAM,
audio/cold bytes and ROM size. Its internal build status retains the earlier
builder's R name; the exact artifact directory and hashes identify T.

T's independent decoded compiled-art review passes 1,134 original body entries
per mapper, excluding Link's nine deliberately replaced unused aim slots. It
also matches all 288 Link entries against frozen L, all 576 Bill/Lance entries
against frozen growth, and 28 weapon records per mapper. Part order and opaque
pixels remain exact; unrelated logical CHR banks and the original ordinary-body
plan remain unchanged. Native DMA validation is a separate evidence group.

Fresh T execution now passes all six shared component groups on both mappers
(injury48, pickup36, eligibility144, laser60, EasySTOP27 and HardINVUL66),
all eight Link native groups (1,044 cases including rectangle, animation graph,
END OAM/DMA and death phases), and 392 Bill/Lance growth executions. Its 263
actual hardware OAM/CHR captures match the compiled discrete spread artwork.
These are component results; ordinary routes and full roster coverage remain
separate. T remains private and the playable working tree remains exact U.

Source callgraph review revoked L's proposed freeze-resume clock reset. Old
Character.freezeTmrLsr calls Level.unfreezeGame, which resumes paused custom
timers; global animation timers continue throughout power-up and injury freeze.
Ordinary pause separately pauses/resumes animation timers with the remaining
delay preserved. The addendum is frozen in
`agent-lsr-easy-link-freeze-clock-addendum-m/source-policy-addendum.json`.
T still holds Link's phase during freeze; a separate private successor must
verify continuity without resetting it. No unverified reset was admitted.

The source-backed continuity successor is now frozen in
`agent-lsr-easy-link-freeze-phase-n/implementation-freeze-n.json`. It advances
only Easy Link's global modulo-36 phase during active pickup/injury updates;
real pause holds it. Both mappers pass82 native arenas, including all36 initial
phases for both freeze kinds, real52-frame Start pauses, recovery/next-live
updates and Hard/foreign/inactive controls. The unchanged T controls complete
all arenas with zero setup failures and8,712 phase disagreements per mapper.
It adds27 SAMUS bytes, no RAM and no bank crossing.

`root49-easy-whip-hot-v` adds inline admission before the generic terrain-probe
and enemy-envelope farcalls. Only Easy Link/Simon reach their existing source
helpers; foreign shots skip the unnecessary bank switch. V adds30 GUEST bytes
and preserves RAM/CHR. `root49-easy-whip-hot-x-profile/report.json` measures
the two paths on the same ordinary1,100-frame Pit input prefix:3,158 terrain
probes and788 envelopes per image. Each foreign call costs139 cycles before
and13 after on MMC3,119 before and13 after on MMC5. Skipped NMIs in that
bounded sequence fall32→19 and21→15 respectively. MMC3's recorded trajectory
fields remain exact throughout; MMC5 first changes motion at1067 as update
timing changes. This is a scoped timing measurement, not a full-game speed or
all-state equivalence claim. W retains the original profiler syntax failure.

`root49-easy-whip-phase-y` combines V with the frozen continuity file, preserving
RAM/CHR and requiring no additional layout move. Fresh native checks pass all
22 groups across both mappers: source rectangles, freeze phase, Mega Man buster,
Samus families, Pit/Rygar attacks, Ryu source weapons, Bass weapons, Sophia
independent weapons and Link/Simon weapon profiles. The first ten nested-test
wrappers used their output folder as TEST_DIR and could not load shared fixture
files; `native/checks-b` supplies the original fixture root and leaves all test
bodies/oracles unchanged. The negative wrappers remain retained.

Ordinary Pit routes are separate. The old S2 fixed sequence diverges on T and
dies in1-1; its MMC5 attempt stops at an obsolete S2-only observer assertion.
Fresh discovery B removes only that passive hard-coded observer and clears1-1
on both mappers, then dies in1-2. Fresh discovery C on Y clears1-1/1-2 on MMC3
and reaches1-3, then falls at frame10089. MMC5 C dies in1-2 at5922. All these
negatives are retained, and none certifies a complete Y playthrough. Remaining
source body/enemy rectangle corrections are separately under investigation.

`root49-easy-whip-phase-y-pit-prefix-d/report.json` independently replays C's
complete ordinary inputs from power-on through frame9600 on Y MMC3. All nine
passive CSVs match the discovery prefixes exactly. It confirms1-1,1-2 and live
movement in1-3, with an intentional frame-limit stop before C's later fall.
This is a partial ordinary route proof, with no end2-2 or recording claim.

The source-backed shared Bill spread-order repair is frozen in
`agent49easy-bill-fan-a/freeze.json`. Each mapper's candidate passes 1,320
actual native allocation cases across modes, variants, poses, facing, aim and
available slots. Each original control fails the 1,200 non-full-pool cases and
passes the 120 full-pool no-op cases. This is a bounded order/allocation repair,
not a claim that all projectile vectors or Bill's full behavior are certified.

`agent49-enemy-geometry-f/freeze.json` freezes the bounded Bill Hammer Bro
repair for normal, machine and spread shots. It uses the original primary and
head rectangles separately, with source-art pivots bound to actual native
OAM/CHR. It does not fill the gap between those rectangles. Source Fraction
edges are quantized once to Q8, with the sub-1/256px residual explicitly
qualified. The spread radius table moves byte for byte into the already
mapped Bill graphics bank; a441-byte helper uses cold space. No RAM/CHR,
header, size or audio change is required. Advanced Laser/Flare source bounds
and update order are a separate investigation, not certified by this repair.

`root49-easy-bro-union-ab/report.json` merges F with private Y. The initial AA
attempt retains a manifest-adapter error before compilation; AB accounts for
F's relative artifact keys and object-valued hash records. Both mappers build.
The status retains the earlier AA builder name; the AB path and exact ROM
hashes identify the actual images. Rebound unchanged frozen native cores pass
384 boundary and176 guard cases per mapper,1,120 cases combined. Independent
review AF recomputes19,954 actual receipts from original XML Fraction
rectangles and rejects963 overlaps which a filled bounding hull would admit.
These counts are for actual AB timings and differ slightly from standalone F.
Other-enemy proxies, Buzzy armor and inactive/dead Bro guards remain checked.

AF also verifies that the199-byte coin routine and320-byte Samus bomb helper
remain byte exact. The new441-byte Bro helper is inserted between them, moving
the bomb helper's address. The first AD verifier incorrectly assumed the
helper was appended and failed that assertion; its script remains retained.
This was a verifier-only correction. The expanded cold segment replaces only
previous FF tail space, and audio bytes/addresses, RAM, header and CHR remain
exact. AB's20 further native regression groups pass: all nine foreign weapon
fixtures and222 Samus bomb cases per mapper, including six controller-created
bombs each. These are component checks, not full-roster route certification.

AB also passes Luigi's complete ordinary Easy route on both mappers:
17,412 frames,17,411 polls, zero deaths, all six stages and all19 recorded
movement/controller fields exact against Y. Lag-flag totals remain100/48.
`ordinary-luigi-ag/report-ah.json` binds the complete native logs for the real
title mode0/selected8 guards. AG's first finalizer searched the truncated
driver output for those messages and left a negative; AH corrects that log
source without altering code, inputs or emulator execution. These interim
runs are unrecorded and do not replace final integrated lossless recordings.

`agent-lsr-ryu-source-body-o/implementation-freeze-o.json` freezes the supported
Ryu source body correction: original80 source frames use standing27px,
air25px and crouching15.75px profiles. Native integer actor contacts use
ceil/floor endpoints of the current Q16 player body. Incoherent native
background-relocation states retain an explicit fallback. This does not
replace enemy proxies, enemy AI or source enemy-cache order. A single cache
byte appends at7FE4, preserving every prior RAM global.

The native moving-platform consumer requires a temporary horizontal broadphase
after exact source-body/platform overlap. Its native CLC/SBC previously dropped
fractional edge equality. Only horizontal bounds are temporarily conservative;
source vertical bounds remain current and all edges are rebuilt afterward.
Final O passes142 body cases,40 platform lifecycle cases,24 fractional-edge
controls and20 actual launch/wall/ceiling/water arenas per mapper:452 total.
The body controls include the actual retained Blooper incident's camera,
fractional velocity and attack-age setup. Old T has314 body disagreements per
mapper. Returned AXYP/SP/R0..7 equality is checked for the142 body components;
full stack/all-RAM equivalence is not claimed.

`root49-easy-ryu-union-ai/report.json` three-way merges the seven old and one
new O files over AB. Both builds pass, with all prior RAM labels exact,
only7FE4 appended and ROM size/header/CHR/audio unchanged. It adds844 cold,
33 COLLISION,25 OBJECT,5 EXPANDED,18 ROSTER and3 SPECIAL_MM bytes. GUEST,
SAMUS and Bill graphics sizes do not change. MMC5 OBJECT has2 bytes left;
EXPANDED has1. Fresh execution on actual AI passes all eight rebound O
component groups and all20 foreign-weapon/bomb groups, including222 Samus
bombs per mapper. Frozen component bodies and case matrices remain unchanged.
These are targeted results; the corrected Ryu ordinary route is being adapted
separately rather than treating an old movie as a geometry oracle.
AI's four Bill boundary/guard groups also pass1,120 cases. AL initially stops
one MMC5 boundary run at case298 with the emulator Lua one-second execution
limit. AM repeats that exact core and assertions without changing the timeout,
source, ROM or case matrix and completes all384 cases. AL's partial evidence
remains retained. Independent review AN recomputes19,955 source receipts and
964 rejected hull-gap contacts on actual AI. The timing-dependent receipt
counts belong to AI, not standalone F or AB.

Luigi's fixed ordinary Easy route now passes all six stages on private K and
Y, on both mappers, with17,412 physical frames,17,411 polls and zero deaths.
All19 listed movement/controller fields match at every frame. The corrected
handoff is `specialist-mario-easy-hard-source-a/routes-y/luigi-full-route-handoff-b.json`.
Its original A handoff remains retained with an explicit profile erratum:
render.lagNmi is a physical-frame boolean, counted directly. Actual Y totals
are100 flagged frames on MMC3 and48 on MMC5. OAM per-scanline maxima are
observations and do not by themselves prove a graphics defect. These runs are
unrecorded interim tests; final integrated lossless recordings remain required.

Pit discovery E finds a real controller-only1-3 platform crossing on Y MMC3.
Its winning branch is independently replayed from power-on with exact input
polls, frames, target and all10,240 RAM bytes, without state loads. Continuation
F clears1-3 and enters1-4, then stops at a controller assertion while the native
firebar cache is being rebuilt. The cache publishes its part count
incrementally; H only defers that tactic's decision during incomplete updates.
G's broader input-hold experiment instead changes a platform jump and dies;
that negative is retained. H clears the first three stages and dies against a
castle flame while the old policy attempts to duck. Discovery I finds a new
controller crossing there and independently cold-verifies it with all10,240
RAM bytes. These are partial route advances, not an end2-2 or recording claim.
Continuation J then dies on the next raised bank. Discovery K independently
cold-verifies its new controller crossing to X2080/Y128 before Bowser.
Continuation L's old over-jump tactic dies against Bowser; discovery M instead
cold-verifies a genuine crossing to X2241/Y128. All negative continuations and
search/verification evidence remain retained. No runtime changes are made to
obtain these ordinary controller branches.
Continuation N clears1-4 and enters2-1 at14788, later collecting an ordinary
power-up. It stops at a finite pipe-cap controller assertion with the game
still alive at X1633/Y176. Discovery O independently cold-verifies a new real
controller crossing to X1808/Y176, retaining the earlier negative policy.
Continuation P later falls at X2272/Y242 in2-1. Its real controller stream and
ordinary power-up/injury sequence remain retained for the next gap search.

The advanced Bill/Lance C2 layer is frozen in
`agent49-enemy-geometry-advanced-g/freeze.json`. It corrects Hard Laser/Flare
source velocity, six-pose muzzle origins, Laser segment spacing and threshold
reveal, diagonal Laser collision bounds and Flare's previous-visible-position
collision cache before orbit publication. These are source2.02 component
repairs, with Q8 scalar quantization explicit. Native expiry, confirmed-hit
ending, Flare armor and rotated/end graphics remain separate successor work.
The held-button cadence is under verification rather than assumed defective.

`root49-easy-advanced-union-ap/report.json` three-way merges those three frozen
files over AI. It preserves the root foreign-shot guards, Link phase repair,
Ryu body repair and shared art. Both mappers build with428 source files and
unchanged prior RAM, header, CHR, ROM size and all audio bytes/addresses.
Relative to AI, GUEST shrinks176 bytes, EXTRA grows286, SPECIAL_ROSTER
shrinks62, BILL_GFX grows1303 and the cold segment grows953. The tightest
remaining areas are BILL_GFX21 bytes and MMC5 cold59 bytes. The earlier AO
host verifier wrongly treated an AUDIO-named BSS segment as ROM data; AP
filters actual RO audio and checks all RAM separately. AO remains retained.

Fresh execution on actual AP passes all40 targeted native groups: AQ runs
all792 frozen C2 cases and unchanged source oracles, AS runs all452 frozen
Ryu body/platform/terrain cases, and AT runs18 foreign-weapon groups plus222
Samus bomb cases per mapper. Every hook is rebound to actual physical bank,
address and instruction bytes. AR independently verifies all1920 compiled
orbit scalar bytes, unchanged72-byte spread radius data, all seven shared AI
graphics datasets and the U foreign-shot render guard. Audio preservation is
checked in the build admission. These are component results, not complete
ordinary route or final recording certification.

AP's existing terrain receipts measure Flare Motion-to-Published foreground
work with equal NMI serials: MMC3 medians1309 cycles right and1420 left,
versus1401/1402 in the retained earlier B profile. This is a bounded combined
ancestry comparison, not isolated placement or whole-game speed attribution.
The AP MMC5 long fixture observes652 right and1408 left Motion/Step/Publish
entries, with1408 left-only scalar fetches and no right scalar fetch. The
native age limit remains240 in this layer; full source expiry is not claimed.

Pit discovery Q independently cold-verifies the next ordinary2-1 gap crossing
on Y MMC3. Continuation R clears the first five stages and enters2-2 at19332,
then dies against a swimming enemy at21170. Discovery S cold-verifies a
controller branch to X2080/Y65 at21259. Continuation T later dies at21633
after the old controller swims above the viewport and descends into another
enemy. No runtime/source change is inferred from these controller negatives.
The next bounded water search retains all earlier inputs, captures and failed
continuations. These Y routes do not certify AP.

`profile-au.json` strengthens the retained Flare comparison: all52 paired
Motion/Published spans have the exact same case, slot, update age and every
recorded projectile field before and after. Right20 paired deltas range-92
to-34 cycles with median-92; left32 range+18 to+63 with median+18. Both sides
remain reported. The earlier MMC5 B profile does not exist, so no comparison
is invented for it.

AV freshly measures the real1100-frame ordinary Pit prefix on actual AP,
observing selected6/mode0 on all560 gameplay-era frames. Each mapper executes
3158 probes and788 envelopes at exactly13 foreground cycles, with zero calls
to the inapplicable whip helpers. All15 listed movement/controller fields
match V on every frame; skipped-NMI totals remain19 MMC3 and15 MMC5. The
intentional frame-limit stop is not a full route certificate.

The specialist's immutable K Easy Mario handoff records full fixed clears on
both mappers:16991 frames/16990 polls, zero deaths and actual2-3 control after
entry16967. Four takeoffs use real moving platforms. Two ordinary native SMB
corner catches at7403/10762 are explicitly classified; no glitchless claim is
made. The mapper routes differ in vertical fields on56 castle frames before
reconverging, rather than being reported as identical.
Root AW independently carries those exact controls to AP on both mappers.
Both full audits pass, actual title mode0/selected0 is observed, all19 listed
movement/controller fields match their respective K mapper at every frame,
and all114 dry fresh-grounded-A receipts remain exact. AW is an unrecorded
interim route proof, not the final combined release or lossless recording.

Pit discovery U cold-verifies another water branch but continuation V dies
six frames after that target. A farther-target search W independently
cold-verifies X2976/Y96 at22029. Continuation X then clears all six stages on
Y MMC3 in23235 frames/23234 polls with zero deaths, enters2-3 at23211 and
demonstrates24 further control frames. BB's fresh fixed power-on replay
passes and all nine actual input/audit CSVs match discovery byte for byte.
Its host finalizer then incorrectly requests a tenth file containing policy
decisions, which fixed replay does not make. BC reuses that completed native
execution, corrects only the comparison file list and preserves the BB
exception/script/report. BC also transfers the ordinary inputs to AP on both
mappers. All earlier failures remain retained.

The human-authorized raised recording cap is now honored by all three host
layers: runner, lossless assembler and native per-segment budget parser.
Their obsolete30GB upper ceilings were removed; positive numeric parsing,
overflow rejection, retained-file accounting, reserve and per-segment guards
remain. `root49-capture-raised-cap-ax/report-ba.json` binds52 actual Win32
host cases, including valid30GB/50GB/uint64 limits, overflow rejection,
under-budget denial, sharing, junction and retained growth controls. Those
host API stubs do not claim native recorder coverage.
Separate AY native recording on AP MMC3 at50GB captures650 physical frames
as649 images. Every decoded RGB frame and continuous PCM sample matches its
retained parts/WAV after assembly, timestamps pass, and all650 trace rows are
exact against the ordinary unrecorded AP Mario prefix. The first AX attempt
corrected only the Python ceilings and retained a native configuration
denial; the subsequent early audit read an uninitialized preference. That
negative is preserved. AY is a recording calibration, not a completed route.
No game ROM, published U source, emulated RAM or registers change in this
capture-tool repair, and no retained files are deleted.

BC retains both AP Pit movie transfers as failures: MMC3 dies at3352 and
MMC5 at5385. On MMC3 the first movement/NMI difference is1221, one skipped
update; no shared gameplay defect is inferred from the fixed-input timing
failure. The Y full clear remains valid and does not certify AP.
Ryu's frozen O/S clear likewise has25280 frames/25279 polls, zero deaths and
nine complete CSV streams exact across discovery/fixed/passive runs. Both AP
transfers die at5814. Their title identity and exact consumed input prefixes
are verified; they remain failed transfer checks, not source defect claims.

BD adds actual hardware-bank/instruction guarded entry-to-real-return timing
on the ordinary3000-frame Pit prefix. It excludes NMI/IRQ cycles, checks real
return stack depth, reports incomplete final spans separately and does not sum
nested inclusive routine costs. Its Y run matches all3000 unprofiled trace
rows exactly. The largest measured weapon subcost is terrain: AP averages
1244/1240 cycles per call on MMC3/MMC5, against weapon-update averages4309/4287.

`root49-easy-pit-empty-be/freeze-bi.json` freezes the resulting18-byte
optimization candidate. Only selected Pit with bullet types26..28 reuses the
existing distinct-cell empty-air terrain path. Actual compiled arrow extents
are symmetric and unchanged; solid dispatch retains facing and row order.
Both builds preserve all old RAM, header, CHR, size, audio bytes/addresses and
linker configuration. No additional RAM or bank crossing is introduced.
BF compares5520 seeded native cases per mapper against AP, including both
modes, three tiers, both facings, all16x16 offsets, page/Y seams, protected
ground, masonry, question/transparent tiles, partial health and opposite
corner order. No checked map/health/solid/coin/time-map hash, player Q16,
reward/enemy/projectile or foreground sound-write observable differs. This
does not claim complete RAM/CPU-flag/stack-scratch equality or independently
certify the old behavior against source. BH also passes all20 foreign-weapon
and Samus bomb groups, with222 bombs/map and six controller-created each.

BG measures the candidate on the same ordinary3000-frame input stream.
Weapon-update mean cost falls4309→3305 cycles on MMC3 and4287→3261 on MMC5;
terrain mean falls1244→535 and1240→537. Locally flagged lag frames fall219→185
and180→107. Changed timing produces different later world states, so these
are bounded real-play measurements rather than an isolated full-game speed
percentage. The controlled solid-contact path can cost up to555 additional
cycles; that regression is retained explicitly alongside the empty-air gain.
The candidate remains private pending final source integration and routes.

The advanced Bill successor remains under development. Its new cold placement
preserves old Zelda audio data/addresses, and bounded fair rendering gives
short active/ending shots draw opportunities while retaining live pickup/HUD
opportunities. Physical lag can repeat a buffer, so fairness is measured in
new draw opportunities and actual DMA is checked. An E relocation defect is
retained: Easy AvBillInput still near-jumped to a return in the former bank.
A separate F fixes that closure and adds both-mode primary controls. Hard art,
pool or damage success alone does not certify that Easy return or source
birth/expiry behavior. E is not integrated.

Ryu's9461 incident is separately proved to be a missing head/corner response.
An actual private AP adaptive run reaches the same spatial/Q16 incident at
9760, observes native JumpUsed1 and keeps X/qVX unchanged while responding at
PY153/fraction0/qVY$00D555. The source-backed candidate uses501 bytes in a new
cold tail and appends receipt7FE5 without moving old RAM/audio/CHR. Both maps'
37 boundary/fallback controls pass. The later controller fall9787 is retained;
the old route depended on the missing ceiling response. Frozen O/S remain
unchanged, inherited regression checks and final integration are separate.

The broader roster audit is still active. Existing full videos and lossless
captures are retained under the user-authorized raised storage limit. Earlier
S2 recordings remain evidence for S2 and do not certify this new mode update.

BJ transfers the frozen S2 Scrooge controller streams to BE. Both fail in1-2:
MMC3 at6767 and MMC5 at13987. BK runs those same controls on parent AP; the
endpoints and all19 movement/controller fields match BE for every observed
frame. Seven other native CSV streams, including sound events, CHR, OAM and
render telemetry, are byte-exact. Scroll register values, order and physical
frame are exact across24288/53728 writes;2780/7740 rows differ only in
subscanline timing. These are negative route transfers with a controlled
foreign-character comparison, not full Scrooge clears or a gameplay diagnosis.

BJ/BK's marker classifier incorrectly expected `emu.log` to reach the native
console. Their original results remain retained. The additive BL review adds
explicit JSON/console identity receipts on four fresh650-frame cold prefixes
(AP/BE and both mappers), each byte-exact against the corresponding original
trace prefix. Actual Scrooge12/Easy0/shadows-off is observed at412. BL reuses
the complete native negatives and does not rerun or reclassify them as clears.
Its final report is `root49-easy-pit-empty-be/ordinary-scrooge-review-bl/report.json`.

Independent root review BM rejects the advanced Bill successor's provisional
speed-only384-row lifetime theorem. `Character.checkPlatform` applies carrier
displacement outside `vxMax`; the source follow camera therefore can advance
faster than Bill's150 walking speed. This identifies a missing proof premise,
not a demonstrated384-update gameplay failure. The specialist agrees and is
replacing that draft with a finite world-extent argument and measured padding
for exact additional orbit data. No arbitrary runtime age kill or original
scalar precision change is admitted. Current art/pool/lifecycle checks remain
separate from this unfinished data-coverage proof.

Ryu's simplified E successor removes the optional side-bypass, receipt and
reset layer. It uses497 cold bytes, adds no RAM and leaves SAMUS/OBJECT code
unchanged. All168 new head controls and452 inherited body/platform/edge/terrain
cases pass across both mappers; actual row51 side offsets8/24 are below the
canonical ceiling after response. The real9760 incident preserves X/qVX,
sets PY153/fraction0/qVY$00D555, and causes no native side clamp. The later9787
fall remains a controller-route failure. E remains private pending freeze and
combined-layout checks; unsupported source-body/terrain combinations remain
outside this scoped repair.

The final Ryu E packet is now frozen and root-reviewed by BP. The compiled
497-byte closure has47 near references checked per mapper, no additional RAM,
and no receipt/side-bypass layer. The earlier501-byte/7FE5 proposal above is
superseded. New combined BQ places RYU_COLD immediately after BILL_COLD in
physical bank25, with326/342 bytes remaining. Actual combined BS passes all168
new head controls; BT passes all452 inherited body/platform/edge/terrain cases.

The advanced Contra H/M successor is frozen in
`agent49-bill-advanced-parity-h/freeze-m.json`. Root CB verifies4152 retained
receipt files, the439-file source catalog and unchanged original oracles.
The rejected speed-only384 proof is superseded by an explicit source-global
visual envelope and4096 exact orbit rows. The largest original source map is
6400 NES pixels; the conservative castle-axe camera bound is5356. Horizontal
and vertical live-center bounds require at most3666/215 updates, respectively;
no runtime age kill is used. Native camera command extent remains a data
measurement rather than a camera-clamp theorem. Exact per-area camera parity,
browser rasterization and source/native timing/rounding limits remain explicit.

BQ combines frozen H/M, Ryu E and Pit BI through an actual retained three-way
merge. Actual CA component checks pass2100 Contra cases per mapper:100 mode,
720 shot-pool,64 lifecycle/armor,48 birth contact,96 art/scheduler/profile,
1048 viewport/cache/global/late expiry,16 genuine-B birth-domain and8 overload
stress arenas. Each map executes696 standard late loads and6240 overload loads
with physical C-bank/shadow/stack restoration checked. Source-valid admission
and deliberately excessive ten-Flare hardware stress are separate claims.
BR passes20 foreign weapon/Samus bomb groups, including222 bombs and six
controller-created bombs per mapper. BZ independently compares32768 compiled
orbit scalar bytes per mapper and36 old audio/DPCM segment addresses/bytes.

BV runs5520 original seeded Pit terrain cases per mapper on BQ; every checked
map/health/solid/coin/time-map, Q16, reward, enemy, shot and audio observable
matches both original AP and BE receipts. Compared with BE the foreground-cost
delta is -2..+4 cycles, median0. The ordinary3000-frame BX measurements retain
the gain: weapon means3303/3271 and terrain535/537 cycles on MMC3/MMC5, with
184/108 locally flagged lag frames versus parent AP219/180. Same controller
inputs do not imply identical later worlds after timing changes; this is not
a whole-game percentage or universal no-lag claim.

Host negatives remain retained. BU rejected two legitimate alias names while
all old addresses were unchanged; BV admits exactly BillDrawTurn=$7F7F and
BillDrawOtherCursor=$7F80, without allocating RAM. BW's copied birth oracle
used a hardcoded old output root; CA changes only that host-root expression,
reuses all four completed native groups, and preserves every native core and
assertion. The missing case count in the late-load report is checked through
its696 actual-fetch/hardware-restore receipts. These were host failures, not
native gameplay failures.

The disabled-Crossover compilation check CE found a duplicate baseline-only
HandlePowerUpCollision label. CF removes it and exposes an unguarded guest
water-policy call. CG additionally restores the original AreaType test under
the baseline branch. Both baseline mapper builds now pass, with MMC3 exactly
matching the existing workspace baseline. Both crossover ROMs are byte-exact
to tested BQ, so the native BQ evidence still applies without another runtime
change. All unsuccessful build artifacts and logs are retained.

Working checkpoint BY installs the440-file CG source and exact tested BQ ROMs
in the workspace. Its manifest is
`build/checkpoints/roster-audit-v49-easy-hard-by/manifest.json`; the prior U
checkpoint and a backup of every replaced existing file remain available.
MMC3 SHA256 is8c79f8f0e8f0c0a0d987d8d828aa2bcd377df89a5c4f4b4cf6c54984a3a947be;
MMC5 isee62d3b7869b9a68430d5b8e0f3fadad1a4878a35e237cfcf6b81c903a587f58.
This is an interim working checkpoint, not an accepted final release.

CC verifies ordinary Easy Mario through2-2 on both exact BQ images:16991 frames,
zero deaths, six stages, all19 movement/controller fields and114 dry takeoff
receipts exact against each frozen K proof. The specialist also freezes Hard
Mario BQ clears at16987 frames per mapper, zero deaths, all19 fields and116
takeoffs exact K. Final integrated lossless recordings remain required.
Luigi/Bill/Simon controller work is moving to this stable runtime. Root CH's
old S2 Mega Man input transfer dies at1169 in1-1, with real Easy0/character1/
outlines-off identity proved; its endpoint shows a Goomba contact after the
second pipe. It is retained for controller adaptation and does not establish
a source movement or collision defect. All13 characters, alternate/upgrade
coverage and final media remain active obligations.

Current BY ordinary-route continuation (root CW) independently cold-verifies
three Mega Man controller branches: CI passes the second-pipe Goombas at
1325/X844/Y176, CP crosses the first underground pit at7112/X1420/Y176 with a
naturally collected mushroom, and CU crosses the final moving-platform chain
at8904/X2581/Y128/power1. Each final power-on verification compares every
controller poll, frame, target and all10,240 RAM bytes without loading a state.
Discovery uses only untouched opaque native states. CW is
`build/verification/root49-by-megaman-progress-cw.json`, SHA256
4631a5e79a46471ed0e19265024fa013cab7528f81328d0c665dffdd0426e6a8.

CR exercises the naturally acquired tier1 charge with75 held updates and
observes weak buster type2. This does not prove tier2/full-charge, every special,
every enemy kill or a complete route. All partial deaths remain retained.
CN's physically guarded jump-consumer replay matches the CL negative; isolated
controller A pulses were not sampled while grounded, so that observation is
not a runtime movement defect. CM malformed observer Lua and CQ's nonexistent
MmCharge logger symbol are retained host failures; CN/CR repair those host
issues without changing the ROM. CT excludes a retracted Piranha from the
controller's waiting target list and reaches the final lifts. CV then jumps
onto the side exit pipe and waits until timer death; CX changes only ordinary
buttons to approach that pipe from its side. No engine change is inferred from
these controller failures.

The specialist freezes current Luigi Easy clears at17412 frames on each map
and Hard clears at17414 frames on each map, six stages with zero deaths.
Easy preserves the accepted historical input stream but is not a movement-
identity claim:1129 MMC3 and1100 MMC5 frames differ from AB at4969..6181,
reconverging at6182. Hard adds two real controller frames at the actual1-2
entry. Its MMC3 replay matches discovery;113 movement frames differ on MMC5
while both endpoints and all stage clears remain valid. These are full
ordinary route proofs, not final recordings or complete upgrade coverage.
The frozen BQ route index is
`specialist-mario-easy-hard-source-a/routes-bq/ordinary-route-complete-index-a.json`,
SHA256449e1f17f01d523ec29ea41162aaa182a44cdb886d879deff6f69c3145fe7d53.

Simon reaches the BY castle axe/victory state but the current continuation
does not advance to2-1. This is an active native victory-sequence lead, pending
guarded writer/source investigation. Scrooge has a real Bowser pogo strike and
clears the first five stages; the underwater route remains controller work.
A separate private Contra body candidate is comparing the actual source
standing/jump/prone hRects and consumer predicates. Inclusive source actor
rectangles, tile/head queries, integer native enemy proxies and bitmap
firebars have separate domains; no blanket source-terrain or contact parity
is admitted. None of these candidates changes installed BY yet.

The human's later retain-lossless/raise-cap instruction supersedes the original
30GB request. The internal workspace ceiling is now55,000,000,000 bytes for
future runs; old frozen receipts retain their actual historical caps. Existing
specialist phase budgets remain unchanged and no captures are deleted.

CX's ordinary side-pipe approach clears1-2 and enters1-3 at10111. CY then
independently cold-verifies11365/X1280/Y64 through the middle treetops.
CZ reaches the later moving-platform gap and its partial death is retained.
DA discovery reaches11999/X1900/Y112, but its first independent verifier exits
4294967295 without a PASS or latched Lua failure during a host timing
interruption. The original negative is unchanged. Separate DB replays the
exact winning inputs, target, RAM oracle, verifier core and power-on settings,
and passes all10,240 RAM bytes and exact frame/poll/target. DB report SHA256 is
2a42f81605c93077cd379e3853efeaf1b4844ff144fcf6d4c976aacc1bc1d38b.
DC continues only ordinary buttons from that independently verified prefix.

Simon's separate passive replay now confirms the castle stall's writer cause
without changing any of nine complete36000-frame audit CSVs or the tenth
base observer. At14063, OperMode2/task2/engine8 forces Right1 but inherited
RgAttack21 routes through guarded Stop/ZeroX and writes all three qVX bytes0.
The same path repeats in35970..35999 while RosterWeapons count stays12776.
The frozen actual review SHA256 is
2fd03a12e9d5bb141410b641b5febe9be29fa59da93662e281678535f050a234.
A narrow automatic-victory movement repair remains private and unadmitted.

Scrooge's current ordinary MMC3 discovery completes all six stages at20170,
with zero deaths and actual2-3 entry20146 plus25 control frames. Its final
fixed audit and MMC5 proof are still pending. The first fixed replay was
interrupted by the host at an incomplete trace, with a negative remaining
timeout; no gameplay failure is inferred. Its negative remains retained and
the exact tape is rerun under a fresh tag. No final recording claim follows
from this discovery.

Scrooge's fixed MMC3 O replay now passes20170/20169, six stages and zero deaths,
all19 movement/controller fields exact M, with81 real dry takeoffs. Handoff
`specialist-scrooge-by/handoff-m3-a.json` SHA256
dbc2121e79575e652e425fc0b6bba466143510bd0509d61482f3ba3a3616cfda;
companion freeze SHA256
c669a9f839f10b18bdae3d0da5a689c3086305d9d1b90d8db38033c91f2d75ef.
MMC5 continuation and final media remain open.

Mega Man DE's bounded search does not reach1590, but its best controller tape
independently cold-verifies14378/X1346/Y112 with all10,240 RAM bytes. Fresh DF
adds ordinary Down+A slide alternatives and cold-verifies14626/X1590/Y128,
again with all10,240 RAM bytes exact. The input stream has82 Down-bearing polls;
that alone is not an actual slide-state proof. DH passively logs real slide
changes while consuming the fixed prefix, then continues controller discovery.
DH uses discovery-fast, so a complete fixed full-frame audit remains required.

Private DG copies the441-file frozen Bill body J catalog and eleven pinned
generated audio includes, then applies only CG's disjoint baseline guards in
collision.s. All four builds pass: crossover NES bytes are exact frozen F on
both mappers, and disabled-crossover NES bytes are exact CG on both. DG report
SHA2563252ea899aa312e7cf8efefeabed360401d32589f468ddb6997dacc7dcb3ad43.
No main source/artifact is replaced. Source-body final packet admission and a
separate exact-arithmetic cost reduction remain pending: measured Bill selector
adds162..166 and publication554..566 cycles per relevant update. Source water
epoch, fractional equality, seam and actor-consumer oracles must be preserved.

Simon's first private B movement gate passes binary/layout guards but adds20
ordinary guest cycles and shifts the real tape's input/NMI phase; its early
death is retained as a pacing negative. Rare-only C instead leaves ordinary
hot code literal and changes only victory farcall operands, appending28 PLAYER
and184 RYU_COLD bytes. The actual I-prefix continuation now clears the castle
and enters2-1 at14784, then dies later at15829. Source getAxe releases buttons
and enters WATCH without canceling attacks; WATCH continues update/animation.
C advances finite action/shoot timers and pending release events. Automatic
native movement during remaining attacks and non-ticking victory projectile
pools are explicit adaptation limits, not a full Flash WATCH equivalence claim.
Native ABI/cycle/component checks and final freeze are still pending.

DH's passive prefix observer confirms actual Mega Man slide pose12 starts at
14496,14561 and14592, with normal ends at14524,14564 and14618. This exercises
the ordinary Down+A ability without state grants. The discovery-fast
continuation dies14848 at the later castle fireball/step. DI searches from its
real safe14804 grounded prefix; a separate cold verifier remains mandatory.

Scrooge MMC5 V guards the actual12033 contact: body[139,116,159,140] touches
Bowserfront[159,130,175,149], while strict pogo[140,116,158,140] misses by one
pixel. The real call chain reaches injury with no valid pogo strike or flash.
This matches the pinned intentionally narrower DuckTales D291 pogo interval
and the already documented generic-body inclusive edge adaptation. It does
not justify enlarging the attack or granting immunity to the body's outer
pixel. Ordinary timing work continues with that concrete limit retained.

The Bill F correctness control is now frozen as freeze-m.json SHA256
36910e7b6568bf15c31d59d53326a03ac0ce2007a4f7aae9f437d950e31ccc70.
DJ independently verifies its211 receipt files,441 source paths, actual
old-RAM/audio/header/CHR invariants and byte-exact transfer to DG runtime;
DJ report SHA256b4f7902dac615fb6b4265f688b6d8495ba06306a3ef3e6cc572e7a8095392e9c.
There are9978 positive cases across both mappers: per mapper2784 body cases
(including1176 actor-consumer cases),2112 head cases,88 flow cases and five
real area resets. The two original enemy contacts still overlap the corrected
native-proxy rectangles and remain source-enemy unclassified. The measured
foreground cost motivates a separate exact-threshold descendant; F remains
the immutable correctness control and neither F nor DG is installed in main.

The later optimized N packet is frozen as freeze-o.json SHA256
c0ee2a77e4bc72442588cc7618b96ce256d3f5aac725e9662c8e1cdef0d16049.
Only bill_source_body.s changes from F: bank9 cold code grows774 to853 bytes;
the rest of both ROMs is literal F. Independent XML endpoint comparisons cover
3,145,728 equalities. Both mappers pass the original9978 source cases. Matched
5568 entry vectors save231..298 publication cycles, with group medians260..298;
one interrupt-crossed MMC3 pair is excluded. This is versus the F correctness
control, not a whole-game improvement measurement relative to BY. The retained
MMC5 jump-input timing negative still disallows whole-trajectory identity.

Frozen rare-victory C now has complete native/component and source-WATCH scope
receipts. Root DO independently recomputes its real Simon prefix/clear evidence
and all native/source pins. The earlier handwritten PLAYER28/free5 budget is
incorrect: actual compiled helper_size30 was already correctly recorded in C's
build report. Additive budget-qualification.json preserves the original freeze
and records30 PLAYER plus184 RYU_COLD bytes; with Bill's8 PLAYER bytes the
combined size8140 leaves3 MMC3 bytes or19 MMC5 bytes. EasyLink's separate
RgBillBurst framegraph is an additional known victory-art limit; advancing the
common RgAttack clock alone does not establish its animation parity.

Private DQ combines CG baseline guards, N and C across442 source paths. All four
builds pass; baselines remain exact CG. Both crossover ROMs differ from N only
in216 actual bytes: two rare call operands and the exact appended C tails.
Root DR executes120 actual-DQ Mario/Luigi fallback cases against N's original
controller, preserving all registers/flags/SP/10240RAM/banks/ordered writes
with only the measured10/14 rare cycles. Actual-DQ specialist rebinds pass9978
Bill source cases and5568 matched profile vectors, plus132 victory/release/
complete-inventory cases. Actor1176/map remains a subset of the body tests.
Root DV verifies144 Bill receipt files and the independently frozen victory
packet before admission. No complete source-WATCH projectile/form-art claim is
introduced; existing enemy/terrain/firebar/body scope qualifications persist.

Working DU is installed, manifest SHA256
d518efb726559ac120ec4517a73e045e674ec9219a0317884efb8be2ddeeb477.
All442 main source hashes and NES/LBL/MAP/DBG artifacts match actual-tested DQ.
Twelve changed/new source paths are backed up; the complete source archive and
both prior BY ROMs remain retained. MMC3 ROM SHA256
2af5234c1a15a96e85779db49ce10c724387ae9bfdadab6ef82ed19d961460b0;
MMC5 ROM SHA256
6c667ed0a0891b02a31fae7e51e27de2080eeb9712281b290e09dab7ea293e0b.
This is an interim working checkpoint, not final all-roster acceptance.

Root Mega Man's BY route clears the actual castle and enters2-1 at16164 (DN),
then dies16861 after jumping toward the Piranha at744. DP independently cold
verifies an ordinary branch to17072/X980/Y176 beyond that pipe. These are BY
results. Replaying the old tape on DQ (DS) dies earlier at7584 in1-2; no old
route proof is relabeled a DU clear. Fresh DQ DT reaches7711/X1809/Y176 with
independent cold proof, but its ordinary DW continuation dies two frames later.
DX adds a read-only actual-physical-bank/eight-byte injury owner observer;
DY searches from the genuine earlier7660 ledge. No runtime edits or state
grants are used. The natural classic charge and source slide observations from
BY remain historical evidence, not automatically transferred DU coverage.

Historical frozen BY Mario/Luigi Easy+Hard both-mapper full routes and Scrooge
Easy MMC3 fixed20170/20169 are retained. Scrooge MMC5 and Simon C ordinary
continuations remain active; they use explicit immutable ROMs and their proof
scope is preserved across the DU install. Future DU routes need fresh replay.
The workspace cap remains55GB with every lossless and negative capture kept;
Scrooge's bounded phase ceiling is extended600MB to800MB within that cap.

Subsequent ordinary testing found a real F/N head-consumer regression, so DU is
no longer the current working build. A genuine fresh Bill Right+A at the first
pipe (frame1650, X722.25/Y171.55556) queries body pipe tile20 at736/176. NYSpd
then cancels upward speed before side resolution. The preceding source main
right735.752136 is left of tile736, with vertically overlapping bounds; both
original HitTester.checkLastHitPoints implementations select sideRight rather
than groundAbove. Full-width head-cell correctness alone did not establish the
native consumer's axis ordering. This concrete failure takes precedence over
the positive seeded geometry fixtures. A source-aware correction stays private
pending actual incident and consumer controls; it must not bypass pipes in
general. The Bill phase ceiling is extended4.5 to4.8GB within global55GB.

Working EC restores every Bill F/N hunk to frozen C's BY-parent behavior while
retaining the rare castle repair. Its manifest SHA256 is
1618a568e0d14e8681efd0dbfc84d68bec1636bfb34703e3c5b9eddea73759d1.
All441 main source paths and both crossover ROMs match frozen C; a fresh private
four-build reproduction also confirms both exact CG baselines. Nine reverted
source paths are backed up, including our added bill_source_body.s; its sole
main copy is removed after exact backup verification. All DU/DQ/N/F copies,
proofs and capture files remain retained. Current ROMs are C MMC3
1d1c0a1024b4cb84edf2b46dca01eec0b28e415ed56292c6a8010dcb7d177db4
and MMC5
bccff505f56396a14cd7b64036d75071092b34c5d3accbf7fc1dd2e9548ca65b.
The temporary DU admission is retained as historical component-scope evidence,
not relabeled a full terrain or final-route acceptance.

DQ Mega Man DX/DZ reproduces DW's entire7713-frame trace and7712 controller
polls literally with a passive bank/eight-byte observer. The actual injury
owners are Goomba0 at1161/184 (frame6867) and Goomba2 at1823/184 (fatal7713),
both grounded, at the native boxes' inclusive horizontal edge. Nearby plants
are not these owners. The natural tier pickup occurs6796 and is lost after the
first injury animation6927; this explains the observed unpowered later route.
KillPlayer's clobbered cpuX0 is not the owner; earlier guarded injury hooks and
ObjectOffset2 retain the fatal owner. DZ report SHA256
9e33736084ec3d9c035d7ffc8f7c1ba687762b9c6cce09aabf61ab3b9f200a54.
DY independently cold-verifies7858/X1980/Y128. Its EA ordinary continuation
clears1-2 and enters1-3 at9761, then dies10261 to Goomba1 at648/40; the actual
injury hook records player636/Y22. These remain DQ-scoped partials. Fresh EC
ordinary routing now starts from the retained BY DM pre-axe prefix, where C's
ordinary instructions are still literal BY, with a separately rebound observer.

The separate EasyLink WATCH follow-up D is private and based on immutable DQ.
Its only source hunk is guest_victory_control.s:60 additional RYU_COLD bytes,
zero PLAYER/RAM growth, existing source FrameCycle before movement and Animate
after the full original BG suffix. Both mapper/baseline builds pass and native
source-phase checks pass; strict compiled foreign/stack and final freeze remain
pending. Later admission must merge its sole helper onto EC or a corrected Bill
successor rather than restoring the rejected Bill consumer behavior.

Working EL now installs only that frozen D helper over EC, with every rejected
Bill F/N hunk still absent. Main441 sources and both ROMs exactly match EJ;
all four builds pass, both baselines exact CG, PLAYER/RAM growth zero. Actual
EJ rebinds pass616 native cases (434 phase,50 pose/pause,132 inherited C) and
1000 strict complete-controller ABI cases, with each discarded stack push cell
itemized and every SMC/nonstack ordered write exact. Foreign/Hard rare cost is
+42cycles, native Mario/Luigi and ordinary added cost zero. Main manifest SHA256
7cf7f1ebf96f21184e5b9b7d2eff5a832038862a1e057f19f7a00018fb0f92e4.
MMC3 ROM2872f04b870ad72cb54b22a67a10333995151a501282c6535f3adfbe0ae32060;
MMC5 ROM3161fa3d8eb002f9a98a7c29cac6347770d955252c49bd0337e5a13b93579d10.
The new EasyLink normal-form animation proof is specifically PlayerVictoryWalk
task2. Bridge-collapse/setup/print tasks0/1/3/4 and full WATCH projectile,
hurt/special-form parity remain open. EL is an interim working checkpoint.

The Bill axis incident is frozen5248dd822c9871781bd51e3db0417271a0dcefb86065e3adf8f01c0a44747b3f,
including69 receipts and independently pinned complete source functions. A-only
and Right+A controls have identical native state through1649: pure A has no
cancel and reachesY102.664932; Right+A cancels once atY171.555557. Private G
adds exact completed Q16 previous-rectangle state and a consumer-only filter,
preserving raw cell getters. Its actual first incident replay keeps raw tile20,
rejects only the proven side candidate at the consumer, preserves upward speed
and reaches862/176 by1780. The first5192-case consumer run retains24 vine-field
failures: native vine26 has SOLID|CLIMB and must retain climb handling. G1 is
not admitted; G2 will explicitly preserve climb policy with the same oracle.
Remaining ordinary controls,9978 inherited cases, closure/RAM/cost and final
EL-plus-corrected-Bill union checks are still required before installation.

Historical BY Scrooge both-mapper full proofs are now frozen in compact index
397ed7cfedf479f4934e9f8cd37232a4f227f143033370437fc5f62c7761049d.
MMC3 is20170frames/20169polls; MMC5 is20412/20411; each has six stages with
zero deaths and25 real controls in2-3. MMC5 actual Scrooge native probes2/13
resolve80dry and12water fresh-A supports, including17408 right13 tile105;
generic Mario probes3/12 had misclassified that water support. The separate
EC coverage inventory03b4c337a254c90659c6fc0048c24842730fc7bc4147c5616b1c3cd0a821a801
retains real tier receipts and identifies unestablished ordinary flower/fire,
Star protection/expiry and final arsenal/audio/art bindings without relabeling
historical passes as absent tests. Bounded natural upgrade runs now use an
additional300MB phase and explicit frozen EC ROMs; no state grants or recording.

Root EC Mega Man EG clears the actual castle and enters2-1 at16164. The EG
guard identifies the next fatal owner as Piranha0 at744/129 (16861), not a
generic stale death slot. EH adopts ordinary DP controls through that pipe,
then its controller waits forever shooting toward targets behind another solid
pipe; timer kills25917 with no actual enemy injury at that point. EI changes
only controller logic: ignore the real fully retracted plant and jump obstacles
before stopping to shoot through them. It progresses to the2-1 spring, then
repeatedly jumps beside it at3025 until timer. EK aligns to the true spring
column3008..3023 and records actual compression1 release, fresh A in2, forceF4
and a real strong launch; it clears the wall but lands before the pole and its
no-jump end policy waits at the base3185 until timer. EN adds an ordinary jump
from the genuine3138 grounded prefix toward the shaft. No spring/pole engine
defect is established by those controller stalls. These are explicit EC partial
discoveries, not final EL full-route or recorded-media acceptance.

The bounded EC ordinary upgrade phase is frozen in handoff9530e4b65453ef0b588e9b8acbb8f37624216aeb7a9e67ced870245de152bdaf,
freeze57e5a300c747299dae66bf231532e92a239991ea792b675d34edfaaa071cbd38.
All eight startup replays (Mario/Luigi, Easy/Hard, MMC3/MMC5) run2250 frames,
2249 polls, zero deaths, natural mushroom then flower contact, exactly60 frames
from each contact to live tier, and actual fireball slots plus hardware audio
events. Root EQ independently checks95 pinned files and all eight canonical
traces/tapes. These are bounded ability receipts, not full clears or final EL
recordings. Complete source art/waveform fidelity, ordinary fireball enemy
defeat, immunity/boss/crouch and Star lifecycle remain separately qualified.
The phase retained313,628,587bytes below its explicitly raised340MB ceiling.
A separate200MB ordinary combat follow-up now addresses the uncovered enemy
contact and Star lifecycle cases without emulated grants or main edits.

Root EN entered actual2-2 at20885. EO changes only the controller's water-A
hold, passes the first coral, then dies21081 at276/155. Guarded InjurePlayer
identifies Blooper0(ID7) at288/144; native boxes113:159:127:187 and127:158:137:164
overlap inclusively. This is an owned ordinary collision, not a new source
geometry defect. EP searches genuine unedited states from21010 and independently
replays its winning inputs from startup:21593/X800/Y112, all10240RAM identical.
It passes the Blooper and reaches actual support. ER now continues that verified
EC prefix. The six-stage-visited field still does not mean end2-2 cleared.
Simon C O separately clears2-1 with a real springF4 producer and enters2-2 at19462;
his owned Blooper death20199 is retained. Water F cold-verifies20455/X1107/Y0,
and continuation P remains separate from the current EL runtime admission.

Root EC Mega Man now actually clears through2-2. EW25571frames/25570polls
enters2-3 at25547 and supplies25 further real controls, X40 to61, zero deaths.
Independent fixed EX has byte-identical full21-field canonical trace and input
tape, plus full render/hardware-audio audit. Root EZ freezes this scoped pass
3a3d33cfa20271a102be3b66d72f8f7158485e3aa2559c1bf54c0d31c0ccf2f9.
MMC5 transfer EY of the same tape is retained negative1725; first19-field
gameplay difference982 is VX2 versus4. This is a distinct timing transfer,
not a demonstrated source collision defect or a successful MMC5 route.
No final integrated replay, every-weapon or perceptual video/audio claim is
made. The endpoint and water entry images were separately inspected.

The EC combat/Star handoff bbe17991a4f287ff4a0fc00d326e4251d4598df940197f8e033cccfc8e609922
now covers eight Mario/Luigi Easy/Hard mapper cases and38 guarded fireball
defeats, both firing directions and ground/air origins. Three MMC3 combat
cases remain responsive startup discoveries rather than fixed repeats.
Easy Mario's natural Star tape independently repeats on both maps, including
pickup3009, protected Goomba contacts3256/3303 with no fireballs/injury, and
expiry3744 after735 updates. Both AS sources specify12000ms; the retained
native35-times21-update timer and flash/music thresholds remain an explicit
approximation. Root FF verifies144 pinned receipt files and these scoped
observables. Other Star avatars/modes/targets and post-expiry hostile contact
remain unestablished by this packet; source art/waveform and final rebind remain
open. New phase retained233,463,504bytes below its240MB ceiling.

Bill G2 correctness is frozen32db2a18b92534b0fab5f33394bd1ee059509ce8f119f74c575b8e7841242a7f:
442 sources,1001 receipts,9978 unchanged plus12746 new cases,5568 matched
profiles and four1780-frame ordinary controls pass. It fixes the actual1650
pipe side/head admission while preserving raw cell20 and upward251. Its cost
prevents final admission: empty ordinary mean adds1060.666MMC3/1034.395MMC5
cycles; sustained seeded six-Goomba MMC3 mean27621.858 becomes30063.013 and
NmiSkipped increments202 become314. MMC5 mean25060.117 becomes26214.889,
increments157 become163. These are scoped arena/controller comparisons, not
a universal game-wide percentage. Main remains EL without rejected Bill F/N.

Private provisional EU combines exactly G2 with the sole installed D/EL
guest_victory_control helper. All four builds pass, baselines remain exactCG,
G2 RAM/PLAYER unchanged, soleROM delta in the rare helper(+60RYU bytes).
Actual combined validation independently passes616 native and1000 strict
compiled G2-to-EU full-controller calls. Root FC verifies the1001 receipts,
442 source catalogs and frozen combined checks; this validates correctness
only and does not override the material cost. A separately hashed hot-path
successor now relocates rare code to make room for near body/head/cache calls.
Its early farcall N/Z return issue is retained and must be repaired with exact
flags/stack/caller state and new scratch cells itemized before admission.

Read-only root FB indexes79 existing complete audited route packets across24
avatar/mapper/first-observed-mode groups, preserving all original ROM scopes
and three missing-artifact inventory errors. It supplies candidate input tapes,
not current-runtime acceptance. EL Bass FD tests the old34b full tape, clears
1-1 and enters1-2 at6702, then encounters owned native Koopa/Goomba contacts
(7874/8037). Responsive FE clears that early group, loses natural tier1 at8958
to Goomba2 and dies9195 to Piranha0; observed native boxes overlap. FG now
searches ordinary controls from actual FE8880 before that group. These are
partial ordinary routes, not new source-defect proofs. Pit EL and Simon C
ordinary continuations remain active and final integrated movies remain open.

Simon C is now independently fixed through2-2:23853frames/23852polls, zero
deaths, real2-3entry23829 followed by25 controls X40to70. All nine audit CSV
streams repeat the discovery literally. Root FJ independently rehashes the
frozen route,441 C/EC sources and eight artifacts. This is the historical C
runtime; final integrated replay, all arsenal and retained movies remain open.

EL Bass FG passes the1-2 pipe/enemy group with natural tier1 and independent
startup/all10240RAM verification. FH clears1-2 and reaches1-3 at11141 before
a11385 pitfall. FI cold-verifies a grounded540/160 first-gap landing with
tier1. FK continues to12419/X1120/Y241 and custom pit death, with no native
injury-owner callback receipt. These controller-only partials establish
ordinary route progress, not a source collision defect or a full clear.
The private Bill hot-layout successor still requires exact closure/flags,
mapper-selector and NMI capture-lifetime checks plus final cost comparison.
Main remains exact EL; no performance-rejected G2/EU code is admitted.

Pit now independently clears EL MMC3 through2-2 in24726frames/24725polls,
with real2-3entry24702 and25 further controls X40to76. Root FT rehashes781
retained files,441 sources and eight artifacts; all19 route fields repeat W.
159 fresh-jump receipts include one explicitly observed native corner catch:
right foot first lands atX737/top128, then side push moves the hero724to721;
the next A uses retained State0 with empty post-push foot cells. This is not
continuous floor support, a glitchless claim or a demonstrated source defect.
The separate MMC5 same-tape attempt dies3442; first checked-field difference
2435 is X1585/VX0 versus1586/VX24. Its native timing failure is retained.
All final media and complete Pit arsenal/source fidelity remain open.

EL Bass FQ clears1-4 and enters2-1 at17217. Its17651 fatal contact is a live
kicked Green Koopa(ID0/state84), not a defeated Goomba(ID6); native boxes
overlap. FR independently verifies17869/X800/Y176. FS and FU time out after
shooting across a solid pipe from1798:32px does not reach its1840 left edge.
FV is a retained startup-only logging syntax negative. Additive FW uses64px,
records actual pipe tiles20/21 at+48/+64, passes both pipes and later falls
at2250/245. FX cold-verifies20285/X2400/Y176; each adopted branch matches
all10240RAM from independent startup. FY continues those ordinary controls.
No source or hitbox change follows these controller failures.

Link's actual12019 head contact is legitimate: source top79.4998 is below
cell bottom80, with prior top82.6665. The separately frozen positive-response
gap remains unfixed: source canonical PY63/fraction0 versus62.4998, source
downward100/120 Q00D555 versus native1/next AirSync010000, and no ceiling-cue
receipt. Only Easy normal15 is demonstrated; Hard, foreign and retained,
crouch/water/cache profiles require separate expectations. A private repair
phase follows the current EL route outcome; no shared fix is installed yet.

Bill V9 remains private. All four builds and strict compiled matrices pass,
but rare native IRQ/NMI-crossed calls, head/reward live-scratch effects and
whole-frame cost comparison are still under review. Relocated JumpEngine
pointer bytes require individual symbol/liveness proofs; no scratch mask is
accepted. The original SPACE-to-world35 warp/code-byte lookup negative remains
outside the authored valid-warp scope. Main remains EL without G2/EU/V9.

Bass FZ now independently replays the flying-fish section to frame/poll20683,
X2899/Y176, with all10240 RAM bytes matching. Ordinary GA clears2-1 and
enters2-2 at22332. Its fatal23909 contact is Blooper ID7 slot3: player box
113:113:127:137 meets enemy103:108:113:114 at the inclusive x113 edge.
GB changes only ordinary controls and independently verifies a real grounded
middle-coral landing at24058/X1640/Y48. No collision widening or source change
was made for those route failures. GC continues the genuine GB tape with a
passive, actual-bank/eight-byte scope profiler covering the water level.
These remain unrecorded discovery routes, not an independent full Bass clear.
The measured Bass phase395.6MB is extended from400MB to600MB for the remaining
route, profile and full-audit work; the global55GB ceiling remains unchanged.

V9's reported ordinary mean cost is still738.654 cycles above EC on MMC3 and
766.025 above EC on MMC5. Six-enemy skipped-NMI counts are292/162 versus
EC202/157. Its correctness checks do not establish performance acceptance.
The specialist also identified a passive-observer ownership error: the four
apparent NMI-crossed BG suffixes actually originated in weapon Activate.
Those captures remain negative evidence while each real consumer is rebound.
Link's separate repair must fit the same eventual runtime; its planned513-byte
helper moves to an explicit bank7 tail rather than conflicting with V9 bank9.
At the time of that V9 review, neither private repair was installed. The later
GQ checkpoint below installs only Link's scoped ceiling response.

Bass now independently clears EL MMC3 through2-2 in26689frames/26688polls,
with zero deaths and real2-3entry26665 followed by25 controls X40to66.
Discovery GK and fixed GL match every byte of the21-field trace and input tape;
GL includes the full physical-frame OAM/CHR/scroll/hardware-audio audit.
Root GN rehashes441 EL sources, eight artifacts and11 adopted all10240RAM
cold-verified branch receipts. This establishes a controller clear on EL,
not every weapon/powerup, a glitchless route or a perceptual movie review.
The separate GO accepted-jump/support audit now passes in root GT:238 actual
accepted launches comprise128 solid-terrain launches, six actual platform
contacts, one compressed spring and103 secondary air jumps. The native
above-screen secondary jump at14037 has highY0 and is valid; the earlier GP
reviewer's blanket highY1 predicate is retained as a reviewer negative.

Bass GM tests that exact timing tape on EL MMC5 with a newly bound actual
physical-bank/eight-byte injury observer. It is a retained negative at2279,
with no hostile-injury callback; the endpoint is a pit death. The first checked
19-field gameplay difference is720, with M3 already jumping while M5 is still
grounded. This supplies no MMC5 full-clear or source-defect claim.

Root GJ freezes two ordinary Bass water profiles. Their shared prefixes match
all21 fields including CPU cycles/NmiSkipped: GA-to-GD through23700 and
GD-to-GG through24720. In GG, completed inclusive GameLoop calls average
23857.8 cycles; draw and weapon children are material contributors. Nested
scope times overlap and cannot be summed as separate costs. No optimization
or universal lag reduction follows merely from those measurements.

V9's correctness-control freeze and76 native receipt files are independently
rehash-checked in root GF. Root GH reconstructs all12 original EC/G2/V9 cost
groups from native entry/return records and confirms the reported regression.
A separate private W6 head shortcut is now being checked: specialist scoped
costs fall by about391 ordinary MMC3 cycles versus V9, with source-empty-domain,
scratch-liveness and complete nested-caller validation still required.
The old raw-head observation negative is retained: the shortcut avoids304
public getter calls. Separate explicit components supply that API coverage;
they are not ordinary route or runtime-pacing proof.

The user's retained-lossless/raised-cap instruction now authorizes the60GB
working ceiling recorded in root49-retention-budget-gk.json. Existing55GB
receipts retain their original scope. All existing captures and negatives are
kept. Local current ceilings are700MB Bass,500MB Rygar,350MB Link response
and5.80GB Bill; final movie phases remain separate work.

GQ is now the current442-source/eight-artifact working checkpoint on both
mappers. Root's admission packet `root49-link-ceiling-admission-gq.json`
reviews the scoped Easy Link normal-jump solid-ceiling response. Only the
admitted pose/profile takes the source-derived canonical position, fractional
velocity and bump cue. Unsupported forms use the native fallback. Ordinary
noncontact gameplay has no added instructions; a rare positive ceiling hit is
more expensive. Question-block and brick PlayerHeadCollision paths bypass
this site and are not established by this repair. The packaging-only source
archive path error was completed by GR; the final GQ manifest is complete.

Root `root49-gq-routes-gu.json` independently rehashes798 frozen Rygar EL
ancestry files and127 frozen GQ transfer files. Rygar, Pit and Bass each pass
the actual GQ MMC3 Easy full fixed replay with zero deaths through2-2 and25
real controls in2-3. Their19 gameplay/input trace fields are identical to the
corresponding EL tapes for20988,24726 and26689 frames respectively. Fresh
physical-bank/eight-byte observer bindings,442 current sources/eight artifacts,
and441 immutable historical EL sources/eight artifacts are checked. Bass's
238 accepted-launch support receipts are independently reclassified on GQ.
Pit retains the explicitly classified native landing/side-push corner catch;
Rygar/Pit inspect fresh pre-input jump attempts, whereas Bass inspects actual
accepted launches. None of these packets claims all-arsenal coverage, Hard,
MMC5 completion, final retained movies, audible waveform fidelity or a
glitchless/source-perfect route.

The current Link GQ ordinary route has cleared1-3 and reached the castle;
the second-bar source/body-sampler discrepancy is bound by HF below.
Private Bill W6 has now frozen its four short ordinary controls and actual
fire-liveness checks. Root `root49-bill-w6-review-gz.json` rehashes444 sources,
eight artifacts and192 native receipt files and independently checks the four
ordinary traces. A physical-frame timing difference, a no-shot component-input
mistake and an initial weapon-type-domain oracle mistake remain retained
negatives. W6 is not installed. Its contextual union must preserve GQ's Link
response, the existing victory helper and the new firebar work below. The full
roster/weapon/upgrade audit and final recorded playthroughs remain open.

Root `root49-link-firebar-lead-hf.json` independently verifies the second-bar
Link discrepancy: the native sampler comparesPY112 against pieceY106 while
the actual normal15 body beginsY129 and all six emitted sprite containers end
by120. The passive replay repeats all nine original failure CSVs. The repair
must gate beforeChgSDir so that a rejected false hit also leaves movement
direction unchanged. Original source bitmap/cached-bounds semantics are bound;
full source/native birth/rotation/anchor parity remains explicitly unproved.
Private H compiles both mappers and unchanged baselines but is not admitted.
Its extra96/85 resident bytes require further layout work with Bill's union.

Sophia's current GQ ordinary route has cleared1-1,1-2 and1-3 and enters the
castle at10652. GY's exported best root and HE's winning platform continuation
are independently cold-verified against every10240RAMbyte; HE reaches1660/Y80
on the far bank at9381. Earlier late jumps, inertia overshoots and missed
platforms remain retained controller negatives. There is no current full2-2
Sophia clear.

Root `root49-sophia-body-lead-hj.json` binds the next real failure. Both passive
replays reproduce the same castle firebar death at11129; all21 trace/input
fields agree with discovery HG, and HH/HI match all nine audit CSVs. Original
2.02 Sophia main HRect is19x15.5NES pixels; native flat body is14x24. The actual
pre-injury10240RAM snapshot has no wall/ceiling/hurt/powerup/water form and is
standing on authored ground144 atPY112. The source flat top is128.5 and the
complete emitted bar ends by128, yet the old PY sampler
injures at pieceY115. A source-shaped body and its consumers need correction
before routing past that point. Other orientations, exact source firebar
phase/anchor and positive pixel parity remain separate obligations. No shared
runtime has changed for this lead.

Root's private Sophia body stage HS is frozen in
`root49-sophia-source-body-hs/implementation-stage-freeze-hx.json`. It projects
the normal19x15.5 source rectangle with exact half-pixel/Q16 endpoints for
integer actor comparisons and rejects proven disjoint firebar containers before
direction/injury mutation. The new guard admits flat ground/air forms in both
behaviors; rotated/vine/death forms remain separate work. No new RAM is used.
The existing Ryu body/platform procedures and Link's firebar leaf move into the
old3A tail. Both character projections keep one ordinary bank fetch. Decoded
instruction review permits only their exact internal code relocations.

Both mapper builds and unchanged baselines pass. HT checks240 compiled rational
body projections,360 unsupported-form ABI controls and1240 firebar fractional
edges. HW independently re-executes92 real emulator FirebarCollision calls;
every10240RAMbyte, register, caller-stack byte and ordered write matches with
zero interrupted gaps. Native cases include both behaviors, both facings,
vertical/horizontal edges, damaging overlaps and foreign-character controls.
This proves the scoped body/consumer stage, not exact source firebar pixels or
positive overlap parity. Actual Ryu caller/platform interruption regression
is assigned separately before contextual integration with Bill's private E.

The original complete Sophia input tape is not portable to HS. HU's fixed
power-on replay first changes its NMI count at637 and position/camera at663;
it enters1-2 at5533 and dies on an owned shell contact at6887. This retained
negative is not a castle-survival claim. Source terrain head/side samplers,
wall/ceiling anchors, the fresh through2-2 route, all weapons/upgrades and final
movies remain required. Earlier host-return/SRAM-fixture mistakes, a mapper5
cold-placement overflow and an overstrict literal relocation check are retained.

Current main remains GQ with442 sources/eight artifacts independently exact.
AR records the private stage, remaining requirements and latest allocations:
60GB global,600MB union,800MB Samus with100MB final audit reserve,500MB aggregate
Sophia body phases,200MB delegated relocation regression. Census is56.650GB;
all capture files remain retained. The goal and final recording work remain active.

The separate HS relocation regression is now frozen at
`agent-lsr-sophia-body-hs-regression-a/freeze.json`. It reexecutes1168 actual
body/platform calls across both mappers with exact AXYP/SP/PC, all10240RAMbytes,
ordered writes and native cycles, and zero interrupted gaps. All Ryu and other
foreign controls retain their original oracles. One old foreign Sophia bbox
oracle is explicitly superseded by the intentional normal source projection.
The saved inner PHP flag difference is individually bound; there is no blanket
stack/SMC exclusion or exhaustive interrupt-phase claim.

The next private normal-terrain successor is
`root49-sophia-source-terrain-ik`. Source head queries cover center/left/right
columns with fractional19x15.5 bounds; the prior-position cache admits direct
below contacts, and wall response uses exact mirrored half-pixel separation.
Existing character-owned Ryu cache storage and Sophia-dormant RgDoubleJump
provide prior coordinates and jumped state without adding RAM. Spring launch
sets that state. Rotated anchors, vine state, complete feet and corner calcAxis
ordering remain outside this scoped correction.

The full native caller exposed two actual IF defects that isolated geometry
checks had missed. Hover could still reach native block effects despite source
BRICK_NONE, and C2/C3 coin attributes could incorrectly cause a solid ceiling
response before the pickup. IK retains the real queried tile/pointer, gates
native block effects according to hover or underwater non-jumpRise state,
ignores hidden blocks in BRICK_NONE, and routes coins before solid response.
Source classic=true is not represented by this gate. The IF negatives and IJ's
out-of-range147-byte branch failure remain retained.

IK has445 pinned sources and all four successful builds. Root IL checks the
unchanged baseline hashes, header/CHR/audio/DPCM/SMC, old RAM addresses and
NMI/IRQ/vine continuations. The original96 compiled terrain fixtures remain
unchanged;132 additive coin/brick-state fixtures also pass. IF's tested spring,
name producer, Ryu3A procedures and Link H leaf retain exact PCs and bytes.
Their prior224 spring and56 name-producer component assertions remain scoped
component evidence, with actual composed spring-caller checks still required.

Actual IK full-caller A+B/wet-rise/hidden controls pass60 cases per mapper;
58 uninterrupted calls per mapper reexecute exactly against all10240RAMbytes,
registers and ordered writes. Mario/Bass calls interrupted by actual NMI are
retained as explicit strict-reexecution gaps. The additive cache/next-AirSync
check has its own receipts. Its first six cue assertions sampled at a later
epoch, after the queue changed02 to00. The final passive receipt guards the
actual writer inside NMI: ExpandedAudioTick ClearQueues STA$0105 in bank38 at
C954/C94C, then its+3 successor. This retained observation negative is separate
from source correctness. The queue receipt is not an audio-waveform proof.
The corrected observation checks the cue immediately at post-BG and then checks
the next AirSync and actual pre-integration cache publication independently.
This is not a fresh ordinary Sophia route or complete source-fidelity admission.

Private Bill E is frozen at `agent49-gq-bill-union-a/freeze-final-e.json`.
Root IM independently rehashes447 sources,21 overlay files,1024 native receipt
files and24 native groups. This checks the frozen handoff's integrity. It does
not install E or turn bounded1780-frame controller controls into stage clears.
Its measured ordinary foreground cost remains347.691/379.062 cycles above EC
for MMC3/MMC5 in the matched controls; no universal lag improvement is claimed.

The contextual E+IK composition is private under
`agent49-e-sophia-union-a`, with449 sources and successful crossover/baseline
builds. Moving an unchanged head bridge into existing resident padding funds
the SAMUS bank fit; the two E Bill spring/history gates remain preserved.
Source-only layout checks do not replace actual contextual native admission,
including the moved spring caller and rebound rare/vine entries. Main GQ is
still unchanged. Final all-roster, arsenal, upgrade and recording work is open.

The Samus GQ MMC3 Easy route has now reached2-2. AO's retained controller stall
at22394/X3025 had zero SpringLaunch events because its floor jump skipped the
spring. AP observes the actual boost at22189/X3008/Y116, spring slot1 with
compression4/forceF4, clears2-1 and enters2-2 at23472. It dies at23711/X308/Y112
on a real Blooper overlap while standing on coral. Source body-edge semantics
are being checked before continuing; this is not yet a confirmed source defect
or full route clear. An earlier nonfatal injury at2030 changes power1 to0, so
this route is not a no-injury/small-only proof. With the phase measured at
836,993,332bytes, root raises its ceiling to1.25GB, retaining100MB for final
audit. Latest measured global storage is57.501GB under60GB, with all lossless
captures and negatives retained.

AS (`root-current49-progress-as.json`) snapshots the terrain correction,
independent frozen-E review, actual HS regression, updated allocations and
57,544,655,991-byte census. Shared GQ remains442 sources/eight artifacts exact;
root has no live child handle. Native admission of the pinned449-source
contextual E+IK build is now authorized to proceed while the specialist closes
the passive cue-clearing-writer attribution. This is an active work handoff,
not a release or completed goal.

Root freezes the scoped IK stage in
`root49-sophia-source-terrain-ik/implementation-stage-freeze-in.json`, after
rehashing1099 specialist packet files. The60+14 native cases per mapper include
58+14 exact full-call reexecutions:144 total. The two NMI-interrupted foreign
cases/map in the60set remain explicit gaps. Main remains GQ.

The next actual source lead is frozen in
`agent-lsr-sophia-feet-source-a/freeze.json`. Both mappers complete74 seeded
cases, with every148 full native caller matching compiled execution exactly
and zero gaps or cycle differences. For each mapper62 cases have strict prior
horizontal overlap and prior bottom<=groundTop:42 miss their source landing,
including38 wrong side clamps. Of20 native landings,6 retain nonzero vertical
fraction through afterBG.14 direct controls are fully correct,10 disjoint
controls pass, and2 true prior corners remain separate calcAxis work. The
clearest case isPX735/PY113 with previousY110: a source19px foot span overlaps
single-cell support720 or752, while both native feet query736. The exact source
groundBelow response must immediately setPY=top-32, FY0, qVY0 and grounded state
while preserving horizontal position, fractions and velocity.

Root independently captures original2.02 SophiaLand NSF track46 in
`root49-sophia-land-source-io`. It has8 audible updates1..8 on pulse2; the
current remaining-effects table has no landing event. The private successor
adds this source stream and extended lookup tables in the existing bank7 tail,
preserving all24 old effects and old audio PCs. Actual landing-transition,
stream/mixer and old-effect regression checks remain assigned before admission.

The private query prototype is frozen in
`root49-sophia-query-perf-ip/implementation-component-freeze-it.json`.
13,312 compiled calls cover every256X value,2 pages and13 rows per mapper.
The direct pointer calculation saves exactly31CPUcycles per query. Registers,
all RAM and ordered semantic writes match, with only the three individually
decoded old discarded JSR/PHA stack residues differing. Both baseline builds,
old audio/DPCM/SMC, RAM, header/CHR and NMI/IRQ/vine continuations remain exact.
The remaining-audio segment is also independently literal. Whole-frame lag,
integrated native interruptions and final routes are still separate evidence.
Initial host path spelling and raw-status fixture mistakes remain retained.

The first wider-foot implementation could not fit the suggested bank3 area:
TITLE4398 plus RENDER3433 leaves361bytes. Its long-branch and852-byte overflow
negatives remain retained. Root IV instead binds bank5's only MUSIC segment,
6047 literal bytes followed by2145 unallocatedFF bytes, on both mappers. The
new optional cold segment uses1213 of that tail, leaving932bytes; no Samus
closure relocation is needed. Private C builds both crossovers and both exact
baselines. Its unchanged74-case source-foot controls pass on MMC3, including
the42 missed landings and6 fractional anchors. Mapper5, previous head/side,
landing audio, foreign ABI and interruption checks remain required.

Contextual E has separately completed its original native geometry/consumer,
full moved spring, rare ABI, compiled NMI and Link checks. Actual short spring
scopes contain0ISR;20,832 per-instruction compiled normal/lag NMI cases are
separate modeled evidence. Final old liveness/reward and four bounded ordinary
controls remain before its frozen packet/root admission. Matched empty-frame
cost is16256.296/15405.247 cycles for MMC3/MMC5:51.901 above frozen bodyE and
399.592/430.963 above EC. Seeded-six lag is249/158 versus prior246/157. These
are scoped costs with timing/AI/interrupt qualifications, not a lag improvement.

AT (`root-current49-progress-at.json`) pins this progress and58,113,466,492bytes
of workspace use. Contextual E now has500MB with50MB final reserve; new feet
implementation has300MB with50MB reserve; Samus has1.25GB with100MB reserve;
global remains60GB and all captures/negatives are retained. The full roster,
arsenal, fidelity, final routes and recorded movies remain unfinished.

Contextual E has now frozen its complete scoped packet in
`agent49-e-sophia-union-a/freeze-final-e.json`. The additive supplement corrects
the earlier Link API count to300/map,600 total, with no assertion/runtime change.
Root IW independently rehashes449 sources,16 artifacts,644 native files across
36 groups and all four bounded ordinary controls; every final report status
passes.25 source paths differ from GQ and no new-path local conflicts exist.
No shared copy has started: active GQ route guards must transition explicitly
before adopting a new shared QA checkpoint. The private wider-foot repair and
all broader remaining requirements stay separate from this scoped admission.

The independent audio specialist is now checking the new feet candidate's
landing25 and original24 effects/mixer/lifecycle on both mappers. Samus AX uses
intrinsic held-A midair Morph and reaches the tall columns; causality versus
reduced shooting is not isolated. AY reaches the upper2752 platform, then a
head response at26732 moves2753/Y48 to2767/Y57 before side separation and a
fish collision. AZ replays that exact tape read-only with actual head-cell,
fractions, active profile and terrain-grid receipts before classifying it.
AT-addendum-IX pins these later findings and the continuing work. There is no
full Samus route, complete roster/arsenal audit or final movie claim yet.

AU continues from that snapshot. The unchanged74-case feet oracles now pass
on both mappers, with296 exact candidate/parent full-call reexecutions and no
feet gaps. Head/side60 and fallback48/cache14 groups also pass per mapper;
actual interrupt gaps in their stricter CPU reconstruction remain explicit.
The bounded four-scene Sophia profile finds a material correctness cost of
roughly900--931cycles/update. In the MMC5 six-Goomba standing scene, a matched
60logical updates span61 versus73 physical frames and skipped-NMI counters
rise30 to43. This is a performance regression, and the next scoped task is to
reduce the redundant work before shared adoption.

Root independently completes ordinary Mario Easy through2-2 on private
source-c, both mappers:16991frames, zero deaths and25 actual2-3 control frames.
All19 movement/controller fields and114 dry-takeoff receipts exactly match the
earlier CC proof. Full hardware telemetry is retained; this is unrecorded and
does not establish all-arsenal or perceptual media fidelity. The frozen result
is `root49-combined-mario-a.json`.

Samus's GQ Easy/MMC3 route is now independently replayed and frozen:28285frames,
zero deaths, real2-3 controlX40 to70, all19 movement/controller and18 sampled
native fields matching discovery. Its136 takeoffs comprise131 real terrain,
four platform-owner and one compressed-spring support, with no unknown support.
The natural mushroom and later nonfatal injury remain explicit. Root rehashes
all1534 retained files in `root49-samus-gq-route-review-be.json`. This proof
remains GQ-only; successor transfer, MMC5, Hard, arsenal and final movie checks
are separate. The specialist has moved to ordinary Bill/Lance route work on
the new immutable candidate.

Independent source-c audio review confirms an actual landing defect: pulse2
timer-high is written every active update1--8, while the source writes only1
and7. Root preserves source-c and creates a landing-only47byte wrapper. The
first private D placement shifts later bank7 code and is retained as a rejected
layout. Successor source-e places the same wrapper after all existing bank7
segments. All four builds pass; layout-e proves exactly49ROMbyte changes/map
against C:47new bytes in formerFF and two bytes of one JSR operand. All prior
segment placements, RAM, other ROM bytes, old streams/music/DPCM and baselines
remain literal. Focused actual landing probes pass Easy/Hard on both mappers;
MMC3 actual timer-high writes are now1,7. Pause/resume, mixer/old24 effects and
strict ISR/ABI review remain pending before admission. NSF subframe write order
is a separate limit; no waveform identity is claimed.

The recoverable GQ backup in `root49-combined-adoption-a` contains461 actual
files:442sources, eight artifacts and11 generated includes. Their normalized
generated content is identical; the initial byte-only guard found CRLF/LF
differences and its host negative is retained. Main has not changed. Under the
user's retain-lossless/raise-cap instruction, the global ceiling increases from
60 to70GB for remaining routes and final retained recordings. The last census
before the new private builds was58,453,542,378bytes, with157.8GB disk free.
Existing specialist caps stay unchanged; new Bill work has1GB with100MB final
audit reserve. No capture or negative was deleted.

The final C packet corrects the strict-call count to526, with14 explicit
actual-interrupt reconstruction gaps; root rehashes2791 packet files. No cold
bank5 interrupt occurred in the matched scenes, so that remains unobserved.
E's actual old24 wrapper review now passes777calls/map, including captured
IRQs, while preserving every live RAM/register/flag/port result and individually
classifying discarded stack pushes. Non25 calls add35cycles. Its final20-case
lifecycle/mixer review remains separate and active.

Root also tries the exact frozen GQ Samus input on E. Both failures are retained
in `root49-combined-samus-transfer-a.json`: MMC3 stops at the first death
transition4322, MMC5 at3528. Actual Easy/Samus identity and exact input prefixes
pass. MMC3's first movement difference is1973, when GQ advances and E's skipped
update count increments; this is timing evidence, not a diagnosed collision
defect. The MMC5 attempt uses the MMC3 input and has no prior MMC5 clear claim.
The completed GQ route remains valid in its own scope. Ordinary inputs need
adaptation on the final candidate; neither transfer is a new clear or recording.

The audio-E landing review is now frozen and independently admitted in
`root49-landing-audio-admission-a.json`: 777 actual old-effect wrapper calls per
mapper, 3072 compiled flag/stack/effect combinations per mapper, and 40 practical
lifecycle controls total. Actual IRQ preemption is included. Landing25 writes
the timer-high on updates1 and7; pause/resume's forced music reflush remains
explicit. Non25 audio costs35cycles/update. Subframe write-order, waveform and
nested-NMI identity are not claimed.

The wider Sophia feet path has a frozen scoped optimization in
`agent-lsr-sophia-feet-perf-a/source-b`. Its364 native cases pass, with354 full
caller reexecutions and ten actual-interrupt reconstruction gaps. The42 foreign
caller controls retain exact RAM, ordered writes, registers and cycles. Normal
flat-ground cases use an admitted X-nibble3..13/prior-displacement-2..4 fast path;
other profiles retain the wider slow path. The four matched scenes per mapper
preserve240x204 canonical fields. Standing saves746/792cycles (MMC3/MMC5), walking
453/484. The measured MMC5 six-Goomba standing span improves73 to63 frames and
skipped-NMI count43 to33; walking72 to68 and42 to38. MMC3 crowd spans do not
improve. Cold-bank5 interrupt restoration and broader lag remain unproved.
Root rehashes all1892 retained files before composition. The unexecuted earlier
decimal98 whitelist candidate is retained and never admitted.

Actual Samus Hard controls exposed a reachable source mismatch: Down+Select
selected a missile mode rather than firing, and B then fired a missile. Source
nonclassic2.02 Special always fires the missile while B remains the beam. The
frozen F correction uses exactly the existing18+43-byte spans with no layout,
RAM, audio or baseline movement. All29 candidate and29 matched-parent cases per
mapper are reviewed independently in `root49-samus-action-review-a`;58 candidate
cases pass. Mature seeded pickup-to-attack controls are explicit, rather than
natural block acquisition or route proofs. Incoherent no-Long-beam powered
states remain diagnostic negatives because normal mushroom progression grants
Long Beam automatically.

Missiles also failed to damage Buzzy Beetles despite source piercing10 versus
armor5. Frozen P corrects a19-byte admission region with only nine differing
ROM bytes per mapper. Its compiled predicate covers24576 cases/map and admits
exactly67,68,70,75,76 while retaining the indexed Knuckle gate. Actual missile
and foreign Bill/Lance contacts pass. The arithmetic changes V, with downstream
liveness qualification; full-P identity is not claimed. Ice's first-freeze and
second-thaw behavior is a separate confirmed mismatch under focused repair.

Root combines the disjoint Sophia and Samus action overlays in
`root49-combined-working-b`, then the missile overlay in
`root49-combined-working-c`. All four builds of each succeed; compiled C is
literally B plus the nine tested armor bytes, with unchanged RAM, segment
layout, CHR, audio and baselines. Twelve unchanged targeted native combat,
inventory, armor, Lance and SFX fixtures pass on C across both mappers.

The broad unchanged-fixture run initially stops on its stock-Mario comparison.
Independent GQ and E reruns are byte-exact to B's521-row trace: the source-Mario
profile already differs from stock acceleration. The report-all wrapper retains
that failure and identical=false, then executes the remaining unchanged
fixtures. It never converts a failure to a pass. Six representative failures
also reproduce on E in `root49-legacy-fixture-triage-a`: Sophia's source19px body
stops at430.5 instead of the fixture's433, the Hard Samus fixture expects legacy
head shattering, the spring fixture assumes stock Mario force, Mega Man's two
oracles require obsolete bank1 instead of actual bank3, and Bill's prior golden
collision CSV differs (E and B's2400 actual rows are identical). Bill's water
boundary failure also predates B. Other failures stay unresolved until reviewed;
none of this establishes a globally passing legacy suite.

Controller adaptation on E now passes Samus's first three stages. A replayed
castle contact has an overlapping conservative part container, so it does not
justify a source collision change. An ordinary supported wait passes that
first firebar; later negatives identify independent hazard phases and a stalled
idle-reference cursor. Read-only GQ phase capture reproduces the complete old
28285-frame clear with byte-identical trace/inputs. It guides ordinary timing
experiments only: no emulated-state grants, new source/bitmap equivalence or
new-candidate clear is claimed. Bill's ordinary new-candidate route reaches2-2;
its successive native enemy contacts and controller changes remain retained.
Full current-candidate routes, remaining arsenal, final fidelity review and
retained lossless final recordings remain unfinished.

The broad B suite is now closed:688 native slots pass,73 mapper/test slots fail,
and the separate stock-Mario comparison also fails. All566 pinned fixture/driver
entries remain unchanged. `root49-full-failure-parent-e-a` reruns67 failed slots
and reuses six exact matching E receipts: all73 reproduce the same first failure
on E, with no parent-pass or different-negative outcome. Root independently
rehashes its295 retained files and every referenced report record in
`root49-full-suite-admission-a.json`. This is pre-existence classification, not
proof of the unexecuted remainder of failed fixtures; the suite stays failed.

Root installs provisional working C in both shared ROMs under
`roster-audit-v49-combined-ground-audio-samus-c/manifest.json` (SHA256
`7bde77980e47d11ed78b9348384016b1a805ff40a02ff180b33f0e8e727b5305`).
All455 source files,11 generated inputs and eight primary artifacts rehash
exactly after installation;35 source paths differ from GQ. The recoverable GQ
backup, immutable source trees, captures and negatives remain retained. MMC3 is
`a4765d19bb90d476f78e14240f4d3b2bf8ee0fa0eda7f8425a9aaea407921005`;
MMC5 is `2c4fad8314a697ecf2cec010e7e8f60a6455502e0b98ef0de7d5bda17ea2e605`.
This includes the frozen P missile correction and excludes the unfinished Ice
successor. It is a working QA integration, not a completed all-roster release.

Samus's later E controller experiments retain actual upper-bar contacts as
negatives. The higher held jump's read-only replay is byte-identical and binds
slot3 point119/77 inside the native box113/56..127/81, so it establishes no
source-disjoint collision defect. The Morph crossing also fails before its
late attained-form assertion; no Morph success or new route clear is claimed.
The independently phased bars cannot both match GQ's phase targets in that
fixed wait: exact primary alignment leaves the secondary1792 phase units away.
Further route adaptation and any spawn-phase investigation remain separate from
the installed runtime fixes.

Working D now replaces C in both shared ROMs. The checkpoint is
`roster-audit-v49-sophia-head-axis-d/manifest.json`, SHA256
`1fcbdec758e0a4c09e769f66b110d4d8d60b05cb11dffa55061bfc32bda55c88`.
Only `src/sophia_source_terrain.s` changes among455 source files; all existing
RAM, segment starts, header, CHR, audio and disabled baselines remain literal.
An actual ordinary Sophia run was stuck at590.5 beside the second1-1 pipe:
priorRight608 equalled the pipe's left edge, but vertical penetration2.833328
exceeded horizontal penetration0.111114. The old unconditional head admission
cancelled every jump. D applies the source's mirrored Q16 corner-axis test,
continues the remaining head probes after rejecting a side corner, and handles
signed prior-left underflow and negative buffer samples at the level origin.
Flash's deferred Ground-list schedule and rotated forms remain separate.

The frozen `root49-sophia-head-axis-d/freeze-k.json` binds27,926 compiled axis
cases, the unchanged96 original head/wall fixtures, two separated-ceiling
fixtures, all256 negative query aliases and an explicit512-case whole-stack,
RAM, flag and ordered-write oracle.109 actual whole resident head callers
reexecute exactly on both mappers, including every register,10240 RAM bytes,
ordered write and cycle; no interrupt occurred inside those short calls.
All26 seeded foreign callers remain literal. Independent source reading
corrects the earlier C origin oversight. Four seeded crowd scenes per mapper
retain all240x204 canonical fields, physical spans, skipped NMIs and DMA counts;
the query guard adds84/92 foreground cycles to standing/walking updates.

Fresh ordinary D discoveries and independent fixed full-audit replays clear
1-1 on both mappers and enter1-2 at4335/4251. They intentionally stop before
the later1-2 deaths; they do not prove a full2-2 route. The previous474 actual
main files are preserved in `root49-sophia-head-adoption-a/before-main-c.zip`.
Both installed D ROMs pass the boot/title/control/floor smoke. MMC3 is
`653ca0e82f27d9aa4a2033d9b4c68488b75ead18ae5b460bbf51bd05fa994a94`;
MMC5 is `1d84dbb52d73a6748c8663c2bc44b09ac303b7a3e31b78119dfe3e57811f468a`.

The current-C Mario and Luigi transfers each clear all six stages with zero
deaths on both mappers:16,991 and17,412 frames respectively. All19 movement and
controller fields match their pinned prior proofs. Bill independently clears
C/MMC3 in31,773 frames with fresh support and physical audit. Samus's complete
ordinary C/MMC3 stream independently clears in28,809 frames; nine whole audit
CSVs and three passive contact streams are literal between discovery and replay.
Those are C proofs and are not automatically relabelled D. Scrooge's older
fixed inputs fail at the1-2 lift gap. Lance and remaining D transfers remain
in progress; all failures are retained.

Root independently rehashes all173 frozen Ice-AQ receipts and456 source files,
then reexecutes its9,216 predicates,92 full native callers and original
source-order/layout/cost checks in `root49-samus-ice-order-review-b`. AQ remains
unadopted: the newer private timer/pool/armor-NSF24/palette work must finish and
be reviewed together. No current Ice source-perfect claim is made.

`root49-goal-coverage-aw.json` keeps all14 identities and66 generated inventory
entries visible, including Easy/Hard distinctions, ROM-added abilities, earlier
shortcut/non-shortcut requirements, all attacks/upgrades, lag and final retained
lossless recordings. It does not turn historical packets into current completed
coverage. The all-roster goal and every previously retained suite failure remain
open; no final recorded release is claimed.

Samus subsequently completes a fresh full-audit fixed replay on actual D/MMC3:
28,809 frames, zero deaths, all six stages and25 controlled2-3 updates. All nine
whole route/hardware CSVs are byte-identical to the immutable C proof. The
103-file C packet is independently rehashed. D/MMC5's attempted transfer of that
MMC3 tape dies at2351; its first movement/camera difference is1253. This is a
retained fixed-controller transfer negative, with no source bug assigned before
an actual injury-owner/phase investigation. `root49-current-d-transfers-a/`
contains both outcomes. Current-D Sophia, remaining identities, arsenal and
retained final recordings remain incomplete.

The next audit pass independently verifies current-D/MMC3 Bill and Lance full
fixed clears in31,773 and31,258 frames, respectively. All nine whole controller,
graphics, scrolling and audio CSVs are literal to their C proofs; actual menu
identities distinguish Bill from Lance. Root also rehashes Lance's frozen C
packet and independently compares31,258 movement rows and30,759 native telemetry
rows. These are zero-death clears, not damage-free or complete-arsenal claims.

Nine additional fixed-controller transfers on frozen D produce full Mario and
Luigi clears in16,991/17,412 frames. Their nine whole CSVs are literal to C.
Actual controlled2-3 movement is40 to56 for Mario and40 to51 for Luigi; the
guest-character40-to70 endpoint must not be assumed for their acceleration.
Mega Man, Link, Simon, Pit, Rygar, Bass and Ryu's older tapes fail on D. Their
first differing movement rows and skipped-NMI counts are retained in
`root49-d-remaining-routes-ax/review.json`. Those failures do not by themselves
prove a physics or collision regression. Parent behavior semantics and the
actual first differing completed update remain to check before runtime changes.

Samus's D/MMC5 passive injury observer is neutral over all nine full CSVs and
binds the original2351 failure to live Goomba2 at869/Y184. Ordinary controller
adaptations subsequently pass1-1,1-2,1-3,1-4 and2-1 and enter2-2 at22,697.
Held-A landings and stationary B proposals needed real release/rising edges;
several earlier wrong support-plane and metatile assertions are retained as
controller negatives. Down produced an actual Morph Ball in the attempted
crouch/fire defense; it was not a demonstrated weapon malfunction. The latest
Q attempt is not a clear: a Blooper1 contact at23,394 removes the power-up, and
Cheep Cheep2/ID10 kills Samus at23,936, player1201.5/Y35 versus1190/Y53. Native
boxes overlap at their edges; exact source enemy geometry is not established.
The late observer's bounded raw-snapshot pool is not a whole-RAM proof for all
later contacts. No controller adaptation writes emulated state or changes ROM.

`root49-goal-coverage-ax.json` now includes actual current-D full-clear candidates
for Mario, Luigi, Samus, Bill and Lance. All14 identities,66 inventory entries,
earlier shortcut/non-shortcut requirements, all upgrades and final lossless
movies remain in scope. Five current-D identities do not complete that scope.

Private Samus Ice successor testing exposes and corrects a moving frozen cannon
bullet, its resulting concurrent-injury sound-priority symptom, and a palette
pending flag incorrectly placed at$EC used by the literal Metroid NSF. The new
pending flag is in appended BSS. Root confirms both foreground EffectsAny
callers, correcting an incomplete caller comment and the cost accounting to
normally86 extra cycles per Samus update. The source die()/removeAllStatusEffects
closure also requires clearing AvFrozen/Hi on defeat; that final cleanup and its
strict protocol/cost review remain private. No successor is installed in D.
When composing it, preserve D's `characters.s` optimized feet dispatch and
`sophia_source_terrain.s` head/origin repairs rather than copying older ancestry.

All earlier73 native suite failures and the separate stock-Mario comparison
remain open. The workspace cap remains70GB after the explicit instruction to
retain lossless captures and raise the original cap; nothing is discarded.

Samus now has an independently verified complete ordinary-controller D/MMC5
clear. The T discovery kills the actual first water Blooper by primary fire;
the late water obstacle needs a short jump with an actual A release rather
than the earlier held high jump into the fish. Fixed replay U completes all
six stages in27,659 frames/27,658 polls, zero deaths, actual2-3 entry27,635 and
25 controlled updates X40 to70. All nine whole route/hardware CSVs plus the
passive injury-owner CSV are byte-identical to T, as are all24 bounded raw
contact snapshots. The report is
`root49-current-d-transfers-a/samus-mmc5-review-ay.json`, SHA256
`49d81d23e7d38d7ed4ad6272a1fde0adfbb96cd5e38ddf0ca505af406140ac40`.
Samus's earlier D/MMC3 proof remains separately bound. Neither route is a
damage-free, every-enemy/item, complete-arsenal or final-movie claim.

Seven older parent tapes were independently replayed for650 native frames on
their actual original ROMs. All650 trace rows match each original proof.
Mega Man, Simon, Pit, Rygar, Bass and Ryu have actual raw behavior0; a blanket
mode-mismatch explanation for their D negatives is contradicted. Link's old
ROM has no behavior-setting symbol; its observer records unavailable(-1),
not a fabricated0 or1. Its pre-options movement cannot be silently treated
as an Easy parity oracle. The combined root review is
`root49-parent-modes-review-ay.json`, SHA256
`3a959d8884b104ecec9f365e389a1efaa8785dc804b80e4b09bf8b6c165fd17b`.
The first AY host failure was a missing conventional Simon ROM filename;
AZ resolves the exact pinned ROM hash without overwriting that negative.

The complete Ice DJ packet is now frozen and independently reviewed. Root
rehashes229 receipts,457 sources, generated inputs and all four build
artifacts, then reexecutes all eight original reports to their exact hashes.
Its source-order checks cover invulnerability, thaw/refreeze, damage/piercing,
360 completed-update STOP, actual cannon bullet movement suppression, beam
pool cleanup and the source NSF24 armor cue. Defeat/absence cleanup clears
both freeze bytes. The palette pending flag lives in appended BSS$07EA,
preserving literal Metroid NSF scratch ownership at$EC/$ED. Local frozen
palette1 leases use NES colors$11/$31/$01, remove the temporary OAM tag before
DMA, and alternate only when an actual ordinary palette1 sprite conflicts.
This explicitly qualifies the Flash four-color/every-frame rendering;
native enemy rectangles and full waveform identity remain separate.

Working E now composes exactly those16 owned paths over D. Both D's optimized
`characters.s` feet dispatch and `sophia_source_terrain.s` head/origin repair
remain byte-identical. Each E ROM changes exactly1,208 bytes from D, precisely
the frozen CY-minus-P patch, with no overlap with D's own binary changes.
Both primary and both disabled-baseline builds succeed; the disabled
baselines remain literal. Fresh E native captures cover12 cleanup cases,
seven actual controller-created-shot/lifetime/pause/palette cases,18 staged
NMI cases and two nonzero AllOnes constructors per mapper. Frozen independent
instruction models reexecute all registers,10240 RAM bytes, stack, mapper
state and ordered writes without new masks:444 cleanup calls per mapper,
492/536 state callers,488 whole ISR bodies, and85/99 independent complete
OAM lease transforms. Source predicates and compiled phase/cost oracles
remain bound to the exact owned binary patch. No natural acquisition or
full-route proof follows from these initial-state component checks.

The previous474 actual main-D files are preserved in
`root49-ice-adoption-e/before-main-d.zip`, SHA256
`1f6f4dde0af103b78bfffb44444433ebcd786030d6b3666b9ca041ec091f0f09`.
E checkpoint `roster-audit-v49-ice-over-sophia-e/manifest.json` has SHA256
`65072e56ce25e03e748248cb1efdc51312378e23d099259261bc02d71a76d64b`.
Installed MMC3 is
`868192d9df8541c999bcecd5460ed547d484a0b1252c96f37cd2bf5cd19b5c82`;
MMC5 is
`369af041f4f7f271e9355adedeb729963b26c315368e11dddd1c0c0d41fb1ae9`.
Both actual installed ROMs pass boot/title/load/controller/floor checks;
all457 main sources,11 generated inputs and eight primary artifacts are
rehashed. The installer initially rejected an absent host-exit string inside
the native log; that bookkeeping negative is retained. The actual smoke
processes had both exited0, and the corrected record binds their log hashes
and observed exits before adoption. No failed game assertion was suppressed.

Ice cost accounting remains explicit: EffectsAny adds43 cycles per call,
normally86 per Samus update; quiet NMI adds24; inactive renderer adds25/26
for MMC3/MMC5; Samus-only freeze clear adds22. Active palette processing costs
thousands of foreground cycles. These are measured local costs, not a claim
that whole-game lag is solved. Full roster/arsenal/upgrade verification, all
retained legacy failures and final lossless recordings remain open. All
earlier C/D route proofs keep their original image and mapper scope; E needs
actual transfers rather than relabelled proofs.

Bill's D/MMC5 discovery K is independently replayed as full-audit L:
39,517 frames/39,516 polls, all six stages, zero deaths,2-3 entry39,493 and
25 controlled updates X40 to70. Root rehashes the843-file D phase freeze,
the earlier1,988-file C freeze and both subordinate D freezes, then compares
all39,517 movement/controller rows and39,018 native telemetry rows exactly
against K. K is explicitly a discovery without the full hardware audit;
only L supplies that complete audit. Actual menu identity is Bill/Easy0,
not Lance or an automatic E transfer. Native enemy-ID correction-j is bound:
7 is Bloober,10 Grey Cheep Cheep,11 Red Cheep Cheep. Earlier ID10 rising-fish
explanations are withdrawn; raw IDs, positions and accepted controls are
preserved. This does not prove original fractional enemy geometry.

Two fresh complete Samus fixed-input transfers on actual installed E fail:
MMC3 at8,174 in1-2 and MMC5 at3,920 in1-1. Their first19-field movement
differences are1,203 (D466/Y93 versus E465/Y94, skipped NMIs28 versus32)
and2,236 (D801/VX0 versus E802/VX20, skipped NMIs35 versus39).
Inputs remain literal prefixes of the successful D tapes. These are retained
actual E negatives, not evidence of a proved movement/collision bug or a
successful E route. Real completed-update/input-producer timing must be
bound before making that diagnosis. The combined independent root report is
`root49-ice-integrated-e/route-review-ba.json`, SHA256
`c9e9f3d3640640fb5e2d8c2c689a47bc0745b1562274a077d9c5b468705bf1fb`.

`root49-goal-coverage-ay.json` adds E without relabelling any C/D proof.
It retains14 identities and66 inventory entries, earlier shortcut/non-shortcut
requirements and all final media/arsenal/lag obligations. At this checkpoint
E has no admitted complete route. The all-roster goal remains active.

Working F optimizes only Samus's active frozen-enemy palette leaf. Processing
four sequential OAM entries per loop avoids the repeated four-INX stepping
for each sprite, while preserving every output and the complete ordered
write sequence. The scoped old/new compiled comparison uses6,328 cases:
184 actual E start states and6,144 independent complete-OAM/physical-flag
components. All registers,10240 RAM bytes, stack, mapper state and ordered
writes are exact. The initial short branch exceeded the assembler range by
three bytes; its source/log/receipt are retained before the equivalent long
branch repair. No failed game assertion was changed.

Four fresh F native groups pass the literal original seven lifecycle/shot/
palette cases,18 NMI cases and two AllOnes constructors per mapper. Original
independent instruction models reexecute1,118 complete callers and471 whole
ISR bodies, with87/127 independently checked complete OAM lease transforms.
All360 completed frozen updates, pause/resume, source NSF24 hit cues,
pending-packet ownership, native DMA and palette conflict rules still pass.
The root native review is
`root49-freeze-render-fast-f/native-review-e/review.json`, SHA256
`de94c59ffbf45addb249693e8f1c97d8b13ef1f9dce7bdf03ec8e4ffed08acb8`.

Matched execution from214 fresh F native start states reduces the active
leaf median from4,134 to3,062 cycles on MMC3 and4,072 to3,062 on MMC5.
Measured savings are1,070..1,072 and1,010..1,012 cycles respectively, roughly
25% of this pass. This isolated instruction comparison excludes ISR/DMA
stalls; the fresh complete native ISR/caller proof is separate. Actual
palette-opportunity counts are retained without claiming identical physical
frame windows or universal FPS improvement. The cost report is
`root49-freeze-render-fast-f/matched-native-cost-f.json`, SHA256
`fcad6f4385698c254ccbe3081b42cbc9ba08c47a547647f17f4894540e743371`.
EffectsAny's usual86 extra cycles, quiet NMI24 and inactive renderer25/26
remain unchanged, as do the open Easy route-transfer negatives.

All457 sources remain E except `src/samus_freeze_render.s`. Each ROM changes
486 bytes, all inside the existing active leaf and its grown trailing local
tables in bank11; every other ROM byte, RAM address and disabled baseline
is literal E. Both installed ROMs pass boot/title/load/control/floor checks.
The actual476 main-E files are preserved in
`root49-freeze-fast-adoption-f/before-main-e.zip`, SHA256
`6411709daf847ee04cd80e9d3bf0736b44567e90ac97f0d1dca62d59d80bae93`.
F checkpoint `roster-audit-v49-freeze-render-fast-f/manifest.json` has SHA256
`c0f31e09027aad704fc539e95adc0a53abb035fef647206b61bb10d94c8068e2`.
Working MMC3 is
`ae0f981a8846238185d2d69549accf69f68b779832cafa7dd35bc431b00b09ca`;
MMC5 is
`c1021595edc43249be76a39e8a93c49e15f41585d51f9c6787d799b8f9ba17f8`.

Sophia independently completes immutable D/Easy/MMC3: AO discovery and AP
full fixed replay are25,661 frames/25,660 polls, zero deaths, all six stages,
real2-3 entry25,637 and25 controlled updates X40 to67. Root rehashes248
frozen receipts,455 sources and the actual image artifacts and independently
compares all nine whole audit CSVs byte-for-byte. AP's single10,240-byte
endpoint RAM dump confirms identity and active2-3; no two-run full-RAM
comparison is claimed. The root review is
`root49-sophia-d-full-review-az.json`, SHA256
`a01e31ed77b3032da3742d3fe2b740c8abcff3b98985fc9914832a7bf45a74cb`.
This is not F/MMC5, a final movie, complete arsenal or whole source geometry
proof. The D phase remains frozen; a separate current-F transfer has begun.

Actual F Samus controller work also exercises the intrinsic Easy Morph Ball
and bombs. A primary-fire defense fails against the first underground
Goomba: captured shots atY186 are above the native proxy boxY198..204.
This does not establish the original enemy bitmap/anchor or a muzzle defect.
Early bomb spam B genuinely morphs, spawns bombs and bomb-boosts Samus, but
explodes too early and then drops bombs while airborne. C waits for the
observed46px enemy approach and creates bombs while grounded. Both initial
Goombas are removed, all three bomb slots expire, and native Up unmorphs
Samus back to grounded control at8,388. C advances toX837 before a later
Goomba death9,659. This is concrete ordinary intrinsic-attack evidence,
not Hard-item acquisition, every enemy or a full F route. All failed
controllers, hardware audit streams and bounded injury snapshots remain.

The later repeat-bomb controller D fails9,486 on an actual approaching
Koopa0 at853/Y184, while ball-Samus is840/Y176. It had watched only the
farther Goombas and had not started any bombs. This is a retained controller
coverage error; account for all approaching actors before choosing that
defense. It is not a demonstrated bomb, movement or source-collision defect.
`root49-current-f-samus-a/review-az.json` independently audits all four
failures and the concrete C intrinsic-attack witness, SHA256
`03a47771d4f0c6f8748a3b771b5890ebedccf895c4ca64e1a6ea7b35815f8726`.

Lance also independently clears D/Easy/MMC5 in33,044 frames/33,043 polls,
all six stages, zero deaths, real2-3 entry33,020 and25 controlled updates
X40 to70. Root rehashes the final1,686-file D catalog and all five preserved
freeze catalogs,455 D sources and eight frozen primary artifacts. All33,044
movement/controller rows and32,545 native telemetry rows match discovery X.
Z supplies the full hardware/stomp audit. Native injury entries7,893 and
27,508 reach ForceInjury;27,643 does not and has no corresponding tier loss.
Its invulnerability counter was not sampled. The frozen AB qualification
explicitly corrects the older callback-count field name without rewriting
M/AA. Both Bill and Lance now have separate complete D proofs on both mappers;
neither is automatically transferred to current F.

The independent Lance review is `root49-lance-d-mmc5-review-az.json`, SHA256
`8babff72d65ecb3592ab35b8b178730a598bbd03bf3d6d62e34c405257f5dbff`.
`root49-goal-coverage-az.json` credits scoped F Ice components and the
ordinary Easy bomb witness, while keeping all14 identities,66 inventory
entries and every outstanding acquisition/interaction/lag/final-media
requirement. No final recorded release or full-goal completion is claimed.

Current F progress BA independently admits Sophia/Easy/MMC3's complete
power-on replay through2-2. Candidate K and independent fixed L each run25,404
frames/25,403 polls, with zero deaths and all six stages. They enter2-3 at25,380
and demonstrate25 controlled rows X40 to67. Root compares all nine entire audit
CSVs byte-for-byte, rehashes101 frozen receipts,457 F sources, eleven generated
files and eight primary artifacts. The single fixed endpoint snapshot contains
all10,240 RAM bytes and confirms identity/options and active2-3 control. There
is no candidate endpoint dump, so no two-run full-RAM equality claim. The root
report is `root49-sophia-f-full-review-ba.json`, SHA256
`60d0999d8e19088b915984abdc9550e708bbd12b18cd8ef4569f3904f0864031`.
This proves an F/MMC3 ordinary route, while MMC5, complete arsenal/source
geometry and final media remain separate. The Sophia phase is frozen and a
separate Link F phase has begun.

Additional ordinary F Samus observations cover three bomb defeats in F/G and
three more in J. J plants bombs and retreats on real floor, allowing both
volleys to complete while Samus remains grounded; its actual enemies are
three Goombas, superseding the preparation's two-enemy description. A genuine
Up release and new press exits Morph Ball, with grounded control restored.
The supporting reports are `root49-current-f-samus-a/review-ba.json`, SHA256
`06231c07f40ec3cfdd8136659fecffd15aef129f14408b0a0a8a0992ec77c833`,
and `review-bb.json`, SHA256
`b8146d1ca3cd2b883e5eb1814cbea991b8f44db6ee8bacbe0e1835af0b9cfbc6`.
The step-jump witness checks real82/82 terrain and a released native A latch
before takeoff. I/J also match their first11,600 whole movement and input rows.
These are intrinsic Easy attacks, not Hard acquisition or complete arsenal
admission. The unused G stand-return hook pointed into its trailing data;
only its actual entry hook attained. Form/pose transitions prove the exit,
and no return-ABI observation is claimed.

Samus L genuinely clears1-1,1-2 and1-3, entering1-4 at17,929, but dies21,109.
The actual guarded owner is Bowser0/ID45 at2179/Y113 with80 remaining HP,
against Samus2164/Y128. Earlier commentary and the first root reviewer
incorrectly called this a flame; the raw callback proves body contact.
The failed reviewer and additive correction receipt remain in
`review-bb-host-negative`. K's initial held-Up diagnosis is also superseded:
its fresh Up exits correctly, then the generic controller remorphs and waits
for a distant Goomba across the pipe corridor. L excludes that corridor from
the stationary bomb tactic and advances. These controller negatives are
retained, and no source geometry defect is inferred from the actual contacts.

The unchanged explicit Hard inventory fixture also passes on both F mappers,
six mature private pickups each. It proves six ownership acquisitions, missile
spawn/type41 and stock20 to19, Ice type46 and Wave type3 creation. Morph inputs
are supplied but the fixture does not assert its resulting body; Varia/Screw
effect contacts are untested here, and Long/mushroom is initial state0x81.
The scope report is `root49-current-f-samus-inventory-ba/scope-b.json`, SHA256
`81d9c85126344481794c3c168e0caf119bdf4b84ad24fae3a39829ec255717aa`.
Root viewed the isolated Ice/Wave screenshots; that is not full animation,
palette, audio or source-pixel acceptance. These are authored arena/state
fixtures, not natural block emergence/drop or controller-only route evidence.

The latest full-scope index is `root49-goal-coverage-bb.json`, SHA256
`0363d4cf0cf73cd31fe68b9df7283e51b0eb93759799472839bcc9ce217187d5`.
It retains all14 identities,66 inventory entries, both route variants, every
acquisition/interaction/lag requirement and retained final recordings. Sophia
is the first complete current-F route; no full-goal completion is claimed.

Root continuation CG installs provisional working G, the Samus head/side-axis
repair. Actual F replay V is quarantined after29,923: an upward jump beside
coral incorrectly separated Y171 to185, then the left-wall clamp advanced
sixteen pixels per update. A passive exact-tape replay identifies the native
head and wall writers; the original minimal regression fails on both F
mappers. The diagnosis is `root49-samus-f-coral-defect-review-bp.json`.

G checks each nonempty head sample against the previous Q8.16 head position
before admitting a ceiling, following pinned2.02 HitTester.checkLastHitPoints.
Walking coin checks, the three head samples and actual brick/reward origins
remain. This does not claim complete original corner-axis equivalence. Both
mappers pass48 coral-side jump arenas,432 head-displacement arenas,150 Easy
head and240 wall arenas,75 debris origins,19 question rewards and a complete
mushroom rise; the existing power-up animation and swimming fixtures also
pass. The corrected wall observer binds actual physical-bank/eight-byte
hooks: its obsolete CurrentBank==1 check missed fixed-bank effects while the
rare head handler mapped bank9. Legacy brick expectations explicitly select
Easy; the original default-Hard failures are preserved. Shared fixtures have
not silently been rewritten to make them pass.

The compiled axis leaf also passes5,070 independent Q16 geometry components
per mapper. Empty complete-head outputs match F outside stack call bytes and
use no mapper writes; measured extra cost is10 walking/32 rising instruction
cycles. This replaces the first private candidate's unconditional banked
sample. The99-byte cold leaf fits both mappers; only the original184-byte
head procedure and the appended cold gap differ in ROM (204 changed bytes).
Baselines are literal F and all old external function/RAM addresses remain.
The twelve native regressions are pinned by
`root49-samus-head-axis-g6-check-bx/review.json`, SHA256
`cc64372af948d3ea2f8bb00d15c8ebf4412ef04305c29660ae41a03671d8f941`.

Working G checkpoint SHA256 is
`feacfe9cf513d6c57dde8a4f2990e0bbd6c14ecda533d971747ad0011cee0fd0`.
Both installed boot/control/floor smokes pass; the476-file F backup is
verified. This remains provisional: replaying the old F V physical tape on G
dies at4,199 in1-1 after position/cadence divergence at2,324, so it does not
demonstrate the underwater repair in an ordinary full route. Fresh G routes
and retained final videos remain required. Frozen D/F proofs retain their
original identities.

Root independently admits Bill and Lance F/Easy/MMC3:34,401/33,254 frames,
all six stages, zero deaths and25 actual2-3 controls X40 to70 each. The frozen
3,311-file/34-packet review preserves30 negatives and rechecks all21 trace
fields, native telemetry, supports and actual256-byte DMA snapshots.
`root49-lance-f-full-review-ca.json` SHA256 is
`82a5739180507824f70ce918e5df7111100b1c3dfeeb0f09eab3c0387faadaad`.
Sophia's earlier independently verified F proof remains separate.
Mega Man and Bass now have independently root-reviewed D/Easy/MMC3 proofs:
28,951/30,281 frames, zero deaths, with real subsequent-stage control.
Bass's full57-file raw/241-receipt/21-file closure rehash and20,943 actual DMA
decodes are in `root49-bass-d-full-review-cd.json`, SHA256
`8e69318409d58fed9d56eee444696652a218a2fd019589ff0050d97c215a2017`.
These are base routes, not complete arsenal/source-geometry/media admission.

Additional Samus F progress legitimately clears five stages and enters2-2;
the later coral displacement is invalid traversal evidence. Both-map Hard
components separately verify first Ice freeze without damage, second real
Ice thaw/damage, frozen-platform contact and authored Screw protection;
forced-roll missile ammo recovery, weapon-slot OAM and authored sound channel
restoration retain their explicit arena/ownership limits. The strengthened
shared passive fixture is the only adopted test change outside G's runtime
source catalog. Actual-route lag and interrupt-exclusive1-2 CPU scopes are
measured, with audio, drawing and enemy work still significant; no broad lag
solution or complete weapon profile is claimed.

The full-scope index is now `root49-goal-coverage-cf.json`. All14 identities,
66 inventory entries, both original1-1 route variants, every enemy/item,
remaining abilities/lag work and retained final recordings remain required.
No full-suite-green claim replaces the original73 failures/stock-Mario
comparison. The user's explicit lossless-retention/cap-raise answer supersedes
the old30GB limit; the bounded internal global cap is80GB, with all previous
allocation receipts and negatives retained. No full-goal completion is claimed.


Root continuation CV keeps the working build at G. Independent root review
`root49-current-route-review-cm.json` verifies Mario and Luigi on both MMC3
and MMC5 through six stages and25 subsequent2-3 controls, zero deaths. Their
routes remain small throughout, without injury; this is not a growth/fire/
Star or complete-specials proof. Two Mario takeoffs are explicitly native
corner catches, not certified terrain-top jumps. Independent fixed replays
match all21 trace and16 native fields; actual hardware/DMA and support checks
pass. Link's G/Easy/MMC3 fixed transfer completes27,058 frames, zero deaths,
25 subsequent controls X40 to62. All nine canonical streams literally match
the original F candidate/fixed pair, and the single10,240-byte G endpoint
matches F fixed. The root rehash covers1,915 F files and46 G files. No complete
Link accepted-ground-A log exists; no universal support, MMC5, source-perfect
or complete-arsenal claim follows. Root receipt SHA256:
`ed8e80955df544744f0b1cc704e2db34faceb22b4bc3b40e495e52b58718cfe9`.

Fresh ordinary G Samus controllers now legitimately pass the first four
stages. Two observed underground bomb encounters produce six native Goomba
defeat-state transitions, three per group. Fresh bridge controls pass Bowser
using the actual moving platform; this does not claim a Bowser kill. The
later2-1 pose guide loops over a shell and farms lives, then dies; a successor
leaves that loop and contacts an actual Green Koopa. Neither is a complete
route or underwater-coral repair proof. The original G bridge host postprocess
mistakenly read the prior F-attempt output directory; its retained report is
superseded by the explicitly tagged actual native manifest in CV. The second
bomb host encountered a missing-result key after an intentional controller
stall; that negative and the actual result-null manifest remain retained.
No runtime patch is inferred from those host/controller failures.

A private H candidate ports the existing MMC5 Metroid flag-scan replacement
to MMC3. It changes75 ROM bytes across five music banks; MMC5 and both
baseline ROMs stay literal G. Working sources and installed ROMs are unchanged.
Compiled checks cover65,536 mask/status combinations with an explicit oracle
for every removed scan RMW/stack write and no unexplained RAM/register/bank/
APU differences. Isolated execution from122 actual F audio-entry snapshots
saves a median1,470 instruction cycles per update (old median5,985; new
median4,531). This is not a whole-game frame-rate measurement. Six existing
native audio fixture groups pass on both mappers: short/long/wave envelopes,
pickup sounds and world effects with physical APU/MMC5 assertions. These are
authored fixtures with setup writes, not ordinary acquisition or final media.
Native interrupt composition and ordinary H traversal remain required before
adoption. Build/CPU/native receipts are under `root49-samus-audio-scan-h`.

The full-scope index is `root49-goal-coverage-cu.json`. All14 identities and
66 inventory entries, remaining routes/upgrades, original1-1 variants and
every enemy/item, lag work, and retained final audio/video are still required.
No original suite failures are erased and no final recordings were made in
this continuation. All negatives/lossless files are retained under the80GB
global allocation authorized after the user's explicit cap-raise answer.


Root continuation EB installs the H MMC3 Samus audio scan optimization. The
frozen H checkpoint is `roster-audit-v49-samus-audio-scan-h`; all458 build
sources,11 generated inputs and8 primary artifacts match installed main.
H changes75 MMC3 ROM bytes; MMC5 and baseline ROMs stay literal G. The earlier
private-H/pending-adoption paragraphs remain historical. Native validation
now includes560 complete AudioUpdate calls with258 actual child IRQs and
233,997 ordered writes exactly reproduced against full10,240-byte RAM and
register/bank/cycle endpoints. No native IRQ occurred inside the changed scan;
5,544 authored boundary injections separately cover the changed instructions.
The installed boot/swimming/power-up checks pass on both mappers. The isolated
median1,470-cycle saving remains a call-level measurement, not total FPS.

Independent root H reviews DL and DW admit seven actual Easy/MMC3 full base
routes: Mario, Luigi, Mega Man, Link, Bill, Lance and Sophia. All six stages
clear with zero deaths and actual control in2-3. All nine canonical input,
gameplay and physical hardware streams literally match their previously
reviewed G/F routes; all137,092 actual DMA snapshots are independently decoded.
Mario/Luigi MMC5 additionally have explicit literal full-ROM identity links to
their prior G executions. Those links are not fabricated fresh H sessions.
Every original source/support/power-tier limitation remains in force.

Four H base-route movies now exist for Mario, Luigi, Link and Mega Man. The
186 native ZMBV parts and continuous PCM recordings, verified lossless MKV
masters and playable MP4 copies are all retained. Root review DZ rehashes752
files and independently checks PCM identity. Automated scans decode all93,975
lossless frames; these runs have no HUD split, CHR-lag, sudden-motion, vertical
shift, black-flash or illegal-stomp flags. Selected contact sheets and menu
samples were inspected. This is not manual inspection of every frame or
every source waveform. Link321 and MegaMan2727 queued sound observations have
physical writes but lack the generic owner-bit evidence; native remapping,
priority and audible correctness remain follow-up work, not waived failures.
Mario/Luigi's observed events all have voice and physical-write evidence.

The export tool now accepts the caller's raised storage allowance instead of
rejecting any value above30GB. Real four-movie exports validate the80GB path.
The frame reviewer prefers a hash-verified lossless master and requires the
exact expected frame count. All prior captures, negatives and receipts remain.

Actual H Mega Man underground profiling covers46,191 calls with all nine
native prefix streams unchanged. Median main GameLoop cost is20,018 cycles;
its95th percentile is28,623. AudioUpdate runs in NMI, median7,125.5 cycles,
and drawing costs median6,754 when performed. MegaManWeapons95th percentile
is6,129 cycles. Parent/child function totals overlap and must not be added.
This identifies remaining music/enemy/drawing/weapon work; it is not a claim
that overall lag or WaterShield is solved. The initial host's all-scopes-main
assertion is retained; the corrected review explicitly separates NMI audio.

New ordinary H Samus play clears the first three stages. The successful first
underground lift crossing walks to the actual32/48px platform edge before
launching, avoiding the earlier overhead sibling. Castle lower-bar timing is
still in discovery. The unchanged old G physical input tape diverges in pose
at H frame1203 after the audio timing improvement; copying its physical frame
schedule is not a physics equivalence proof. G native producer capture remains
G,18,497 actual movement entries with literal G input/trace prefix. Retained
host/controller negatives include the frame-limit label, large-platform flag
being actor-slot rather than zero, and nearest-pose/platform/phase failures.
No production collision patch is inferred from these controller failures.

The full-scope index is `root49-goal-coverage-eb.json`. All14 identities and66
inventory entries, every special/upgrade/acquisition, original1-1 shortcut and
nonshortcut/everyenemy/item requests, remaining lag work and complete final
recordings stay required. The original73 suite failures and stock comparison
are not erased. Global allowance remains80GB under the user's explicit
lossless-retention/cap-raise answer, superseding the old30GB goal text. Current
specialist caps are MLS1GB, MegaMan/Bass1GB and LSR1.4GB, each100MB reserve.


Root continuation FJ keeps installed main at immutable H. Scrooge and Bass
now have actual H full fixed replays, independently rehashed with full physical
OAM decoding. Scrooge clears21,742 frames and Bass29,543, both zero deaths
with25 responsive native2-3 rows. Eleven Scrooge and14 Bass streams match
their separately reviewed G proofs literally. The H total is now nine
identities and177,948 independently decoded actual DMA snapshots. All original
corner/platform/spring/source/power/audio limitations remain. There are still
four retained H base movies, not final recordings for the entire roster.

Actual H Samus now clears five stages. A late supported jump from the moving
castle platform at2188 passes Bowser; the earlier jump bonked the real ceiling
and the stationary wait was carried into his rising body. The old guide's
future AreaPointer rejection and recomputing past an already active fallback
were controller defects. One observer is used in the successor, retaining the
old duplicate-log negative. Real supported coral jumps now reach2-2 X2097;
the remaining failure is a native fish contact on descent. No source-disjoint
claim is inferred from that inclusive collision. Pit has a new25,750-frame H
discovery clear; independent full hardware/support replay is still pending.
Rygar passed the first low-ceiling pit using an actual1274 edge takeoff and
later reached a second Goomba. The three identities are not yet root-admitted.

The original H authored WaterShield checks retain two MMC5 max-cycle failures,
6113/6114 versus the existing6100 bound. Private cache proposal EQ/ES moves
the vector-key guard into its sole caller, removing only a redundant JSR/RTS
on cache hits. It saves12 cycles per reused ball, typically84 per expansion
update. Both baselines, foreign addresses and RAM ABI stay unchanged. Root EW
checks10,240 compiled cases, exact remaining ordered writes/registers/liveRAM,
with only the two individually identified dead call-stack cells excepted.
Eighteen unchanged native groups cover exact signed orbit, nonuniform expansion
and lifetime, world/Y wrap, source-left reveal, terrain corners, OAM, Bass
specials and MegaMan special armor. These are explicitly authored arenas.
MMC5 expansion max falls to6029/6030 and actual DMA is60/62; MMC3 still has
18/62 or21/62 missed expansion opportunities. FE's original prose20 is corrected
to21 in its additive receipt; raw attached metrics were always21. Serious
populated-level lag is not solved by this small optimization.

Root independently reruns the frozen private H MegaMan audio verifier:1167
pinned files,44,428 foreign symbols,16,008 compiled lifecycle calls,200 actual
native calls with195 child IRQs and1936 exact native instruction clocks pass.
Observed same-entry savings are362..516 cycles. Only the owned MMC3 audio
closure changes; MMC5 is literal H. A local copy of py65's cycle table repairs
its CE/DEC-absolute3-cycle entry to the native6-cycle value; shared dependencies
are untouched. The old H controller tape's private timing/death negative is
retained and never promoted to a route clear. Private combined I now builds
as the exact disjoint union:1508 MMC3 bytes,149 MMC5 bytes, both baselines
literal H. Its18 combined native groups pass. It remains private, with no
adoption, full ordinary-route transfer or final-media claim.

The new equipment audit distinguishes11 MegaMan and9 Bass equipment nodes,
including intrinsic Busters, automatic Charge and passive/replacement Balancer.
The existing66-ID index already includes Charge10; it never covered all
intrinsic/mode/refill/animation/SFX/lifecycle requirements by itself. Historical
170 subsystem passes and six retained failures remain historical. Source
review identifies Super Arm's wrong payment time (native lift versus source
throw), and source-valid low-energy Rush behavior requiring focused witnesses.
Private Arm correction is authorized in its own measured phase; main remains H.
All prior captures, lossless masters, negatives and receipts remain retained.
The later raised-storage authorization supersedes the original30GB request;
the measured working ceiling remains80GB.


Additive root FP review now admits actual H Pit's independent full replay,
25,750 frames with zero deaths,25 native2-3 control rows and22,440 actual
DMA snapshots independently decoded again. The133-file frozen packet and
source458/generated11/frozen16 proofs recheck. All153 actual accepted launches
are classified:148 solid tops,three live platform owners,one specifically
qualified landing/side-resolution corner at5872,one compressed spring18699.
Nested spring callbacks18707 are the same armed continuation. The one13940
motion candidate retains actual native side/stop chronology, with no universal
writer/source-equivalence claim. Power0->1->0 is observed; exact item/injury
lifecycle and tier2 flight remain separate. The installed H total is now ten
identities and200,388 independently decoded actual DMA snapshots. Samus,
Rygar, Simon and Ryu still need complete current-build proofs. Overall
equipment/source/mode/lag and all-character final media remain incomplete.


Root GD independently reexecutes the435-file Pit/Rygar packet and separately
decodes Rygar H21537/21536, zero deaths, all six stages and25 responsive2-3
controls. All111 actual launches classify as107 terrain,three live platform
owners and one compressed spring;18,621 DMA snapshots decode independently.
This is the eleventh H base identity and219,009 total independently decoded
DMA snapshots. Rygar tier0 alone and equipment/source/movie limits remain.
The real late HUD split remains unresolved: raw PPU4943 maps completed4944,
scan34/dots277,289, aligned DMA1/lagFlag0 after prior DMA0/lagFlag1. Both NMI
paths programIRQ31; no intentional34 deferral is claimed. The source owner
and cause need new passive chronology; no clean physical-video claim.
Samus, Simon and Ryu current-build proofs and all broader requirements remain.


Root GK admits actual H Samus independent32224/32223/all6/zero deaths,
25 responsive2-3 controls X40 to70. Whole input/trace/events repeat discovery
literally. All170 actual source accepted jumps classify164 terrain/five
native platform owners/one compressed spring26022, actor top184/phase2.
The indexedSpring hook had zero calls and is not claimed as exercised.
Intrinsic Easy Morph and its5NESpx displacement are observed; the prior GF
standing-only host assertion and GG B-bomb-lift bound remain observer/control
negatives. GH used a clearly scoped tail observer; GJ observes the full replay.
Actual DMA decoded independently: 24939. Twelve H base identities
are admitted; all physical findings and equipment/source/movie limits remain.
Root GE independently reexecutes all180 frozen Arm native fullcaller pairs
and rehashes470 source files/16 artifacts/451 raw receipts. Arm/I remain
private; Rush source and confirmed HUD queue overflow repairs are in progress.


Root GN/GO/GP rehashes frozen777-file G Simon and separately executes actualH
28793/28792/all6/zero deaths/25 responsive2-3 controls X40 to70. All11
original streams and full endpoint RAM are literalG/H. New exact native
source hooks pair226 consumed launches with actual prior fresh inputs:
146 terrain,five liveplatform owners,75 genuine available-secondary consumes.
Six unavailable-air inputs reject; above-viewport secondary jumps remain
source-valid. One nativeSpring entry is observed, without a downstream-index
claim. All25,537 actualDMA snapshots independently decode. InstalledH now
has13 base identities/269,485 actualDMA snapshots; Ryu remains incomplete.
Source geometry, equipment, mode, SFX/waveform and final movie obligations
remain open. Private audio/Water/Arm/Rush/HUD work has not been installed.


Root GS/GU/GV/HF: all14 actual H Easy/MMC3 base identities now independently
clear through2-2, with289401 decoded actualDMA snapshots. Ryu23098frames,
zero deaths,2-3entry23074 plus25 controlled frames X40to77. All11 G/H streams
and endpointRAM are literal.167 fresh inputs produce118 ground launches
(113terrain,4platform,1spring),46wall launches,2Down+A drops and1rejection.
42wall launches have current source cached contact;4 remain legacy fallback,
an explicit source geometry gap. Eight positive14..16px motion flags remain:
specialist unchangedH passive replay identifies exact native bank10 LeftClamp
STA atA2F5, opposite cached source climb side. Private narrow repair underway;
this base clear does not establish glitchless or complete2.02 source behavior.

Root GW independently rehashes frozen Rush mechanics470source/16artifacts/
889receipts and reexecutes all143 native fullcall pairs and560 source edges,
plus exact relocated-return lifetime controls. Land SFX remains a separate
private successor; no main install. HUD overflow repair likewise remains
private, with original offset100 versus84 capacity proof retained and material
mixed-queue foreground cost still unresolved. Native discovery is not yet a
bothmapper/fullroute acceptance.

Root GY/HA/HC/HD/HB/HG: privateI successor J changes47 bytes in the old50B
enemy-candidate scan on each mapper, preserving all RAM and outside-span PCs.
It hoists only the unchanged native offscreen rejection.18048 compiled scan
cases and18 unchanged native mechanics/geometry/OAM/foreign groups pass.
Twelve H/I/J profiles require actual native target eligibility; all attain
full8 shield orbit and expansion. Matched offscreen samples save4995(M3) or
4831(M5) cycles per8-ball update,32 samples peridentity/map. Genuine visible
enemy expansion remains about11.5Kto11.8K weapon cycles and is still laggy.
GQ/GT predecessors counted active actors without native offscreen admission,
so their full8 active-target windows do not establish visible-contact stress.
Skipped-consumer scratch liveness, further visible-target optimization and
full combined validation/adoption remain open. All candidate builds remain
uninstalled; installed source458/generated11/primary8 are again literalH.

The user's retained-lossless/raise-cap instruction now has a100GB working
cap,143GB free at allocation. All original inventory66/intrinsic/upgrade/
acquisition/ammo/icon/SFX/lifecycle/mode,1-1 variants/enemies/items and final
real audio/video requirements remain active. Only four retained H base movies
exist; no fullgoal/source-perfect/final-release claim is made.

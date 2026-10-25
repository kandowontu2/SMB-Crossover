Mario / Luigi / SMB3 brothers / Scrooge / Darkwing bounded source audit
2026-10-25 -- assignment 7; PRIVATE proposal, not adopted

Accepted parent: f00c2a7ad0459a3cd0b369bb4fbc9f374dc27d9335b2cc1fe1867f3f98d73d23
Private proposal: cb4408155507a54c65590dcd1c3c2e31205701627a839492aec569cfd22178b4
External evidence root:
C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/mario-scrooge-audit-v1

Confirmed defects and first incorrect decisions

1. SMB3 fireballs AND hammers cannot damage Bowser. In accepted bank 90,
   M3ShotEnemies A766 loads the actual ID $2D; CMP #$15 at A769 makes the
   following A76D JMP A7CE reject him before geometry or damage. An overlapping
   shot leaves native BowserHitPoints at 5 and remains alive. The authored
   original SMB3 common fireball/hammer handler accepts original Bowser ID $18;
   actual instructions decrement his original hit counter 34 -> 33 for both.

2. SMB3 hammers cannot defeat Buzzy Beetles. Accepted bank 90 A777 CMP #$02 /
   A779 BEQ A7CE rejects both weapon kinds. Authentic original attributes $51
   grant fire immunity rather than general weapon immunity. Actual original
   handler leaves a fire-hit Buzzy alive, but a hammer sets OBJSTATE_KILLED=6.
   Accepted port leaves it alive for both. Goombas are positive controls;
   Podoboos remain protected in both accepted/proposed port matrices.

Minimal private proposal

proposal-v2/implementation.patch contains all three source edits, including the
new appended helper include and entrypoint include. proposal-v2/source is an
overlay, not a complete replacement source tree. The prepare command rebuilds
against the current root sources and verifies parent parity outside bank 90.
Only 51 ROM bytes differ, all in bank 90. Existing exported code/RAM labels,
header and every CHR byte are unchanged. No new RAM is allocated. Two existing
call spans remain the same size; helpers are appended after existing content.

Bowser deliberately uses SMB1's existing HandleEnemyFBallCol HP/progression
policy, consistent with other native additions. This DOES NOT reproduce
original SMB3 Bowser's 35-hit balance. Hammer contacts retain the port's
existing per-update contact behavior. This is a host-enemy integration repair,
not a claim of complete SMB3 enemy-balance fidelity.

Current implementation / differences / open evidence

Mario
  Implemented: A jump, B run/fire; crouch, swimming, vines, springs and native
  fireballs. Easy uses the old site's faster acceleration/lower walk cap and
  variable-release jump profile; Hard uses 2.02's height-limited jump profile.
  Easy a normal pickup advances one tier; Hard mushroom and flower independently
  target Super/Fire. Both keep normal stomps. The Hard fireball-brick admission
  is present. Twelve actual pickup-tier components pass.
  Unproved here: complete motion oracle, every terrain seam, physical emergence,
  scrolling/NMI, every SFX and actual displayed art. No new Mario defect found.

Luigi
  Implemented: native SMB1 movement, initial dry jump velocity minus 51/256,
  ground braking minus floor(native force / 8), original acceleration, water
  and scripted-motion exclusions. This is the user's retained custom profile.
  648 actual traction contexts and 32 jump-fraction contexts pass.
  Caveat: current Mario uses separate Flash Easy/Hard movement; Luigi is based
  on native SMB1, not a literal inheritance of that newer current Mario routine.
  Existing source comments intentionally retain this choice. No speculative
  feel change was made. End-to-end current-hash comparison remains unproved.

SMB3 Mario / SMB3 Luigi
  Implemented in both modes: small/Super, Fire, Raccoon, Frog, Tanooki and
  Hammer; ordinary stomps; native run/P-meter and flight, tail, statue, two
  projectile slots; Select at the portrait changes brother. Both use the same
  SMB3 movement repertoire. Powered blocks choose one of five forms randomly;
  repeated forms are possible. Small players receive a mushroom.
  P-meter source uses Player_Power bits to draw six original chevrons plus
  a two-tile P. Queue capacity and cached redraw logic are present. Actual PPU
  layout was not inspected in this assignment.
  Existing statue-damage fix still cancels queued statue/suit state, tail and
  flight flags on damage; 24 form/brother/mode components pass. Higher suit ->
  Super; Super -> small. Previously repaired shrink CHR code remains present;
  its old native receipt is a separate hash, not a new visual pass here.
  Broken: the two weapon filters above. Private repair CPU matrix passes.
  Unproved: every natural form, source projectile terrain/armor/boss parity,
  actual CHR/OAM/palette uploads, full P-meter native timing and fresh traversal.

Scrooge
  Implemented: A jump/release cutoff, B cane, held Down+B pogo; source-phase
  translated DuckTales jump/gravity; successful pogo rebound and per-strike hit
  receipts. Cane probes use actual world coordinates at both vertical ends.
  Ordinary Easy stomps are a ROM adaptation; Hard uses cane/pogo contact rules.
  Shared SMB power tiers are retained rather than inventing a 1.0/2.02 Scrooge.
  Sixteen actual launch/release/gravity components pass. This is not a complete
  DuckTales health/treasure/carryable-world reproduction. Native-source body
  evidence remains the earlier pinned scrooge.json/hitbox receipt.
  Unproved here: actual pogo-vs-enemy/terrain seams, art, all SFX and lag.

Darkwing Duck
  Implemented: original-style movement/crouch/shooting, four health, free normal
  gas gun, one carried Heavy/Arrow/Thunder adaptor, Select toggles normal/adaptor,
  forward cape guard for eligible hostile projectiles, attached-Arrow hanging
  and jump/drop release. Generic ordinary-ledge hanging is not demonstrated by
  the current DwHangUpdate; its search only considers attached Arrow actors.
  Arrow costs 3 gas; Heavy and Thunder cost 2. Caps: normal 3, Heavy 1, Arrow 2,
  Thunder 1. Gas caps at 99. Enemy drops/health aids and temporary wall arrows
  are implemented; tall-pipe recovery cache is an explicit SMB adaptation.
  480 actual launch/cap/gas/facing/standing/crouching/air contexts pass.
  Easy permits normal stomps; Hard ordinary body landings hurt. Health, gas and
  adaptors remain separate from the mode switch. No new Darkwing defect proved.
  Unproved: original-ROM full motion/weapon parity, ordinary ledge behavior,
  every natural adaptor/drop/arrow lifecycle, actual graphics and all SFX.

Verification and reproducibility

Tool: tools/audit/mario_scrooge_audit_v1.py
Final accepted-parent observations: baseline-final-v5/proof.json
Final private-positive components: proposal-final-v5/proof.json
Both execute 1,248 bounded components: 32 projectile, 24 suit-loss, 648 Luigi
traction, 32 Luigi jump, 12 Mario pickup tiers, 480 Darkwing launch/caps/stances,
16 Scrooge physics, four actual original SMB3 projectile handler cases.
Baseline final receipt deliberately says passed=false with three recorded
weapon failures. Private final receipt says passed=true, accepted=false.
The original SMB3 ROM SHA is
1ddc4b429490e298c05fa70389034107c0cb50f671c7c1baaa3f228224afc2e9.
Its rebuilt PRG/CHR payload matches byte-for-byte. The only declared original
handler trap is Score_PopUp, after successful weapon damage was decided.

Earlier baseline-cpu-v1/proposal-cpu-v1 were smaller checks; their permissive
passed field is superseded by final-v5's explicit baseline failure. Two source
oracle fixture failures are retained: v2 assumed killed-state 4 instead of the
source's 6; v3 tried to read an enum absent from the FNS export. Final-v5 reads
the enum directly from the authenticated source and keeps the damage assertion.

NO Mesen worker, game-source/config change, download install, Git change,
interrupt simulation, PPU replay, acoustic comparison or campaign clear was
performed by this assignment. Native qualification is required before adoption.

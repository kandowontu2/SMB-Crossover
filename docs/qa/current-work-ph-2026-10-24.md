# Current PC continuation: PF, PG and PH

Goal active and incomplete. Continue the full task; this note is not a reason
to pause, block or complete it. No gameplay source, checkpoint, public ROM,
guide or original negative receipt was replaced in this continuation.

Current ROM remains `build/checkpoints/smb3-shrink-pc/candidate.nes`, SHA
`37ad64c6f5e8859a29fc1982df6851a8f462292b3b44743c0283497774239af7`.
PC/OV adoption finalizers and the successful OG archiver must never be rerun.
The prior detailed handoff is `current-work-pe-2026-10-24.md`.

## Current-hash progress

An immutable ledger at external `2026-10-24-roster-ph/status-v1/proof.json`
records63clean discovery pairs and35strict independent direct replay pairs,
out of74required. It snapshots its changing input indices. The live direct
batch continues beyond that snapshot; do not mistake the snapshot for final
coverage or add old-hash OJ/OV totals. `roster_status_pi.py` makes another
ledger under a fresh output name when needed.

Eleven discovery pairs remain unresolved: Mario Hard; Link both; Grant both;
Pit Hard; Rygar Hard; Bass Hard; Chip both; Dale Hard. Every original PE
failure remains recorded. Six PE failures now have strict current-hash direct
replays: Mario Easy, Mega Man Easy, Proto Easy, Samus Hard and ZeldaII both.
Four SMB3 pairs already passed before this continuation.

## Active jobs at handoff

- Exec session40048: `replay_roster_pf.py`, external
  `2026-10-24-roster-pf/direct-batch-v1`. Sequential53passing PE discoveries,
  actual physical PPU frame captures, exact independent inputs/trace and strict
  unchanged review. `progress.json` is authoritative; only completed entries
  are saved. Failed raw reviews remain recorded; a separate positive native
  probe observer may resolve exact temporary projectile origins. No threshold
  is relaxed. The job was still running at handoff.
- Exec session67045: `scan_replay_batch_ph.py`, external
  `2026-10-24-roster-ph/scans-v1`. CPU-only diagnostic, no Mesen instance.
  Frozen27-pair subset from the then-completed PF batch plus four follow-ups
  and ZeldaII both. It decodes every indexed PNG and checks conservative
  three-frame background transients. Candidate sheets require investigation;
  zero candidates does not certify graphics. Later PF pairs need another
  filtered snapshot rather than counting this27-pair subset as all74.
- Exec session53293: one native worker, Grant Easy/Hard discovery with the
  source-owned wall-leap head-clearance controller; external
  `2026-10-24-roster-ph/grant-discover-v2`. Still running at handoff. Its final
  index is `discover-results.json`. The controller/preparation live at
  `grant-policy-v2` and `prepare-grant-v2.py` in that external PH folder.

Maximum two native Mesen workers. Check these jobs before launching more.
The four follow-up replay job76249, ZeldaII replay77741, firebar job40020,
both PG discovery jobs13527/54458 and old Grant job7160 are terminal.

## Controller diagnosis and positive follow-ups

- PF restored OM controls only for explicitly previously proven pairs.
  Mario Easy3057, Mega Easy5053 and Proto Easy5015clear and independently
  replay. Pit Hard3466andChip Easy2503still fail; retain those negatives.
  Trying ordinary generic navigation for Mario Hard fails1213/x1957at an
  enemy without collecting the first mushroom. This is not a physics repair;
  a future attempt should use the actual OM Mario controller before changing
  native behavior.
- Samus Hard's failed PE prefix was independently observed with all six
  enemy slots.317completed updates1800..2116hold Down+Left while facing right,
  crouched, never firing, with two Goombas approaching from the left. The
  hidden-Piranha hypothesis was disproved in that window. SamusMovement skips
  facing changes while Down is held. The corrected controller turns upright
  first, then crouches and fires. It clears5819and passes independent strict
  direct replay in `2026-10-24-roster-pf/followup-direct-v1`; zero game writes.
  `samus-observe-v1` and `samus-policy-v1` retain cause/provenance. A separate
  direct scan decodes all5,619frames,3,997eligible triples, zero candidates.
- ZeldaII's old one-shot bump controller began A in mid-air and kept it held
  through landing, missing its next jump edge. The PG controller lands,
  physically reveals/pursues/collects Jump and casts it. The first PG retries
  actually collect Jump, then fail because Lua requested unexported
  `Z2ActiveSpells`; the source-defined alias is `r('Z2LearnedSpells',2)`.
  Corrected PGv2clears Easy4427/Hard4657and both pass strict independent direct
  replay under `2026-10-24-roster-pg/zelda-direct-v1`. Original game bytes and
  motion are unchanged. Do not classify the Lua alias failures as ROM defects.
- Link's reduced idle attack spam remains a failed controller candidate,
  not an adopted repair. PGv1Easy dies2825/x1995; Hard1639/x801.
- Grant's later takeoff controller clears the first pit, then times out:
  Easy x1729/y136andHard near x721. Read-only observer PHv2confirms201completed
  updates at x1729/y136alternating climb0/1, Right/Up, no attack and no A.
  Wall retention's foot probe loses the corner, while its side probe grabs
  again. PH's first always-leap controller detaches too early at the pipe and
  both modes time out; retain `grant-discover-v1` as failed. The current v2
  controller climbs while head height is solid, then uses the already present
  fresh-Awall leap when head clearance is empty. No jump/speed/collision buffs.
  Grant observer v1sampled an earlier combat window; v2is the stuck window.

## Firebar screenshot: fresh current-hash evidence

External `2026-10-24-firebars-ph/current-v1/proof.json` passes four diagnostic
cases,1-4/6-4by character Easy/Hard:256actual hardware DMA frames,1,024owner
checks and139,520native mapped CHR byte checks. The unchanged NT fixture was
hash-checked and copied. Public settings/player/scroll seeds remain explicit;
no enemies, OAM, CHR, CPU, ROM or hardware registers are injected.

`current-source.json` confirms the actual linked39-byte castle actor stream
is byte-exact with original SMB and NT. Seven of eight tracked source files
are unchanged; later metasprite changes are covered by the new native tests.
Additional direct console pixels are retained at PPU1254/1341with rawARGB,
RGB and PNG round trips. Root inspected both images. Corresponding Easy/Hard
images are identical: two ordinary bars in1-4, all four in6-4. The pictured
empty mounts are authored later-world gates. No extra hazards were added.
This resolves the supplied screenshot, not every previous castle report or
ordinary castle traversal. `firebar-empty-mounts-2026-10-24.md` is updated.

## Review and remaining scope

Root inspected24-frame overviews for Luigi both, Mario Easy, Mega Easy,
Proto Easy, Samus Hard, ZeldaII both, Bass Easy and Rygar Easy:240sampled
route frames, not exhaustive human review. Two full-size Mario frames and
failed endpoints were also examined. Bass uses the guarded-review folder;
the failed raw review has no overview. Never guess a guarded folder exists.

Current PC linked legacy Hard requirements were re-extracted:86rows/10
identities, all explicitly unverified for item execution. External
`2026-10-24-roster-pg/legacy-item-requirements-v1`. Use systemPython for py65
tools; bundledPython has PIL/numpy but not py65. An initial bundled import
failed before creating output; this was a host dependency error.

Every-item emergence/pickup/use/graphics/SFX/damage/expiry, full37identity
inventory, exhaustive visual/source behavior/art/music checks, ordinary/heavy
lag, native TMNT audio, Kirby/Meta music and final full oversizedMMC3/MMC5
release remain open. Earlier staged/rejected audio candidates are not adopted.
All public ROMs and Astra's48-page guide remain unchanged.

Workspace measured29,986,817,377bytes before the last small tools/notes,
about13MBheadroom. All new large evidence is external. Keep below30GB; preserve
lossless files and protected latest/parent checkpoints. No user apps were
closed and no external messages/automations were sent.

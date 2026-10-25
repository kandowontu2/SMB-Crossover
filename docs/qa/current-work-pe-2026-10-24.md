# Current work after PC

The goal remains active and incomplete. Do not pause, complete, or mark blocked
because this note exists. Continue the full roster/item/fidelity/mapper work.

## Live source and retained builds

- Current live source/checkpoint: `build/checkpoints/smb3-shrink-pc/`.
  ROM `37ad64c6f5e8859a29fc1982df6851a8f462292b3b44743c0283497774239af7`;
  source ZIP `3bd63d55251ed49744770195157995f22cbd6f411cd373e6239f76c65e95a468`.
  1,132 source files; exact independent source-only rebuild and both ordinary
  flag-off hashes pass. The successful PC finalizer must never be rerun.
- PC fixes two operand bytes in SMB3 growth rendering. Actual original ROM
  growth/shrink code plus real port rendering passes376cases, repairing188wrong
  shrink phases. Four fresh Mario/Luigi Easy/Hard discoveries and strict direct
  replays reach movable1-2with zero deaths;13,698actual PPU frames retained.
  Same natural Mario Hard controls/gameplay match parent except CPU timestamps;
  all pixels outside the body match across the51frame injury window. Root
  viewed all51before/after body frames plus96sampled whole-route images.
- Parent OV checkpoint `build/checkpoints/render-dispatch-ov/` is adopted.
  ROM `4dcc0e87dd1c7dcbd6c11c92c5dc9d269616769e1cb7148b820cc5df2c463972`;
  source ZIP `30ff5df8263e2972712dea4de5c96ab37b24cccd5e0d2e43f6b0500f59e60711`;
  1,125source files. Successful OV finalizer must never be rerun.
- OV shallow graphics/new-character drawing gates change458bytes, preserve
  prior addresses/CHR/RAM, pass3,900owner-admission cases and7,842actual IRQ
  injections. Native Sophia/Chip600update components preserve every recorded
  input/gameplay field and improve lag. Held-input turtle PB components also
  match every field; heavy lag27→26/25→23. Original poll-indexed turtle comparison
  had one input difference at Donatello update500and is not an exact-workload
  pass. Its first adoption attempt stopped before any source copy; PB repaired
  the component timing and the later adoption succeeded.
- OV has37cold entries,7audio fixtures including4,096exact Samus calls,28injury
  scenes,7strict route pairs. These old-hash totals are not added to PC's four.
- OJ remains local at `build/checkpoints/collision-dispatch-oj/`, with53strict
  pairs/74attempted pairs on its hash. Its counts are historical.
- OG's six checkpoint files were moved, not deleted, to the existing verified
  external workspace archive by `archive_closed_og_pd.py`. SHA/mtime exact;
 18,136,489bytes. Successful archiver must never be rerun. Locate with
  `tools/workspace_storage.py --locate build/checkpoints/inventory-stack-og`.
- Workspace after PC adoption:29,986,738,143bytes, plus a few tiny later tools/
  notes. All new capture/build evidence is external. Latest/current and parent
  snapshots and all published ROMs remain protected. Public ROM hashes and
  player guide are unchanged. Never kill the user's Acrobat or user apps.

## PE discovery job completed

Exec session **70946** completed discovery for35other identities×Easy/Hard on the
current PC ROM; Mario3/Luigi3already have the four current-hash proofs above.
It exited1because its mixed aggregate contains failures. No native job from
this turn remains active. Continue with independent direct replays of passing
discoveries and targeted read-only controller corrections. Maximum two Mesen
instances at a time.

Output:
`C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-roster-pe/matrix-v1`.
Frozen controller:
`.../2026-10-24-roster-pe/policy-v1/policy.lua`, SHA
`f4e84baefbafa94986a3a56ff1209fd135549d24eb2ef58ba8749ccdfd4f61cc`.
Prepared by `bind_roster_controls_pe.py`; no game-memory/physics/equipment grants.
Do not alter this frozen policy or its evidence.

Final PE result:70attempts,53clean discoveries,17failures. The final mixed
`discover-results.json` remains false and retained. Those53are not independently
replayed passes. With PC's separate four SMB3proofs, all37identities have now
been attempted in both modes on PC:57clean discoveries, four strict independent
direct pairs. Do not call this a57pair replay pass.

PE failed pairs: Mario Easy/Hard; Mega/Proto Easy; Samus Hard; Link Easy/Hard;
ZeldaII Easy/Hard; Grant Easy/Hard; Pit Hard; Rygar Hard; Bass Hard; Chip Easy/Hard;
Dale Hard. Dale Easy now clears. Use the unchanged final index for exact fields.

## Controller follow-up: avoid repeating known regressions

PE inherits broad OO grounded-A/ledge changes. It therefore reintroduces some
controller failures for identities that already passed with OM controls. These
are not evidence that the two M3-only operand changes damaged those characters.
Prepare a new frozen per-identity/mode controller and rerun only failed current
pairs after the ongoing job ends. Do not mutate PE or erase its failures.

Use the old explicitly proven controls where applicable:

- OM44positive keys: external `2026-10-24-matrix-om/strict-guarded-v1/proof.json`,
  with `.../policies-v3/policy.lua` SHA
  `550622acf3b3f7ddc3fea34eefb6180e11697578292825ccc152bd936153ea06`.
  Includes Mario Easy, both Mega/Proto modes, Pit Hard and the ordinary heroes.
- OO5additional keys: `.../strict-guarded-followup-v1/proof.json` and
  `.../failed-policies-v1/policy.lua` SHA
  `2f4d57be9fb1068cb6ec59e7dbc66270cc1c2df4fa9ec4b353702c9da30aa276`.
  Luigi both, Samus Easy, Bass Easy, Ryu Easy.
- OV OZ: `2026-10-24-render-dispatch-ov/controls-oz-v1/policy.lua`, SHA
  `c2c0ab326f04551dd791c124b378a3471fc1fad2ee163c3f68fc1be1ad503671`.
  Stopping empty-floor B spam produced clean Ryu/Sypha/Alucard Hard discoveries;
  Sypha Hard has an exact strict direct replay on OV. Current PE also uses OZ.
  Grant still fails. Ryu Easy OV raw strict trace has an unresolved large-step
  rejection; do not turn it into a pass without a positive probe observation.
- Sophia's pinned original controller SHA
  `7967e15b2889e316f217f52316191e1c2a566029547f033b66819798b4be0586`
  already overrides PE's generic policy; both OV modes have guarded/direct
  strict clears. Darkwing's physical Arrow-cache recovery policy is nested in
  OM/OZ. Its separate OL source SHA is
  `e73700bdc44a61ac8db66c6bb6eb1fffa8498a5f920919c43e273a8a60dd3f3a`.
- PC's four SMB3routes use OW SHA
  `cd7656ee1264658ae059563c14e22383ed9cfb0bd479e4c0406ae203c0be0308`.
  Ordinary solid flagpole base requires a real jump; it was a controller issue.

Hypotheses to investigate, not confirmed engine defects:

- Samus Hard still dies at2119/x897before the tall pipe, with low Goombas.
  `c.enemy()` picks nearest actors including hidden Piranhas. A nearer hidden
  plant may make the current crouch-beam helper stand up while low Goombas are
  still approaching. A read-only selector prioritizing real low threats, or a
  held crouch-shoot command, is a plausible controller correction. Demonstrate
  actual fields before attributing it to the game.
- Mario Hard's OO ledge target2440may be wrong for its approach/inertia. The
  original generic navigation (used by the passing Luigi controller) is worth
  trying. Do not assume small Mario's position origin moves to192: SMB terrain
  feet commonly retain the32px logical origin. Do not alter native physics.
- Link and ZeldaII's constant empty-floor B may also lock walking/jump timing,
  as it demonstrably did CV3/Ryu. Source movement/combat and failed footage must
  be checked; stopping idle attacks is a controller candidate, not a game fix.

## Reliable capture/review tools

Old `emu.takeScreenshot()` PNGs can lag actual emulation by1–2frames. Their
filenames do not prove physical-frame alignment. Old exact native input/trace,
DMA/CHR, CPU/IRQ and stack observations retain their independent validity.
The correction is in `direct-frame-capture-2026-10-24.md`.

- `capture_direct_replay_ot.py`: requires passing same-hash discovery; actual
  getScreenBuffer/PPU frame IDs, RGB verification, lossless raw gzip roundtrip,
  exact independent input/trace and zero-death movable1-2.
- `review_direct_route_pa.py`: original strict logical world<=8/camera0..4,
  visible scanline31, body CHR and direct-index hash checks. Optional positive
  `--guard` observations resolve only exact temporary projectile/block probes.
- `reproduce_sophia_lock_og.py --expect repaired --until-clear --movement`:
  generic read-only NMI/SMC/completed-loop/probe observer despite its name.
- `scan_direct_background_ox.py`: diagnostic only.0..8image alignment covers
  real skipped-publication catch-up; it does not relax gameplay bounds or prove
  no graphic defects. Empty candidate lists are not whole-graphics passes.
- `observe_failed_route_oy.py`: failed-prefix diagnosis after completed GameLoop,
  validated unexported-symbol aliases, one actual direct endpoint. First Sypha
  probe failed on an unexported field; retained, not a game defect. Original
  input/trace prefix must match exactly. Native control logs can be sampled;
  full current-hash clears still need independent verified replays.

Full every-item requirements/physical delivery/SFX/use/damage/expiry, all source
music/art/behavior gaps, heavy/ordinary lag, and complete oversizedMMC3remain
open. Legacy OP extraction has86Hard requirement rows for10identities only;
it is not a full roster inventory or test pass. Original TMNT native audio is
still staged/rejected on old performance. Current OV optimizations may create
enough headroom to revisit it, but current source/Gradius/last-bank ownership
must be audited and fresh native performance must pass before adoption.

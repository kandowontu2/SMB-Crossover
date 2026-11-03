# Bub landing fix and November 2 nightly

Installed ROM SHA-256:
`9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15`.
The Downloads nightly was replaced directly, without a backup. Before/after
patch guards found no same-name automatic patches. The sole IPS on GitHub's
Latest `Current` release reconstructs these exact bytes from clean headered
Super Mario Bros. (World). IPS SHA-256:
`08ac42e7613f8d236c621713bee7f1c4b280e991b692cf5f3e84f936a73630ec`.

The change resets the original Bub/Bob jump state after actual supported
landings. The 18-byte adapter replaces source-dead telemetry and existing
spare space, retaining the original movement component. Three owning spans
change 370 bytes after relinking; Sunny's five palette fixes remain exact.
No helper platforms, new RAM, carrier allocations or shared menu changes
were added for this fix. The menu already selects Bub/Bob through Mr. Gimmick.

Bub passes non-shortcut Hard 1-1 on both the candidate and the actual
Downloads launch: 13,471 physical frames, 5,257 Main updates, lives 2 to 2,
active 1-2. Both runs pass 61,844 source/hardware checks with zero failures,
17 natural enemy pops and six original bubble rides. The route clears all
four early pipes and all three gaps, using source-valid supported jumps and
brief retreats on the tall staircases. Both endpoint images were inspected.
The generic observer's `full_stage` field remains false; the authoritative
outer `full11.json` records actual active 1-2 and the complete route assertions.

Bob also passes non-shortcut Hard 1-1 on the same ROM: 13,513 physical
frames / 5,253 Main updates, lives 2 to 2, active 1-2. All four early pipes
and all three gaps pass, with 17 natural pops and six bubble rides; 61,696
source/hardware checks report zero failures. The endpoint was inspected.
The corrected controller requests fresh Right+B from the confirmed real
left wall, following the donor's movement-before-bubble-publication order.
This changes only controller inputs, with no ROM or physics changes.

The earlier Bob run failed its bounded rearm because actual source tile
probes stop a requested retreat at X647 rather than X644. That negative
and the historical v43 partial-route receipt remain unchanged. Bob's later
completed candidate run is preserved in
`docs/qa/checkpoints/2026-11-02/bob-full11-v45`. The actual Downloads full
route was tested as Bub; no actual Downloads Bob full-route claim is made.

The compact checkpoint is
`docs/qa/checkpoints/2026-11-02/bub-landing-delivery-v43`.
Candidate and Downloads receipts are retained separately. Earlier source
packets `bub-landing-v27` and `bub-landing-v35` remain dependencies; terminal
loose v28/v31/v34 capture paths removed after verified archiving are not live.

Idle/walk bridge performance, broader roster admission,
all powerups, shortcut/Easy runs and audio fidelity remain unfinished. Prince
of Persia and Donkey Kong Jr. are private integrations, not new unlocks here.

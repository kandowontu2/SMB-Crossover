# Steve: four natural stock pickups on the current nightly

The actual Downloads ROM `7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc`
passes the ordinary-input four-pickup replay. No ROM, actor data, pickup rules,
health, physics, platform placement or runtime state was changed for this test.
The same-name patch guard was clear before and after the Downloads launch.

Run through `run_bounded_build_v1.py` using the existing two-file
`build/metal-flower-native-1112` task, with the shared Mesen queue and capture
watchdog. The test created no capture files or images.

## Physical result

`replay_steve_star_current_1113.py --combat-chase` generates Lua
`92e1e53d2c08c9b7fd7924302c3cdea7891cd093a163dd68a31461fd883ad1ee`.
The native receipt is
`0583fdc07843afefa0dde6748ab57b2198cb1154d1a0c68bb0f2e2ed1640939c`.

- 4,065 physical frames; 2,130 active updates and 2,188 source projections.
- Four real preparations and four mature native collections in dynamic slot5.
- Preparation kinds0/3/1/2: first Alpha, hidden1UP, second Alpha, Star.
- First Alpha: block left336, collection actor336/120, player324/112.
- Hidden1UP: block left1024, collection actor1058/164, player1058/176.
  The native deferred award increments lives2 to3 exactly once. The observed
  old/new RMW bus writes are2/3, not two life awards.
- Second Alpha: block left1248, collection actor1248/120, player1236/112.
- Star: block left1616, collection actor1751/178, player1739/176; its actual
  collector grants the native timer and music, with actor erasure checked.
- After24 further source projections: X1742/Y176, source pattern5, HP6,
  lives3 and Star timer33. There is no life loss. HP4 before the chase becomes
  HP6 through ordinary gameplay; the controller never writes health.
- All three runtime owner identities and mounted bytes authenticate, and46
  sprite-DMA comparisons match. This replay stops after the Star continuation;
  it is not a second full-stage or zero-lag performance claim.

## Cause of the earlier replay failures

The old controls and negative receipts remain recorded in
`steve-four-pickups-native-followup-1113.md`. The separate current-ROM adapter
strictly reverses7ef to526 and then62 before binding the frozen controller.
It does not relax the frozen APIs or accept arbitrary successor ROMs.

Observation-only current Lua
`187ef3399a2319324f8dd9c66ba26b47301cbb4ae27dff636f7d58bbc43c04f2`
fails with receipt
`4894c95601a42a8834802b37f0dc2bb54be39a26029632d002ebab74cfae44dd`.
Its bounded trace proves that the attempted fresh-A jump actually occurs:
playerY176 at projection2028, Y166 at2032, apexY156 at2037 and grounded again
at2049. The head encounters the brick row while the Star rises above it.
This supersedes the earlier statement that no successful jump was established;
the short jump itself is observed, but it does not collect the Star.
Ground enemies then injure and kill Steve before that Star is collected.

The passing controller retains the two earlier approach-Goomba punches and
replaces the short jump with ordinary directional/B inputs to face and punch
nearby grounded enemies. It spends10 chase updates defending, then follows
the moving Star until its real contact. The chase horizon permits600 updates;
the same mature-item, native-collector, sound/music, source-pattern and life
assertions remain enforced. No item-erasure assertion was weakened.

The controller observes a bounded96-row trace in memory. Console reporting
includes only changes, while the receipt hash authenticates the full result.
Metadata mode compiles without launching Mesen or creating output files.

## Remaining scope

The current nightly already has an independently recorded full1-1 Steve clear
and private armor-combat qualification. This result closes the outstanding
physical four-stock-item route. It does not complete the overall101-identity
powerup/stage audit, and no new ROM or IPS delivery is implied by a controls-only
verification.

# Metal Storm combat integration

Installed nightly SHA256:
`fae2f7e83d4afe8aa54fd580715e241d1b9735610b2c465c2e63a4d6cb15c2e5`.

Original source shot slots2/3 now test native enemy contact through service34,
the real `HuWeaponTail` reached by `NrObjectWeaponTail`. Initial service4-only
integration passed direct CPU calls but failed native gameplay; that version
was never installed. Retain this distinction when interpreting earlier captures.

Normal shot rectangles use donor offsets [2,5,6,9]; upgraded slot2 uses
[0,15,0,15], slot3 [0,7,0,15]. These are checked against the original ROM tables.
The adapter uses the host's 16x24 enemy-body proxy and native fireball defeat
transaction, including score, SFX and drops. Platforms, firebars and items are
excluded. Original shot movement and aiming remain source-owned. Native
fireproof enemy behavior remains in effect; a complete source HP/armor mapping
is still unfinished.

Verification on the installed candidate:

- 300 rectangle boundary cases across camera/page positions through actual
  `HuWeaponTail`; native Goomba defeat, score100, smack SFX and source shot
  retirement checked. Six non-enemy object exclusions checked.
- Callback cost:1764 CPU cycles with no shots,2155–4173 in tested shot cases.
  Minimum standalone stack pointer150. These are callback measurements, not
  a Main/IRQ or whole-game lag qualification.
- Controller-only Mesen cold title/select/start, first Goomba defeat and
  worldX401 reached with both lives retained:1083 total frames.
  `build/metal-storm-shots-1101-v35/native-shot-tail/capture/result.json`.
  Defeat screenshot inspected; no ROM/RAM grants used in the controller run.
- Downloads bytes match candidate. Before/after automatic-patch guard passed.
  No backup created. User Mesen remained open; reopen to load changed bytes.

The predecessor's Metal death/respawn fix and Mario the Tank walking fix are
retained. Metal full1-1, all pickups/upgrades, source armor graphics/audio,
explosion artwork, idle/walking lag and any helper-platform needs remain open.
Next: continue the route beyond the first pipe; source jumping/gravity should
be exercised before deciding a platform is needed. Continue the rest of the
roster afterwards; this is not completion of the all-character objective.

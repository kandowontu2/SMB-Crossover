# Bullet Bill rapid-spawn repair

Guest whirlpool immunity cleared `Whirlpool_Flag` on every update, including dry areas. That byte is also `Cannon_Timer[0]`. The first cannon's native14-tick cooldown was reset to zero immediately after it fired, allowing repeated Bullet Bills a few frames apart.

The area-type check now precedes the guest-water branch. Dry areas leave the shared timer untouched; underwater behavior is retained. The same instructions were reordered, with no new RAM, no size growth and no moved old code/RAM labels. Header, CHR and rebuilt baseline ROMs remain identical. Dry dispatch also avoids the unnecessary guest check; this is a small common-path saving, not a claim that all lag is fixed.

## Native verification

- The permanent native regression passes112 cases on each mapper: all14 identities, both modes, all4 area types and all6 shared timer bytes. The old ROM fails precisely on guest character1, dry area1, timer14 overwritten with0.
- Mario water, Luigi's native whirlpool control, Bill water and Mega Man water pass on both mappers.
- The same2,200-frame controller stream selects5-2 and enables invincibility using the actual new menu. This is an explicitly cheated diagnostic, not a final route. The old MMC3 run is byte-identical to the original discovery trace, including cycles. The old run has26 fire attempts and26 forced cooldown clears; the new run has5 attempts, zero forced clears and56 native countdown writes. The minimum attempt interval changes from3 to118 physical frames in this specific stimulus. MMC5 produces the same repaired counts.
- Before and after each retain2,199 native video images and continuous real PCM audio. Both lossless RGB/PCM proofs pass. Full-frame review finds no motion, HUD split, vertical displacement or large background flash candidates in these bounded clips. Audio-ownership candidates are not a source-SFX certification. Multiple normally spaced native Bills remain allowed.

Evidence: `build/verification/cannon-repair-by/summary.json`; native recordings and controller inputs are under `build/roster-through-2-2/cannon-bx-before-3-v0-mmc3/` and `cannon-bx-after-3-v0-mmc3/`. The MMC5 read-only diagnostic is `cannon-bx-after-mmc5-3-v0-mmc5/`. Checkpoint: `build/checkpoints/cannon-cooldown-bz/manifest.json`.

Missing later-castle firebars remain unresolved. Earlier exact Mario/Bill movie replays show all seven1-4 firebars at the firebar OAM pass, but do not prove the later-castle report fixed. Diagnostic4-4 drivers currently fail at the first ceiling/gap combination before reaching the firebars; those negatives are retained. All other source-fidelity, private component composition, natural Hard upgrade showcases, lag optimization and final every-character recordings remain required. Lossless originals and negatives are retained under the user-authorized100GB cap.
